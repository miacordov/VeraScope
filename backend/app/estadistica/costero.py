"""Aviso `nino_costero`: Niño 1+2 como índice complementario (decisión de B3, hora 20).

El índice principal es el ONI: el escaneo, el veredicto y las líneas se calculan con
él. En la costa norte del Perú los Niños costeros (por ejemplo, el de 2017) casi no se
ven en el ONI y sí en Niño 1+2. Por eso, en esa franja, si Niño 1+2 tiene un vínculo
significativo con la serie y más fuerte que el del ONI, se avisa y se ofrece ese
índice. El aviso **no cambia** ningún número del veredicto.

Función pura: recibe arreglos alineados mes a mes; sin red, sin disco y sin FastAPI.
"""

import numpy as np

from app.estadistica.constantes import ALFA, COSTA_NINO12_LAT, COSTA_NINO12_LON, MIN_MESES
from app.estadistica.enso import quitar_enso

AVISO_COSTERO = "nino_costero"


def en_costa_nino12(lat: float, lon: float) -> bool:
    """`True` si el punto cae en la franja `COSTA_NINO12_LAT` × `COSTA_NINO12_LON` (con bordes)."""
    lat0, lat1 = COSTA_NINO12_LAT
    lon0, lon1 = COSTA_NINO12_LON
    return lat0 <= lat <= lat1 and lon0 <= lon <= lon1


def aviso_nino_costero(lat, lon, anomalias, oni, nino12) -> tuple[str, str] | None:
    """Devuelve `(código, texto)` del aviso o `None`.

    Se usan solo los meses en que la serie y ambos índices son finitos (Niño 1+2 empieza
    en 1982). Hay aviso si el punto está en la costa, quedan al menos `MIN_MESES` meses,
    el vínculo con Niño 1+2 (cálculo C11, con tamaño efectivo) tiene `p < ALFA` y su
    |r| supera el del ONI sobre esos mismos meses. No modifica la entrada.
    """
    if not en_costa_nino12(lat, lon):
        return None
    a = np.asarray(anomalias, float)
    e_oni = np.asarray(oni, float)
    e_n12 = np.asarray(nino12, float)
    k = np.isfinite(a) & np.isfinite(e_oni) & np.isfinite(e_n12)
    if k.sum() < MIN_MESES:
        return None
    con_oni = quitar_enso(a[k], e_oni[k])
    con_n12 = quitar_enso(a[k], e_n12[k])
    if not (np.isfinite(con_n12.p) and con_n12.p < ALFA and abs(con_n12.r) > abs(con_oni.r)):
        return None
    return (
        AVISO_COSTERO,
        "En la costa norte del Perú, el índice Niño 1+2 (que capta los Niños costeros) "
        f"sigue mejor a esta serie que el ONI: correlación {abs(con_n12.r):.2f} frente a "
        f"{abs(con_oni.r):.2f}. Puedes repetir el análisis con el índice Niño 1+2.",
    )


AVISO_NO_LINEAL = "respuesta_no_lineal"
VARIABLE_NO_LINEAL = "PRECTOTCORR"


def aviso_respuesta_no_lineal(lat, lon, variable) -> tuple[str, str] | None:
    """Cálculo C12, respuesta no lineal: `(código, texto)` o `None`.

    Regla del informe técnico (diagnósticos y limitaciones): la lluvia de la costa norte
    del Perú responde sobre todo a eventos extremos, no de forma proporcional al índice,
    y la interfaz lo indica en esa región. Quitar El Niño es una regresión lineal, así que
    parte de esa señal puede quedar en la serie sin El Niño. Solo para la lluvia y en la
    misma franja que `en_costa_nino12`.
    """
    if variable != VARIABLE_NO_LINEAL or not en_costa_nino12(lat, lon):
        return None
    return (
        AVISO_NO_LINEAL,
        "En la costa norte del Perú, la lluvia responde sobre todo a eventos extremos de "
        "El Niño y no en proporción al índice. Quitar El Niño es un ajuste lineal, así que "
        "parte de su efecto puede quedar en la serie sin El Niño.",
    )
