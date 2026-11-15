"""Cliente de NASA POWER: la única implementación, compartida con el preparador.

Reglas (backend/CLAUDE.md, sección 6):
- Una petición por celda trae las 5 variables (``community=AG``, endpoint mensual).
- El timeout es un parámetro: 8 s en vivo (``VERASCOPE_POWER_TIMEOUT``), 60 s en lote.
- ``-999`` (o el ``fill_value`` del encabezado) es faltante → ``NaN``.
- La clave de mes ``"13"`` es el promedio anual: se ignora.
- ~1 petición por segundo y espera creciente ante errores y ante ``429``.
- La URL sale de ``VERASCOPE_POWER_URL`` en el momento de la llamada.

Este módulo no importa FastAPI: el preparador ``verascope_datos`` lo usa tal cual.
"""

from __future__ import annotations

import gzip
import json
import os
import time
from datetime import date
from pathlib import Path
from typing import Callable

import numpy as np
import requests

VARIABLES_POWER = ("PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M")
POWER_URL_POR_DEFECTO = "https://power.larc.nasa.gov/api/temporal/monthly/point"
TIMEOUT_VIVO_POR_DEFECTO = 8.0
TIMEOUT_LOTE = 60
PAUSA_S = 1.0
ANIO_INICIO = 1981
ESPERA_MAXIMA_S = 60


class PowerLento(Exception):
    """POWER no respondió dentro del timeout (la API responde ``power_lento``, 504)."""


class PowerError(RuntimeError):
    """POWER falló o se agotaron los reintentos (la API responde ``power_error``, 502)."""


def timeout_vivo() -> float:
    """Espera máxima en vivo, en segundos: ``$VERASCOPE_POWER_TIMEOUT`` o 8."""
    valor = os.environ.get("VERASCOPE_POWER_TIMEOUT", "").strip()
    try:
        segundos = float(valor)
    except ValueError:
        return TIMEOUT_VIVO_POR_DEFECTO
    return segundos if segundos > 0 else TIMEOUT_VIVO_POR_DEFECTO


def url_power() -> str:
    """URL de POWER leída en cada llamada (las pruebas la apuntan a un servidor falso)."""
    return os.environ.get("VERASCOPE_POWER_URL", "").strip() or POWER_URL_POR_DEFECTO


def _anio_fin() -> int:
    # Misma regla que VERASCOPE_FIN de la API; datos/ no importa de estadistica/.
    return int(os.environ.get("VERASCOPE_FIN", date.today().year - 1))


def parsear(respuesta: dict, meses: list[str]) -> dict[str, np.ndarray]:
    """JSON de POWER → ``{codigo: arreglo float32 alineado a meses}``.

    ``meses`` son claves ``"AAAA-MM"`` (o ``"AAAAMM"``). Los faltantes quedan en ``NaN``.
    """
    props = respuesta["properties"]["parameter"]
    relleno = respuesta.get("header", {}).get("fill_value", -999)
    claves = [m.replace("-", "") for m in meses]
    out = {}
    for cod in VARIABLES_POWER:
        d = props.get(cod, {})
        v = np.full(len(claves), np.nan, dtype=np.float32)
        for k, clave in enumerate(claves):
            if clave.endswith("13"):  # promedio anual, no es un mes
                continue
            x = d.get(clave)
            if x is not None and x != relleno and x > -998:
                v[k] = x
        out[cod] = v
    return out


class ClientePower:
    """Pide una celda a POWER con las 5 variables, con pausa y reintentos."""

    def __init__(
        self,
        timeout: float,
        pausa: float = PAUSA_S,
        intentos: int = 4,
        sesion=None,
        url: str | None = None,
        crudo: Path | None = None,
        dormir: Callable[[float], None] = time.sleep,
    ):
        self.timeout = timeout
        self.pausa, self.intentos = pausa, max(1, intentos)
        self.sesion = sesion or requests.Session()
        self.url = url
        self.crudo = crudo  # carpeta para guardar la respuesta original comprimida
        self.dormir = dormir
        self._ultimo: float | None = None

    def _esperar_turno(self) -> None:
        if self._ultimo is not None:
            falta = self.pausa - (time.monotonic() - self._ultimo)
            if falta > 0:
                self.dormir(falta)
        self._ultimo = time.monotonic()

    def celda(self, lat: float, lon: float, anio_inicio: int = ANIO_INICIO, anio_fin=None) -> dict:
        params = {
            "parameters": ",".join(VARIABLES_POWER),
            "community": "AG",
            "latitude": lat,
            "longitude": lon,
            "start": anio_inicio,
            "end": anio_fin or _anio_fin(),
            "format": "JSON",
        }
        url = self.url or url_power()
        error: Exception | None = None
        for k in range(self.intentos):
            if k:
                self.dormir(min(ESPERA_MAXIMA_S, 2**k))  # espera creciente: 2, 4, 8… s
            self._esperar_turno()
            try:
                r = self.sesion.get(url, params=params, timeout=self.timeout)
                if r.status_code == 429:
                    raise PowerError("NASA POWER pidió esperar (429)")
                r.raise_for_status()
                datos = r.json()
            except requests.Timeout as e:
                raise PowerLento(
                    f"NASA POWER tardó más de {self.timeout:g} s en responder. Inténtalo más tarde."
                ) from e
            except Exception as e:  # red, 429, 5xx, JSON inválido
                error = e
                continue
            if self.crudo is not None:
                f = Path(self.crudo) / f"power_{lat:+06.2f}_{lon:+07.2f}.json.gz"
                f.write_bytes(gzip.compress(json.dumps(datos).encode()))
            return datos
        raise PowerError(
            f"NASA POWER no respondió bien tras {self.intentos} intentos ({error}). "
            "Inténtalo más tarde."
        ) from error
