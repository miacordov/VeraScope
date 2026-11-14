"""T1: selección explícita de escenarios y límites del contrato HTTP/JSON."""

import copy

import pytest
from pydantic import ValidationError

BASE = {"variable": "PRECTOTCORR", "lat": -5.0, "lon": -80.5}
ANALISIS = {**BASE, "inicio": 1981, "fin": 1990}
PERIODOS = {**BASE, "p1_inicio": 1981, "p1_fin": 2001, "p2_inicio": 2003, "p2_fin": 2025}
CONSULTAS = [("/analyze", ANALISIS), ("/teleconnect", BASE), ("/compare-periods", PERIODOS)]
ESCENARIO_AUSENTE = (
    "No hay un escenario simulado para estos parámetros. "
    "Consulta los ejemplos disponibles en la documentación de la API."
)
RANGO = "Elige años desde 1981 hasta el último año completo, en orden."
CORTA = (
    "La ventana tiene menos de 10 años. Con tan pocos años, el ruido entre "
    "años impide ver tendencias; elige al menos 10."
)
ENTRADA = (
    "Faltan parámetros o tienen valores no válidos. Revisa las opciones y "
    "los años de inicio y fin, e inténtalo de nuevo."
)


def comprobar_rechazo(cliente, ruta, parametros, codigo, mensaje):
    salud = cliente.get("/api/v1/salud").json()
    original = cliente.get("/api/v1/analyze", params=ANALISIS).json()
    respuesta = cliente.get("/api/v1" + ruta, params=parametros)
    assert respuesta.status_code == 422, respuesta.text
    assert respuesta.json() == {
        "error": {"codigo": codigo, "mensaje": mensaje, "celda_cercana": None}
    }
    assert cliente.get("/api/v1/salud").json() == salud
    assert cliente.get("/api/v1/analyze", params=ANALISIS).json() == original


def test_escenario_analyze_coincide_con_todos_los_selectores(cliente):
    respuesta = cliente.get("/api/v1/analyze", params={**ANALISIS, "indice": "ONI"})
    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["variable"] == BASE["variable"]
    assert {k: datos["celda"][k] for k in ("lat", "lon")} == {"lat": -5.0, "lon": -80.5}
    assert datos["indice"]["id"] == "ONI"
    assert datos["ventana"] == {
        "inicio": "1981-01",
        "fin": "1990-12",
        "meses": 120,
        "meses_analizados": 120,
    }


@pytest.mark.parametrize(("ruta", "parametros"), CONSULTAS)
@pytest.mark.parametrize("cambio", [{"variable": "GWETROOT"}, {"lat": -6.0}, {"lon": -80.0}])
def test_no_se_ignora_variable_ni_celda(cliente, ruta, parametros, cambio):
    comprobar_rechazo(cliente, ruta, {**parametros, **cambio}, "fuera_de_rango", ESCENARIO_AUSENTE)


@pytest.mark.parametrize(
    ("ruta", "parametros", "cambio"),
    [
        ("/analyze", ANALISIS, {"indice": "NINO12"}),
        ("/analyze", ANALISIS, {"inicio": 1982, "fin": 1991}),
        ("/analyze", ANALISIS, {"fin": 2025}),
        ("/compare-periods", PERIODOS, {"p1_fin": 2000}),
        ("/compare-periods", PERIODOS, {"p2_inicio": 2004}),
        ("/scan/layer", {"variable": "PRECTOTCORR"}, {"variable": "T2M"}),
    ],
)
def test_combinaciones_sin_fixture_no_se_sustituyen(cliente, ruta, parametros, cambio):
    comprobar_rechazo(cliente, ruta, {**parametros, **cambio}, "fuera_de_rango", ESCENARIO_AUSENTE)


@pytest.mark.parametrize(("ruta", "parametros"), CONSULTAS)
@pytest.mark.parametrize(
    "cambio",
    [{"lat": -90.1}, {"lat": 90.1}, {"lon": -180.1}, {"lon": 360.1}, {"lat": "nan"}],
)
def test_limites_geograficos(cliente, ruta, parametros, cambio):
    comprobar_rechazo(cliente, ruta, {**parametros, **cambio}, "fuera_de_rango", ENTRADA)


@pytest.mark.parametrize(("ruta", "parametros"), CONSULTAS)
def test_longitud_0_a_360_se_normaliza_sin_cambiar_escenario(cliente, ruta, parametros):
    original = cliente.get("/api/v1" + ruta, params=parametros)
    normalizada = cliente.get("/api/v1" + ruta, params={**parametros, "lon": 279.5})
    assert normalizada.status_code == original.status_code == 200
    assert normalizada.json() == original.json()


