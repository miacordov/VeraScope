"""V12 MODIS NDVI (MOD13A3 v061, mensual a 1 km) mediante la API de AppEEARS.

AppEEARS recorta del lado del servidor y entrega NetCDF4. Las tareas tardan minutos u horas:
el programa las envía, guarda su número y, si se vuelve a correr, retoma la misma tarea.
"""
import json
import netrc
import os
import time
from pathlib import Path

import numpy as np
import requests
import xarray as xr

from .. import config
from .region import anio_mes, caja, promedio_caja

BASE = "https://appeears.earthdatacloud.nasa.gov/api"
PRODUCTO, CAPA = "MOD13A3.061", "_1_km_monthly_NDVI"  # AppEEARS no ofrece MOD13C2 (CMG 0.05°)


def credenciales():
    u, p = os.environ.get("EARTHDATA_USERNAME"), os.environ.get("EARTHDATA_PASSWORD")
    if u and p:
        return u, p
    try:
        a = netrc.netrc().authenticators("urs.earthdata.nasa.gov")
        if a:
            return a[0], a[2]
    except (FileNotFoundError, netrc.NetrcParseError):
        pass
    raise RuntimeError("Faltan credenciales de NASA Earthdata para AppEEARS (ver README).")


def tarea(lugar, anio_inicio, anio_fin):
    la0, la1, lo0, lo1 = caja(lugar, mitad=0.5)       # recuadro de 1°, se promedia luego sobre la celda
    poligono = [[[lo0, la0], [lo1, la0], [lo1, la1], [lo0, la1], [lo0, la0]]]
    return {"task_type": "area", "task_name": f"verascope_ndvi_{lugar.id}",
            "params": {"dates": [{"startDate": f"01-01-{max(anio_inicio, 2000)}", "endDate": f"12-31-{anio_fin}"}],
                       "layers": [{"product": PRODUCTO, "layer": CAPA}],
                       "output": {"format": {"type": "netcdf4"}, "projection": "geographic"},
                       "geo": {"type": "FeatureCollection", "features": [
                           {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": poligono}}]}}}


class AppEEARS:
    def __init__(self, estado: Path, sesion=None):
        self.s = sesion or requests.Session()
        self.estado_f = estado
        self.estado = json.loads(estado.read_text()) if estado.exists() else {}
        self.token = None

    def _guardar(self):
        self.estado_f.write_text(json.dumps(self.estado, indent=2))

    def entrar(self):
        u, p = credenciales()
        r = self.s.post(f"{BASE}/login", auth=(u, p), timeout=60)
        r.raise_for_status()
        self.token = r.json()["token"]
        self.s.headers["Authorization"] = f"Bearer {self.token}"

    def enviar(self, lugar, anio_inicio, anio_fin):
        if lugar.id in self.estado:
            return self.estado[lugar.id]
        r = self.s.post(f"{BASE}/task", json=tarea(lugar, anio_inicio, anio_fin), timeout=60)
        r.raise_for_status()
        self.estado[lugar.id] = r.json()["task_id"]
        self._guardar()
        return self.estado[lugar.id]

    def esperar(self, task_id, cada_s=30, max_h=6, avisar=None):
        fin = time.time() + max_h * 3600
        while time.time() < fin:
            st = self.s.get(f"{BASE}/task/{task_id}", timeout=60).json().get("status")
            if avisar:
                avisar(st)
            if st == "done":
                return
            if st == "error":
                raise RuntimeError(f"AppEEARS marcó error en la tarea {task_id}")
            time.sleep(cada_s)
        raise TimeoutError(f"La tarea {task_id} de AppEEARS sigue en proceso; vuelve a correr el comando más tarde.")

    def descargar(self, task_id, carpeta: Path):
        archivos = self.s.get(f"{BASE}/bundle/{task_id}", timeout=60).json()["files"]
        salida = []
        for a in archivos:
            if a["file_name"].endswith(".nc"):
                destino = carpeta / Path(a["file_name"]).name
                with self.s.get(f"{BASE}/bundle/{task_id}/{a['file_id']}", stream=True, allow_redirects=True, timeout=300) as r:
                    r.raise_for_status()
                    with open(destino, "wb") as f:
                        for trozo in r.iter_content(1 << 20):
                            f.write(trozo)
                salida.append(destino)
        return salida


def leer_ndvi(archivo, lugar):
    """NetCDF de AppEEARS -> {AAAA-MM: NDVI}. Busca la variable que contenga 'NDVI' (AppEEARS ajusta los nombres)."""
    with xr.open_dataset(archivo) as ds:
        nombre = next((v for v in ds.data_vars if "NDVI" in v.upper()), None)
        if nombre is None:
            raise KeyError(f"No hay variable de NDVI en {archivo}")
        da = ds[nombre]
        if float(da.max(skipna=True)) > 1.5:            # sin escalar: se aplica el factor 0.0001
            da = da * 0.0001
        da = da.where((da >= -0.2) & (da <= 1.0))
        serie = promedio_caja(da, lugar)
        return {anio_mes(x): float(v) for x, v in zip(serie["time"].values, serie.values) if np.isfinite(v)}
