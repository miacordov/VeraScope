"""Análisis simulado: selección de JSON, sin cálculo ni descarga."""

from fastapi import Request

from app.api import router
from app.api.simulados import escenario_para_celda
from app.api.validacion import LatitudConsulta, LongitudConsulta, validar_ventana
from app.contracts import AnalyzeRespuesta, IndiceId, Variable


@router.get("/analyze", response_model=AnalyzeRespuesta)
def analyze(
    request: Request,
    variable: Variable,
    lat: LatitudConsulta,
    lon: LongitudConsulta,
    inicio: int,
    fin: int,
    indice: IndiceId = IndiceId.ONI,
):
    """Ejemplo: PRECTOTCORR, Piura (-5, -80.5), 1981–1990, ONI.

    Solo se sirven las combinaciones con un JSON local; las demás reciben 422.
    """
    validar_ventana(inicio, fin)
    return escenario_para_celda(
        request, "analyze", variable, lat, lon, inicio=inicio, fin=fin, indice=indice
    )
