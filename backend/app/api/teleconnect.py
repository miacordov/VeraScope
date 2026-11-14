"""Líneas simuladas, sin búsqueda sobre datos reales."""

from fastapi import Request

from app.api import router
from app.api.simulados import escenario_para_celda
from app.api.validacion import LatitudConsulta, LongitudConsulta
from app.contracts import TeleconnectRespuesta, Variable


@router.get("/teleconnect", response_model=TeleconnectRespuesta)
def teleconnect(request: Request, variable: Variable, lat: LatitudConsulta, lon: LongitudConsulta):
    """Ejemplo en Piura (-5, -80.5): PRECTOTCORR o T2M (sin líneas).

    Cualquier otra selección sin JSON recibe 422. Se aceptan longitudes 0–360.
    """
    nombre = "teleconnect-t2m" if variable == Variable.TEMPERATURA else "teleconnect"
    return escenario_para_celda(request, nombre, variable, lat, lon)
