"""Catálogos públicos, guiones y estado del servicio simulado."""

from typing import Literal

from fastapi import Request

from app.api import router
from app.api.simulados import escenario
from app.contracts import DemoRespuesta, GlosarioRespuesta, SaludRespuesta, VariablesRespuesta
from app.estadistica.constantes import VERSION_METODO, ventana_fin


@router.get("/salud", response_model=SaludRespuesta)
def salud(request: Request):
    simulado = request.app.state.simulado
    return SaludRespuesta(
        simulado=simulado,
        ventana_fin=ventana_fin(),
        version_metodo=VERSION_METODO,
        escaneo={
            "estado": "completo" if simulado else "en_curso",
            "celdas_listas": 2 if simulado else 0,
            "celdas_total": 2 if simulado else 4235,
        },
    )


@router.get("/variables", response_model=VariablesRespuesta)
def variables(request: Request):
    return escenario(request, "variables")


@router.get("/glosario", response_model=GlosarioRespuesta)
def glosario(request: Request):
    return escenario(request, "glosario")


@router.get("/demos/{id}", response_model=DemoRespuesta)
def demo(request: Request, id: Literal["efecto-espejo", "senal-o-ruido"]):
    return escenario(request, id)
