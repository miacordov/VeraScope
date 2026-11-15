"""Pruebas de app/estadistica/periodos.py (guía §11, cálculos C16 y C17; issue #6)."""

import numpy as np
import pytest

from app.estadistica.constantes import PERIODOS_DEFECTO
from app.estadistica.periodos import (
    NOTA_DESCRIPTIVA,
    PeriodoCorto,
    comparar_periodos,
    meses_inusuales,
)


def _fechas(anio_inicio, anio_fin):
    return [f"{a}-{m:02d}" for a in range(anio_inicio, anio_fin + 1) for m in range(1, 13)]


FECHAS = _fechas(1981, 2025)
N = len(FECHAS)


# ------------------------------------------------------------- C17 inusuales


def test_meses_inusuales_umbral_y_fase_rezagada():
    z = np.zeros(N)
    z[[10, 50, 51, 300]] = [2.5, -3.0, 2.0, 4.1]  # 2.0 exacto no cuenta (|z| > 2)
    fases = ["neutro"] * N
    fases[47], fases[48], fases[297] = "nina", "nino", "nino"
    res = meses_inusuales(z, FECHAS, fases, rezago=3)
    assert [(m.fecha, m.z, m.fase) for m in res] == [
        (FECHAS[10], 2.5, "neutro"),
        (FECHAS[50], -3.0, "nina"),
        (FECHAS[300], pytest.approx(4.1), "nino"),
    ]


def test_meses_antes_del_rezago_no_se_etiquetan():
    z = np.zeros(N)
    z[[0, 2, 3]] = 5.0
    res = meses_inusuales(z, FECHAS, ["nino"] * N, rezago=3)
    assert [m.fecha for m in res] == [FECHAS[3]]


def test_meses_inusuales_ignora_nan():
    z = np.full(N, np.nan)
    z[100] = -2.6
    res = meses_inusuales(z, FECHAS, ["nina"] * N, rezago=0)
    assert [(m.fecha, m.fase) for m in res] == [(FECHAS[100], "nina")]


def test_meses_inusuales_valida_largos():
    with pytest.raises(ValueError):
        meses_inusuales(np.zeros(N), FECHAS[:-1], ["neutro"] * N, rezago=0)


# ------------------------------------------------------------- C16 periodos


def _series():
    t = np.arange(N)
    original = 0.01 * t  # sube
    sin_el_nino = 0.002 * t
    sin_el_nino[:3] = np.nan  # rezago 3
    return original, sin_el_nino


def test_comparar_periodos_medias_y_deltas():
    original, sin = _series()
    p1, p2 = (1981, 2001), (2003, 2025)
    res = comparar_periodos(original, sin, FECHAS, [], p1, p2)
    anios = np.array([int(f[:4]) for f in FECHAS])
    en1 = (anios >= 1981) & (anios <= 2001)
    en2 = (anios >= 2003) & (anios <= 2025)
    assert res.p1.anios == p1 and res.p2.anios == p2
    assert res.p1.media_original == pytest.approx(original[en1].mean())
    assert res.p1.media_sin_el_nino == pytest.approx(np.nanmean(sin[en1]))
    assert res.p2.media_original == pytest.approx(original[en2].mean())
    assert res.delta_original == pytest.approx(original[en2].mean() - original[en1].mean())
    assert res.delta_sin_el_nino == pytest.approx(np.nanmean(sin[en2]) - np.nanmean(sin[en1]))
    assert (
        res.nota
        == NOTA_DESCRIPTIVA
        == "Comparación descriptiva: la significancia la da la tendencia."
    )


def test_cuenta_meses_inusuales_por_periodo_y_en_el_nino():
    original, sin = _series()
    fases = ["neutro"] * N
    z = np.zeros(N)
    z[[24, 36, 300, 301, 330]] = [3, -3, 3, 3, -3]
    fases[24 - 3], fases[300 - 3], fases[301 - 3] = "nino", "nino", "nino"
    inusuales = meses_inusuales(z, FECHAS, fases, rezago=3)
    res = comparar_periodos(original, sin, FECHAS, inusuales, (1981, 2001), (2003, 2025))
    assert (res.p1.meses_inusuales, res.p1.meses_inusuales_en_el_nino) == (2, 1)
    assert (res.p2.meses_inusuales, res.p2.meses_inusuales_en_el_nino) == (3, 2)


def test_periodos_por_defecto_vienen_de_constantes():
    original, sin = _series()
    res = comparar_periodos(original, sin, FECHAS, [])
    assert (res.p1.anios, res.p2.anios) == PERIODOS_DEFECTO


@pytest.mark.parametrize(
    "p1, p2",
    [
        ((1981, 1989), (2003, 2025)),  # P1 de 9 años
        ((1981, 2001), (2017, 2025)),  # P2 de 9 años
        ((1972, 1989), (2003, 2025)),  # P1 empieza antes de los datos: solo 9 años con datos
    ],
)
def test_periodo_de_menos_de_diez_anios_con_datos_es_ventana_corta(p1, p2):
    original, sin = _series()
    with pytest.raises(PeriodoCorto) as error:
        comparar_periodos(original, sin, FECHAS, [], p1, p2)
    assert error.value.codigo == "ventana_corta"
    assert "10 años" in str(error.value)


def test_periodo_que_empieza_antes_de_los_datos_cuenta_solo_meses_con_datos():
    original, sin = _series()
    res = comparar_periodos(original, sin, FECHAS, [], (1975, 1990), (2003, 2025))
    assert res.p1.anios == (1975, 1990)
    assert res.p1.media_original == pytest.approx(original[: 10 * 12].mean())


def test_compare_periods_valida_contra_el_contrato():
    from app.contracts import ComparePeriodsRespuesta

    original, sin = _series()
    res = comparar_periodos(original, sin, FECHAS, [])
    ComparePeriodsRespuesta.model_validate(res.como_contrato())
