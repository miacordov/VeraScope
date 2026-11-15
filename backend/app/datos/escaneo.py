"""Estado del escaneo de ScanMap en disco (guía §9 y §12; contrato `Escaneo`).

`jobs/scanmap.py` lo escribe mientras calcula; la API lo lee para `salud.escaneo`, para
el feed (`escaneo.estado = "en_curso"` con 200) y para responder 503
`escaneo_en_curso` en `teleconnect` y `scan/layer`. Vive en `{VERASCOPE_DATOS}/escaneo.json`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from app.datos.celdas import rejilla

ARCHIVO_ESTADO = "escaneo.json"
ARCHIVO_RESULTADOS = "resultados.parquet"
EN_CURSO = "en_curso"
COMPLETO = "completo"
_ESTADOS = (EN_CURSO, COMPLETO)


def celdas_rejilla() -> int:
    """Celdas de la rejilla de ScanMap (4235 con el paso de 2°)."""
    return len(rejilla())


def escribir_estado(carpeta, estado: str, celdas_listas: int, celdas_total: int) -> None:
    """Guarda el estado de forma atómica: el lector nunca ve un archivo a medias."""
    if estado not in _ESTADOS:
        raise ValueError(f"estado del escaneo desconocido: {estado!r}")
    carpeta = Path(carpeta)
    destino = carpeta / ARCHIVO_ESTADO
    temporal = carpeta / f"{ARCHIVO_ESTADO}.{os.getpid()}.tmp"
    datos = {
        "estado": estado,
        "celdas_listas": int(celdas_listas),
        "celdas_total": int(celdas_total),
    }
    temporal.write_text(json.dumps(datos), encoding="utf-8")
    os.replace(temporal, destino)


def leer_estado(carpeta) -> dict:
    """Estado con la forma del contrato `Escaneo`.

    - Con `escaneo.json`: lo que escribió el job.
    - Sin `escaneo.json` pero con `resultados.parquet` (paquete instalado con
      `verascope-datos instalar`, que no lleva el estado): `completo`.
    - Sin nada, o con un archivo ilegible: `en_curso` con 0 celdas listas.
    """
    carpeta = Path(carpeta)
    total = celdas_rejilla()
    try:
        datos = json.loads((carpeta / ARCHIVO_ESTADO).read_text(encoding="utf-8"))
        if datos.get("estado") in _ESTADOS:
            return {
                "estado": datos["estado"],
                "celdas_listas": int(datos["celdas_listas"]),
                "celdas_total": int(datos["celdas_total"]),
            }
    except FileNotFoundError:
        if (carpeta / ARCHIVO_RESULTADOS).exists():
            return {"estado": COMPLETO, "celdas_listas": total, "celdas_total": total}
    except (ValueError, KeyError, TypeError, OSError):
        pass
    return {"estado": EN_CURSO, "celdas_listas": 0, "celdas_total": total}
