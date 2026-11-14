"""Análisis simulado: escenario fijo, sin cálculo ni descarga."""

from fastapi import HTTPException, Request

from app.api import router
from app.api.simulados import escenario
from app.contracts import AnalyzeRespuesta, IndiceId, Variable
from app.estadistica.constantes import ventana_fin


@router.get("/analyze", response_model=AnalyzeRespuesta)
def analyze(
    request: Request,
    variable: Variable,
    lat: float,
    lon: float,
    inicio: int,
    fin: int,
    indice: IndiceId = IndiceId.ONI,
):
    """Devuelve el escenario local fijo; los años son obligatorios también aquí."""
    if inicio < 1981 or fin > ventana_fin() or inicio > fin:
        raise HTTPException(
            422,
            detail={
                "codigo": "fuera_de_rango",
                "mensaje": "Elige años desde 1981 hasta el último año completo, en orden.",
                "celda_cercana": None,
            },
        )
    if fin - inicio + 1 < 10:
        raise HTTPException(
            422,
            detail={
                "codigo": "ventana_corta",
                "mensaje": "La ventana tiene menos de 10 años. Con tan pocos años, el ruido entre "
                "años impide ver tendencias; elige al menos 10.",
                "celda_cercana": None,
            },
        )
    return escenario(request, "analyze")
