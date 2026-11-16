"""T5 · S5: catálogo canónico y progreso real, sin datos externos."""

import json
from pathlib import Path

import pytest

from app.contracts import GlosarioRespuesta, SaludRespuesta, VariablesRespuesta
from app.datos.escaneo import escribir_estado
from tests.test_scan_api_real import api_real as api_real

CATALOGO = Path(__file__).resolve().parents[1] / "app" / "catalogo"


def test_salud_lee_y_actualiza_avance_del_disco(api_real):
    for estado, listas in [("en_curso", 213), ("completo", 4235)]:
        escribir_estado(api_real.app.state.datos, estado, listas, 4235)
        respuesta = api_real.get("/api/v1/salud")
        assert respuesta.status_code == 200
        datos = respuesta.json()
        assert SaludRespuesta.model_validate(datos).model_dump(mode="json") == datos
        assert datos["escaneo"] == {
            "estado": estado,
            "celdas_listas": listas,
            "celdas_total": 4235,
        }


def test_salud_sin_estado_usa_existencia_de_parquet(api_real):
    respuesta = api_real.get("/api/v1/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["escaneo"] == {
        "estado": "en_curso",
        "celdas_listas": 0,
        "celdas_total": 4235,
    }
    # Sólo se comprueba existencia, no se carga un parquet ni se accede a red.
    (api_real.app.state.datos / "resultados.parquet").write_bytes(b"")
    respuesta = api_real.get("/api/v1/salud")
    assert respuesta.status_code == 200
    assert respuesta.json()["escaneo"] == {
        "estado": "completo",
        "celdas_listas": 4235,
        "celdas_total": 4235,
    }


@pytest.mark.parametrize(
    "ruta,modelo",
    [
        ("variables", VariablesRespuesta),
        ("glosario", GlosarioRespuesta),
    ],
)
def test_catalogo_real_procede_del_json_canonico(api_real, ruta, modelo):
    respuesta = api_real.get(f"/api/v1/{ruta}")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert modelo.model_validate(datos).model_dump(mode="json") == datos
    assert datos == json.loads((CATALOGO / f"{ruta}.json").read_text("utf-8"))
    if ruta == "variables":
        assert len(datos["variables"]) == 5
        assert {v["id"] for v in datos["variables"]} == {
            "PRECTOTCORR",
            "T2M",
            "GWETROOT",
            "GWETTOP",
            "RH2M",
        }
        assert len(datos["indices"]) == 2
        assert {i["id"] for i in datos["indices"]} == {"ONI", "NINO12"}
    else:
        assert "Datos simulados" not in respuesta.text
