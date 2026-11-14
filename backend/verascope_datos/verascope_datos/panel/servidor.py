"""Panel visual de VeraScope.

Levanta un servidor que escucha SOLO en tu computadora (127.0.0.1) y muestra una página web con botones
para cada paso. Cada botón lanza el mismo comando que escribirías en la terminal, como un proceso aparte:
por eso cortar, reanudar y reintentar funcionan igual que en la terminal, y lo descargado nunca se pierde.
"""
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
import webbrowser
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from .. import __version__, config
from ..almacen import Casillero, lugar_celda
from ..variables import POWER, SATELITE, VARIABLES

AQUI = Path(__file__).parent
RAIZ_PAQUETE = AQUI.parents[1]                       # carpeta que contiene verascope_datos/
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
MARCA_PASO = re.compile(r"(\d)/6\s")                 # «3/6 Satélites…» en los títulos de «todo»
VEREDICTOS = ("cambio_robusto", "sensible_a_el_nino", "cambio_oculto", "sin_tendencia")
# Índice de El Niño con el que se compara la lluvia de cada demo. Piura responde al Niño costero
# (Niño 1+2, frente a Ecuador y el norte del Perú) más que al ONI del Pacífico central.
INDICE_ESPEJO = {"piura": "NINO12"}

ETIQUETAS = {
    "indices": "Índices de El Niño (NOAA)",
    "power": "NASA POWER",
    "satelites": "Satélites (GPM, GLDAS, MODIS)",
    "calcular": "Cálculo de tendencias",
    "demos": "Respaldo de las demos",
    "empaquetar": "Paquete para el equipo",
    "instalar": "Instalación del paquete recibido",
    "probar_sesion": "Prueba de tu cuenta de NASA",
    "prueba_rapida": "Prueba rápida",
    "todo": "Todo el proceso",
}
ORDEN_PASOS = ["indices", "power", "satelites", "calcular", "demos", "empaquetar"]


class ErrorPanel(Exception):
    def __init__(self, mensaje, codigo=400):
        super().__init__(mensaje)
        self.codigo = codigo


def _carpeta_valida(texto):
    p = Path(str(texto)).expanduser()
    if not p.is_dir():
        raise ErrorPanel(f"No encuentro la carpeta: {texto}")
    return str(p.resolve())


def plan(orden, o):
    """Traduce un botón del panel en uno o varios comandos: [(paso, argumentos del comando)]."""
    o = o or {}
    if orden == "indices":
        a = ["indices"] + (["--carpeta", _carpeta_valida(o["carpeta"])] if o.get("carpeta") else [])
        return [("indices", a)]
    if orden in ("power", "todo"):
        a = [orden]
        if o.get("solo_demos"):
            a.append("--solo-demos")
        if o.get("limite"):
            a += ["--limite", str(int(o["limite"]))]
        if orden == "todo":
            return [("todo", a)]
        return [("power", a)]
    if orden == "satelites":
        a = ["satelites"]
        solo = [x for x in (o.get("solo") or []) if x in ("imerg", "gldas", "ndvi")]
        if solo:
            a += ["--solo", ",".join(solo)]
        if o.get("archivos_locales"):
            a += ["--archivos-locales", _carpeta_valida(o["archivos_locales"])]
        return [("satelites", a)]
    if orden in ("calcular", "demos", "empaquetar"):
        return [(orden, [orden])]
    if orden == "prueba_rapida":
        return [("indices", ["indices"]), ("power", ["power", "--solo-demos"])]
    if orden == "instalar":
        f = Path(str(o.get("paquete", ""))).expanduser()
        if not f.is_file():
            raise ErrorPanel("No encuentro el archivo del paquete.")
        return [("instalar", ["instalar", str(f.resolve())])]
    if orden == "probar_sesion":
        return [("probar_sesion", None)]
    raise ErrorPanel("Orden desconocida.")


