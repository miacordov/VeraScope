"""Preservación del bloqueo de red y comprobaciones de la capa HTTP."""

import inspect
import socket

import pytest
from fastapi.routing import APIRoute


def test_canal_interno_de_asyncio_no_debilita_bloqueo_de_red(cliente):
    assert cliente.get("/api/v1/salud").status_code == 200
    with socket.socket() as conexion:
        for llamada in (
            lambda: conexion.connect(("127.0.0.1", 9)),
            lambda: conexion.connect_ex(("127.0.0.1", 9)),
            lambda: socket.create_connection(("127.0.0.1", 9)),
            lambda: socket.getaddrinfo("example.invalid", 80),
        ):
            with pytest.raises(
                AssertionError, match="Las pruebas de contratos no pueden abrir conexiones de red"
            ):
                llamada()


def test_rutas_del_contrato_son_sincronas(cliente):
    from app.api import router

    rutas = [
        ruta
        for ruta in router.routes
        if isinstance(ruta, APIRoute) and ruta.path.startswith("/api/v1/")
    ]
    assert len(rutas) == 9
    assert all(not inspect.iscoroutinefunction(ruta.endpoint) for ruta in rutas)


def test_gzip_no_altera_el_json_publico(cliente):
    parametros = {
        "variable": "PRECTOTCORR",
        "lat": -5.0,
        "lon": -80.5,
        "inicio": 1981,
        "fin": 2025,
    }
    comprimida = cliente.get(
        "/api/v1/analyze", params=parametros, headers={"Accept-Encoding": "gzip"}
    )
    original = cliente.get(
        "/api/v1/analyze", params=parametros, headers={"Accept-Encoding": "identity"}
    )
    assert comprimida.status_code == original.status_code == 200
    assert comprimida.headers["content-encoding"] == "gzip"
    assert "content-encoding" not in original.headers
    assert comprimida.json() == original.json()
