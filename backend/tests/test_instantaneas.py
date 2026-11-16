"""Pruebas del job de instantáneas para demos sin red."""

import json
from pathlib import Path

import pytest

from app.contracts import (
    AnalyzeRespuesta,
    ComparePeriodsRespuesta,
    DemoRespuesta,
    TeleconnectRespuesta,
)

RESPUESTAS = Path(__file__).resolve().parents[1] / "data" / "demo" / "respuestas"

ARCHIVOS_ESPERADOS = {
    "analyze_PRECTOTCORR_-6.0_-80.0.json": AnalyzeRespuesta,
    "analyze_T2M_-6.0_-80.0.json": AnalyzeRespuesta,
    "analyze_T2M_-6.0_-80.0_1981-1990.json": AnalyzeRespuesta,
    "compare-periods_T2M_-6.0_-80.0.json": ComparePeriodsRespuesta,
    "demos_efecto-espejo.json": DemoRespuesta,
    "demos_senal-o-ruido.json": DemoRespuesta,
    "teleconnect_PRECTOTCORR_-6.0_-80.0.json": TeleconnectRespuesta,
}


@pytest.mark.parametrize("archivo,modelo", ARCHIVOS_ESPERADOS.items())
def test_respuesta_valida_contra_modelo(archivo, modelo):
    """Cada JSON generado valida contra su modelo Pydantic."""
    ruta = RESPUESTAS / archivo
    assert ruta.exists(), f"Falta {archivo}; corre `python -m jobs.instantaneas`"
    datos = json.loads(ruta.read_text(encoding="utf-8"))
    # Valida y verifica que la serialización es idéntica
    validado = modelo.model_validate(datos)
    assert validado.model_dump(mode="json") == datos


def test_respuestas_estables():
    """Las respuestas no cambian entre ejecuciones (sin red ni aleatoriedad)."""
    for archivo in ARCHIVOS_ESPERADOS:
        ruta = RESPUESTAS / archivo
        if not ruta.exists():
            pytest.skip(f"Falta {archivo}")
        contenido = ruta.read_text(encoding="utf-8")
        # Verificar que es JSON válido y determinista
        datos = json.loads(contenido)
        regenerado = json.dumps(datos, ensure_ascii=False, indent=2) + "\n"
        assert contenido == regenerado, f"{archivo} no está normalizado"


def test_analyze_tiene_series_completas():
    """Los analyze tienen 540 meses de datos (1981-2025)."""
    for archivo in ARCHIVOS_ESPERADOS:
        if not archivo.startswith("analyze_"):
            continue
        ruta = RESPUESTAS / archivo
        if not ruta.exists():
            continue
        datos = json.loads(ruta.read_text(encoding="utf-8"))
        # Ventana corta tiene menos meses
        if "1981-1990" in archivo:
            assert datos["ventana"]["meses"] == 120
        else:
            assert datos["ventana"]["meses"] == 540
