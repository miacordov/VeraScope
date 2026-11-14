"""Respaldo de las demos (JSON) y el paquete de datos para compartir con el equipo."""
import datetime as dt
import hashlib
import json
import tarfile
from pathlib import Path

import numpy as np

from . import __version__, config
from .almacen import Casillero
from .variables import VARIABLES


def _redondear(v):
    return [None if not np.isfinite(x) else round(float(x), 4) for x in v]


def exportar_demos(rutas):
    """Un JSON por lugar de demo con las 13 variables alineadas: funciona sin red el día de la presentación."""
    meses = config.meses()
    cas = Casillero(rutas.casillero)
    hechos = []
    for l in config.LUGARES_DEMO:
        datos = {}
        for v in VARIABLES:
            lugar = "indice" if v.capa in ("indice", "contexto") else f"demo:{l.id}"
            serie = cas.leer_alineada(v.codigo, lugar, meses)
            if np.isfinite(serie).any():
                datos[v.codigo] = {"id": v.id, "nombre": v.nombre, "unidad": v.unidad, "fuente": v.fuente,
                                   "valores": _redondear(serie)}
        doc = {"lugar": l.nombre, "lat": config.cuantizar(l.lat), "lon": config.cuantizar(l.lon),
               "inicio": meses[0], "fin": meses[-1], "variables": datos}
        f = rutas.demos / f"{l.id}.json"
        f.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")))
        hechos.append((l.id, len(datos), f.stat().st_size))
    cas.cerrar()
    return hechos


def _sha(f):
    h = hashlib.sha256()
    with open(f, "rb") as x:
        for b in iter(lambda: x.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def empaquetar(rutas):
    piezas = [rutas.casillero, rutas.resultados] + sorted(rutas.tabla.glob("*")) + sorted(rutas.demos.glob("*.json"))
    piezas = [p for p in piezas if p.exists()]
    manifiesto = {"programa": f"verascope-datos {__version__}",
                  "creado": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                  "ventana": [config.meses()[0], config.meses()[-1]],
                  "archivos": {str(p.relative_to(rutas.base)): _sha(p) for p in piezas}}
    mf = rutas.base / "manifiesto.json"
    mf.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False))
    nombre = rutas.paquetes / f"verascope-datos-{dt.date.today():%Y%m%d}.tar.gz"
    with tarfile.open(nombre, "w:gz") as tar:
        for p in piezas + [mf]:
            tar.add(p, arcname=str(p.relative_to(rutas.base)))
    return nombre, len(piezas)


def instalar(paquete: Path, rutas):
    with tarfile.open(paquete, "r:gz") as tar:
        for m in tar.getmembers():
            if m.name.startswith("/") or ".." in Path(m.name).parts:
                raise RuntimeError(f"Ruta no permitida en el paquete: {m.name}")
        tar.extractall(rutas.base, filter="data")
    mf = json.loads((rutas.base / "manifiesto.json").read_text())
    malos = [n for n, h in mf["archivos"].items() if _sha(rutas.base / n) != h]
    if malos:
        raise RuntimeError(f"Archivos dañados en el paquete: {malos}")
    return mf
