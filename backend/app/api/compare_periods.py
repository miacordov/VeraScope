"""Comparación descriptiva entre dos periodos de una misma celda (guía §11, cálculo C16).

Reutiliza `analyze` sobre la ventana por defecto (1981 → último año completo, índice ONI):
las series, el rezago y los meses inusuales son los mismos que muestra la tarjeta.
"""

import numpy as np
from fastapi import Request
from fastapi.responses import JSONResponse

from app.api import router
from app.api.analyze import analyze
from app.api.validacion import LatitudConsulta, LongitudConsulta, rechazar, validar_ventana
from app.contracts import ComparePeriodsRespuesta, IndiceId, Variable
from app.estadistica.constantes import ventana_fin
from app.estadistica.periodos import MesInusual, PeriodoCorto, comparar_periodos


def _arreglo(serie) -> np.ndarray:
    """Serie del contrato (`null` donde no hay dato) a `float` con `NaN`."""
    return np.array([np.nan if v is None else v for v in serie], dtype=float)


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
    """Promedio de cada periodo con y sin El Niño, sus diferencias y meses inusuales.

    Es descriptiva: la significancia la da la tendencia. Cada periodo requiere diez
    años. Ejemplo: PRECTOTCORR en Piura, 1981–2001 frente a 2003–2025.
    """
    validar_ventana(p1_inicio, p1_fin)
    validar_ventana(p2_inicio, p2_fin)
    celda = analyze(request, variable, lat, lon, 1981, ventana_fin(), IndiceId.ONI)
    if isinstance(celda, JSONResponse):  # power_lento o power_error, tal cual
        return celda
    try:
        comparacion = comparar_periodos(
            _arreglo(celda.serie_original),
            _arreglo(celda.serie_sin_el_nino),
            celda.fechas,
            [MesInusual(fecha=m.fecha, z=m.z, fase=m.fase) for m in celda.meses_inusuales],
            p1=(p1_inicio, p1_fin),
            p2=(p2_inicio, p2_fin),
        )
    except PeriodoCorto as error:
        rechazar("ventana_corta", str(error))
    return ComparePeriodsRespuesta.model_validate(comparacion.como_contrato())
