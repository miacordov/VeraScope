"""Comandos del cargador de datos de VeraScope.

    python -m verascope_datos todo          # hace todo, en orden
    python -m verascope_datos estado        # qué hay descargado
    python -m verascope_datos --ayuda       # lista de comandos
"""
import argparse
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from . import __version__, config
from .almacen import Casillero, compactar, lugar_celda
from .variables import INDICES, POWER, VARIABLES

con = Console()


def barra():
    return Progress(SpinnerColumn(), TextColumn("[bold]{task.description}"), BarColumn(), MofNCompleteColumn(),
                    TextColumn("·"), TimeRemainingColumn(), console=con)


# ---------------------------------------------------------------- variables / estado
def cmd_variables(a, r):
    if a.json:
        import dataclasses, json
        texto = json.dumps([dataclasses.asdict(v) for v in VARIABLES], ensure_ascii=False, indent=2) + "\n"
        if a.json == "-":
            sys.stdout.write(texto)
        else:
            Path(a.json).write_text(texto, encoding="utf-8")
            con.print(f"[green]✔ Catálogo escrito en {a.json}[/]")
        return
    t = Table(title="Las 13 variables de VeraScope", header_style="bold")
    for c in ("ID", "Código", "Nombre", "Unidad", "Capa", "Fuente", "Desde"):
        t.add_column(c)
    for v in VARIABLES:
        t.add_row(v.id, v.codigo, v.nombre, v.unidad, v.capa, v.fuente, str(v.desde))
    con.print(t)


def cmd_estado(a, r):
    cas = Casillero(r.casillero)
    res = {v: (n, ini, largo, act) for v, n, ini, largo, act in cas.resumen()}
    total = len(config.rejilla()) + len(config.LUGARES_DEMO)
    t = Table(title=f"Estado de los datos · ventana {config.ANIO_INICIO}–{config.ANIO_FIN} · carpeta {r.base}", header_style="bold")
    for c in ("ID", "Variable", "Lugares", "Desde", "Actualizado"):
        t.add_column(c)
    for v in VARIABLES:
        n, ini, _, act = res.get(v.codigo, (0, "—", 0, "—"))
        meta = f"{n}/{total}" if v.capa == "vivo" else (f"{n}/{len(config.LUGARES_DEMO)}" if v.capa == "precalculada" else str(n))
        color = "green" if n else "red"
        t.add_row(v.id, v.nombre, f"[{color}]{meta}[/]", ini or "—", (act or "—")[:16])
    con.print(t)
    piezas = {"Tabla gigante": (r.tabla / "PRECTOTCORR.npy").exists(), "Lista de resultados": r.resultados.exists(),
              "Respaldo de demos": any(r.demos.glob("*.json")), "Paquete": any(r.paquetes.glob("*.tar.gz"))}
    con.print("  ".join(f"{'[green]✔' if ok else '[dim]·'} {k}[/]" for k, ok in piezas.items()))
    f = cas.fallos()
    if f:
        con.print(f"[yellow]{len(f)} descargas fallidas pendientes; vuelve a correr el comando para reintentarlas.[/]")
    cas.cerrar()


# ---------------------------------------------------------------- índices (V6, V7, V13)
def cmd_indices(a, r):
    from .fuentes import noaa
    meses = config.meses(1950)
    cas = Casillero(r.casillero)
    fuentes = [("ONI", noaa.URL_ONI, "oni.ascii.txt", noaa.parsear_oni),
               ("NINO12", noaa.URL_SSTOI, "sstoi.indices", noaa.parsear_nino12),
               ("CO2", noaa.URL_CO2, "co2_mm_mlo.txt", noaa.parsear_co2)]
    for cod, url, nombre, parser in fuentes:
        try:
            if a.carpeta:
                texto = (Path(a.carpeta) / nombre).read_text()
            else:
                texto = noaa.bajar(url)
                (r.crudo / nombre).write_text(texto)
            ini, v = compactar(meses, parser(texto, meses))
            if v is None:
                raise ValueError("el archivo no tiene datos reconocibles")
            cas.guardar(cod, "indice", ini, v, unidad="ppm" if cod == "CO2" else "°C", fuente="NOAA")
            con.print(f"[green]✔[/] {cod}: {v.size} meses desde {ini}")
        except Exception as e:
            cas.fallo(cod, "indice", e)
            con.print(f"[red]✘ {cod}: {e}[/]  (descarga {nombre} a mano y usa --carpeta; en el panel, la opción «Mi internet bloquea NOAA»)")
    cas.cerrar()


