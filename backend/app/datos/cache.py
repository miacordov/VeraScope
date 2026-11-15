"""Caché de dos niveles para VeraScope (guía §6, issue #3).

Nivel 1 — series mensuales: reutiliza ``verascope_datos.almacen.Casillero``
(SQLite WAL, float32, llave ``lugar_celda``). Archivo: ``{VERASCOPE_DATOS}/casillero.sqlite``.

Nivel 2 — resultados calculados: tabla SQLite en el mismo archivo. Llave =
celda + variable + ventana + índice + ``VERSION_METODO``. Solo se invalida al
subir ``VERSION_METODO``.

Cerrojo por celda: dos peticiones simultáneas a la misma celda nueva producen
una sola llamada a POWER.
"""

from __future__ import annotations

import gzip
import json
import logging
import threading
from pathlib import Path
from typing import Any

from app.estadistica import constantes

logger = logging.getLogger(__name__)

ARCHIVO_CASILLERO = "casillero.sqlite"

# ── Cerrojo por celda ────────────────────────────────────────────────────────

_cerrojos_lock = threading.Lock()
_cerrojos: dict[str, threading.Lock] = {}


def cerrojo_celda(llave: str) -> threading.Lock:
    """Devuelve (o crea) un Lock exclusivo para una llave de celda.

    Garantiza que dos peticiones a la misma celda nueva no disparen dos llamadas
    a POWER: la segunda espera a que la primera termine y luego lee de caché.
    """
    with _cerrojos_lock:
        if llave not in _cerrojos:
            _cerrojos[llave] = threading.Lock()
        return _cerrojos[llave]


# ── Nivel 2: resultados calculados ───────────────────────────────────────────

_ESQUEMA_N2 = """
CREATE TABLE IF NOT EXISTS resultados (
    llave TEXT PRIMARY KEY,
    version INTEGER NOT NULL,
    datos BLOB NOT NULL
);
"""


def _llave_n2(variable: str, lat: float, lon: float,
              inicio: int, fin: int, indice: str) -> str:
    """Llave determinista para el nivel 2."""
    return f"{variable}:{lat:+.2f}:{lon:+.2f}:{inicio}:{fin}:{indice}"


class CacheResultados:
    """Caché de nivel 2: resultados de ``analizar_celda`` serializados con gzip+JSON.

    Comparte el archivo SQLite del Casillero pero en una tabla separada
    (``resultados``). Cada entrada guarda ``VERSION_METODO`` con la que se
    calculó; una versión distinta equivale a un fallo de caché.
    """

    def __init__(self, ruta: Path) -> None:
        import sqlite3

        self.db = sqlite3.connect(str(ruta), timeout=30, check_same_thread=False)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(_ESQUEMA_N2)

    def cerrar(self) -> None:
        self.db.close()

    def leer(self, variable: str, lat: float, lon: float,
             inicio: int, fin: int, indice: str) -> dict[str, Any] | None:
        """Devuelve el resultado guardado o ``None`` si no existe o la versión cambió."""
        llave = _llave_n2(variable, lat, lon, inicio, fin, indice)
        fila = self.db.execute(
            "SELECT version, datos FROM resultados WHERE llave = ?",
            (llave,),
        ).fetchone()
        if fila is None:
            logger.debug("cache_n2 fallo llave=%s motivo=no_existe", llave)
            return None
        if fila[0] != constantes.VERSION_METODO:
            logger.debug("cache_n2 fallo llave=%s motivo=version v_guardada=%d v_actual=%d",
                         llave, fila[0], constantes.VERSION_METODO)
            return None
        logger.debug("cache_n2 acierto llave=%s", llave)
        return json.loads(gzip.decompress(fila[1]))

    def guardar(self, variable: str, lat: float, lon: float,
                inicio: int, fin: int, indice: str,
                resultado: dict[str, Any]) -> None:
        """Guarda un resultado serializado con la ``VERSION_METODO`` actual."""
        llave = _llave_n2(variable, lat, lon, inicio, fin, indice)
        blob = gzip.compress(json.dumps(resultado, ensure_ascii=False).encode())
        self.db.execute(
            "INSERT OR REPLACE INTO resultados (llave, version, datos) VALUES (?, ?, ?)",
            (llave, constantes.VERSION_METODO, blob),
        )
        self.db.commit()
        logger.debug("cache_n2 guardado llave=%s version=%d", llave, constantes.VERSION_METODO)


# ── Fachada unificada ────────────────────────────────────────────────────────


class Cache:
    """Fachada que expone ambos niveles y el cerrojo por celda.

    Uso típico desde ``analyze``::

        with cache.cerrojo(llave):
            resultado = cache.resultados.leer(...)
            if resultado is not None:
                return resultado  # acierto N2
            serie = cache.series.leer(variable, llave)
            if serie is None:
                serie = descargar_de_power(...)
                cache.series.guardar(variable, llave, ...)
            res = analizar_celda(serie, ...)
            cache.resultados.guardar(..., res)
    """

    def __init__(self, carpeta_datos: Path) -> None:
        import sqlite3

        from verascope_datos.almacen import Casillero

        ruta_sqlite = carpeta_datos / ARCHIVO_CASILLERO

        # Construcción normal para preservar cualquier estado futuro del
        # constructor.  Después reemplazamos solo la conexión por una con
        # check_same_thread=False, necesaria porque FastAPI sirve peticiones
        # desde hilos distintos al de arranque.
        casillero = Casillero(str(ruta_sqlite))
        casillero.db.close()
        casillero.db = sqlite3.connect(
            str(ruta_sqlite), timeout=30, check_same_thread=False,
        )
        casillero.db.execute("PRAGMA journal_mode=WAL")
        self.series = casillero
        self.resultados = CacheResultados(ruta_sqlite)

    def cerrojo(self, llave: str) -> threading.Lock:
        """Lock exclusivo para la celda identificada por ``llave``."""
        return cerrojo_celda(llave)

    def cerrar(self) -> None:
        self.series.cerrar()
        self.resultados.cerrar()
