"""Control de calidad de las series mensuales (cálculo C2; guía, sección 6).

Implementación única: la usan la API en vivo, el job de ScanMap y el preparador
(`verascope_datos.motor` importa `rellenar_huecos` de aquí). Los umbrales viven
solo en `app/estadistica/constantes.py`. Este módulo no depende de FastAPI.

Reglas, en este orden:
1. `-999` y rellenos → faltante (`NaN`).
2. Huecos de hasta `MAX_HUECO` meses seguidos → interpolación lineal.
3. Más de `MAX_FALTANTE` faltante, o un hueco mayor a `MAX_HUECO` → se descarta.
4. Al menos `MIN_MESES` meses; bajo `AVISO_POTENCIA_MESES`, aviso de potencia baja.
5. Desviación estándar nula → se descarta.
6. Humedad del suelo sobre el mar: POWER entrega `GWETROOT` todo en `-999` y
   `GWETTOP` constante en 1.0 (docs/comprobaciones-b2.md) → `sin_datos_tierra`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.estadistica.constantes import (
    AVISO_POTENCIA_MESES,
    MAX_FALTANTE,
    MAX_HUECO,
    MIN_MESES,
)

VARIABLES_SUELO = frozenset({"GWETROOT", "GWETTOP"})
"""Variables sin sentido sobre el océano."""

UMBRAL_RELLENO = -998.0
"""POWER marca el faltante con -999; todo valor en o bajo este umbral es relleno."""

# Motivos de descarte. Los dos primeros coinciden con códigos de error del contrato.
VENTANA_CORTA = "ventana_corta"
SIN_DATOS_TIERRA = "sin_datos_tierra"
FALTANTE_EXCESIVO = "faltante_excesivo"
HUECO_LARGO = "hueco_largo"
SERIE_CONSTANTE = "serie_constante"


@dataclass(frozen=True)
class Calidad:
    """Resultado del control de calidad de una serie."""

    valores: np.ndarray | None
    """Serie limpia e interpolada, o `None` si se descarta."""
    motivo: str | None
    """Por qué se descartó (`None` si se acepta)."""
    aviso_potencia: bool
    """Menos de `AVISO_POTENCIA_MESES` meses: se avisa `potencia_baja`."""
    faltante: float
    """Fracción de meses faltantes tras pasar los rellenos a `NaN`."""


def limpiar(valores) -> np.ndarray:
    """Copia en `float` con los rellenos de POWER (`-999`) convertidos en `NaN`."""
    v = np.asarray(valores, float).copy()
    v[v <= UMBRAL_RELLENO] = np.nan
    return v


def rellenar_huecos(y, max_hueco=MAX_HUECO, max_faltante=MAX_FALTANTE):
    """Interpola huecos cortos o devuelve `None` si la serie no pasa (reglas 2 y 3).

    Devuelve una copia: igual si no hay faltantes, interpolada linealmente si la
    fracción faltante es ≤ `max_faltante` y ningún hueco supera `max_hueco` meses.
    """
    y = np.asarray(y, float).copy()
    malo = np.isnan(y)
    if not malo.any():
        return y
    if malo.mean() > max_faltante:
        return None
    racha = 0
    for b in malo:
        racha = racha + 1 if b else 0
        if racha > max_hueco:
            return None
    i = np.arange(y.size)
    y[malo] = np.interp(i[malo], i[~malo], y[~malo])
    return y


def validar_ventana(n_meses: int) -> str | None:
    """`ventana_corta` si hay menos de `MIN_MESES` meses; `None` si alcanza."""
    return VENTANA_CORTA if n_meses < MIN_MESES else None


def _es_mar(v: np.ndarray) -> bool:
    """Humedad del suelo sin datos o constante: así llega POWER sobre el océano."""
    finitos = v[~np.isnan(v)]
    return finitos.size == 0 or bool(np.all(finitos == finitos[0]))


def validar_serie(y, variable: str) -> Calidad:
    """Aplica el control de calidad completo a una serie mensual de `variable`."""
    v = limpiar(y)
    faltante = float(np.isnan(v).mean()) if v.size else 1.0
    aviso = v.size < AVISO_POTENCIA_MESES

    def descarte(motivo: str) -> Calidad:
        return Calidad(None, motivo, aviso, faltante)

    motivo_ventana = validar_ventana(v.size)
    if motivo_ventana:
        return descarte(motivo_ventana)
    if variable in VARIABLES_SUELO and _es_mar(v):
        return descarte(SIN_DATOS_TIERRA)
    relleno = rellenar_huecos(v)
    if relleno is None:
        return descarte(FALTANTE_EXCESIVO if faltante > MAX_FALTANTE else HUECO_LARGO)
    if np.std(relleno) == 0:
        return descarte(SERIE_CONSTANTE)
    return Calidad(relleno, None, aviso, faltante)
