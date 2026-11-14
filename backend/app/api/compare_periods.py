"""Comparación descriptiva del escenario simulado."""

from fastapi import Request

from app.api import router
from app.api.simulados import escenario_para_celda
from app.api.validacion import LatitudConsulta, LongitudConsulta, validar_ventana
from app.contracts import ComparePeriodsRespuesta, Variable


@router.get("/compare-periods", response_model=ComparePeriodsRespuesta)
def compare_periods(
    request: Request,
    variable: Variable,
    lat: LatitudConsulta,
    lon: LongitudConsulta,
    p1_inicio: int,
    p1_fin: int,
    p2_inicio: int,
    p2_fin: int,
):
    """Ejemplo: PRECTOTCORR en Piura, 1981–2001 frente a 2003–2025.

    Cada periodo requiere diez años. Otras combinaciones sin JSON reciben 422.
    """
    validar_ventana(p1_inicio, p1_fin)
    validar_ventana(p2_inicio, p2_fin)
    return escenario_para_celda(
        request,
        "compare-periods",
        variable,
        lat,
        lon,
        p1_inicio=p1_inicio,
        p1_fin=p1_fin,
        p2_inicio=p2_inicio,
        p2_fin=p2_fin,
    )
