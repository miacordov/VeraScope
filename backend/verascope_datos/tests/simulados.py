"""Genera archivos de prueba con el MISMO formato que entregan NASA y NOAA, para probar sin red.

No son datos reales: tienen un El Niño simulado que hace llover en Piura y secarse Borneo y el norte
de Australia, y un calentamiento de fondo de 0.25 °C por década.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr

from verascope_datos import config
from verascope_datos.fuentes.noaa import TEMPORADAS

RNG = np.random.default_rng(7)


def oni_simulado(meses):
    t = np.arange(len(meses))
    e = 0.9 * np.sin(2 * np.pi * t / 46) + 0.6 * np.sin(2 * np.pi * t / 70 + 1)
    e += np.convolve(RNG.normal(0, 0.25, len(t)), np.ones(6) / 6, "same")
    return np.round(e, 2)


MESES_LARGOS = config.meses(1950)
ONI = oni_simulado(MESES_LARGOS)
ONI_DE = dict(zip(MESES_LARGOS, ONI))


def respuesta(lat, lon):
    if -12 <= lat <= 2 and -84 <= lon <= -76:
        return 3.0
    if -22 <= lat <= 6 and 95 <= lon <= 150:
        return -2.5
    return 0.15


def textos_noaa(carpeta: Path):
    carpeta.mkdir(parents=True, exist_ok=True)
    l = ["SEAS  YR   TOTAL   ANOM"] + [f"{TEMPORADAS[int(m[5:]) - 1]} {m[:4]}  27.00  {ONI_DE[m]:5.2f}" for m in MESES_LARGOS]
    (carpeta / "oni.ascii.txt").write_text("\n".join(l))
    l = [" YR   MON  NINO1+2  ANOM   NINO3    ANOM   NINO4    ANOM NINO3.4    ANOM"]
    l += [f"{m[:4]}  {int(m[5:]):3d}  24.10  {ONI_DE[m] * 1.3:6.2f}  25.80  0.00  28.30  0.00  26.70  0.00" for m in MESES_LARGOS if m >= "1982-01"]
    (carpeta / "sstoi.indices").write_text("\n".join(l))
    l = ["# CO2 de prueba", "# year month decimal average deseasonalized ndays sdev unc"]
    for k, m in enumerate(config.meses(1958)):
        l.append(f"{m[:4]} {int(m[5:]):4d} {int(m[:4]) + int(m[5:]) / 12:10.4f} {315 + k * 0.12:8.2f} {315 + k * 0.12:8.2f} 28 0.3 0.1")
    (carpeta / "co2_mm_mlo.txt").write_text("\n".join(l))


class PowerFalso:
    """Imita la respuesta JSON de POWER (incluye el mes 13 anual y −999 sobre el océano)."""
    def __init__(self, fallar_cada=0):
        self.llamadas = 0; self.fallar_cada = fallar_cada

    def celda(self, lat, lon, *_, **__):
        self.llamadas += 1
        if self.fallar_cada and self.llamadas % self.fallar_cada == 0:
            raise RuntimeError("corte simulado de red")
        a = respuesta(lat, lon); meses = config.meses(); n = len(meses)
        mc = np.array([int(m[5:]) for m in meses]); t = np.arange(n)
        e = np.array([ONI_DE[m] for m in meses])
        lluvia = np.maximum(3 + 2 * np.sin(2 * np.pi * mc / 12) + a * e + RNG.normal(0, 1, n), 0)
        temp = 25 + 3 * np.cos(2 * np.pi * mc / 12) + 0.025 * t / 12 + 0.3 * np.sign(a) * e + RNG.normal(0, 0.4, n)
        suelo = np.clip(0.5 + 0.08 * a * e + RNG.normal(0, 0.05, n), 0, 1)
        oceano = abs(lon) < 60 or (-170 < lon < -90 and abs(lat) < 20 and not (-84 <= lon <= -76))
        hum = 70 + 3 * a * e + RNG.normal(0, 2, n)

        def dic(v, relleno=False):
            d = {m.replace("-", ""): (-999.0 if relleno else round(float(x), 3)) for m, x in zip(meses, v)}
            for y in sorted({m[:4] for m in meses}):
                d[f"{y}13"] = 0.0
            return d
        return {"header": {"fill_value": -999.0},
                "properties": {"parameter": {"PRECTOTCORR": dic(lluvia), "T2M": dic(temp), "RH2M": dic(hum),
                                             "GWETROOT": dic(suelo, oceano), "GWETTOP": dic(suelo, oceano)}}}


# Como los archivos reales: GPM y AppEEARS fechan con calendario juliano (xarray devuelve fechas de cftime).
JULIANO_GPM = {"time": {"units": "seconds since 1980-01-06 00:00:00 UTC", "calendar": "julian"}}
JULIANO_APPEEARS = {"time": {"units": "seconds since 2000-01-01 00:00:00+00:00", "calendar": "julian"}}


def _rejilla_local(paso, cajas):
    return np.unique(np.concatenate([np.arange(a, b, paso) + paso / 2 for a, b in cajas])).round(4)


def archivos_satelite(carpeta: Path, anios=(2018, 2019)):
    """IMERG (HDF5, grupo Grid, dims time·lon·lat) y GLDAS (NetCDF4, dims time·lat·lon), un archivo por mes."""
    (carpeta / "imerg").mkdir(parents=True, exist_ok=True); (carpeta / "gldas").mkdir(exist_ok=True); (carpeta / "ndvi").mkdir(exist_ok=True)
    lon_i = _rejilla_local(0.1, [(-82, -79), (114, 118), (130, 134)]) - 0.05
    lat_i = _rejilla_local(0.1, [(-17, 1)]) - 0.05
    lon_g = _rejilla_local(0.25, [(-82, -79), (114, 118), (130, 134)]) - 0.125
    lat_g = _rejilla_local(0.25, [(-17, 1)]) - 0.125
    resp = np.vectorize(respuesta)
    for y in range(anios[0], anios[1] + 1):
        for m in range(1, 13):
            mes = f"{y}-{m:02d}"; e = ONI_DE[mes]; t = pd.to_datetime([f"{mes}-01"])
            LA, LO = np.meshgrid(lat_i, lon_i)              # IMERG: lon antes que lat
            pr = np.maximum((3 + resp(LA, LO) * e) / 24.0, 0).astype("float32")[None]
            ds = xr.Dataset({"precipitation": (("time", "lon", "lat"), pr, {"units": "mm/hr"})},
                            coords={"time": t, "lon": lon_i, "lat": lat_i})
            ds.to_netcdf(carpeta / "imerg" / f"3B-MO.MS.MRG.3IMERG.{y}{m:02d}01-S000000-E235959.{m:02d}.V07B.HDF5",
                         engine="h5netcdf", group="Grid", encoding=JULIANO_GPM)
            LA, LO = np.meshgrid(lat_g, lon_g, indexing="ij")
            r = resp(LA, LO)
            gl = xr.Dataset({"Evap_tavg": (("time", "lat", "lon"), ((2 + 0.3 * r * e) / 86400.0)[None].astype("float32")),
                             "Qs_acc": (("time", "lat", "lon"), ((0.5 + 0.2 * r * e) / 8)[None].astype("float32")),
                             "Qsb_acc": (("time", "lat", "lon"), np.full((1,) + LA.shape, 0.01, "float32")),
                             "SoilMoi0_10cm_inst": (("time", "lat", "lon"), (25 + 3 * r * e)[None].astype("float32"))},
                            coords={"time": t, "lat": lat_g, "lon": lon_g})
            gl.to_netcdf(carpeta / "gldas" / f"GLDAS_NOAH025_M.A{y}{m:02d}.021.nc4", engine="h5netcdf")
    # NDVI como lo entrega AppEEARS: entero sin escalar y latitud descendente
    for l in config.LUGARES_DEMO:
        la = np.arange(l.lat + 0.5, l.lat - 0.5, -0.05); lo = np.arange(l.lon - 0.5, l.lon + 0.5, 0.05)
        meses = config.meses(2000); t = pd.to_datetime([f"{m}-01" for m in meses])
        base = np.array([0.6 - 0.05 * respuesta(l.lat, l.lon) * ONI_DE[m] for m in meses])
        v = (np.clip(base, -0.2, 1) * 10000)[:, None, None] * np.ones((1, la.size, lo.size))
        xr.Dataset({"_1_km_monthly_NDVI": (("time", "lat", "lon"), v.astype("int16"))},
                   coords={"time": t, "lat": la, "lon": lo}).to_netcdf(carpeta / "ndvi" / f"{l.id}.nc", engine="h5netcdf",
                                                         encoding=JULIANO_APPEEARS)