class Trabajos:
    """Corre un trabajo a la vez como proceso aparte, guarda su registro y permite detenerlo."""

    def __init__(self, rutas):
        self.rutas = rutas
        self.cred = {}
        self.lock = threading.Lock()
        self.lineas = deque(maxlen=4000)
        self.total = 0
        self.proc = None
        self.hilo = None
        self.detener_pedido = False
        self.info = dict(corriendo=False, orden=None, etiqueta=None, paso=None, inicio=None, fin=None,
                         codigo=None, detenido=False, deteniendo=False, resumen=None, numero=0)

    # ---------------------------------------------------------------- registro
    def escribir(self, texto):
        with self.lock:
            for l in str(texto).splitlines() or [""]:
                self.lineas.append(l); self.total += 1

    def leer_registro(self, desde):
        with self.lock:
            ini = self.total - len(self.lineas)
            desde = max(desde, ini)
            return list(self.lineas)[desde - ini:], self.total

    def paso_activo(self):
        with self.lock:
            i = dict(self.info)
            if not i["corriendo"]:
                return None
            if i["paso"] != "todo":
                return i["paso"]
            ultimo = 1
            for l in self.lineas:
                m = MARCA_PASO.match(l.lstrip(" ─-"))
                if m:
                    ultimo = int(m.group(1))
            return ORDEN_PASOS[min(max(ultimo, 1), 6) - 1]

    def estado(self):
        with self.lock:
            i = dict(self.info)
        i["paso_activo"] = self.paso_activo()
        i["registro"] = self.total
        return i

    # ---------------------------------------------------------------- ejecución
    def iniciar(self, orden, opciones):
        pasos = plan(orden, opciones)
        with self.lock:
            if self.info["corriendo"]:
                raise ErrorPanel("Ya hay un trabajo en marcha. Espera a que termine o detenlo.", 409)
            self.info.update(corriendo=True, orden=orden, etiqueta=ETIQUETAS.get(orden, orden), paso=pasos[0][0],
                             inicio=time.time(), fin=None, codigo=None, detenido=False, deteniendo=False, resumen=None,
                             numero=self.info["numero"] + 1)
            self.detener_pedido = False
        self.hilo = threading.Thread(target=self._correr, args=(orden, pasos), daemon=True)
        self.hilo.start()

    def _entorno(self):
        e = dict(os.environ)
        e.update(PYTHONIOENCODING="utf-8", PYTHONUNBUFFERED="1", NO_COLOR="1", TERM="dumb", COLUMNS="110",
                 PYTHONPATH=str(RAIZ_PAQUETE) + os.pathsep + e.get("PYTHONPATH", ""))
        if self.cred.get("usuario") and self.cred.get("clave"):
            e["EARTHDATA_USERNAME"] = self.cred["usuario"]; e["EARTHDATA_PASSWORD"] = self.cred["clave"]
        return e

    def _correr(self, orden, pasos):
        t0 = time.time(); codigo = 0; fallas = 0
        self.escribir(f"▶ {ETIQUETAS.get(orden, orden)}")
        for clave, argumentos in pasos:
            with self.lock:
                self.info["paso"] = clave
            if len(pasos) > 1:
                self.escribir(f"── {ETIQUETAS.get(clave, clave)}")
            if argumentos is None:
                cmd = [sys.executable, "-u", "-m", "verascope_datos.panel.probar_sesion"]
            else:
                cmd = [sys.executable, "-u", "-m", "verascope_datos", "--datos", str(self.rutas.base.resolve()),
                       "--fin", str(config.ANIO_FIN), *argumentos]
            extra = {"start_new_session": True} if os.name != "nt" else \
                {"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW}
            try:
                self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                             env=self._entorno(), **extra)
            except Exception as e:
                self.escribir(f"✘ No pude arrancar el programa: {e}"); codigo = 1
                break
            for crudo in self.proc.stdout:
                linea = ANSI.sub("", crudo.decode("utf-8", "replace").rstrip("\r\n"))
                fallas += "✘" in linea
                self.escribir(linea)
            codigo = self.proc.wait()
            if codigo != 0 or self.detener_pedido:
                break
        dur = time.time() - t0
        detenido = self.detener_pedido
        if detenido:
            resumen = "Detenido. Lo descargado quedó guardado: al volver a ejecutar, sigue donde se quedó."
        elif codigo == 0 and fallas:
            codigo = 1
            resumen = f"Terminó en {self._duracion(dur)}, pero algo falló. Revisa el registro de abajo."
        elif codigo == 0:
            resumen = f"Terminó bien en {self._duracion(dur)}."
        else:
            resumen = f"Terminó con errores (código {codigo}). Mira el registro de abajo."
        self.escribir(("■ " if codigo == 0 or detenido else "✘ ") + resumen)
        with self.lock:
            self.info.update(corriendo=False, fin=time.time(), codigo=codigo, detenido=detenido, deteniendo=False, resumen=resumen)
            self.proc = None

    @staticmethod
    def _duracion(s):
        return f"{s:.0f} s" if s < 90 else (f"{s / 60:.0f} min" if s < 5400 else f"{s / 3600:.1f} h")

    def detener(self):
        """Pide detener el trabajo y vuelve al instante; el proceso se corta en segundo plano."""
        p = self.proc
        if p is None or p.poll() is not None:
            return False
        if self.detener_pedido:
            return True
        self.detener_pedido = True
        with self.lock:
            self.info["deteniendo"] = True
        self.escribir("… deteniendo (lo ya descargado queda guardado)")
        threading.Thread(target=self._matar, args=(p,), daemon=True).start()
        return True

    def detener_y_esperar(self, segundos=20):
        if self.detener() and self.hilo:
            self.hilo.join(segundos)

    @staticmethod
    def _matar(p):
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(p.pid), "/T", "/F"], capture_output=True)
                return
            os.killpg(p.pid, signal.SIGINT)                      # como Ctrl+C: el programa guarda y sale
            for senal, espera in ((None, 8), (signal.SIGTERM, 4), (signal.SIGKILL, 2)):
                if senal:
                    os.killpg(p.pid, senal)
                try:
                    p.wait(timeout=espera)
                    return
                except subprocess.TimeoutExpired:
                    continue
        except (ProcessLookupError, PermissionError):
            pass


