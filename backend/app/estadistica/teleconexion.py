"""Líneas causa → consecuencia desde una celda de origen (guía §10; cálculos C14–C15).

Dada una celda de origen, encuentra sola las regiones lejanas que sufren lo opuesto
(o lo mismo) en los mismos meses **y** responden a El Niño. Mide variabilidad
compartida, no tendencias opuestas ni causalidad: la redacción es "ocurren a la vez y
ambos responden a El Niño".

Funciones puras: reciben arreglos de numpy (las matrices las prepara la API al
arrancar con `preparar_matrices`), sin red, sin disco y sin FastAPI. Los umbrales
salen solo de `constantes.py`.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from app.estadistica.anomalias import estandarizar
from app.estadistica.constantes import (
    ALFA,
    FDR_Q,
    KM_MIN_DESTINO,
    KM_SEP_DESTINOS,
    MAX_LINEAS_IGUALES,
    MAX_LINEAS_OPUESTAS,
    UMBRAL_COINCIDENCIA,
)
from app.estadistica.enso import p_correlacion, r1
from app.estadistica.fdr import benjamini_hochberg

RADIO_TIERRA_KM = 6371.0088
"""Radio medio de la Tierra (IUGG), para la distancia de círculo máximo."""

VARIABLES_CON_LINEAS = frozenset({"PRECTOTCORR", "GWETROOT", "GWETTOP", "RH2M"})
"""V1, V3, V4 y V5: las variables para las que el informe estadístico define líneas."""

MENSAJE_SIN_VINCULO = "No se encontró un vínculo que cumpla los criterios."
MENSAJE_VARIABLE_SIN_LINEAS = (
    "Para la temperatura no se buscan líneas: el informe estadístico las define solo "
    "para la lluvia y las humedades."
)

OPUESTO = "opuesto"
MISMO = "mismo"


def haversine_km(lat1, lon1, lat2, lon2):
    """Distancia de círculo máximo en km (guía §10, paso 4). Vectorizable.

    Acepta longitudes en −180..180 o en 0..360: la fórmula usa `sin²(Δλ/2)`, que es
    periódica, así que el cruce de ±180° sale bien sin normalizar.
    """
    f1, f2 = np.radians(lat1), np.radians(lat2)
    dlat = f2 - f1
    dlon = np.radians(np.asarray(lon2, float) - np.asarray(lon1, float))
    h = np.sin(dlat / 2) ** 2 + np.cos(f1) * np.cos(f2) * np.sin(dlon / 2) ** 2
    d = 2 * RADIO_TIERRA_KM * np.arcsin(np.sqrt(np.clip(h, 0.0, 1.0)))
    return float(d) if np.ndim(d) == 0 else d


def celda_mas_cercana(lat: float, lon: float, lats, lons) -> tuple[int, float]:
    """Celda de ScanMap más cercana a un clic fuera de la rejilla (guía §10, paso 7).

    Devuelve `(índice, distancia_km)`; la distancia se informa como
    `distancia_a_clic_km`.
    """
    d = haversine_km(lat, lon, np.asarray(lats, float), np.asarray(lons, float))
    i = int(np.argmin(d))
    return i, float(d[i])


@dataclass(frozen=True)
class Matrices:
    """Matrices de una variable, precalculadas al arrancar (guía §10, paso 1)."""

    z: np.ndarray
    """Anomalías estandarizadas (celdas × meses, `float32`); 0 en celdas no válidas."""
    validas: np.ndarray
    """Celdas con serie completa y no constante tras el control de calidad."""
    rho1: np.ndarray
    """Autocorrelación de rezago 1 de cada celda (insumo del tamaño efectivo)."""
    n: int
    """Meses de cada serie."""


def preparar_matrices(anomalias) -> Matrices:
    """Paso 1 de la guía §10: `Z`, máscara de celdas válidas y `ρ₁` por celda.

    `anomalias` es la matriz (celdas × meses) de la serie **original** (cálculo C3).
    `Z` usa la desviación estándar poblacional (`estandarizar`) y se guarda en `float32`
    para ahorrar memoria; `r` coincide con el de `float64` a 1e-5.
    """
    a = np.asarray(anomalias, float)
    if a.ndim != 2:
        raise ValueError("las anomalías deben ser una matriz celdas × meses")
    with np.errstate(invalid="ignore"):
        validas = np.all(np.isfinite(a), axis=1) & (np.nanstd(a, axis=1) > 0)
    z = np.zeros(a.shape, dtype=np.float32)
    rho1 = np.full(a.shape[0], np.nan)
    if validas.any():
        z[validas] = estandarizar(a[validas]).astype(np.float32)
        rho1[validas] = r1(a[validas])
    return Matrices(z=z, validas=validas, rho1=rho1, n=int(a.shape[1]))


@dataclass(frozen=True)
class LineaTeleconexion:
    """Una línea hacia un destino (campos de `Linea` del contrato)."""

    tipo: str
    lat: float
    lon: float
    r: float
    p_ajustado: float
    distancia_km: float
    r_el_nino_origen: float
    r_el_nino_destino: float
    meses_coincidencia: tuple[tuple[str, str], ...]
    """(fecha "AAAA-MM", fase del índice en ese mismo mes)."""

    def como_contrato(self) -> dict:
        """Diccionario con la forma de `Linea` (guía §17)."""
        return {
            "tipo": self.tipo,
            "lat": self.lat,
            "lon": self.lon,
            "r": self.r,
            "p_ajustado": self.p_ajustado,
            "distancia_km": self.distancia_km,
            "r_el_nino_origen": self.r_el_nino_origen,
            "r_el_nino_destino": self.r_el_nino_destino,
            "meses_coincidencia": [
                {"fecha": fecha, "fase": fase} for fecha, fase in self.meses_coincidencia
            ],
        }


@dataclass(frozen=True)
class ResultadoTeleconexion:
    """Líneas encontradas desde un origen; sin líneas, `mensaje_vacio` lo explica."""

    lineas: list[LineaTeleconexion]
    mensaje_vacio: str | None


def _coincidencias(zi, zj, tipo, fechas, fases) -> tuple[tuple[str, str], ...]:
    """Paso 5: meses en que ambos lados se salen de lo normal a la vez.

    Opuesto: `z_i > 1` y `z_j < −1`, o al revés. Mismo efecto: ambos del mismo lado.
    La fase es la del índice **en el propio mes**, sin rezago (informe estadístico).
    """
    u = UMBRAL_COINCIDENCIA
    if tipo == OPUESTO:
        meses = ((zi > u) & (zj < -u)) | ((zi < -u) & (zj > u))
    else:
        meses = ((zi > u) & (zj > u)) | ((zi < -u) & (zj < -u))
    return tuple((fechas[k], str(fases[k])) for k in np.flatnonzero(meses))


def buscar_lineas(
    variable: str,
    origen: int,
    matrices: Matrices,
    lats,
    lons,
    r_enso,
    p_enso,
    fechas: Sequence[str],
    fases: Sequence[str],
) -> ResultadoTeleconexion:
    """Guía §10, pasos 1–6: hasta 3 líneas de efecto opuesto y 2 de mismo efecto.

    1. `r = Z @ Z[origen] / n` contra todas las celdas en una operación.
    2. Candidatas: celdas válidas, a más de `KM_MIN_DESTINO` del origen y con `p_enso`
       finito. El p de cada `r` usa el tamaño efectivo (cálculo C11, con piso
       `NEFF_PISO`) y se corrige con Benjamini-Hochberg sobre todas las candidatas
       (cálculo C14); entra si `p_ajustado < FDR_Q`.
    3. Causa común: origen y destino con `p_enso < ALFA`; signos opuestos de `r_enso`
       para una línea de efecto opuesto (`r < 0`) e iguales para mismo efecto
       (`r > 0`).
    4. Se eligen por |r| descendente; cada destino a más de `KM_SEP_DESTINOS` de los
       ya elegidos (de cualquier tipo). Primero las opuestas, después las iguales.
    5. `meses_coincidencia` con la fase del propio mes (`_coincidencias`).
    6. Sin ninguna: lista vacía y `MENSAJE_SIN_VINCULO`. También es un resultado.

    `r_enso` y `p_enso` son las columnas de `resultados.parquet` (el escaneo decide si
    `p_enso` llega corregido por BH, decisión L13). `fases` sale de `indices.fases`
    sobre el índice alineado con `fechas`. Variables sin líneas (`T2M`): lista vacía
    con `MENSAJE_VARIABLE_SIN_LINEAS`.
    """
    if variable not in VARIABLES_CON_LINEAS:
        return ResultadoTeleconexion([], MENSAJE_VARIABLE_SIN_LINEAS)
    vacio = ResultadoTeleconexion([], MENSAJE_SIN_VINCULO)
    lats = np.asarray(lats, float)
    lons = np.asarray(lons, float)
    r_enso = np.asarray(r_enso, float)
    p_enso = np.asarray(p_enso, float)
    if len(fechas) != matrices.n or len(fases) != matrices.n:
        raise ValueError("fechas y fases deben tener un valor por mes de la matriz")
    if not matrices.validas[origen] or not (p_enso[origen] < ALFA):
        return vacio

    z = matrices.z
    r = (z @ z[origen]).astype(float) / matrices.n
    distancia = haversine_km(lats[origen], lons[origen], lats, lons)
    candidatas = matrices.validas & (distancia > KM_MIN_DESTINO) & np.isfinite(p_enso)
    candidatas[origen] = False
    if not candidatas.any():
        return vacio

    p, _ = p_correlacion(
        r[candidatas], matrices.rho1[origen], matrices.rho1[candidatas], z.shape[1]
    )
    p_ajustado = np.full(r.shape, np.nan)
    p_ajustado[candidatas] = benjamini_hochberg(p)

    with np.errstate(invalid="ignore"):
        base = candidatas & (p_ajustado < FDR_Q) & (p_enso < ALFA)
        mismo_signo = np.sign(r_enso) == np.sign(r_enso[origen])
    reglas = (
        (OPUESTO, base & (r < 0) & ~mismo_signo, MAX_LINEAS_OPUESTAS),
        (MISMO, base & (r > 0) & mismo_signo, MAX_LINEAS_IGUALES),
    )

    lineas: list[LineaTeleconexion] = []
    for tipo, elegibles, maximo in reglas:
        elegidas = 0
        for j in sorted(np.flatnonzero(elegibles), key=lambda k: -abs(r[k])):
            if elegidas == maximo:
                break
            lejos = all(
                haversine_km(lats[j], lons[j], li.lat, li.lon) > KM_SEP_DESTINOS for li in lineas
            )
            if not lejos:
                continue
            lineas.append(
                LineaTeleconexion(
                    tipo=tipo,
                    lat=float(lats[j]),
                    lon=float(lons[j]),
                    r=float(r[j]),
                    p_ajustado=float(p_ajustado[j]),
                    distancia_km=float(distancia[j]),
                    r_el_nino_origen=float(r_enso[origen]),
                    r_el_nino_destino=float(r_enso[j]),
                    meses_coincidencia=_coincidencias(z[origen], z[j], tipo, fechas, fases),
                )
            )
            elegidas += 1
    return ResultadoTeleconexion(lineas, None) if lineas else vacio
