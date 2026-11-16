"""S1–S2: vocabulario cerrado, constantes y acciones de demos estrictas."""

import copy
import importlib

import pytest
from pydantic import BaseModel

import app.contracts as contratos

ENUMERACIONES = [
    {"cambio_robusto", "sensible_a_el_nino", "cambio_oculto", "sin_tendencia"},
    {"sube", "baja", "plana"},
    {"nino", "nina", "neutro"},
    {"escaneo", "individual"},
    {"opuesto", "mismo"},
    {
        "colinealidad",
        "potencia_baja",
        "respuesta_no_lineal",
        "nino_costero",
        "fuera_de_rejilla",
        "muestra_efectiva_baja",
    },
    {
        "ventana_corta",
        "fuera_de_rango",
        "sin_datos_tierra",
        "power_lento",
        "power_error",
        "escaneo_en_curso",
    },
    {"PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M"},
    {"ONI", "NINO12"},
    {"fuertes", "opuestas", "ocultas"},
]
ACCIONES = {
    "seleccionar_variable",
    "seleccionar_celda",
    "fijar_ventana",
    "quitar_el_nino",
    "reproducir",
    "detener",
    "ir_al_mes",
    "ir_a_destino",
    "mostrar_periodos",
}
DEMO = {
    "id": "efecto-espejo",
    "titulo": "El efecto espejo de El Niño",
    "variable": "PRECTOTCORR",
    "celda": {"lat": -5.0, "lon": -80.5},
    "pasos": [
        {
            "n": 1,
            "texto": "Esta es Piura.",
            "acciones": [{"tipo": "seleccionar_celda", "lat": -5.0, "lon": -80.5}],
        }
    ],
}
CONSTANTES = {
    "ALFA": 0.05,
    "FDR_Q": 0.05,
    "REZAGO_MAX": 6,
    "LAG_HAMED_RAO": 12,
    "MIN_MESES": 120,
    "AVISO_POTENCIA_MESES": 240,
    "MAX_HUECO": 2,
    "MAX_FALTANTE": 0.10,
    "ESCALA_DECADA": 120,
    "UMBRAL_FASE": 0.5,
    "COLINEALIDAD_MAX": 0.3,
    "UMBRAL_INUSUAL": 2,
    "UMBRAL_COINCIDENCIA": 1,
    "KM_MIN_DESTINO": 1500,
    "KM_SEP_DESTINOS": 1000,
    "MAX_LINEAS_OPUESTAS": 3,
    "MAX_LINEAS_IGUALES": 2,
    "NEFF_MIN_PRUEBA_T": 10,
    "NEFF_PISO": 3,
    "VERSION_METODO": 3,
    "GRILLA_PASO": 2.0,
    "CELDA": 0.5,
}


def nodos(valor):
    """Recorre JSON Schema sin depender de nombres internos de los modelos."""
    if isinstance(valor, dict):
        yield valor
        for hijo in valor.values():
            yield from nodos(hijo)
    elif isinstance(valor, list):
        for hijo in valor:
            yield from nodos(hijo)


@pytest.mark.parametrize("esperados", ENUMERACIONES, ids=lambda valores: sorted(valores)[0])
def test_enumeraciones_exactas_en_contratos_publicos(esperados):
    esquemas = [
        modelo.model_json_schema()
        for modelo in vars(contratos).values()
        if isinstance(modelo, type) and issubclass(modelo, BaseModel) and modelo is not BaseModel
    ]
    enums = [set(nodo["enum"]) for esquema in esquemas for nodo in nodos(esquema) if "enum" in nodo]
    assert esperados in enums


@pytest.mark.parametrize(("nombre", "valor"), CONSTANTES.items())
def test_constantes_compartidas(nombre, valor):
    constantes = importlib.import_module("app.estadistica.constantes")
    assert getattr(constantes, nombre) == valor
    if nombre == "VERSION_METODO":
        assert type(constantes.VERSION_METODO) is int


def test_periodos_por_defecto_usan_fin_configurado(monkeypatch):
    monkeypatch.setenv("VERASCOPE_FIN", "2025")
    constantes = importlib.import_module("app.estadistica.constantes")
    assert constantes.PERIODOS_DEFECTO == ((1981, 2001), (2003, 2025))


def test_acciones_son_union_discriminada_cerrada():
    esquema = contratos.DemoRespuesta.model_json_schema()
    uniones = [
        nodo
        for nodo in nodos(esquema)
        if nodo.get("discriminator", {}).get("propertyName") == "tipo"
    ]
    assert len(uniones) == 1
    union = uniones[0]
    assert set(union["discriminator"]["mapping"]) == ACCIONES
    assert len(union["oneOf"]) == len(ACCIONES)
    for referencia in union["discriminator"]["mapping"].values():
        variante = esquema["$defs"][referencia.rsplit("/", 1)[-1]]
        assert variante["additionalProperties"] is False
        assert "tipo" in variante["required"]


@pytest.mark.parametrize(
    "accion",
    [
        {"tipo": "seleccionar_celda", "lat": -5.0, "lon": -80.5},
        {"tipo": "quitar_el_nino", "valor": False},
    ],
)
def test_acciones_documentadas_validan(accion):
    datos = copy.deepcopy(DEMO)
    datos["pasos"][0]["acciones"] = [accion]
    assert contratos.DemoRespuesta.model_validate(datos).model_dump(mode="json") == datos


@pytest.mark.parametrize(
    "accion",
    [
        {},
        {"tipo": "accion_desconocida"},
        {"tipo": "seleccionar_celda", "lat": -5.0},
        {"tipo": "seleccionar_celda", "lat": -5.0, "lon": -80.5, "valor": False},
        {"tipo": "quitar_el_nino"},
        {"tipo": "quitar_el_nino", "valor": False, "lat": -5.0},
        {"tipo": "quitar_el_nino", "valor": "false"},
        {"tipo": "quitar_el_nino", "valor": 0},
    ],
)
def test_acciones_incompletas_mezcladas_o_coercibles_se_rechazan(accion):
    from pydantic import ValidationError

    original = copy.deepcopy(DEMO)
    datos = copy.deepcopy(original)
    datos["pasos"][0]["acciones"] = [accion]
    with pytest.raises(ValidationError):
        contratos.DemoRespuesta.model_validate(datos)
    assert DEMO == original