# ---------------------------------------------------------------- POWER (V1–V5)
def lista_power(solo_demos=False, paso=None):
    demos = [(f"demo:{l.id}", config.cuantizar(l.lat), config.cuantizar(l.lon)) for l in config.LUGARES_DEMO]
    if solo_demos:
        return demos
    return demos + [(lugar_celda(la, lo), la, lo) for la, lo in config.rejilla(paso)]


def cmd_power(a, r, cliente=None):
    from .fuentes.power import ClientePower, parsear
    meses = config.meses()
    cas = Casillero(r.casillero)
    todos = lista_power(a.solo_demos, a.paso)
    pendientes = [x for x in todos if not cas.existe("PRECTOTCORR", x[0])]
    faltan = pendientes[: a.limite] if a.limite else pendientes
    con.print(f"NASA POWER: {len(todos) - len(pendientes)} de {len(todos)} lugares ya están guardados; faltan {len(pendientes)}"
              + (f" (en esta corrida, {len(faltan)})." if len(faltan) < len(pendientes) else "."))
    if not faltan:
        cas.cerrar(); return
    cliente = cliente or ClientePower(pausa=a.pausa, crudo=r.crudo if a.guardar_crudo else None)
    ok = mal = 0
    try:
        with barra() as p:
            t = p.add_task("Descargando de NASA POWER", total=len(faltan))
            for lugar, la, lo in faltan:
                try:
                    vals = parsear(cliente.celda(la, lo), meses)
                    for cod in POWER:
                        ini, v = compactar(meses, vals[cod])
                        if v is not None:
                            cas.guardar(cod, lugar, ini, v, la, lo, fuente="NASA POWER (MERRA-2)")
                    cas.resuelto("power", lugar)
                    ok += 1
                except Exception as e:
                    cas.fallo("power", lugar, e); mal += 1
                p.advance(t)
    except KeyboardInterrupt:
        con.print("\n[yellow]Pausado. Lo descargado ya está guardado: vuelve a correr el comando para seguir.[/]")
    con.print(f"[green]✔ {ok} lugares nuevos[/]" + (f"  [red]✘ {mal} fallidos (se reintentan la próxima vez)[/]" if mal else ""))
    cas.cerrar()


# ---------------------------------------------------------------- satélites (V8–V12)
def _guardar_mapa(cas, cod, mapa, meses, unidad, fuente):
    import numpy as np
    for lid, serie in mapa.items():
        v = np.array([serie.get(m, np.nan) for m in meses], dtype=np.float32)
        ini, v = compactar(meses, v)
        if v is not None:
            l = next(x for x in config.LUGARES_DEMO if x.id == lid)
            cas.guardar(cod, f"demo:{lid}", ini, v, config.cuantizar(l.lat), config.cuantizar(l.lon), unidad, fuente)
            con.print(f"[green]✔[/] {cod} · {l.nombre}: {v.size} meses desde {ini}")


def cmd_satelites(a, r):
    from .fuentes import earthdata
    meses = config.meses()
    lugares = list(config.LUGARES_DEMO)
    cas = Casillero(r.casillero)
    que = set(a.solo.split(",")) if a.solo else {"imerg", "gldas", "ndvi"}
    local = Path(a.archivos_locales) if a.archivos_locales else None

    def abrir(producto, desde, carpeta, patron):
        if local:
            fs = sorted((local / carpeta).glob(patron))
            if not fs:
                raise FileNotFoundError(f"No hay archivos {patron} en {local / carpeta}")
            return fs
        earthdata.iniciar_sesion()
        return earthdata.buscar_y_abrir(producto, max(desde, config.ANIO_INICIO), config.ANIO_FIN, lugares)

    for nombre, producto, desde, carpeta, patron in (("imerg", earthdata.IMERG, 1998, "imerg", "*.HDF5"),
                                                     ("gldas", earthdata.GLDAS, 2000, "gldas", "*.nc4")):
        if nombre not in que:
            continue
        try:
            archivos = abrir(producto, desde, carpeta, patron)
            with barra() as p:
                t = p.add_task(f"Leyendo {producto['short_name']}", total=len(archivos))
                fn = earthdata.extraer_imerg if nombre == "imerg" else earthdata.extraer_gldas
                datos = fn(archivos, lugares, avance=lambda: p.advance(t))
            if nombre == "imerg":
                _guardar_mapa(cas, "IMERG", datos, meses, "mm/día", "GPM_3IMERGM v07")
            else:
                for cod, unidad in (("GLDAS_EVAP", "mm/día"), ("GLDAS_ESCORRENTIA", "mm/día"), ("GLDAS_SUELO", "mm")):
                    _guardar_mapa(cas, cod, datos[cod], meses, unidad, "GLDAS_NOAH025_M v2.1")
        except Exception as e:
            cas.fallo(nombre, "demo", e)
            con.print(f"[red]✘ {nombre}: {e}[/]")

    if "ndvi" in que:
        from .fuentes import appeears
        try:
            mapa = {}
            if local:
                for l in lugares:
                    f = local / "ndvi" / f"{l.id}.nc"
                    if f.exists():
                        mapa[l.id] = appeears.leer_ndvi(f, l)
            else:
                cli = appeears.AppEEARS(r.crudo / "appeears_tareas.json"); cli.entrar()
                for l in lugares:
                    tid = cli.enviar(l, config.ANIO_INICIO, config.ANIO_FIN)
                    with con.status(f"AppEEARS procesa {l.nombre} (puede tardar; se puede cortar y retomar)") as st:
                        cli.esperar(tid, avisar=lambda s: st.update(f"AppEEARS · {l.nombre}: {s}"))
                    carpeta = r.crudo / f"ndvi_{l.id}"; carpeta.mkdir(exist_ok=True)
                    for f in cli.descargar(tid, carpeta):
                        mapa[l.id] = appeears.leer_ndvi(f, l)
            _guardar_mapa(cas, "NDVI", mapa, meses, "adimensional", "MOD13C2 v061")
        except Exception as e:
            cas.fallo("ndvi", "demo", e)
            con.print(f"[red]✘ ndvi: {e}[/]")
    cas.cerrar()


