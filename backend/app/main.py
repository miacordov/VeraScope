"""Arranque del servicio: carga datos, caché, cliente POWER y catálogo."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api import analyze, catalogo, compare_periods, router, scan, teleconnect  # noqa: F401
from app.api.rejilla import cargar_rejilla
from app.api.simulados import cargar_catalogos, cargar_escenarios
from app.contracts import ErrorRespuesta, VariablesRespuesta
from app.datos import carpeta_datos
from app.datos.cache import Cache
from app.datos.escaneo import ARCHIVO_RESULTADOS
from app.datos.power_client import ClientePower, timeout_vivo

logger = logging.getLogger(__name__)


def _cargar_variables(validado: VariablesRespuesta) -> dict:
    """Deriva el diccionario por id del catálogo ya validado en el arranque."""
    return {variable.id: variable.model_dump(mode="json") for variable in validado.variables}


def _cargar_resultados(carpeta: Path):
    """Carga resultados.parquet si existe; devuelve (DataFrame | None, mtime | None)."""
    ruta = carpeta / ARCHIVO_RESULTADOS
    if not ruta.exists():
        return None, None
    try:
        import pandas as pd

        return pd.read_parquet(ruta), ruta.stat().st_mtime
    except Exception:
        logger.warning("No se pudo cargar %s; el escaneo se considerará en curso.", ruta)
        return None, None


@asynccontextmanager
async def lifespan(app: FastAPI):
    datos = carpeta_datos()
    simulado = os.environ.get("VERASCOPE_SIMULADO", "0") == "1"

    app.state.simulado = simulado
    app.state.datos = datos
    catalogos = cargar_catalogos()
    app.state.catalogo_variables = catalogos["variables"]
    app.state.catalogo_glosario = catalogos["glosario"]
    app.state.escenarios = cargar_escenarios(catalogos) if simulado else {}
    app.state.variables = _cargar_variables(app.state.catalogo_variables)

    # Caché de dos niveles (N1 series + N2 resultados)
    cache = Cache(datos)
    app.state.cache = cache

    # Cliente POWER para descargas en vivo
    app.state.power = ClientePower(timeout=timeout_vivo())

    # Resultados del escaneo (ScanMap)
    app.state.escaneo_resultados, app.state._resultados_mtime = _cargar_resultados(datos)
    app.state.feed_titulares = scan.cargar_titulares()
    scan.reiniciar_cache_feed(app.state)

    # Matrices de la rejilla para teleconnect (≈ 16 s y ≈ 32 MB con la rejilla completa)
    app.state.rejilla = None if simulado else cargar_rejilla(datos)

    logger.info(
        "arranque simulado=%s datos=%s escaneo=%s",
        simulado,
        datos,
        "cargado" if app.state.escaneo_resultados is not None else "no_disponible",
    )
    try:
        yield
    finally:
        cache.cerrar()


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

    # Recargar resultados.parquet si cambió en disco
    estado = request.app.state
    if not estado.simulado:
        ruta_res = estado.datos / ARCHIVO_RESULTADOS
        if ruta_res.exists():
            mtime = ruta_res.stat().st_mtime
            if estado._resultados_mtime is None or mtime > estado._resultados_mtime:
                estado.escaneo_resultados, estado._resultados_mtime = _cargar_resultados(
                    estado.datos
                )
                scan.reiniciar_cache_feed(estado)
                logger.info("escaneo recargado mtime=%.2f", mtime)

    respuesta = await call_next(request)

    # Detectar acierto/fallo de caché desde los headers internos
    cache_estado = respuesta.headers.get("X-VeraScope-Cache", "no_aplica")
    logger.info(
        "peticion metodo=%s ruta=%s estado=%s t_total_ms=%.2f cache=%s",
        request.method,
        request.scope.get("route").path if request.scope.get("route") else "desconocida",
        respuesta.status_code,
        (perf_counter() - inicio) * 1000,
        cache_estado,
    )
    return respuesta
