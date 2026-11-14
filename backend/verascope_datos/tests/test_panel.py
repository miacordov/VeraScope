"""El panel visual: seguridad, ejecución de pasos como procesos, registro, detener y lectura de resultados."""
import json
import re
import threading
import time
import urllib.error
import urllib.request

import pytest

from verascope_datos import cli, config
from verascope_datos.panel.servidor import crear_servidor

from . import simulados


class Cliente:
    def __init__(self, base, token, srv):
        self.base, self.token, self.srv = base, token, srv

    def pedir(self, ruta, cuerpo=None, token=True, cabeceras=None, datos=None):
        h = {"Content-Type": "application/json", **(cabeceras or {})}
        if token:
            h["X-Token"] = self.token
        if cuerpo is not None:
            datos = json.dumps(cuerpo).encode()
        req = urllib.request.Request(self.base + ruta, data=datos, headers=h, method="POST" if datos is not None or cuerpo is not None else "GET")
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read() or b"{}")

    def esperar_fin(self, limite=90):
        t0 = time.time()
        while time.time() - t0 < limite:
            e = self.pedir("/api/estado")[1]
            if not e["trabajo"]["corriendo"]:
                return e
            time.sleep(0.4)
        raise AssertionError("el trabajo no terminó")

    def registro(self):
        return "\n".join(self.pedir("/api/log?desde=0")[1]["lineas"])


@pytest.fixture
def panel(tmp_path, monkeypatch):
    anio, paso = config.ANIO_FIN, config.REJILLA_PASO
    config.ANIO_FIN, config.REJILLA_PASO = 2024, 2.0
    monkeypatch.setenv("VERASCOPE_POWER_URL", "http://127.0.0.1:9/")        # puerto cerrado: nunca toca la red real
    rutas = config.rutas(tmp_path / "datos")
    srv = crear_servidor(rutas, 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    html = urllib.request.urlopen(base + "/").read().decode()
    assert "__TOKEN__" not in html and "__TIERRA__" not in html and "/*__FUENTES__*/" not in html
    token = re.search(r'const TOKEN = "([^"]+)"', html).group(1)
    yield Cliente(base, token, srv)
    srv.panel.trabajos.detener_y_esperar()
    srv.shutdown(); srv.server_close()
    config.ANIO_FIN, config.REJILLA_PASO = anio, paso


def test_seguridad(panel):
    assert panel.pedir("/api/estado", token=False)[0] == 403
    assert panel.pedir("/api/ejecutar", {"orden": "indices"}, token=False)[0] == 403
    assert panel.pedir("/api/estado", cabeceras={"Host": "sitio-malo.com"})[0] == 403         # contra DNS rebinding
    assert panel.pedir("/api/ejecutar", {"orden": "rm -rf"})[0] == 400                        # solo órdenes conocidas
    assert panel.pedir("/api/ejecutar", {"orden": "indices", "opciones": {"carpeta": "/no/existe"}})[0] == 400


def test_estado_inicial(panel):
    e = panel.pedir("/api/estado")[1]
    assert [p["id"] for p in e["pasos"]] == ["indices", "power", "satelites", "calcular", "demos", "empaquetar"]
    assert all(p["estado"] == "pendiente" for p in e["pasos"])
    assert len(e["variables"]) == 13 and e["rejilla"]["nlat"] * e["rejilla"]["nlon"] == 4235
    assert e["trabajo"]["corriendo"] is False


def test_ejecutar_indices_y_registro(panel, tmp_path):
    simulados.textos_noaa(tmp_path / "noaa")
    assert panel.pedir("/api/ejecutar", {"orden": "indices", "opciones": {"carpeta": str(tmp_path / "noaa")}})[0] == 200
    e = panel.esperar_fin()
    assert e["trabajo"]["codigo"] == 0 and e["pasos"][0]["estado"] == "listo"
    log = panel.registro()
    assert "▶ Índices de El Niño" in log and "✔ ONI" in log and "■ Terminó bien" in log


def test_detener_y_un_trabajo_a_la_vez(panel):
    assert panel.pedir("/api/ejecutar", {"orden": "power", "opciones": {"solo_demos": True}})[0] == 200
    t0 = time.time()
    while "NASA POWER:" not in panel.registro() and time.time() - t0 < 30:
        time.sleep(0.3)
    assert panel.pedir("/api/ejecutar", {"orden": "indices"})[0] == 409                          # ya hay uno en marcha
    assert panel.pedir("/api/detener", {})[1]["ok"] is True
    e = panel.esperar_fin(30)
    assert e["trabajo"]["detenido"] is True
    assert "Detenido" in panel.registro()


def test_cuenta_no_se_filtra(panel):
    r = panel.pedir("/api/credenciales", {"usuario": "ana", "clave": "secreto-123"})[1]
    assert r["definidas"] is True and r["origen"] == "panel"
    assert "secreto-123" not in json.dumps(panel.pedir("/api/estado")[1])
    assert panel.pedir("/api/credenciales", {"usuario": "", "clave": ""})[1]["origen"] != "panel"


def test_espejo_y_mapa_con_datos(panel, tmp_path):
    assert panel.pedir("/api/espejo")[1]["disponible"] is False
    r = config.rutas(tmp_path / "datos")
    simulados.textos_noaa(tmp_path / "noaa")
    cli.main(["--datos", str(r.base), "--fin", "2024", "indices", "--carpeta", str(tmp_path / "noaa")])
    original = cli.cmd_power
    cli.cmd_power = lambda a, rr: original(a, rr, cliente=simulados.PowerFalso())
    try:
        cli.main(["--datos", str(r.base), "--fin", "2024", "power", "--solo-demos", "--pausa", "0"])
    finally:
        cli.cmd_power = original
    d = panel.pedir("/api/espejo")[1]
    assert d["disponible"] and len(d["oni"]) == len(d["meses"])
    por = {s["id"]: s for s in d["series"]}
    assert por["piura"]["r"] > 0.5 and por["piura"]["coherente"]                                   # El Niño: más lluvia en Piura
    assert por["piura"]["indice"] == "NINO12" and por["borneo"]["indice"] == "ONI"                 # Piura se mide con el Niño costero
    assert por["borneo"]["r"] < -0.5 and por["borneo"]["coherente"]                                # y menos en Borneo
    m = panel.pedir("/api/mapa?capa=descarga")[1]["celdas"]
    assert len(m) == 4235 and set(m) == {"0"}                                                      # demos listas, rejilla vacía
    e = panel.pedir("/api/estado")[1]
    assert e["pasos"][1]["demos"] == 3 and e["pasos"][1]["estado"] == "parcial"


def test_subida_de_paquete_no_sale_de_su_carpeta(panel):
    assert panel.pedir("/api/subir_paquete", datos=b"x", cabeceras={"X-Nombre": "virus.exe", "Content-Type": "application/octet-stream"})[0] == 400
    s, _ = panel.pedir("/api/subir_paquete", datos=b"no es un tar", cabeceras={"X-Nombre": "../../fuera.tar.gz", "Content-Type": "application/octet-stream"})
    assert s == 200
    e = panel.esperar_fin()
    assert e["trabajo"]["codigo"] != 0                                                             # no es un paquete válido: error claro
    assert (panel.srv.panel.rutas.paquetes / "recibidos" / "fuera.tar.gz").exists()
    assert not (panel.srv.panel.rutas.base.parent / "fuera.tar.gz").exists()
