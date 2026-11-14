"""Contratos de issue #1: aplicación en memoria, sin datos reales ni red."""

import asyncio
import importlib
import socket

import pytest


@pytest.fixture(autouse=True)
def sin_red(monkeypatch):
    # En Windows, asyncio crea su canal interno con socketpair sobre loopback.
    # Se prepara antes del bloqueo; todo el código bajo prueba sigue sin red.
    bucle = asyncio.new_event_loop()

    def prohibida(*args, **kwargs):
        raise AssertionError("Las pruebas de contratos no pueden abrir conexiones de red")

    monkeypatch.setattr(socket.socket, "connect", prohibida)
    monkeypatch.setattr(socket.socket, "connect_ex", prohibida)
    monkeypatch.setattr(socket, "create_connection", prohibida)
    monkeypatch.setattr(socket, "getaddrinfo", prohibida)
    yield bucle
    if not bucle.is_closed():
        bucle.close()


@pytest.fixture
def cliente(monkeypatch, tmp_path, sin_red):
    # La configuración debe fijarse antes de importar o arrancar la aplicación.
    monkeypatch.setenv("VERASCOPE_SIMULADO", "1")
    monkeypatch.setenv("VERASCOPE_FIN", "2025")
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path))
    monkeypatch.setenv("VERASCOPE_CORS", "https://web.example,https://otra.example")
    from fastapi.testclient import TestClient

    modulo = importlib.import_module("app.main")
    with TestClient(modulo.app, backend_options={"loop_factory": lambda: sin_red}) as cliente:
        yield cliente


@pytest.fixture
def esquema(cliente):
    respuesta = cliente.get("/openapi.json")
    assert respuesta.status_code == 200
    return respuesta.json()


@pytest.fixture
def modelos():
    from pydantic import BaseModel

    contratos = importlib.import_module("app.contracts")
    return {
        nombre: modelo
        for nombre, modelo in vars(contratos).items()
        if isinstance(modelo, type) and issubclass(modelo, BaseModel) and modelo is not BaseModel
    }


@pytest.fixture
def modelo_respuesta(esquema, modelos):
    def resolver(ruta, estado="200"):
        respuesta = esquema["paths"][ruta]["get"]["responses"][estado]
        referencia = respuesta["content"]["application/json"]["schema"]["$ref"]
        nombre = referencia.rsplit("/", 1)[-1]
        assert nombre in modelos, f"app.contracts debe exportar el modelo {nombre}"
        return modelos[nombre]

    return resolver
