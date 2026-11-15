"""Vínculo con El Niño: rezago, serie sin El Niño y significancia (cálculos C9–C12; guía §8).

Implementación única: la usan la API en vivo, el job de ScanMap, el preparador y la
teleconexión. Funciones puras, sin red ni disco. La serie y el índice llegan
**alineados mes a mes y sin faltantes**; `a[ℓ:]` se empareja con `E[:n−ℓ]`.

Prohibido `scipy.stats.pearsonr` para el p-valor: se usa el tamaño efectivo de muestra.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import t as dist_t

from app.estadistica.constantes import COLINEALIDAD_MAX, NEFF_PISO, REZAGO_MAX


def r1(x):
    """Autocorrelación de rezago 1 (`ρ₁`), insumo del cálculo C11.

    Correlación de Pearson entre `x[:-1]` y `x[1:]` sobre el último eje.
    Con una serie (n,) devuelve un `float`; con una matriz (celdas, n), un arreglo.
    """
    x = np.asarray(x, float)
    u, v = x[..., :-1], x[..., 1:]
    u = u - u.mean(axis=-1, keepdims=True)
    v = v - v.mean(axis=-1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (u * v).sum(-1) / np.sqrt((u * u).sum(-1) * (v * v).sum(-1))
    return float(r) if np.ndim(r) == 0 else r


def n_efectivo(r1x, r1y, n):
    """Cálculo C11: tamaño efectivo de muestra de Bretherton (1999).

    `n_e = n·(1 − ρ₁ₓρ₁ᵧ)/(1 + ρ₁ₓρ₁ᵧ)`, acotado a `[NEFF_PISO, n]`. Vectorizable.
    """
    rr = np.asarray(r1x, float) * np.asarray(r1y, float)
    with np.errstate(invalid="ignore", divide="ignore"):
        ne = np.clip(n * (1 - rr) / (1 + rr), NEFF_PISO, n)
    return ne[()] if np.ndim(ne) == 0 else ne


def p_correlacion(r, r1x, r1y, n):
    """Cálculo C11: p-valor bilateral de una correlación entre series autocorrelacionadas.

    `t = r·√((n_e − 2)/(1 − r²))` con `n_e − 2` grados de libertad. Devuelve
    `(p, n_efectivo)`. Vectorizable: la teleconexión la usa con todas las celdas.
    """
    r = np.asarray(r, float)
    ne = n_efectivo(r1x, r1y, n)
    tt = r * np.sqrt((ne - 2) / np.maximum(1 - r**2, 1e-12))
    p = 2 * dist_t.sf(np.abs(tt), ne - 2)
    return (p[()] if np.ndim(p) == 0 else p), ne


@dataclass(frozen=True)
class ResultadoEnso:
    """Resultado de quitar El Niño de una serie de anomalías (cálculos C9–C12)."""

    rezago: int
    """`ℓ*` en meses (0..`REZAGO_MAX`)."""
    r: float
    """Correlación entre `a[ℓ:]` y `E[:n−ℓ]`."""
    p: float
    """p-valor con tamaño efectivo (C11). **Indicativo**: elegir el máximo de 7 rezagos lo infla."""
    n_efectivo: float
    """Tamaño efectivo de muestra usado en `p`."""
    gamma: float
    """`γ̂` de la regresión conjunta (C10)."""
    colinealidad: float
    """`corr(E[:n−ℓ], t)` **con signo** (C12)."""
    limpia: np.ndarray
    """Serie sin El Niño, largo n, con `NaN` en los primeros `ℓ*` meses."""
    indicativo: bool = True
    """La significancia de `p` es indicativa (C9)."""

    @property
    def colineal(self) -> bool:
        """Aviso de colinealidad (C12): `|corr(E, t)| > COLINEALIDAD_MAX`."""
        return bool(abs(self.colinealidad) > COLINEALIDAD_MAX)


def quitar_enso(a, indice, rezago_max=REZAGO_MAX) -> ResultadoEnso:
    """Cálculos C9, C10, C11 y C12 sobre una serie de anomalías `a` (cualquier variable).

    - C9: `ℓ* = argmax_ℓ |corr(E[:n−ℓ], a[ℓ:])|` para `ℓ` en `0..rezago_max` (empate → menor).
    - C10: regresión **conjunta** `a[ℓ:] = α + β·t + γ·(E − Ē) + ε` con `lstsq`;
      serie sin El Niño `r_t = a_t − γ̂·(E_{t−ℓ} − Ē)`. γ se estima junto con β para no
      atribuirle la tendencia a El Niño.
    - C11: p-valor de `r` con tamaño efectivo (`ρ₁` de `E[:n−ℓ]` y de `a[ℓ:]`).
    - C12: colinealidad `corr(E[:n−ℓ], t)` con signo.
    """
    a = np.asarray(a, float)
    e = np.asarray(indice, float)
    if a.ndim != 1 or a.shape != e.shape:
        raise ValueError("la serie y el índice deben tener el mismo largo, alineados mes a mes")
    n = a.size
    if not 0 <= rezago_max < n - 2:
        raise ValueError("el rezago máximo no cabe en la serie")

    rs = np.array([np.corrcoef(e[: n - ell], a[ell:])[0, 1] for ell in range(rezago_max + 1)])
    rezago = int(np.argmax(np.nan_to_num(np.abs(rs), nan=-1.0)))
    r = float(rs[rezago])

    ee, y = e[: n - rezago], a[rezago:]
    t = np.arange(y.size, dtype=float)
    centrado = ee - ee.mean()
    X = np.column_stack([np.ones_like(t), t, centrado])
    gamma = float(np.linalg.lstsq(X, y, rcond=None)[0][2])

    limpia = np.full(n, np.nan)
    limpia[rezago:] = y - gamma * centrado
    p, ne = p_correlacion(r, r1(ee), r1(y), y.size)
    return ResultadoEnso(
        rezago=rezago,
        r=r,
        p=float(p),
        n_efectivo=float(ne),
        gamma=gamma,
        colinealidad=float(np.corrcoef(ee, t)[0, 1]),
        limpia=limpia,
    )
