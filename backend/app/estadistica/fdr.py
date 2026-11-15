"""Benjamini-Hochberg para el escaneo masivo (cálculo C14; corrección C18).

Funciones puras y vectorizadas: sin red, sin disco y sin FastAPI.
"""

from collections.abc import Mapping

import numpy as np
from scipy.stats import false_discovery_control


def benjamini_hochberg(p) -> np.ndarray:
    """Cálculo C14: p-valores ajustados por Benjamini-Hochberg.

    Ajusta solo los valores finitos; los NaN (celdas sin serie válida) siguen en su
    lugar y no cuentan como pruebas. Conserva la forma de la entrada y no la modifica.
    Para decidir el descubrimiento se compara el ajustado con `FDR_Q` usando
    `veredicto.significativa`. Aplica a las cinco variables.
    """
    p = np.asarray(p, dtype=float)
    ajustado = np.full(p.shape, np.nan)
    finitos = np.isfinite(p)
    if finitos.any():
        ajustado[finitos] = false_discovery_control(p[finitos], method="bh")
    return ajustado


def por_familias(p_por_familia: Mapping[str, object]) -> dict[str, np.ndarray]:
    """Cálculo C14: ajusta cada familia de pruebas por separado, sin mezclarlas.

    Familias del escaneo: la tendencia original y la tendencia sin El Niño (corrección
    C18) y, por decisión de B3 (L13), `p_enso` de cada variable. Devuelve un diccionario
    con las mismas llaves y los p ajustados de cada familia.
    """
    return {nombre: benjamini_hochberg(p) for nombre, p in p_por_familia.items()}