class Panel:
    """Lo que el panel sabe leer del casillero y de los resultados (solo lectura, sin tocar nada)."""

    def __init__(self, rutas):
        self.rutas = rutas
        self.trabajos = Trabajos(rutas)
        self._cache = {}

    # ---------------------------------------------------------------- lectura barata del casillero
    def _consultar(self, sql, args=()):
        import sqlite3
        if not self.rutas.casillero.exists():
            return []
        db = sqlite3.connect(self.rutas.casillero, timeout=30)
        try:
            return db.execute(sql, args).fetchall()
        except sqlite3.OperationalError:
            return []
        finally:
            db.close()

    def _con_cache(self, clave, segundos, fn):
        t, v = self._cache.get(clave, (0, None))
        if time.time() - t > segundos:
            v = fn(); self._cache[clave] = (time.time(), v)
        return v

    def _total_power(self):
        return self._con_cache("total", 3600, lambda: len(config.rejilla()) + len(config.LUGARES_DEMO))

    def _detalle_series(self):
        def f():
            return {v: (ini, largo, act) for v, ini, largo, act in self._consultar(
                "SELECT variable, MIN(inicio), MAX(n), MAX(actualizado) FROM series GROUP BY variable")}
        return self._con_cache("detalle", 20, f)

    def credenciales(self):
        if self.trabajos.cred.get("usuario"):
            return {"definidas": True, "origen": "panel"}
        if os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"):
            return {"definidas": True, "origen": "entorno"}
        for n in (".netrc", "_netrc"):
            try:
                if "urs.earthdata.nasa.gov" in (Path.home() / n).read_text(errors="ignore"):
                    return {"definidas": True, "origen": "netrc"}
            except OSError:
                pass
        return {"definidas": False, "origen": "ninguna"}

    def estado(self):
        r = self.rutas
        todos = dict(self._consultar("SELECT variable, COUNT(*) FROM series GROUP BY variable"))
        demos = dict(self._consultar("SELECT variable, COUNT(*) FROM series WHERE lugar LIKE 'demo:%' GROUP BY variable"))
        detalle = self._detalle_series()
        total, n_demo = self._total_power(), len(config.LUGARES_DEMO)
        variables = []
        for v in VARIABLES:
            if v.capa == "vivo":
                hecho, tot = todos.get(v.codigo, 0), total
            elif v.capa == "precalculada":
                hecho, tot = demos.get(v.codigo, 0), n_demo
            else:
                hecho, tot = todos.get(v.codigo, 0), 1
            ini, largo, act = detalle.get(v.codigo, (None, 0, None))
            variables.append(dict(id=v.id, codigo=v.codigo, nombre=v.nombre, unidad=v.unidad, capa=v.capa, fuente=v.fuente,
                                  desde=v.desde, nota=v.nota, hecho=hecho, total=tot, inicio=ini, meses=largo, actualizado=act))
        por = {v["codigo"]: v for v in variables}
        n_resul = r.resultados.exists()
        demos_json = len(list(r.demos.glob("*.json"))) if r.demos.exists() else 0
        paquetes = sorted(r.paquetes.glob("*.tar.gz"), key=lambda f: f.stat().st_mtime) if r.paquetes.exists() else []
        satelites = sum(min(por[c]["hecho"], n_demo) for c in SATELITE)

        def est(h, t):
            return "listo" if h >= t else ("parcial" if h > 0 else "pendiente")

        indices = sum(1 for c in ("ONI", "NINO12", "CO2") if por[c]["hecho"])
        pasos = [
            dict(id="indices", hecho=indices, total=3, estado=est(indices, 3)),
            dict(id="power", hecho=por["PRECTOTCORR"]["hecho"], total=total, demos=demos.get("PRECTOTCORR", 0),
                 estado=est(por["PRECTOTCORR"]["hecho"], total)),
            dict(id="satelites", hecho=satelites, total=len(SATELITE) * n_demo, estado=est(satelites, len(SATELITE) * n_demo)),
            dict(id="calcular", hecho=int(n_resul), total=1, estado="listo" if n_resul else "pendiente",
                 actualizado=r.resultados.stat().st_mtime if n_resul else None),
            dict(id="demos", hecho=demos_json, total=n_demo, estado=est(demos_json, n_demo)),
            dict(id="empaquetar", hecho=len(paquetes), total=1, estado="listo" if paquetes else "pendiente",
                 archivo=paquetes[-1].name if paquetes else None, peso=paquetes[-1].stat().st_size if paquetes else None),
        ]
        fallos = self._consultar("SELECT tarea, lugar, error, cuando FROM fallos ORDER BY cuando DESC LIMIT 30")
        n_fallos = (self._consultar("SELECT COUNT(*) FROM fallos") or [(0,)])[0][0]
        return dict(version=__version__, datos=str(r.base.resolve()), ventana=[config.ANIO_INICIO, config.ANIO_FIN],
                    pasos=pasos, variables=variables, credenciales=self.credenciales(), trabajo=self.trabajos.estado(),
                    fallos=[dict(tarea=a, lugar=b, error=c, cuando=d) for a, b, c, d in fallos], n_fallos=n_fallos,
                    demos=[dict(id=l.id, nombre=l.nombre, lat=l.lat, lon=l.lon) for l in config.LUGARES_DEMO],
                    rejilla=self.meta_rejilla())

    def meta_rejilla(self):
        import numpy as np
        lats = np.arange(config.REJILLA_LAT[0], config.REJILLA_LAT[1] + 1e-9, config.REJILLA_PASO)
        lons = np.arange(config.REJILLA_LON_0_360[0], config.REJILLA_LON_0_360[1] + 1e-9, config.REJILLA_PASO)
        return dict(lat0=float(lats[0]), lat1=float(lats[-1]), lon0=float(lons[0]), lon1=float(lons[-1]),
                    paso=config.REJILLA_PASO, nlat=int(lats.size), nlon=int(lons.size))

    # ---------------------------------------------------------------- mapa
    def mapa_descarga(self):
        nombres = {x[0] for x in self._consultar("SELECT lugar FROM series WHERE variable='PRECTOTCORR' AND lugar LIKE 'celda:%'")}
        return "".join("1" if lugar_celda(la, lo) in nombres else "0" for la, lo in config.rejilla())

    def _resultados(self):
        f = self.rutas.resultados
        if not f.exists():
            return None
        marca = f.stat().st_mtime
        if self._cache.get("res_marca") != marca:
            import pandas as pd
            self._cache["res"] = pd.read_parquet(f, columns=["variable", "celda", "veredicto", "pareja", "ventana"])
            self._cache["res_marca"] = marca
        return self._cache["res"]

    def mapa_resultados(self, variable):
        df = self._resultados()
        if df is None:
            return None
        import numpy as np
        n = len(config.rejilla())
        out = np.zeros(n, dtype="U1"); out[:] = "0"
        codigo = {v: str(k + 1) for k, v in enumerate(VEREDICTOS)}
        g = df[df.variable == variable]
        for k, v in zip(g.celda.to_numpy(), g.veredicto.to_numpy()):
            if 0 <= k < n:
                out[k] = codigo.get(v, "0")
        return "".join(out)

    def resumen_resultados(self):
        df = self._resultados()
        if df is None:
            return {"disponible": False}
        vars_ = {}
        for cod, g in df.groupby("variable"):
            c = g.veredicto.value_counts()
            vars_[cod] = {k: int(c.get(k, 0)) for k in VEREDICTOS}
        return {"disponible": True, "ventana": str(df.ventana.iloc[0]), "variables": vars_,
                "pares": int(df.pareja.notna().sum() // 2)}

    # ---------------------------------------------------------------- chequeo Piura / Borneo
    def espejo(self):
        import numpy as np
        import pandas as pd
        from .. import motor
        if not self.rutas.casillero.exists():
            return {"disponible": False, "falta": "Todavía no hay nada descargado."}
        meses = config.meses(); cal = np.array([int(m[5:7]) for m in meses])
        cas = Casillero(self.rutas.casillero)
        try:
            oni = cas.leer_alineada("ONI", "indice", meses)
            if np.isfinite(oni).sum() < 120:
                return {"disponible": False, "falta": "Faltan los índices de El Niño (paso 1)."}
            indices = {"ONI": oni, "NINO12": cas.leer_alineada("NINO12", "indice", meses)}
            series = []
            for l in config.LUGARES_DEMO:
                s = cas.leer_alineada("PRECTOTCORR", f"demo:{l.id}", meses)
                if np.isfinite(s).sum() < 120:
                    continue
                a = motor.anomalias(s, cal)
                indice = INDICE_ESPEJO.get(l.id, "ONI")
                if np.isfinite(indices[indice]).sum() < 120:
                    indice = "ONI"
                e = indices[indice]
                mejor = None
                for L in range(7):
                    x, y = e[: len(a) - L], a[L:]
                    ok = np.isfinite(x) & np.isfinite(y)
                    if ok.sum() > 60:
                        r = float(np.corrcoef(x[ok], y[ok])[0, 1])
                        if mejor is None or abs(r) > abs(mejor[1]):
                            mejor = (L, r)
                if mejor:
                    series.append((l, a, mejor, indice))
        finally:
            cas.cerrar()
        if not series:
            return {"disponible": False, "falta": "Falta la lluvia de Piura y Borneo (paso 2, aunque sea la prueba rápida)."}

        def suave(v):
            z = pd.Series(v).rolling(3, center=True, min_periods=2).mean().to_numpy()
            return z / np.nanstd(z)

        def lista(v):
            return [None if not np.isfinite(x) else round(float(x), 2) for x in v]
        umbral = {"piura": ("sube", 0.25), "borneo": ("baja", -0.25), "norte_australia": ("baja", -0.15)}
        return {"disponible": True, "meses": meses, "oni": lista(suave(oni)),
                "series": [dict(id=l.id, nombre=l.nombre, valores=lista(suave(a)), rezago=int(m[0]), r=round(m[1], 2),
                                coherente=(m[1] > umbral[l.id][1] if umbral[l.id][0] == "sube" else m[1] < umbral[l.id][1]),
                                esperado=umbral[l.id][0], indice=ind) for l, a, m, ind in series]}

    # ---------------------------------------------------------------- utilidades
    def abrir_carpeta(self):
        ruta = str(self.rutas.base.resolve())
        if sys.platform.startswith("win"):
            os.startfile(ruta)                                                   # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Manejador(BaseHTTPRequestHandler):
    server_version = "VeraScopePanel"
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    # ---------------------------------------------------------------- ayudas
    def _enviar(self, cuerpo, tipo="application/json; charset=utf-8", codigo=200):
        datos = cuerpo if isinstance(cuerpo, bytes) else cuerpo.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(datos)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(datos)

    def _json(self, obj, codigo=200):
        self._enviar(json.dumps(obj, ensure_ascii=False), codigo=codigo)

    def _host_ok(self):
        return self.headers.get("Host", "").split(":")[0] in ("127.0.0.1", "localhost")

    def _token_ok(self):
        return secrets.compare_digest(self.headers.get("X-Token", ""), self.server.token)

    def _vaciar(self):
        """Lee y descarta el cuerpo que nadie usó, para no ensuciar la siguiente petición de la misma conexión."""
        n = int(self.headers.get("Content-Length") or 0)
        if n > 8 * 1024 * 1024:
            self.close_connection = True
            return
        while n > 0:
            trozo = self.rfile.read(min(65536, n))
            if not trozo:
                break
            n -= len(trozo)

    def _cuerpo_json(self):
        self._leido = True
        n = int(self.headers.get("Content-Length") or 0)
        if n > 65536:
            raise ErrorPanel("Cuerpo demasiado grande.", 413)
        return json.loads(self.rfile.read(n) or b"{}") if n else {}

    def _atender(self, fn):
        try:
            if not self._host_ok():
                raise ErrorPanel("Host no permitido.", 403)
            fn()
        except ErrorPanel as e:
            self._json({"error": str(e)}, e.codigo)
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:                                                   # el panel nunca debe caerse
            try:
                self._json({"error": f"Error interno: {e}"}, 500)
            except Exception:
                pass

    # ---------------------------------------------------------------- GET
    def do_GET(self):
        self._atender(self._get)

    def _get(self):
        u = urlparse(self.path); q = parse_qs(u.query); panel = self.server.panel
        if u.path in ("/", "/index.html"):
            html = (AQUI / "pagina.html").read_text(encoding="utf-8")
            html = (html.replace("/*__FUENTES__*/", (AQUI / "fuentes.css").read_text())
                    .replace("__TOKEN__", self.server.token).replace("__VERSION__", __version__)
                    .replace("__TIERRA__", (AQUI / "tierra.txt").read_text()))
            return self._enviar(html, "text/html; charset=utf-8")
        if u.path in ("/logo.svg", "/favicon.ico", "/favicon.svg"):
            return self._enviar((AQUI / "logo.svg").read_bytes(), "image/svg+xml")
        if not u.path.startswith("/api/"):
            raise ErrorPanel("No encontrado.", 404)
        if not self._token_ok():
            raise ErrorPanel("Sin permiso.", 403)
        if u.path == "/api/estado":
            return self._json(panel.estado())
        if u.path == "/api/log":
            lineas, total = panel.trabajos.leer_registro(int(q.get("desde", ["0"])[0]))
            return self._json({"lineas": lineas, "siguiente": total})
        if u.path == "/api/mapa":
            capa = q.get("capa", ["descarga"])[0]
            if capa == "resultados":
                cel = panel.mapa_resultados(q.get("variable", ["T2M"])[0])
                return self._json({"capa": capa, "celdas": cel, "disponible": cel is not None})
            return self._json({"capa": "descarga", "celdas": panel.mapa_descarga(), "disponible": True})
        if u.path == "/api/resultados":
            return self._json(panel.resumen_resultados())
        if u.path == "/api/espejo":
            return self._json(panel.espejo())
        raise ErrorPanel("No encontrado.", 404)

    # ---------------------------------------------------------------- POST
    def do_POST(self):
        self._leido = False
        self._atender(self._post)
        if not self._leido:
            try:
                self._vaciar()
            except (OSError, ValueError):
                self.close_connection = True

    def _post(self):
        panel = self.server.panel; ruta = urlparse(self.path).path
        if not self._token_ok():
            raise ErrorPanel("Sin permiso.", 403)
        if ruta == "/api/ejecutar":
            c = self._cuerpo_json()
            panel.trabajos.iniciar(str(c.get("orden", "")), c.get("opciones") or {})
            return self._json({"ok": True})
        if ruta == "/api/detener":
            return self._json({"ok": panel.trabajos.detener()})
        if ruta == "/api/credenciales":
            c = self._cuerpo_json()
            u, p = str(c.get("usuario", "")).strip(), str(c.get("clave", ""))
            if not u or not p:
                panel.trabajos.cred.clear()
            else:
                panel.trabajos.cred.update(usuario=u, clave=p)
            return self._json({"ok": True, **panel.credenciales()})
        if ruta == "/api/abrir_carpeta":
            panel.abrir_carpeta()
            return self._json({"ok": True})
        if ruta == "/api/subir_paquete":
            nombre = Path(self.headers.get("X-Nombre", "paquete.tar.gz")).name
            if not re.search(r"\.(tar\.gz|tgz)$", nombre, re.I):
                raise ErrorPanel("El paquete debe ser un archivo .tar.gz")
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > 4 * 1024 ** 3:
                raise ErrorPanel("Tamaño de archivo no válido.")
            self._leido = True
            carpeta = panel.rutas.paquetes / "recibidos"; carpeta.mkdir(parents=True, exist_ok=True)
            destino = carpeta / nombre; falta = n
            with open(destino, "wb") as f:
                while falta:
                    trozo = self.rfile.read(min(1 << 20, falta))
                    if not trozo:
                        break
                    f.write(trozo); falta -= len(trozo)
            if falta:
                destino.unlink(missing_ok=True)
                raise ErrorPanel("La subida se interrumpió; vuelve a intentarlo.")
            panel.trabajos.iniciar("instalar", {"paquete": str(destino)})
            return self._json({"ok": True})
        if ruta == "/api/apagar":
            if panel.trabajos.estado()["corriendo"]:
                raise ErrorPanel("Hay un trabajo en marcha: detenlo antes de apagar el panel.", 409)
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return self._json({"ok": True})
        raise ErrorPanel("No encontrado.", 404)


def crear_servidor(rutas, puerto=8765):
    """Crea el servidor en 127.0.0.1 (solo tu computadora). Con puerto 0 elige uno libre."""
    srv = None
    for p in ([puerto] if puerto == 0 else range(puerto, puerto + 30)):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", p), Manejador)
            break
        except OSError:
            continue
    if srv is None:
        raise OSError(f"No encontré un puerto libre desde {puerto}.")
    srv.daemon_threads = True
    srv.token = secrets.token_urlsafe(24)
    srv.panel = Panel(rutas)
    return srv


def servir(rutas, puerto=8765, abrir=True):
    srv = crear_servidor(rutas, puerto)
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"\n  VeraScope · Centro de datos\n  Abre esta dirección en el navegador:  {url}\n"
          f"  Para apagarlo: botón «Apagar panel» de la página, o cierra esta ventana (Ctrl+C).\n", flush=True)
    if abrir:
        threading.Timer(0.8, webbrowser.open, (url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.panel.trabajos.detener_y_esperar()
        srv.server_close()
