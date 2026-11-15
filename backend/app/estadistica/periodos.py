"""Comparación entre periodos y meses inusuales (guía §11; cálculos C16 y C17).

Funciones puras: reciben las series que ya calculó `analizar_celda` (anomalías
originales, serie sin El Niño y `serie_z`), sin red, sin disco y sin FastAPI. Los
umbrales salen solo de `constantes.py`. La fase de cada mes llega ya calculada
(`indices.fases`), así este paquete no depende de `datos/`.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from app.estadistica import constantes
from app.estadistica.constantes import MIN_MESES, UMBRAL_INUSUAL

NOTA_DESCRIPTIVA = "Comparación descriptiva: la significancia la da la tendencia."
FASE_NINO = "nino"


class PeriodoCorto(ValueError):
    """Un periodo comparado tiene menos de 10 años con datos (error `ventana_corta`)."""

    codigo = "ventana_corta"


@dataclass(frozen=True)
class MesInusual:
    """Un mes con `|z| > UMBRAL_INUSUAL` (campos de `MesInusual` del contrato)."""

    fecha: str
    z: float
    fase: str


def meses_inusuales(
    serie_z, fechas: Sequence[str], fases: Sequence[str], rezago: int
) -> list[MesInusual]:
    """Cálculo C17: meses con `|z_t| > UMBRAL_INUSUAL`, con la fase del índice en `t − ℓ*`.

    `serie_z` es la anomalía original estandarizada (`serie_z` de `analyze`); `fases`,
    la fase del índice en cada mes, alineada con `fechas`. Los primeros `rezago` meses
    no tienen índice en `t − ℓ*` y quedan fuera, igual que en las dos tendencias. Los
    `NaN` no cuentan. Va en `analyze` y se cuenta por periodo en `compare-periods`.
    """
    z = np.asarray(serie_z, float)
    if not (z.size == len(fechas) == len(fases)):
        raise ValueError("serie_z, fechas y fases deben tener un valor por mes")
    if not 0 <= rezago < z.size:
        raise ValueError("el rezago no cabe en la serie")
    with np.errstate(invalid="ignore"):
        inusual = np.abs(z) > UMBRAL_INUSUAL
    inusual[:rezago] = False
    return [
        MesInusual(fecha=fechas[t], z=float(z[t]), fase=str(fases[t - rezago]))
        for t in np.flatnonzero(inusual)
    ]


@dataclass(frozen=True)
class ResumenPeriodo:
    """Un periodo de la comparación (campos de `Periodo` del contrato)."""

    anios: tuple[int, int]
    media_original: float
    media_sin_el_nino: float
    meses_inusuales: int
    meses_inusuales_en_el_nino: int

    def como_contrato(self) -> dict:
        return {
            "anios": self.anios,
            "media_original": self.media_original,
            "media_sin_el_nino": self.media_sin_el_nino,
            "meses_inusuales": self.meses_inusuales,
            "meses_inusuales_en_el_nino": self.meses_inusuales_en_el_nino,
        }


@dataclass(frozen=True)
class ComparacionPeriodos:
    """Resultado de `compare-periods` (campos de `ComparePeriodsRespuesta`)."""

    p1: ResumenPeriodo
    p2: ResumenPeriodo
    delta_original: float
    delta_sin_el_nino: float
    nota: str = NOTA_DESCRIPTIVA

    def como_contrato(self) -> dict:
        return {
            "p1": self.p1.como_contrato(),
            "p2": self.p2.como_contrato(),
            "delta_original": self.delta_original,
            "delta_sin_el_nino": self.delta_sin_el_nino,
            "nota": self.nota,
        }


def _media(valores) -> float:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # periodo sin serie limpia → NaN
        return float(np.nanmean(valores))


def _resumen(original, sin_el_nino, anios, inusuales, periodo) -> ResumenPeriodo:
    inicio, fin = int(periodo[0]), int(periodo[1])
    if inicio > fin:
        raise ValueError("el periodo debe empezar antes de terminar")
    dentro = (anios >= inicio) & (anios <= fin)
    if np.count_nonzero(dentro & np.isfinite(original)) < MIN_MESES:
        raise PeriodoCorto(
            f"El periodo {inicio}–{fin} tiene menos de 10 años con datos. Con tan pocos "
            "años, el ruido entre años impide comparar; elige al menos 10 años por periodo."
        )
    en_periodo = [m for m in inusuales if inicio <= int(m.fecha[:4]) <= fin]
    return ResumenPeriodo(
        anios=(inicio, fin),
        media_original=_media(original[dentro]),
        media_sin_el_nino=_media(sin_el_nino[dentro]),
        meses_inusuales=len(en_periodo),
        meses_inusuales_en_el_nino=sum(m.fase == FASE_NINO for m in en_periodo),
    )


def comparar_periodos(
    serie_original,
    serie_sin_el_nino,
    fechas: Sequence[str],
    inusuales: Sequence[MesInusual],
    p1: tuple[int, int] | None = None,
    p2: tuple[int, int] | None = None,
) -> ComparacionPeriodos:
    """Cálculo C16: `Δ = ā_P2 − ā_P1` sobre la serie original y sobre la sin El Niño.

    Es **descriptiva**: no hay prueba de diferencia de medias (habría que corregir la
    autocorrelación y el desbalance de fases entre periodos); la significancia la da
    la tendencia. Si `Δ_sin` conserva signo y magnitud de `Δ`, el cambio no se debe a
    que un periodo tuvo más Niños. Por defecto, `PERIODOS_DEFECTO`. Cada periodo
    necesita al menos `MIN_MESES` meses con datos; si no, `PeriodoCorto`
    (`ventana_corta`). `inusuales` sale de `meses_inusuales` y se cuenta por periodo.
    """
    original = np.asarray(serie_original, float)
    sin_el_nino = np.asarray(serie_sin_el_nino, float)
    if not (original.size == sin_el_nino.size == len(fechas)):
        raise ValueError("las dos series y las fechas deben tener el mismo largo")
    if p1 is None or p2 is None:
        defecto_1, defecto_2 = constantes.PERIODOS_DEFECTO
        p1 = p1 if p1 is not None else defecto_1
        p2 = p2 if p2 is not None else defecto_2
    anios = np.array([int(f[:4]) for f in fechas])
    r1 = _resumen(original, sin_el_nino, anios, inusuales, p1)
    r2 = _resumen(original, sin_el_nino, anios, inusuales, p2)
    return ComparacionPeriodos(
        p1=r1,
        p2=r2,
        delta_original=r2.media_original - r1.media_original,
        delta_sin_el_nino=r2.media_sin_el_nino - r1.media_sin_el_nino,
    )
