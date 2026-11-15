"""V6 ONI, V7 Niño 1+2 y V13 CO₂: archivos de texto pequeños de NOAA.

La lectura de ONI y Niño 1+2 vive en el backend (`app.datos.indices`): una sola implementación.
"""
import numpy as np
import requests

from app.datos.indices import TEMPORADAS, parsear_nino12, parsear_oni  # noqa: F401

URL_ONI = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"
URL_SSTOI = "https://www.cpc.ncep.noaa.gov/data/indices/sstoi.indices"
URL_CO2 = "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_mm_mlo.txt"


def bajar(url, timeout=60):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def _a_serie(tabla, meses):
    return np.array([tabla.get(m, np.nan) for m in meses], dtype=np.float32)


def parsear_co2(texto, meses):
    """co2_mm_mlo.txt: año mes fecha_decimal promedio desestacionalizado ... Líneas con # son comentarios."""
    t = {}
    for linea in texto.splitlines():
        if linea.startswith("#") or not linea.strip():
            continue
        p = linea.split()
        try:
            v = float(p[3])
            if v > 0:
                t[f"{int(p[0])}-{int(p[1]):02d}"] = v
        except (ValueError, IndexError):
            continue
    return _a_serie(t, meses)
