"""Rutas síncronas y composición de los contratos públicos."""

from fastapi import APIRouter

from app.contracts import ErrorRespuesta

router = APIRouter(
    prefix="/api/v1",
    responses={codigo: {"model": ErrorRespuesta} for codigo in (422, 502, 503, 504)},
)
