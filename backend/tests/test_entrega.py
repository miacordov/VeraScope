"""T4: configuración reproducible de imagen, CI y estructura del backend."""

from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[2]
BACKEND = RAIZ / "backend"


@pytest.mark.parametrize(
    "ruta",
    [
        BACKEND / "Dockerfile",
        BACKEND / ".dockerignore",
        RAIZ / ".github" / "workflows" / "backend.yml",
        BACKEND / "app" / "datos" / "__init__.py",
        BACKEND / "jobs" / "__init__.py",
    ],
)
def test_archivos_de_entrega_y_paquetes_existen(ruta):
    assert ruta.is_file(), f"Falta {ruta.relative_to(RAIZ)}"


def test_dockerfile_usa_python_311_un_worker_y_solo_la_api():
    texto = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    assert "FROM python:3.11-slim" in texto
    assert "--workers 1" in texto
    assert "app.main:app" in texto
    assert "verascope_datos" not in texto
    assert "COPY data" not in texto


def test_dockerfile_corre_sin_root_con_volumen_de_datos_y_salud():
    texto = (BACKEND / "Dockerfile").read_text(encoding="utf-8")
    assert "USER verascope" in texto
    assert "VERASCOPE_DATOS=/data" in texto
    assert 'VOLUME ["/data"]' in texto
    assert "HEALTHCHECK" in texto and "/api/v1/salud" in texto
    assert "COPY --from=construccion" in texto


def test_dockerignore_excluye_preparador_datos_jobs_y_pruebas():
    lineas = {
        linea.strip()
        for linea in (BACKEND / ".dockerignore").read_text(encoding="utf-8").splitlines()
        if linea.strip() and not linea.lstrip().startswith("#")
    }
    assert {"verascope_datos/", "data/", "tests/", "jobs/", ".venv/"} <= lineas


def test_ci_fija_python_311_y_ejecuta_lint_formato_y_pruebas():
    texto = (RAIZ / ".github" / "workflows" / "backend.yml").read_text(encoding="utf-8")
    for esperado in (
        'python-version: "3.11"',
        'pip install -e ".[dev]"',
        "ruff check",
        "ruff format --check",
        "pytest -q",
    ):
        assert esperado in texto


def test_readme_documenta_arranque_simulado_y_variables():
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    for esperado in (
        "VERASCOPE_SIMULADO=1",
        "uvicorn app.main:app",
        "VERASCOPE_CORS",
        "VERASCOPE_FIN",
        "/api/v1/salud",
    ):
        assert esperado in texto
