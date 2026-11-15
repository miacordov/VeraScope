"""Matrices de la rejilla de ScanMap para `teleconnect` (guía §10, paso 1).

Se preparan una vez al arrancar, a partir de lo que deja el preparador en `tabla/`:
`celdas.npy`, `meses.json`, el ONI y una matriz por variable. Esta capa compone
`datos/` (lectura de archivos) con `estadistica/` (anomalías y matrices); ninguno de
los dos paquetes importa al otro.
"""

from __future__ import annotations

import json
import logging
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.datos import indices
from app.estadistica.anomalias import preparar
from app.estadistica.teleconexion import VARIABLES_CON_LINEAS, Matrices, preparar_matrices

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Rejilla:
    """Lo que `teleconnect` necesita de la rejilla, ya en memoria."""

    lats: np.ndarray
    """Latitud de cada celda (fila de `celdas.npy`)."""
    lons: np.ndarray
    """Longitud de cada celda, en −180..180."""
    fechas: list[str]
    """Meses de la ventana con ONI, la misma que usa el escaneo."""
    fases: list[str]
    """Fase del ONI en cada mes de `fechas` (sin rezago)."""
    matrices: dict[str, Matrices]
    """Por variable con líneas: `Z`, celdas válidas y `ρ₁`."""


def _anomalias(valores: np.ndarray, meses_calendario: np.ndarray) -> np.ndarray:
    """Anomalías de cada celda con el mismo control de calidad que el escaneo.

    Las celdas que no lo pasan (por ejemplo, humedad del suelo sobre el mar) quedan en
    `NaN`, y `preparar_matrices` las marca como no válidas.
    """
    salida = np.full(valores.shape, np.nan)
    for i, fila in enumerate(valores):
        serie = preparar(fila, meses_calendario)
        if serie is not None:
            salida[i] = serie
    return salida


def cargar_rejilla(carpeta: Path | str) -> Rejilla | None:
    """Prepara las matrices; `None` si faltan los archivos del preparador.

    Sin rejilla, `teleconnect` responde 503 `escaneo_en_curso`.
    """
    tabla = Path(carpeta) / "tabla"
    try:
        meses = json.loads((tabla / "meses.json").read_text(encoding="utf-8"))
        celdas = np.load(tabla / "celdas.npy")
        _, oni = indices.cargar_indice("ONI", carpeta)
    except (FileNotFoundError, ValueError, OSError):
        logger.warning("rejilla no disponible en %s: teleconnect responde 503", tabla)
        return None

    inicio, fin = indices.ventana_valida(oni)
    fechas = list(meses[inicio:fin])
    calendario = np.array([int(m[5:7]) for m in fechas])
    matrices: dict[str, Matrices] = {}
    for variable in sorted(VARIABLES_CON_LINEAS):
        archivo = tabla / f"{variable}.npy"
        if not archivo.exists():
            logger.warning("falta %s: %s queda sin líneas", archivo, variable)
            continue
        valores = np.load(archivo).astype(float)[:, inicio:fin]
        with warnings.catch_warnings():
            # Las celdas sin ningún dato válido dan avisos de numpy; se marcan no válidas.
            warnings.simplefilter("ignore", RuntimeWarning)
            matrices[variable] = preparar_matrices(_anomalias(valores, calendario))

    return Rejilla(
        lats=celdas[:, 0].astype(float),
        lons=celdas[:, 1].astype(float),
        fechas=fechas,
        fases=[str(f) for f in indices.fases(oni[inicio:fin])],
        matrices=matrices,
    )
