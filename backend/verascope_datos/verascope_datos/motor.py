"""Reexportación del motor único de `app.estadistica` (guía §7: una sola implementación).

El preparador no tiene cálculos propios: todo sale de `app.estadistica` y `app.datos`,
los mismos módulos que usa la API en vivo. Se conservan los nombres de antes para no
romper a quien los importa.
"""
from app.datos.validacion import rellenar_huecos
from app.estadistica.anomalias import anomalias
from app.estadistica.celda import analizar_celda
from app.estadistica.constantes import ALFA, MIN_MESES
from app.estadistica.fdr import benjamini_hochberg as fdr
from app.estadistica.tendencia import tendencia as _tendencia
from app.estadistica.veredicto import estado as veredicto

__all__ = ["ALFA", "MIN_MESES", "analizar", "anomalias", "fdr", "rellenar_huecos", "tendencia", "veredicto"]


def tendencia(y, alfa=ALFA):
    """`app.estadistica.tendencia.tendencia` con la forma de diccionario de antes."""
    r = _tendencia(y, alfa)
    return {"pendiente_dec": r.pendiente_decada, "ic": (r.ic_bajo, r.ic_alto), "p": r.p}


def analizar(valores, oni, meses_calendario, variable=None):
    """Fila de `resultados.parquet` de una celda (`analizar_celda`), o None si se descarta."""
    r = analizar_celda(valores, meses_calendario, oni, variable)
    return None if r is None else r.fila_escaneo()
