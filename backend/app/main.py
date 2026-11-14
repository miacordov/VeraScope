"""Arranque del servicio de contratos con escenarios explícitamente simulados."""

import logging
import os
from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api import analyze, catalogo, compare_periods, router, scan, teleconnect  # noqa: F401
from app.api.simulados import cargar_escenarios
from app.contracts import ErrorRespuesta

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.simulado = os.environ.get("VERASCOPE_SIMULADO", "0") == "1"
    app.state.escenarios = cargar_escenarios() if app.state.simulado else {}
    yield


app = FastAPI(
    title="VeraScope",
    version="0.1.0",
    description="API mensual. En modo simulado entrega escenarios fijos, no resultados reales.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origen.strip()
        for origen in os.environ.get("VERASCOPE_CORS", "http://localhost:8081").split(",")
        if origen.strip()
    ],
    allow_methods=["GET"],
)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.include_router(router)


@app.exception_handler(RequestValidationError)
def entrada_invalida(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorRespuesta(
            error={
                "codigo": "fuera_de_rango",
                "mensaje": "Faltan parámetros o tienen valores no válidos. Revisa las opciones y "
                "los años de inicio y fin, e inténtalo de nuevo.",
                "celda_cercana": None,
            }
        ).model_dump(mode="json"),
    )


@app.exception_handler(HTTPException)
def error_http(request: Request, exc: HTTPException):
    detalle = (
        exc.detail
        if isinstance(exc.detail, dict)
        else {
            "codigo": "fuera_de_rango",
            "mensaje": "No se encontró esta opción. Revisa la ruta y vuelve a intentarlo.",
            "celda_cercana": None,
        }
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorRespuesta(error=detalle).model_dump(mode="json"),
        headers=exc.headers,
    )


@app.middleware("http")
async def registrar_peticion(request: Request, call_next):
    inicio = perf_counter()
    respuesta = await call_next(request)
    logger.info(
        "peticion metodo=%s ruta=%s estado=%s t_total_ms=%.2f cache=no_aplica",
        request.method,
        request.scope.get("route").path if request.scope.get("route") else "desconocida",
        respuesta.status_code,
        (perf_counter() - inicio) * 1000,
    )
    return respuesta
