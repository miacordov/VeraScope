"""Series sintéticas con semilla fija para las pruebas del motor (sección 13 de la guía).

Cada serie se arma con parámetros conocidos para comprobar que el motor los recupera:

    valor_t = ciclo_estacional(mes_t) + β·t + γ·E_{t−ℓ} + ε_t

- β viene en unidades **por década** (`beta_dec`); por mes es `beta_dec / 120`.
- E es un índice tipo ONI: AR(1) con autocorrelación alta (ρ = 0.93 por defecto).
- ε es ruido AR(1) (autocorrelacionado, como las series mensuales reales).
- El índice se entrega **alineado mes a mes** con la serie, como lo espera el motor:
  `indice[t]` es E del mes t, y el valor del mes t depende de `indice[t − ℓ]`.
  Para los primeros ℓ meses se usan valores del índice anteriores a la ventana,
  así el efecto de El Niño existe en toda la serie.

Reglas: ninguna prueba toca la red y toda serie sale de un `numpy.random.Generator`
creado con una semilla fija (`generador(i)`). Estas cifras son de series sintéticas,
no de datos reales; no se citan como resultados de la plataforma.
"""

from dataclasses import dataclass

import numpy as np

SEMILLA = 20261003
"""Semilla base de todas las pruebas. Cambiarla cambia todas las series: no la toques."""

MESES_POR_DECADA = 120
FALTANTE_POWER = -999.0


def generador(repeticion=0):
    """Generador reproducible para la repetición `repeticion` (0, 1, 2, ...)."""
    return np.random.default_rng([SEMILLA, int(repeticion)])


def ar1(n, rho, sigma, rng):
    """Proceso AR(1) estacionario de largo `n`: x_t = ρ·x_{t−1} + e_t, con desviación total `sigma`.

    El primer valor sale de la distribución estacionaria, así no hay periodo de arranque.
    """
    if not -1 < rho < 1:
        raise ValueError("rho debe estar entre -1 y 1 (sin incluirlos)")
    e = rng.normal(0.0, sigma * np.sqrt(1 - rho**2), n)
    x = np.empty(n)
    x[0] = rng.normal(0.0, sigma)
    for t in range(1, n):
        x[t] = rho * x[t - 1] + e[t]
    return x


@dataclass(frozen=True)
class SerieSintetica:
    valores: np.ndarray
    """Serie mensual con ciclo estacional (lo que entregaría POWER)."""
    indice: np.ndarray
    """Índice tipo ONI alineado mes a mes con `valores`, sin faltantes."""
    meses_calendario: np.ndarray
    """1..12, empezando en `mes_inicial`."""
    beta_dec: float
    gamma: float
    rezago: int
    componente_enso: np.ndarray
    """γ·E_{t−ℓ} de cada mes, para comprobar la serie sin El Niño."""


def serie(
    rng,
    n=480,
    beta_dec=0.0,
    gamma=0.0,
    rezago=0,
    rho_indice=0.93,
    sigma_indice=1.0,
    rho_ruido=0.3,
    sigma_ruido=1.0,
    amplitud_estacional=2.0,
    mes_inicial=1,
):
    """Serie mensual sintética con tendencia β, efecto de El Niño γ y rezago ℓ conocidos."""
    if rezago < 0:
        raise ValueError("el rezago no puede ser negativo")
    indice_extendido = ar1(n + rezago, rho_indice, sigma_indice, rng)
    indice = indice_extendido[rezago:]
    indice_desfasado = indice_extendido[:n]  # E_{t−ℓ} para t = 0..n−1
    meses = (np.arange(n) + mes_inicial - 1) % 12 + 1
    ciclo = amplitud_estacional * np.sin(2 * np.pi * (meses - 1) / 12)
    t = np.arange(n)
    enso = gamma * indice_desfasado
    ruido = ar1(n, rho_ruido, sigma_ruido, rng)
    valores = ciclo + beta_dec / MESES_POR_DECADA * t + enso + ruido
    return SerieSintetica(valores, indice, meses, float(beta_dec), float(gamma), int(rezago), enso)


def series_independientes(rng, n=480, rho=0.9):
    """Dos series AR(1) sin relación entre sí (prueba de correlación: falsas alarmas ≈ 5 %)."""
    return ar1(n, rho, 1.0, rng), ar1(n, rho, 1.0, rng)


def con_huecos(valores, inicio, largo, relleno=np.nan):
    """Copia de `valores` con `largo` meses seguidos faltantes desde `inicio`.

    `relleno=FALTANTE_POWER` imita el -999 de POWER (el control de calidad lo pasa a NaN).
    """
    v = np.asarray(valores, float).copy()
    if inicio < 0 or largo < 0 or inicio + largo > v.size:
        raise ValueError("el hueco se sale de la serie")
    v[inicio : inicio + largo] = relleno
    return v
