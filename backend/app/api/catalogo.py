"""Catálogos públicos, guiones simulados y estado del servicio."""

from typing import Literal

from fastapi import Request

from app.api import router
from app.api.simulados import cargar_guion_demo, escenario
from app.contracts import DemoRespuesta, GlosarioRespuesta, SaludRespuesta, VariablesRespuesta
from app.datos.escaneo import leer_estado
from app.estadistica.constantes import VERSION_METODO, ventana_fin


@router.get("/salud", response_model=SaludRespuesta)
def salud(request: Request):
    simulado = request.app.state.simulado
    return SaludRespuesta(
        simulado=simulado,
        ventana_fin=ventana_fin(),
        version_metodo=VERSION_METODO,
        escaneo=(
            {"estado": "completo", "celdas_listas": 2, "celdas_total": 2}
            if simulado
            else leer_estado(request.app.state.datos)
        ),
    )


@router.get("/variables", response_model=VariablesRespuesta)
def variables(request: Request):
    if request.app.state.simulado:
        return escenario(request, "variables")
    return request.app.state.catalogo_variables.model_copy(deep=True)


@router.get("/glosario", response_model=GlosarioRespuesta)
def glosario(request: Request):
    if request.app.state.simulado:
        return escenario(request, "glosario")
    return request.app.state.catalogo_glosario.model_copy(deep=True)


@router.get("/demos/{id}", response_model=DemoRespuesta)
def demo(request: Request, id: Literal["efecto-espejo", "senal-o-ruido"]):
    # Los guiones se sirven tanto en modo real como simulado
    return cargar_guion_demo(id)
