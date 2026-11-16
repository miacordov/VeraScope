"""Construye y levanta la imagen real. Opcional: VERASCOPE_PRUEBA_DOCKER=1.

No corre por defecto porque descarga la imagen base de Python y necesita Docker.
Toda la comunicación con el contenedor pasa por la CLI de Docker en un
subproceso, así que el bloqueo de red de las pruebas sigue activo.
"""

import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.skipif(
    os.environ.get("VERASCOPE_PRUEBA_DOCKER") != "1" or shutil.which("docker") is None,
    reason="Prueba de imagen opcional: exporta VERASCOPE_PRUEBA_DOCKER=1 y ten Docker activo.",
)


def docker(*argumentos, timeout=60):
    return subprocess.run(
        ["docker", *argumentos], capture_output=True, text=True, timeout=timeout, check=True
    ).stdout.strip()


@pytest.fixture(scope="module")
def contenedor():
    etiqueta = f"verascope-prueba:{uuid.uuid4().hex[:8]}"
    nombre = f"verascope-prueba-{uuid.uuid4().hex[:8]}"
    docker("build", "-t", etiqueta, str(BACKEND), timeout=600)
    try:
        try:
            docker("run", "-d", "--name", nombre, etiqueta)
            yield etiqueta, nombre
        finally:
            subprocess.run(["docker", "rm", "-f", nombre], capture_output=True)
    finally:
        subprocess.run(["docker", "rmi", "-f", etiqueta], capture_output=True)


def test_imagen_arranca_y_queda_sana(contenedor):
    _, nombre = contenedor
    estado = ""
    for _ in range(120):
        estado = docker("inspect", "-f", "{{.State.Health.Status}}", nombre)
        if estado in {"healthy", "unhealthy"}:
            break
        time.sleep(1)
    assert estado == "healthy", docker("logs", nombre)


def test_imagen_corre_sin_root_y_puede_escribir_en_datos(contenedor):
    _, nombre = contenedor
    assert docker("exec", nombre, "id", "-u") == "10001"
    assert docker("exec", nombre, "sh", "-c", "echo $VERASCOPE_DATOS") == "/data"
    docker("exec", nombre, "sh", "-c", "touch /data/.escritura && rm /data/.escritura")


def test_imagen_no_lleva_preparador_jobs_ni_pruebas(contenedor):
    etiqueta, _ = contenedor
    salida = docker(
        "run",
        "--rm",
        "--entrypoint",
        "python",
        etiqueta,
        "-c",
        "import importlib.util as u;"
        "print([m for m in ('jobs', 'verascope_datos', 'tests') if u.find_spec(m)])",
    )
    assert salida == "[]"
