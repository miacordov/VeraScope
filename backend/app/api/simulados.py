"""Lectura única y validada de escenarios; nunca abre la carpeta de datos."""

from pathlib import Path

from fastapi import HTTPException, Request

from app.api.validacion import exigir_seleccion
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
    "teleconnect-t2m": TeleconnectRespuesta,
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


def escenario_para_celda(request: Request, nombre: str, variable, lat, lon, **selectores):
    """Selecciona el JSON sin cambiar sus campos ni fabricar resultados.

    Los ejemplos de celda comparten el clic de Piura del análisis; teleconnect
    informa la celda de escaneo más cercana, no las coordenadas del clic.
    Compare-periods no contiene variable/celda: usa la misma referencia local.
    """
    respuesta = escenario(request, nombre)
    referencia = escenario(request, "analyze")
    disponible = {
        "variable": getattr(respuesta, "variable", referencia.variable),
        "lat": referencia.celda.lat,
        "lon": referencia.celda.lon,
    }
    if nombre == "analyze":
        disponible.update(
            inicio=int(respuesta.ventana.inicio[:4]),
            fin=int(respuesta.ventana.fin[:4]),
            indice=respuesta.indice.id,
        )
    elif nombre == "compare-periods":
        disponible.update(
            p1_inicio=respuesta.p1.anios[0],
            p1_fin=respuesta.p1.anios[1],
            p2_inicio=respuesta.p2.anios[0],
            p2_fin=respuesta.p2.anios[1],
        )
    exigir_seleccion(
        {"variable": variable, "lat": lat, "lon": lon - 360 if lon > 180 else lon, **selectores},
        disponible,
    )
    return respuesta
