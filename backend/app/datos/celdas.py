"""Celdas de VeraScope: la única cuantización a 0.5° y la rejilla de ScanMap.

Reglas (backend/CLAUDE.md, sección 6):
- Todo punto se cuantiza con ``0.5 * redondeo(x / 0.5)`` antes de usarlo.
- Empates exactos (x.25, x.75) van hacia +infinito, igual que ``Math.round``
  de JavaScript, para que la app y la API coincidan. El ``round`` de Python
  redondea al par y daría otra celda.
- Longitudes en (−180, 180]: 180 se escribe +180 y −180 también, igual que
  ``config.rejilla()`` del preparador, para compartir llaves del casillero. La celda que devuelve la API
  es la autoridad.
- La llave de lugar es la misma del casillero del preparador
  (``verascope_datos.almacen.lugar_celda``).
"""

from __future__ import annotations

import math

PASO_CELDA = 0.5

# Rejilla de ScanMap: 34°S–34°N, 90°E–30°O, paso 2° → 35 × 121 = 4235 celdas.
REJILLA_LAT = (-34.0, 34.0)
REJILLA_LON_0_360 = (90.0, 330.0)
REJILLA_PASO = 2.0


def _sin_cero_negativo(x: float) -> float:
    return x + 0.0


def cuantizar(valor: float, paso: float = PASO_CELDA) -> float:
    """Lleva un valor al centro de celda más cercano (empates hacia +inf)."""
    return _sin_cero_negativo(round(math.floor(valor / paso + 0.5) * paso, 4))


def lon_a_180(lon: float) -> float:
    """Convierte una longitud cualquiera a (−180, 180] (−180 → 180)."""
    x = round((lon + 180.0) % 360.0 - 180.0, 4)
    return _sin_cero_negativo(180.0 if x == -180.0 else x)


def lon_a_360(lon: float) -> float:
    """Convierte una longitud cualquiera a 0..360 (360 → 0)."""
    return _sin_cero_negativo(round(lon % 360.0, 4))


def celda(lat: float, lon: float) -> tuple[float, float]:
    """Celda de 0.5° de un punto: (lat, lon) con lon en (−180, 180]."""
    lat_c = min(90.0, max(-90.0, cuantizar(lat)))
    return lat_c, lon_a_180(cuantizar(lon_a_180(lon)))


def lugar_celda(lat: float, lon: float) -> str:
    """Llave del casillero para una celda ya cuantizada."""
    return f"celda:{_sin_cero_negativo(lat):+.2f}:{_sin_cero_negativo(lon):+.2f}"


def rejilla() -> list[tuple[float, float]]:
    """Celdas de ScanMap como (lat, lon), orden lat-mayor, lon en (−180, 180]."""
    n_lat = round((REJILLA_LAT[1] - REJILLA_LAT[0]) / REJILLA_PASO) + 1
    n_lon = round((REJILLA_LON_0_360[1] - REJILLA_LON_0_360[0]) / REJILLA_PASO) + 1
    return [
        (
            REJILLA_LAT[0] + i * REJILLA_PASO,
            lon_a_180(REJILLA_LON_0_360[0] + j * REJILLA_PASO),
        )
        for i in range(n_lat)
        for j in range(n_lon)
    ]
