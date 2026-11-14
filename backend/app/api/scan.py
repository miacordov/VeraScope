"""Feed y mosaico de ejemplo, sin ejecutar el escaneo."""

from fastapi import Query, Request

from app.api import router
from app.api.simulados import escenario
from app.api.validacion import exigir_seleccion
from app.contracts import FeedRespuesta, LayerRespuesta, TipoFeed, Variable


@router.get("/scan/feed", response_model=FeedRespuesta)
def feed(request: Request, tipo: TipoFeed, pagina: int = Query(default=0, ge=0)):
    respuesta = escenario(request, "feed")
    respuesta.tipo = tipo
    respuesta.pagina = pagina
    if tipo != TipoFeed.FUERTES or pagina != 0:
        respuesta.tarjetas = []
        if tipo != TipoFeed.FUERTES:
            respuesta.total = 0
    return respuesta


@router.get("/scan/layer", response_model=LayerRespuesta)
def layer(request: Request, variable: Variable):
    """Ejemplo de lluvia (PRECTOTCORR); otras variables sin JSON reciben 422."""
    respuesta = escenario(request, "layer")
    exigir_seleccion({"variable": variable}, {"variable": respuesta.variable})
    return respuesta
