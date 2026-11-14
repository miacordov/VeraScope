"""Comparación descriptiva del escenario simulado."""

from fastapi import Request

from app.api import router
from app.api.simulados import escenario
from app.contracts import ComparePeriodsRespuesta, Variable


@router.get("/compare-periods", response_model=ComparePeriodsRespuesta)
def compare_periods(
    request: Request,
    variable: Variable,
    lat: float,
    lon: float,
    p1_inicio: int,
    p1_fin: int,
    p2_inicio: int,
    p2_fin: int,
):
    return escenario(request, "compare-periods")
