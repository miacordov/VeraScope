"""Análisis completo de una celda y una variable (guía §8: "un solo análisis, mensual").

Implementación única: la usan por igual la ruta `analyze`, el job de ScanMap y el
preparador (`verascope_datos`). Si el escaneo y el análisis en vivo dieran números
distintos para una misma celda, sería un bug. Función pura: sin FastAPI, sin disco y
sin red. Aplica a las cinco variables de POWER.
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

import numpy as np

from app.datos.validacion import limpiar
from app.estadistica import veredicto as ver
from app.estadistica.anomalias import estandarizar, preparar
from app.estadistica.constantes import ALFA, MIN_MESES
from app.estadistica.enso import quitar_enso
from app.estadistica.tendencia import (
    ResultadoTendencia,
    cambio_pct_decada,
    cambio_total,
    recta,
    tendencia,
)


@dataclass(frozen=True)
class TendenciaCelda:
    """Una de las dos tendencias de la celda, con los campos de `Tendencia` del contrato.

    `p_ajustado` no está aquí: solo existe cuando el veredicto sale del escaneo (BH sobre
    todas las celdas) y lo agrega quien arma la respuesta. `significativa` usa `p < ALFA`.
    """

    pendiente_decada: float
    ic_bajo: float
    ic_alto: float
    p: float
    significativa: bool
    direccion: str
    cambio_total: float
    cambio_pct_decada: float | None
    recta: list[float | None]
    calculo: ResultadoTendencia


@dataclass(frozen=True)
class VinculoCelda:
    """Vínculo con El Niño (campos de `Vinculo` del contrato)."""

    rezago_meses: int
    r: float
    p: float
    n_efectivo: float
    significativo: bool
    indicativo: bool


@dataclass(frozen=True)
class ResultadoCelda:
    """Todo lo que una celda aporta a `AnalyzeRespuesta` (guía §17) y a `resultados.parquet`.

    Las series son arreglos de largo `meses` (la ventana completa); `serie_sin_el_nino`
    tiene `NaN` en los primeros `rezago` meses (el contrato los envía como `null`).
    """

    variable: str | None
    meses: int
    """Meses de la ventana (largo de `fechas`)."""
    meses_analizados: int
    """Meses usados por las dos tendencias: `meses − rezago`."""
    rezago: int
    serie_original: np.ndarray
    """Anomalías mensuales (C3) con los huecos cortos ya interpolados (C2)."""
    serie_sin_el_nino: np.ndarray
    serie_z: np.ndarray
    tendencia_original: TendenciaCelda
    tendencia_sin_el_nino: TendenciaCelda
    veredicto: str
    """Veredicto individual (p sin ajustar); en el escaneo se recalcula con BH."""
    vinculo_el_nino: VinculoCelda
    colinealidad: float
    avisos: tuple[tuple[str, str], ...]
    """(código, texto en español sencillo) con regla numérica (C12)."""
    efecto: float
    """Pendiente sin El Niño por década ÷ desviación estándar de las anomalías."""

    def fila_escaneo(self) -> dict:
        """Columnas de `resultados.parquet` que salen de una celda (guía §6), más `n_efectivo`.

        Las columnas de BH (`p_original_ajustado`, `p_ajustado`, `p_enso_ajustado`), el
        veredicto del escaneo y los metadatos (celda, variable, unidad…) los agrega el job.
        `meses` es el largo de la ventana, como en el preparador original.
        """
        sin = self.tendencia_sin_el_nino
        return {
            "pendiente_original": self.tendencia_original.pendiente_decada,
            "p_original": self.tendencia_original.p,
            "pendiente": sin.pendiente_decada,
            "ic_bajo": sin.ic_bajo,
            "ic_alto": sin.ic_alto,
            "p": sin.p,
            "rezago": self.rezago,
            "r_enso": self.vinculo_el_nino.r,
            "p_enso": self.vinculo_el_nino.p,
            "n_efectivo": self.vinculo_el_nino.n_efectivo,
            "colinealidad": self.colinealidad,
            "efecto": self.efecto,
            "meses": self.meses,
        }


def _referencia(valores) -> float:
    """Climatología de la celda en la ventana: promedio de la serie bruta (sin rellenos)."""
    bruta = limpiar(valores)
    if not np.isfinite(bruta).any():
        return float("nan")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        return float(np.nanmean(bruta))


def _tendencia_celda(y, n, rezago, referencia, variable) -> TendenciaCelda:
    res = tendencia(y)
    sig = bool(ver.significativa(res.p, ALFA))
    return TendenciaCelda(
        pendiente_decada=res.pendiente_decada,
        ic_bajo=res.ic_bajo,
        ic_alto=res.ic_alto,
        p=res.p,
        significativa=sig,
        direccion=str(ver.direccion(res.pendiente_decada, sig)),
        cambio_total=cambio_total(res.pendiente_mes, res.n),
        cambio_pct_decada=cambio_pct_decada(res.pendiente_decada, referencia, variable),
        recta=recta(res, n, rezago),
        calculo=res,
    )


def analizar_celda(valores, meses_calendario, indice, variable) -> ResultadoCelda | None:
    """Analiza una celda y una variable; devuelve `None` si la serie se descarta.

    Pasos (los "C#" son cálculos del informe estadístico, guía §8):

    1. C2 + C3 (`anomalias.preparar`, orden de L13): rellenos `-999` → `NaN`, anomalías
       con la climatología de la ventana y después interpolación de huecos ≤ 2 meses.
       Se descarta si hay un hueco largo, más del 10 % faltante, menos de `MIN_MESES`
       meses o la serie es constante.
    2. C9, C10, C11 y C12 (`enso.quitar_enso`): rezago `ℓ*` en 0..6 (C9), regresión
       conjunta con la tendencia y serie sin El Niño con `NaN` en `[:ℓ*]` (C10), `r` y
       su p con `n_efectivo`, indicativo (C11), y colinealidad (C12).
    3. C4–C7 (`tendencia.tendencia`): las **dos** tendencias sobre **los mismos meses**
       `a[ℓ*:]` y `limpia[ℓ*:]` (diferencia 1 de la guía §7), cambio total, cambio %
       por década (nunca en `T2M`; referencia = promedio de la serie bruta de la celda
       en la ventana) y rectas con `None` antes de `ℓ*`.
    4. C13 (`veredicto`): significancia individual con `p < ALFA`, cuatro estados y
       dirección. Con celdas de ScanMap el job rehace el veredicto con p ajustados (C14).
    5. C12: avisos de colinealidad, potencia baja (meses analizados) y muestra efectiva.

    Supuestos: `valores`, `meses_calendario` (1..12) e `indice` tienen el mismo largo y
    están alineados mes a mes; el índice no tiene faltantes. `variable` es el código
    POWER (decide solo el cambio porcentual). No modifica las entradas.
    """
    a = preparar(valores, meses_calendario)
    if a is None or a.size < MIN_MESES or not np.std(a) > 0:
        return None
    n = int(a.size)
    en = quitar_enso(a, indice)
    ell = en.rezago
    referencia = _referencia(valores)
    original = _tendencia_celda(a[ell:], n, ell, referencia, variable)
    sin = _tendencia_celda(en.limpia[ell:], n, ell, referencia, variable)
    vinculo = VinculoCelda(
        rezago_meses=ell,
        r=en.r,
        p=en.p,
        n_efectivo=en.n_efectivo,
        significativo=bool(ver.significativa(en.p, ALFA)),
        indicativo=en.indicativo,
    )
    return ResultadoCelda(
        variable=variable,
        meses=n,
        meses_analizados=n - ell,
        rezago=ell,
        serie_original=a,
        serie_sin_el_nino=en.limpia,
        serie_z=estandarizar(a),
        tendencia_original=original,
        tendencia_sin_el_nino=sin,
        veredicto=str(ver.estado(original.significativa, sin.significativa)),
        vinculo_el_nino=vinculo,
        colinealidad=en.colinealidad,
        avisos=tuple(ver.avisos(n - ell, en.colinealidad, en.n_efectivo)),
        efecto=sin.pendiente_decada / float(np.std(a)),
    )
