"""S1–S2: superficie HTTP y contrato de las rutas sin datos."""

import pytest

RUTAS_SIN_DATOS = [
    ("/salud", {}),
    ("/variables", {}),
    ("/glosario", {}),
]


@pytest.mark.parametrize(("ruta", "parametros"), RUTAS_SIN_DATOS)
def test_respuesta_publica_tiene_modelo_exportado_y_valida(
    cliente, modelo_respuesta, ruta, parametros
):
    respuesta = cliente.get("/api/v1" + ruta, params=parametros)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    modelo = modelo_respuesta("/api/v1" + ruta)
    validado = modelo.model_validate(datos)
    assert validado.model_dump(mode="json") == datos
    assert modelo.model_config.get("extra") == "forbid"


def test_openapi_publica_rutas_y_anios_obligatorios(esquema):
    assert esquema["openapi"].startswith("3.")
    for ruta, _ in RUTAS_SIN_DATOS:
        assert "get" in esquema["paths"]["/api/v1" + ruta]
    parametros = esquema["paths"]["/api/v1/analyze"]["get"]["parameters"]
    por_nombre = {parametro["name"]: parametro for parametro in parametros}
    for nombre in ("inicio", "fin"):
        assert por_nombre[nombre]["in"] == "query"
        assert por_nombre[nombre]["required"] is True
        assert por_nombre[nombre]["schema"]["type"] == "integer"


def test_salud_identifica_version_y_escaneo(cliente):
    respuesta = cliente.get("/api/v1/salud")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == {"ventana_fin", "version_metodo", "escaneo"}
    assert datos["ventana_fin"] == 2025
    assert datos["version_metodo"] == 3
    assert set(datos["escaneo"]) == {"estado", "celdas_listas", "celdas_total"}




@pytest.mark.parametrize(
    ("ruta", "claves"), [("variables", {"variables", "indices"}), ("glosario", {"terminos"})]
)
def test_catalogos_son_objetos_con_listas(cliente, ruta, claves):
    respuesta = cliente.get("/api/v1/" + ruta)
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == claves
    assert all(isinstance(datos[clave], list) and datos[clave] for clave in claves)
    if ruta == "variables":
        # El resumen no fija el nombre del identificador de cada entrada.
        assert len(datos["variables"]) == 5
        assert len(datos["indices"]) == 2


@pytest.mark.parametrize(
    "origen",
    [
        "https://web.example",
        "https://otra.example",
        "https://no-permitida.example",
        "http://localhost:8081",
    ],
)
def test_cors_respeta_lista_del_entorno(cliente, origen):
    respuesta = cliente.options(
        "/api/v1/salud",
        headers={"Origin": origen, "Access-Control-Request-Method": "GET"},
    )
    permitido = origen in {"https://web.example", "https://otra.example"}
    assert respuesta.status_code == (200 if permitido else 400)
    assert respuesta.headers.get("access-control-allow-origin") == (origen if permitido else None)
