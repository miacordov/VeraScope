"""Promedio de un campo satelital sobre la celda de 0.5° de un lugar, ponderado por el coseno de la latitud."""
import numpy as np
import pandas as pd

from .. import config


def anio_mes(fecha):
    """Fecha de un NetCDF -> "AAAA-MM". Acepta numpy/pandas y fechas de cftime (GPM y AppEEARS usan calendario juliano)."""
    if hasattr(fecha, "calendar"):                     # cftime: no se puede pasar a pandas.Timestamp
        return f"{fecha.year}-{fecha.month:02d}"
    t = pd.Timestamp(fecha)
    return f"{t.year}-{t.month:02d}"


def caja(lugar, mitad=None):
    mitad = mitad if mitad is not None else config.CELDA / 2
    la, lo = config.cuantizar(lugar.lat), config.cuantizar(lugar.lon)
    return la - mitad, la + mitad, lo - mitad, lo + mitad


def _nombre(da, opciones):
    for n in opciones:
        if n in da.dims or n in da.coords:
            return n
    raise KeyError(f"No encuentro la coordenada {opciones} en {list(da.coords)}")


def promedio_caja(da, lugar):
    """`da`: DataArray con coordenadas de latitud y longitud (en cualquier orden de dimensiones)."""
    lat_n = _nombre(da, ("lat", "latitude", "y"))
    lon_n = _nombre(da, ("lon", "longitude", "x"))
    la0, la1, lo0, lo1 = caja(lugar)
    lat = da[lat_n].values
    sub = da.sel({lat_n: slice(la0, la1) if lat[0] < lat[-1] else slice(la1, la0), lon_n: slice(lo0, lo1)})
    if sub[lat_n].size == 0 or sub[lon_n].size == 0:
        # celda más chica que un píxel: se toma el píxel más cercano
        sub = da.sel({lat_n: [config.cuantizar(lugar.lat)], lon_n: [config.cuantizar(lugar.lon)]}, method="nearest")
    w = np.cos(np.deg2rad(sub[lat_n]))
    otras = [d for d in sub.dims if d not in (lat_n, lon_n)]
    m = sub.weighted(w.fillna(0)).mean(dim=[lat_n, lon_n], skipna=True)
    return m if otras else float(m)