# ---------------------------------------------------------------- cálculo, demos, paquete
def cmd_calcular(a, r):
    from . import calcular
    with con.status("Armando la tabla gigante (celdas × meses)…"):
        n, m = calcular.armar_tabla(r)
    con.print(f"[green]✔[/] Tabla gigante: {n} celdas × {m} meses por variable")
    with barra() as p:
        t = p.add_task("Calculando tendencias con y sin El Niño", total=n * len(POWER))
        df = calcular.calcular_resultados(r, procesos=a.procesos, avance=lambda k: p.advance(t, k))
    t = Table(title=f"Lista de resultados · {len(df)} series · ventana {df.ventana.iloc[0]}", header_style="bold")
    for c in ("Variable", "Cambio robusto", "Sensible a El Niño", "Cambio oculto", "Sin tendencia"):
        t.add_column(c)
    for cod, g in df.groupby("variable"):
        c = g.veredicto.value_counts()
        t.add_row(cod, *[str(c.get(k, 0)) for k in ("cambio_robusto", "sensible_a_el_nino", "cambio_oculto", "sin_tendencia")])
    con.print(t)


def cmd_demos(a, r):
    from .paquete import exportar_demos
    for lid, nvars, peso in exportar_demos(r):
        con.print(f"[green]✔[/] demo/{lid}.json · {nvars} de 13 variables · {peso / 1024:.0f} KB")


def cmd_empaquetar(a, r):
    from .paquete import empaquetar
    f, n = empaquetar(r)
    con.print(f"[green]✔[/] Paquete listo: {f} ({f.stat().st_size / 1e6:.1f} MB, {n} archivos). "
              "Súbelo a un release de GitHub o a una carpeta compartida.")


def cmd_instalar(a, r):
    from .paquete import instalar
    mf = instalar(Path(a.paquete), r)
    con.print(f"[green]✔[/] Datos instalados en {r.base} · creados {mf['creado']} · ventana {mf['ventana'][0]} a {mf['ventana'][1]} · "
              f"{len(mf['archivos'])} archivos verificados")


def cmd_panel(a, r):
    from .panel.servidor import servir
    servir(r, puerto=a.puerto, abrir=not a.no_abrir)


def cmd_todo(a, r):
    pasos = [("1/6 Índices de NOAA (V6, V7, V13)", cmd_indices),
             ("2/6 NASA POWER (V1–V5): primero las demos, luego la rejilla", cmd_power),
             ("3/6 Satélites (V8–V12) para los lugares de las demos", cmd_satelites),
             ("4/6 Tabla gigante y resultados estadísticos", cmd_calcular),
             ("5/6 Respaldo de las demos", cmd_demos),
             ("6/6 Paquete para el equipo", cmd_empaquetar)]
    for titulo, fn in pasos:
        con.rule(f"[bold]{titulo}")
        try:
            fn(a, r)
        except Exception as e:
            con.print(f"[red]✘ {e}[/]")
            if fn in (cmd_calcular,):
                con.print("[yellow]Sigo con los pasos siguientes; corrige el error y vuelve a correr 'todo'.[/]")
    con.rule()
    cmd_estado(a, r)


