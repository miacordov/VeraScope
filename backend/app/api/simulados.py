"""Lectura única y validada de escenarios; nunca abre la carpeta de datos."""

from pathlib import Path

from fastapi import HTTPException, Request

from app.contracts import (
    AnalyzeRespuesta,
    ComparePeriodsRespuesta,
    DemoRespuesta,
    FeedRespuesta,
    GlosarioRespuesta,
    LayerRespuesta,
    TeleconnectRespuesta,
    VariablesRespuesta,
)

MODELOS = {
    "analyze": AnalyzeRespuesta,
    "compare-periods": ComparePeriodsRespuesta,
    "efecto-espejo": DemoRespuesta,
    "senal-o-ruido": DemoRespuesta,
    "feed": FeedRespuesta,
    "glosario": GlosarioRespuesta,
    "layer": LayerRespuesta,
    "teleconnect": TeleconnectRespuesta,
    "variables": VariablesRespuesta,
}


def cargar_escenarios():
    """Valida los archivos empaquetados antes de aceptar peticiones."""
    carpeta = Path(__file__).resolve().parents[1] / "catalogo" / "simulado"
    return {
        nombre: modelo.model_validate_json((carpeta / f"{nombre}.json").read_text("utf-8"))
        for nombre, modelo in MODELOS.items()
    }


def escenario(request: Request, nombre: str):
    """Entrega una copia para que una petición no altere las siguientes."""
    if not request.app.state.simulado:
        raise HTTPException(
            status_code=503,
            detail={
                "codigo": "escaneo_en_curso",
                "mensaje": "Los datos reales aún no están disponibles. Usa el modo simulado.",
                "celda_cercana": None,
            },
        )
    return request.app.state.escenarios[nombre].model_copy(deep=True)
