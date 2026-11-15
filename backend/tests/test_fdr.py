"""Benjamini-Hochberg del escaneo (cálculo C14), sin red ni disco."""

import numpy as np
import pytest
from scipy.stats import false_discovery_control

from app.estadistica import fdr
from app.estadistica.constantes import FDR_Q
from app.estadistica.veredicto import significativa


def _p_con_nan(semilla=7, n=200):
    rng = np.random.default_rng(semilla)
    p = rng.uniform(0, 1, n) ** 3
    p[[0, 13, 57, n - 1]] = np.nan
    return p


def test_bh_igual_a_scipy_en_los_finitos():
    p = _p_con_nan()
    ok = np.isfinite(p)
    ajustado = fdr.benjamini_hochberg(p)
    np.testing.assert_allclose(ajustado[ok], false_discovery_control(p[ok], method="bh"))


def test_bh_conserva_nan_en_su_lugar_y_la_forma():
    p = _p_con_nan()
    ajustado = fdr.benjamini_hochberg(p)
    assert ajustado.shape == p.shape
    np.testing.assert_array_equal(np.isnan(ajustado), np.isnan(p))


def test_bh_no_modifica_la_entrada_y_acepta_listas():
    p = _p_con_nan()
    copia = p.copy()
    fdr.benjamini_hochberg(p)
    np.testing.assert_array_equal(p, copia)
    lista = [0.01, 0.04, float("nan"), 0.03]
    ajustado = fdr.benjamini_hochberg(lista)
    assert np.isnan(ajustado[2])
    np.testing.assert_allclose(
        ajustado[[0, 1, 3]], false_discovery_control([0.01, 0.04, 0.03], method="bh")
    )


def test_bh_todo_nan_o_vacio():
    assert np.isnan(fdr.benjamini_hochberg([np.nan, np.nan])).all()
    assert fdr.benjamini_hochberg([]).shape == (0,)


def test_bh_bajo_hipotesis_nula_rechaza_menos_del_5_por_ciento():
    # 4235 celdas sin tendencia real (sección 13, "sin tendencia"): p uniformes.
    p = np.random.default_rng(2026).uniform(0, 1, 4235)
    rechazos = significativa(fdr.benjamini_hochberg(p), FDR_Q)
    assert rechazos.mean() < 0.05
    # Sin corregir se rechazaría cerca del 5 %: BH es lo que evita los falsos hallazgos.
    assert significativa(p, FDR_Q).mean() > rechazos.mean()


def test_por_familias_ajusta_cada_familia_por_separado():
    original = _p_con_nan(1, 150)
    sin_el_nino = _p_con_nan(2, 300)
    p_enso = _p_con_nan(3, 80)
    salida = fdr.por_familias(
        {"original": original, "sin_el_nino": sin_el_nino, "p_enso_PRECTOTCORR": p_enso}
    )
    assert set(salida) == {"original", "sin_el_nino", "p_enso_PRECTOTCORR"}
    for nombre, p in (
        ("original", original),
        ("sin_el_nino", sin_el_nino),
        ("p_enso_PRECTOTCORR", p_enso),
    ):
        np.testing.assert_allclose(salida[nombre], fdr.benjamini_hochberg(p), equal_nan=True)
    # Mezclar las familias daría otros números: confirma que no se mezclan.
    juntas = fdr.benjamini_hochberg(np.concatenate([original, sin_el_nino]))
    assert not np.allclose(salida["original"], juntas[:150], equal_nan=True)


def test_paridad_con_el_preparador():
    motor = pytest.importorskip("verascope_datos.motor")
    p = _p_con_nan(11, 500)
    np.testing.assert_allclose(fdr.benjamini_hochberg(p), motor.fdr(p), equal_nan=True)


def test_docstrings_citan_el_calculo():
    assert "C14" in fdr.benjamini_hochberg.__doc__
    assert "C14" in fdr.por_familias.__doc__
