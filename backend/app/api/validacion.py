"""Validación de consultas, también aplicable a los escenarios simulados."""

from typing import Annotated

from fastapi import HTTPException, Query

from app.estadistica.constantes import MIN_MESES, ventana_fin

LatitudConsulta = Annotated[float, Query(ge=-90, le=90, allow_inf_nan=False)]
LongitudConsulta = Annotated[float, Query(ge=-180, le=360, allow_inf_nan=False)]


def rechazar(codigo: str, mensaje: str):
    """Un único cuerpo estándar para todos los rechazos de consulta."""
    raise HTTPException(422, detail={"codigo": codigo, "mensaje": mensaje, "celda_cercana": None})


def validar_ventana(inicio: int, fin: int):
    """Años inclusivos, dentro de los disponibles y con al menos 120 meses."""
    if inicio < 1981 or fin > ventana_fin() or inicio > fin:
        rechazar(
            "fuera_de_rango",
            "Elige años desde 1981 hasta el último año completo, en orden.",
        )
    if (fin - inicio + 1) * 12 < MIN_MESES:
        rechazar(
            "ventana_corta",
            "La ventana tiene menos de 10 años. Con tan pocos años, el ruido entre "
            "años impide ver tendencias; elige al menos 10.",
        )


def exigir_seleccion(recibida: dict, disponible: dict):
    """No sustituye silenciosamente una consulta por un escenario distinto."""
    if recibida != disponible:
        rechazar(
            "fuera_de_rango",
            "No hay un escenario simulado para estos parámetros. "
            "Consulta los ejemplos disponibles en la documentación de la API.",
        )
