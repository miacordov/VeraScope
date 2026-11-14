"""Líneas simuladas, sin búsqueda sobre datos reales."""

from fastapi import Request

from app.api import router
from app.api.simulados import escenario
from app.contracts import TeleconnectRespuesta, Variable


@router.get("/teleconnect", response_model=TeleconnectRespuesta)
def teleconnect(request: Request, variable: Variable, lat: float, lon: float):
    respuesta = escenario(request, "teleconnect")
    if variable == Variable.TEMPERATURA:
        respuesta.variable = variable
        respuesta.lineas = []
        respuesta.mensaje_vacio = "No se buscan líneas para la temperatura."
    return respuesta