def main(argv=None):
    import signal
    try:
        signal.signal(signal.SIGINT, signal.default_int_handler)   # algunos entornos lo dejan ignorado: Ctrl+C debe cortar
    except ValueError:                                           # fuera del hilo principal (pruebas, panel)
        pass
    ap = argparse.ArgumentParser(prog="verascope-datos", add_help=False,
                                 description="Baja, ordena, calcula y empaqueta las 13 variables de VeraScope.")
    ap.add_argument("--ayuda", "-h", action="help", help="muestra esta ayuda")
    ap.add_argument("--datos", help="carpeta de datos (por defecto $VERASCOPE_DATOS, si no backend/data del repo, si no ./datos)")
    ap.add_argument("--fin", type=int, help=f"último año de la ventana (por defecto {config.ANIO_FIN})")
    ap.add_argument("--version", action="version", version=f"verascope-datos {__version__}", help="muestra la versión")
    ap._positionals.title, ap._optionals.title = "comandos", "opciones"
    sub = ap.add_subparsers(dest="cmd", metavar="comando")

    def com(nombre, fn, ayuda):
        s = sub.add_parser(nombre, help=ayuda, add_help=False)
        s.add_argument("--ayuda", "-h", action="help")
        s.set_defaults(fn=fn)
        return s

    def opciones_power(s):
        s.add_argument("--solo-demos", action="store_true", help="solo los 3 lugares de las demos")
        s.add_argument("--paso", type=float, default=config.REJILLA_PASO, help="paso de la rejilla en grados (2 por defecto)")
        s.add_argument("--pausa", type=float, default=config.POWER_PAUSA_S, help="segundos entre peticiones")
        s.add_argument("--limite", type=int, help="descargar como máximo N lugares en esta corrida")
        s.add_argument("--guardar-crudo", action="store_true", help="guardar también el JSON original comprimido")

    def opciones_sat(s):
        s.add_argument("--solo", help="imerg, gldas y/o ndvi, separados por coma")
        s.add_argument("--archivos-locales", help="usar archivos ya descargados (carpetas imerg/, gldas/, ndvi/)")

    s = com("panel", cmd_panel, "abre el panel visual en el navegador (sin comandos)")
    s.add_argument("--puerto", type=int, default=8765, help="puerto local (8765 por defecto)")
    s.add_argument("--no-abrir", action="store_true", help="no abrir el navegador automáticamente")
    s = com("variables", cmd_variables, "lista las 13 variables")
    s.add_argument("--json", metavar="ARCHIVO", help="exporta el catálogo en JSON (- para la pantalla); fuente única: variables.py")
    com("estado", cmd_estado, "muestra qué está descargado y qué falta")
    s = com("indices", cmd_indices, "baja ONI, Niño 1+2 y CO₂ de NOAA")
    s.add_argument("--carpeta", help="leer los archivos de NOAA desde esta carpeta en vez de internet")
    opciones_power(com("power", cmd_power, "baja V1–V5 de NASA POWER (se puede cortar y retomar)"))
    opciones_sat(com("satelites", cmd_satelites, "baja V8–V12 (GPM, GLDAS, MODIS) para las demos"))
    s = com("calcular", cmd_calcular, "arma la tabla gigante y la lista de resultados")
    s.add_argument("--procesos", type=int, help="núcleos de CPU a usar")
    s.add_argument("--paso", type=float, default=config.REJILLA_PASO, help="paso de la rejilla usada al descargar")
    com("demos", cmd_demos, "exporta el respaldo JSON de las demos")
    com("empaquetar", cmd_empaquetar, "junta todo en un archivo para el equipo")
    s = com("instalar", cmd_instalar, "instala un paquete recibido de otro integrante")
    s.add_argument("paquete")
    s = com("todo", cmd_todo, "hace todos los pasos en orden")
    opciones_power(s); opciones_sat(s)
    s.add_argument("--carpeta"); s.add_argument("--procesos", type=int)

    a = ap.parse_args(argv)
    if not a.cmd:
        con.print(f"[bold]VeraScope · cargador de datos {__version__}[/]\n")
        ap.print_help(); return
    if a.fin:
        config.ANIO_FIN = a.fin
    if getattr(a, "paso", None):
        config.REJILLA_PASO = a.paso
    for k in ("solo_demos", "limite", "guardar_crudo", "solo", "archivos_locales", "carpeta", "procesos"):
        if not hasattr(a, k):
            setattr(a, k, None)
    for k, v in (("paso", config.REJILLA_PASO), ("pausa", config.POWER_PAUSA_S)):
        if not hasattr(a, k):
            setattr(a, k, v)
    r = config.rutas(a.datos)
    t0 = time.time()
    a.fn(a, r)
    if a.cmd in ("todo", "power", "calcular", "satelites") and a.cmd != "panel":
        con.print(f"[dim]Tiempo: {(time.time() - t0) / 60:.1f} min[/]")


if __name__ == "__main__":
    sys.exit(main())
