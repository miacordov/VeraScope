"""V1–V5 · NASA POWER: una petición por celda trae las 5 variables, de 1981 al último año completo."""
import gzip
import json
import time

import numpy as np
import requests

from .. import config
from ..variables import POWER


def parsear(respuesta, meses):
    """JSON de POWER -> {codigo: arreglo alineado a `meses`}. Ignora el mes 13 (anual) y −999."""
    props = respuesta["properties"]["parameter"]
    relleno = respuesta.get("header", {}).get("fill_value", -999)
    out = {}
    for cod in POWER:
        d = props.get(cod, {})
        v = np.full(len(meses), np.nan, dtype=np.float32)
        for k, m in enumerate(meses):
            x = d.get(m.replace("-", ""))
            if x is not None and x != relleno and x > -998:
                v[k] = x
        out[cod] = v
    return out


class ClientePower:
    def __init__(self, pausa=config.POWER_PAUSA_S, intentos=4, sesion=None, crudo=None):
        self.pausa, self.intentos = pausa, intentos
        self.sesion = sesion or requests.Session()
        self.crudo = crudo          # carpeta para guardar la respuesta original comprimida
        self._ultimo = 0.0

    def _esperar(self):
        falta = self.pausa - (time.monotonic() - self._ultimo)
        if falta > 0:
            time.sleep(falta)
        self._ultimo = time.monotonic()

    def celda(self, lat, lon, anio_inicio=config.ANIO_INICIO, anio_fin=None):
        anio_fin = anio_fin or config.ANIO_FIN
        params = {"parameters": ",".join(POWER), "community": "AG", "latitude": lat, "longitude": lon,
                  "start": anio_inicio, "end": anio_fin, "format": "JSON"}
        error = None
        for k in range(self.intentos):
            self._esperar()
            try:
                r = self.sesion.get(config.POWER_URL, params=params, timeout=config.POWER_TIMEOUT_S)
                if r.status_code == 429:
                    raise RuntimeError("POWER pidió esperar (429)")
                r.raise_for_status()
                datos = r.json()
                if self.crudo is not None:
                    f = self.crudo / f"power_{lat:+06.2f}_{lon:+07.2f}.json.gz"
                    f.write_bytes(gzip.compress(json.dumps(datos).encode()))
                return datos
            except Exception as e:  # red, 5xx, JSON inválido
                error = e
                time.sleep(min(60, 2 ** (k + 1)))
        raise RuntimeError(f"POWER no respondió tras {self.intentos} intentos: {error}")
