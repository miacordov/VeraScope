"""S1–S2: superficie HTTP y respuestas simuladas de las nueve rutas."""

import json
from pathlib import Path

import pytest

BASE = {"variable": "PRECTOTCORR", "lat": -5.0, "lon": -80.5}
# La consulta debe seleccionar la ventana real del JSON local, no sustituirla.
ANALISIS = {**BASE, "inicio": 1981, "fin": 1990}
RUTAS = [
    ("/salud", {}),
    ("/variables", {}),
    ("/glosario", {}),
    ("/analyze", ANALISIS),
    ("/teleconnect", BASE),
    (
        "/compare-periods",
        {**BASE, "p1_inicio": 1981, "p1_fin": 2001, "p2_inicio": 2003, "p2_fin": 2025},
    ),
    ("/scan/feed", {"tipo": "fuertes", "pagina": 0}),
    ("/scan/layer", {"variable": "PRECTOTCORR"}),
    ("/demos/efecto-espejo", {}),
]


def ruta_esquema(ruta):
    return "/api/v1" + ("/demos/{id}" if ruta.startswith("/demos/") else ruta)


@pytest.mark.parametrize(("ruta", "parametros"), RUTAS)
def test_respuesta_publica_tiene_modelo_exportado_y_valida(
    cliente, modelo_respuesta, ruta, parametros
):
    respuesta = cliente.get("/api/v1" + ruta, params=parametros)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    modelo = modelo_respuesta(ruta_esquema(ruta))
    validado = modelo.model_validate(datos)
    assert validado.model_dump(mode="json") == datos
    assert modelo.model_config.get("extra") == "forbid"


def test_openapi_publica_nueve_rutas_y_anios_obligatorios(esquema):
    assert esquema["openapi"].startswith("3.")
    for ruta, _ in RUTAS:
        assert "get" in esquema["paths"][ruta_esquema(ruta)]
    parametros = esquema["paths"]["/api/v1/analyze"]["get"]["parameters"]
    por_nombre = {parametro["name"]: parametro for parametro in parametros}
    for nombre in ("inicio", "fin"):
        assert por_nombre[nombre]["in"] == "query"
        assert por_nombre[nombre]["required"] is True
        assert por_nombre[nombre]["schema"]["type"] == "integer"


def test_salud_identifica_simulados_y_version(cliente):
    respuesta = cliente.get("/api/v1/salud")
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert set(datos) == {"simulado", "ventana_fin", "version_metodo", "escaneo"}
    assert datos["simulado"] is True
    assert datos["ventana_fin"] == 2025
    assert datos["version_metodo"] == 3

    assert set(datos["escaneo"]) == {"estado", "celdas_listas", "celdas_total"}


@pytest.mark.parametrize("faltan", [("inicio",), ("fin",), ("inicio", "fin")])
def test_analyze_no_inventa_anios_y_devuelve_error_estandar(cliente, modelo_respuesta, faltan):
    antes = cliente.get("/api/v1/salud").json()
    parametros = {nombre: valor for nombre, valor in ANALISIS.items() if nombre not in faltan}
    respuesta = cliente.get("/api/v1/analyze", params=parametros)
    assert respuesta.status_code == 422
    datos = respuesta.json()
    assert set(datos) == {"error"}
    assert set(datos["error"]) == {"codigo", "mensaje", "celda_cercana"}
    assert datos["error"]["codigo"] == "fuera_de_rango"
    assert datos["error"]["mensaje"].strip()
    assert datos["error"]["celda_cercana"] is None
    modelo = modelo_respuesta("/api/v1/analyze", "422")
    assert modelo.model_validate(datos).model_dump(mode="json") == datos
    assert cliente.get("/api/v1/salud").json() == antes


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


def test_cada_respuesta_simulada_procede_de_json_local_validado(cliente, modelo_respuesta):
    catalogo = Path(__file__).resolve().parents[1] / "app" / "catalogo"
    carpeta = catalogo / "simulado"
    # Variables y glosario son editoriales, compartidos por ambos modos.
    archivos = sorted(
        archivo
        for archivo in carpeta.glob("*.json")
        if archivo.stem not in {"variables", "glosario"}
    ) + [catalogo / "variables.json", catalogo / "glosario.json"]
    assert archivos, "Faltan los JSON locales del catálogo"
    documentos = {archivo: json.loads(archivo.read_text(encoding="utf-8")) for archivo in archivos}
    utilizados = set()
    for ruta, parametros in RUTAS:
        if ruta == "/salud":  # Salud refleja configuración, no una serie simulada.
            continue
        respuesta = cliente.get("/api/v1" + ruta, params=parametros)
        assert respuesta.status_code == 200
        datos = respuesta.json()
        coinciden = [archivo for archivo, documento in documentos.items() if documento == datos]
        assert coinciden, f"{ruta} no coincide con ningún JSON local autorizado"
        for archivo in coinciden:
            assert archivo.parent == (catalogo if ruta in {"/variables", "/glosario"} else carpeta)
        modelo = modelo_respuesta(ruta_esquema(ruta))
        for archivo in coinciden:
            modelo.model_validate(documentos[archivo])
        utilizados.update(coinciden)
    # También se admiten otros escenarios; todos deben validar contra algún contrato público.
    modelos = [modelo_respuesta(ruta_esquema(ruta)) for ruta, _ in RUTAS]
    from pydantic import ValidationError

    for archivo in documentos.keys() - utilizados:
        for modelo in modelos:
            try:
                modelo.model_validate(documentos[archivo])
                break
            except ValidationError:
                continue
        else:
            pytest.fail(f"{archivo.name} no valida contra ningún modelo de respuesta")
