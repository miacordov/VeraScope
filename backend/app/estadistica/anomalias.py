"""Anomalías mensuales y serie estandarizada (cálculo C3; guía §8).

Implementación única: la usan la API en vivo, el job de ScanMap y el preparador.
Funciones puras y vectorizables (operan sobre el último eje), sin red ni disco.
Aplica a las cinco variables de POWER (`PRECTOTCORR`, `T2M`, `GWETROOT`, `GWETTOP`, `RH2M`).
"""

from __future__ import annotations

import warnings

import numpy as np

from app.datos.validacion import limpiar, rellenar_huecos


def anomalias(valores, meses_calendario) -> np.ndarray:
    """Cálculo C3: resta a cada mes la climatología de su mes calendario.

    La climatología es la media (`nanmean`) de cada mes calendario **dentro de lo
    recibido**: la ventana que se analiza, no un periodo fijo. Los faltantes (`NaN`)
    no entran en la climatología y siguen como `NaN` en la salida.

    `valores` puede ser una serie (n,) o una matriz (celdas, n); `meses_calendario`
    (1..12) tiene largo n y se aplica sobre el último eje.
    """
    v = np.asarray(valores, float)
    m = np.asarray(meses_calendario)
    if m.ndim != 1 or v.shape[-1] != m.size:
        raise ValueError("la serie y los meses calendario deben tener el mismo largo")
    out = np.full_like(v, np.nan)
    with warnings.catch_warnings():
        # Un mes calendario sin datos deja su climatología en NaN, sin aviso.
        warnings.simplefilter("ignore", RuntimeWarning)
        for k in range(1, 13):
            sel = m == k
            if sel.any():
                out[..., sel] = v[..., sel] - np.nanmean(v[..., sel], axis=-1, keepdims=True)
    return out


def estandarizar(a) -> np.ndarray:
    """Serie `z` de las anomalías (usada por el cálculo C17 y la teleconexión, guía §10).

    `z = (a − media) / desviación estándar poblacional` (ddof = 0), sobre el último eje.
    Una serie constante no tiene escala: devuelve `NaN`.
    """
    a = np.asarray(a, float)
    media = np.nanmean(a, axis=-1, keepdims=True)
    desv = np.nanstd(a, axis=-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(desv > 0, (a - media) / desv, np.nan)


def preparar(valores, meses_calendario) -> np.ndarray | None:
    """Cálculos C2 + C3 en el orden decidido por B3 (L13): **anomalías y después relleno**.

    1. Los rellenos de POWER (`-999`) pasan a `NaN` (`validacion.limpiar`).
    2. Anomalías (C3) con la climatología calculada solo con meses reales.
    3. Huecos cortos interpolados sobre las anomalías (`validacion.rellenar_huecos`).

    Este orden evita meter datos interpolados en la climatología. Es el mismo en el
    escaneo y en vivo. Devuelve `None` si `rellenar_huecos` descarta la serie
    (hueco largo o demasiado faltante). No modifica la entrada.
    """
    return rellenar_huecos(anomalias(limpiar(valores), meses_calendario))
