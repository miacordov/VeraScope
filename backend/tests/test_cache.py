"""S1–S3: persistencia de ambos niveles y exclusión por celda, sin red."""

import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from app.datos.cache import Cache, CacheResultados, cerrojo_celda
from app.datos.celdas import lugar_celda
from app.estadistica import constantes

LLAVE = lugar_celda(-5.0, -80.5)
CONSULTA = ("PRECTOTCORR", -5.0, -80.5, 1981, 2025, "ONI")
RESULTADO = {"veredicto": "cambio_robusto", "pendiente": 0.25, "avisos": [], "p": None}


@pytest.fixture
def cache(tmp_path):
    instancia = Cache(tmp_path)
    try:
        yield instancia
    finally:
        instancia.cerrar()


def test_cache_n1_guardar_y_leer(cache):
    valores = np.linspace(3.0, 4.0, 12, dtype=np.float32)
    cache.series.guardar("PRECTOTCORR", LLAVE, "1981-01", valores)
    inicio, leidos = cache.series.leer("PRECTOTCORR", LLAVE)
    assert inicio == "1981-01"
    np.testing.assert_array_equal(leidos, valores)


def test_cache_n1_fallo_luego_acierto(cache):
    assert cache.series.leer("T2M", LLAVE) == (None, None)
    assert not cache.series.existe("T2M", LLAVE)
    valores = np.arange(12, dtype=np.float32)
    cache.series.guardar("T2M", LLAVE, "1981-01", valores)
    inicio, leidos = cache.series.leer("T2M", LLAVE)
    assert inicio == "1981-01"
    assert cache.series.existe("T2M", LLAVE)
    np.testing.assert_array_equal(leidos, valores)


def test_cache_n2_guardar_y_leer(cache):
    assert cache.resultados.leer(*CONSULTA) is None
    cache.resultados.guardar(*CONSULTA, RESULTADO)
    assert cache.resultados.leer(*CONSULTA) == RESULTADO


def test_cache_n2_invalida_por_version(cache, monkeypatch):
    cache.resultados.guardar(*CONSULTA, RESULTADO)
    assert cache.resultados.leer(*CONSULTA) == RESULTADO
    with monkeypatch.context() as parche:
        parche.setattr(constantes, "VERSION_METODO", constantes.VERSION_METODO + 1)
        assert cache.resultados.leer(*CONSULTA) is None
    assert cache.resultados.leer(*CONSULTA) == RESULTADO


def test_cache_n2_sobrevive_reinicio(tmp_path):
    ruta = tmp_path / "casillero.sqlite"
    primera = CacheResultados(ruta)
    try:
        primera.guardar(*CONSULTA, RESULTADO)
    finally:
        primera.cerrar()
    segunda = CacheResultados(ruta)
    try:
        assert segunda.leer(*CONSULTA) == RESULTADO
    finally:
        segunda.cerrar()


def test_cerrojo_misma_llave_mismo_lock(cache):
    assert cache.cerrojo(LLAVE) is cerrojo_celda(LLAVE)
    assert cerrojo_celda(LLAVE) is cerrojo_celda(LLAVE)


def test_cerrojo_distinta_llave_distinto_lock():
    assert cerrojo_celda(LLAVE) is not cerrojo_celda(lugar_celda(-5.5, -80.5))


def test_cerrojo_dos_hilos_una_peticion(tmp_path):
    llamadas = {"n": 0}
    barrera = threading.Barrier(2)

    def descargar():
        # Cada conexión SQLite pertenece a su hilo; el cerrojo es global por celda.
        barrera.wait(timeout=10)
        with cerrojo_celda(LLAVE):
            cache = Cache(tmp_path)
            try:
                if not cache.series.existe("T2M", LLAVE):
                    llamadas["n"] += 1
                    cache.series.guardar("T2M", LLAVE, "1981-01", np.zeros(12))
            finally:
                cache.cerrar()

    with ThreadPoolExecutor(max_workers=2) as ejecutor:
        futuros = [ejecutor.submit(descargar) for _ in range(2)]
        for futuro in futuros:
            futuro.result(timeout=20)
    assert llamadas["n"] == 1
    cache = Cache(tmp_path)
    try:
        inicio, valores = cache.series.leer("T2M", LLAVE)
        assert inicio == "1981-01"
        np.testing.assert_array_equal(valores, np.zeros(12))
    finally:
        cache.cerrar()
