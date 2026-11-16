"""Líneas causa → consecuencia desde una celda (guía §10).

Usa las matrices de la rejilla (`app.state.rejilla`) y el vínculo con
El Niño de cada celda que dejó el escaneo (`r_enso`, `p_enso` de `resultados.parquet`).
"""

import numpy as np
from fastapi import HTTPException, Request

from app.api import router
from app.api.validacion import LatitudConsulta, LongitudConsulta, rechazar
from app.contracts import TeleconnectRespuesta, Variable
from app.datos import celdas
from app.estadistica.teleconexion import VARIABLES_CON_LINEAS, buscar_lineas, celda_mas_cercana

MENSAJE_ESCANEO_EN_CURSO = (
    "El escaneo de ScanMap todavía no terminó, así que aún no se pueden buscar líneas. "
    "Inténtalo más tarde; el análisis de la celda sí está disponible."
)


def _escaneo_en_curso():
    raise HTTPException(
        status_code=503,
        detail={
            "codigo": "escaneo_en_curso",
            "mensaje": MENSAJE_ESCANEO_EN_CURSO,
            "celda_cercana": None,
        },
    )


def _vinculo_por_celda(escaneo, variable: str, n_celdas: int) -> tuple[np.ndarray, np.ndarray]:
    """`r_enso` y `p_enso` de cada celda de la rejilla (NaN donde el escaneo no tiene fila)."""
    r_enso = np.full(n_celdas, np.nan)
    p_enso = np.full(n_celdas, np.nan)
    filas = escaneo.loc[escaneo["variable"] == variable]
    posiciones = filas["celda"].to_numpy(dtype=int)
    r_enso[posiciones] = filas["r_enso"].to_numpy(dtype=float)
    p_enso[posiciones] = filas["p_enso"].to_numpy(dtype=float)
    return r_enso, p_enso


@router.get("/teleconnect", response_model=TeleconnectRespuesta)
def teleconnect(request: Request, variable: Variable, lat: LatitudConsulta, lon: LongitudConsulta):
    """Hasta 3 líneas de efecto opuesto y 2 de mismo efecto desde la celda pedida.

    El origen es la celda de ScanMap más cercana al clic, con su distancia. Para `T2M`
    responde sin líneas y lo explica. Mientras no haya escaneo, 503 `escaneo_en_curso`.
    Se aceptan longitudes 0–360. Ejemplo: PRECTOTCORR en Piura (-5, -80.5).
    """
    estado = request.app.state
    rejilla = getattr(estado, "rejilla", None)
    escaneo = estado.escaneo_resultados
    if rejilla is None or escaneo is None:
        _escaneo_en_curso()
    con_lineas = variable in VARIABLES_CON_LINEAS
    matrices = rejilla.matrices.get(variable)
    if con_lineas and matrices is None:
        _escaneo_en_curso()

    origen, distancia = celda_mas_cercana(lat, celdas.lon_a_180(lon), rejilla.lats, rejilla.lons)
    r_enso, p_enso = _vinculo_por_celda(escaneo, variable, len(rejilla.lats))
    if not np.isfinite(r_enso[origen]) or (con_lineas and not matrices.validas[origen]):
        rechazar(
            "sin_datos_tierra",
            "Esta celda no tiene suficientes datos válidos para buscar líneas. "
            "Para humedad del suelo, elige una celda sobre tierra.",
        )

    resultado = buscar_lineas(
        variable,
        origen,
        matrices,
        rejilla.lats,
        rejilla.lons,
        r_enso,
        p_enso,
        rejilla.fechas,
        rejilla.fases,
    )
    return TeleconnectRespuesta(
        variable=variable,
        origen={
            "lat": float(rejilla.lats[origen]),
            "lon": float(rejilla.lons[origen]),
            "distancia_a_clic_km": round(distancia, 6),
            "r_el_nino": float(r_enso[origen]),
        },
        lineas=[linea.como_contrato() for linea in resultado.lineas],
        mensaje_vacio=resultado.mensaje_vacio,
    )
