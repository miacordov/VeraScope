"""Respaldo de las demos (JSON) y el paquete de datos para compartir con el equipo."""
import datetime as dt
import hashlib
import json
import os
import shutil
import tarfile
import tempfile
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
        f.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
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
    mf.write_text(json.dumps(manifiesto, indent=2, ensure_ascii=False), encoding="utf-8")
    nombre = rutas.paquetes / f"verascope-datos-{dt.date.today():%Y%m%d}.tar.gz"
    with tarfile.open(nombre, "w:gz") as tar:
        for p in piezas + [mf]:
            tar.add(p, arcname=str(p.relative_to(rutas.base)))
    return nombre, len(piezas)


def _restos_del_casillero(rutas):
    """`-wal` y `-shm` de SQLite: existen mientras una API tiene abierto el casillero o si se cortó de golpe."""
    return [rutas.casillero.with_name(rutas.casillero.name + s) for s in ("-wal", "-shm")]


def casillero_en_uso(rutas) -> bool:
    """Hay señales de una API corriendo (o cortada) sobre el casillero."""
    return any(p.exists() for p in _restos_del_casillero(rutas))


def instalar(paquete: Path, rutas):
    """Instala el paquete en `rutas.base` sin dejar datos a medias.

    1. Descomprime en una carpeta temporal dentro de `rutas.base` y verifica el SHA-256 de cada archivo ahí:
       si el paquete está dañado, lo instalado no se toca.
    2. Reemplaza cada archivo con `os.replace` (un archivo nuevo, no una escritura encima del viejo). Una API que
       tenga abierto el casillero sigue con su copia vieja y, al apagarse, ya no puede volcar su `-wal` sobre el
       casillero nuevo (eso lo dañaba).
    3. Borra el `-wal` y el `-shm` del casillero viejo, para que SQLite no los aplique al nuevo.
    """
    rutas.base.mkdir(parents=True, exist_ok=True)
    temporal = Path(tempfile.mkdtemp(prefix=".instalando-", dir=rutas.base))
    try:
        with tarfile.open(paquete, "r:gz") as tar:
            for m in tar.getmembers():
                if m.name.startswith("/") or ".." in Path(m.name).parts:
                    raise RuntimeError(f"Ruta no permitida en el paquete: {m.name}")
            tar.extractall(temporal, filter="data")
        mf = json.loads((temporal / "manifiesto.json").read_text(encoding="utf-8"))
        malos = [n for n, h in mf["archivos"].items() if _sha(temporal / n) != h]
        if malos:
            raise RuntimeError(f"Archivos dañados en el paquete: {malos}")
        try:
            for nombre in [*mf["archivos"], "manifiesto.json"]:
                destino = rutas.base / nombre
                destino.parent.mkdir(parents=True, exist_ok=True)
                os.replace(temporal / nombre, destino)
        except PermissionError as error:  # Windows no reemplaza un archivo que otro programa tiene abierto
            raise RuntimeError(
                "No se pudo reemplazar un archivo de datos porque está en uso. "
                "Apaga la API (o `npm run dev`) y vuelve a instalar."
            ) from error
        for resto in _restos_del_casillero(rutas):
            resto.unlink(missing_ok=True)
    finally:
        shutil.rmtree(temporal, ignore_errors=True)
    return mf