@pytest.mark.parametrize("prefijo", ["", "p1_", "p2_"])
@pytest.mark.parametrize(
    ("inicio", "fin", "codigo", "mensaje"),
    [
        (1980, 1990, "fuera_de_rango", RANGO),
        (2015, 2026, "fuera_de_rango", RANGO),
        (2000, 1990, "fuera_de_rango", RANGO),
        (1981, 1989, "ventana_corta", CORTA),
    ],
)
def test_orden_rango_y_minimo_de_ambos_periodos(cliente, prefijo, inicio, fin, codigo, mensaje):
    ruta, base = ("/compare-periods", PERIODOS) if prefijo else ("/analyze", ANALISIS)
    parametros = {**base, prefijo + "inicio": inicio, prefijo + "fin": fin}
    comprobar_rechazo(cliente, ruta, parametros, codigo, mensaje)


def test_periodos_admitidos_se_conservan(cliente):
    respuesta = cliente.get("/api/v1/compare-periods", params=PERIODOS)
    assert respuesta.status_code == 200
    assert respuesta.json()["p1"]["anios"] == [1981, 2001]
    assert respuesta.json()["p2"]["anios"] == [2003, 2025]


def test_ejemplos_primarios_son_lluvia_en_piura(cliente):
    capa = cliente.get("/api/v1/scan/layer", params={"variable": "PRECTOTCORR"})
    feed = cliente.get("/api/v1/scan/feed", params={"tipo": "fuertes", "pagina": 0})
    assert capa.status_code == feed.status_code == 200
    assert capa.json()["variable"] == "PRECTOTCORR"
    assert (capa.json()["lat"][0], capa.json()["lon"][0]) == (-5.0, -80.5)
    tarjeta = feed.json()["tarjetas"][0]
    assert tarjeta["variable"] == "PRECTOTCORR"
    assert tarjeta["celda"] == {"lat": -5.0, "lon": -80.5}
    assert tarjeta["unidad"] == "mm/día"


def test_temperatura_conserva_teleconexion_vacia(cliente):
    respuesta = cliente.get("/api/v1/teleconnect", params={**BASE, "variable": "T2M"})
    assert respuesta.status_code == 200
    assert respuesta.json()["variable"] == "T2M"
    assert respuesta.json()["lineas"] == []
    assert respuesta.json()["mensaje_vacio"] == "No se buscan líneas para la temperatura."


@pytest.mark.parametrize(
    ("metodo", "ruta", "estado"), [("GET", "/ausente", 404), ("POST", "/salud", 405)]
)
def test_errores_de_starlette_son_estandar(cliente, metodo, ruta, estado):
    antes = cliente.get("/api/v1/salud").json()
    respuesta = cliente.request(metodo, "/api/v1" + ruta)
    assert respuesta.status_code == estado
    assert respuesta.json() == {
        "error": {
            "codigo": "fuera_de_rango",
            "mensaje": "No se encontró esta opción. Revisa la ruta y vuelve a intentarlo.",
            "celda_cercana": None,
        }
    }
    if estado == 405:
        assert "GET" in respuesta.headers["allow"]
    assert cliente.get("/api/v1/salud").json() == antes


@pytest.mark.parametrize(
    "campo",
    [
        "serie_original",
        "serie_sin_el_nino",
        "serie_z",
        "indice_valores",
        "fase",
        "tendencia_original",
        "tendencia_sin_el_nino",
        "fechas",
        "ventana",
    ],
)
def test_analyze_rechaza_series_desalineadas(cliente, modelo_respuesta, campo):
    original = cliente.get("/api/v1/analyze", params=ANALISIS).json()
    datos = copy.deepcopy(original)
    if campo.startswith("tendencia"):
        datos[campo]["recta"].pop()
    elif campo == "ventana":
        datos[campo]["meses"] += 1
    else:
        datos[campo].pop()
    with pytest.raises(ValidationError):
        modelo_respuesta("/api/v1/analyze").model_validate(datos)
    assert cliente.get("/api/v1/analyze", params=ANALISIS).json() == original


@pytest.mark.parametrize("campo", ["lat", "lon", "veredicto", "pendiente_decada", "efecto"])
def test_layer_rechaza_columnas_desalineadas(cliente, modelo_respuesta, campo):
    # La respuesta base se valida aunque la implementación aún use otra variable en RED.
    original = cliente.get("/api/v1/scan/layer", params={"variable": "PRECTOTCORR"}).json()
    datos = copy.deepcopy(original)
    datos[campo].pop()
    with pytest.raises(ValidationError):
        modelo_respuesta("/api/v1/scan/layer").model_validate(datos)
    assert cliente.get("/api/v1/scan/layer", params={"variable": "PRECTOTCORR"}).json() == original
