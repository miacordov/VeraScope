"""Catálogos públicos y estado del servicio."""

from fastapi import Request

from app.api import router
from app.contracts import GlosarioRespuesta, SaludRespuesta, VariablesRespuesta
from app.datos.escaneo import leer_estado
from app.estadistica.constantes import VERSION_METODO, ventana_fin


@router.get("/salud", response_model=SaludRespuesta)
def salud(request: Request):
    return SaludRespuesta(
        ventana_fin=ventana_fin(),
        version_metodo=VERSION_METODO,
        escaneo=leer_estado(request.app.state.datos),
    )


@router.get("/variables", response_model=VariablesRespuesta)
def variables(request: Request):
    return request.app.state.catalogo_variables.model_copy(deep=True)


@router.get("/glosario", response_model=GlosarioRespuesta)
def glosario(request: Request):
    return request.app.state.catalogo_glosario.model_copy(deep=True)
