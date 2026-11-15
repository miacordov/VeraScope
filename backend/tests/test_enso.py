"""Pruebas de app/estadistica/enso.py (cálculos C9–C12; guía §13, Recuperación, Correlación,
Mismos meses).

Series sintéticas con semilla fija (tests/sinteticas.py); ninguna toca la red. Las cifras
son de simulaciones y no se citan como resultados de la plataforma.
"""

import dataclasses

import numpy as np
import pytest

from app.estadistica.anomalias import anomalias
from app.estadistica.constantes import ALFA, COLINEALIDAD_MAX, NEFF_PISO, REZAGO_MAX
from app.estadistica.enso import (
    ResultadoEnso,
    n_efectivo,
    p_correlacion,
    quitar_enso,
    r1,
)
from tests.sinteticas import ar1, generador, serie, series_independientes

N = 480


def _caso(repeticion=0, n=N, gamma=1.0, rezago=3, beta_dec=0.3):
    s = serie(generador(repeticion), n=n, beta_dec=beta_dec, gamma=gamma, rezago=rezago)
    return s, anomalias(s.valores, s.meses_calendario)


# --- r1 ---------------------------------------------------------------------


def test_r1_recupera_la_autocorrelacion_de_un_ar1():
    x = ar1(5000, 0.7, 1.0, generador(1))
    assert r1(x) == pytest.approx(0.7, abs=0.03)


def test_r1_vectorizado_por_filas():
    filas = np.stack([ar1(300, 0.5, 1.0, generador(i)) for i in range(4)])
    juntas = r1(filas)
    assert juntas.shape == (4,)
    np.testing.assert_allclose(juntas, [r1(f) for f in filas])
    np.testing.assert_allclose(r1(filas[0]), np.corrcoef(filas[0][:-1], filas[0][1:])[0, 1])


# --- n_efectivo (C11, Bretherton 1999) --------------------------------------


def test_n_efectivo_formula_de_bretherton():
    assert n_efectivo(0.5, 0.4, 240) == pytest.approx(240 * (1 - 0.2) / (1 + 0.2))


def test_n_efectivo_sin_autocorrelacion_es_n():
    assert n_efectivo(0.0, 0.9, 240) == pytest.approx(240)


def test_n_efectivo_tiene_piso_y_techo():
    assert n_efectivo(0.999, 0.999, 240) == NEFF_PISO
    # Autocorrelaciones de signo contrario no inflan la muestra por encima de n.
    assert n_efectivo(0.8, -0.8, 240) == 240
    ne = n_efectivo(np.linspace(-0.99, 0.99, 50), 0.95, 300)
    assert (ne <= 300).all() and (ne >= NEFF_PISO).all()


# --- p_correlacion (C11) ----------------------------------------------------


def test_p_correlacion_devuelve_p_y_n_efectivo():
    p, ne = p_correlacion(0.3, 0.5, 0.4, 240)
    assert ne == pytest.approx(n_efectivo(0.5, 0.4, 240))
    assert 0 < p < 1


def test_p_correlacion_es_mas_conservadora_que_la_ingenua():
    p_ingenua, _ = p_correlacion(0.2, 0.0, 0.0, 240)
    p_corregida, _ = p_correlacion(0.2, 0.9, 0.9, 240)
    assert p_corregida > p_ingenua


def test_p_correlacion_vectorizada():
    r = np.array([0.0, 0.1, -0.3, 0.6])
    r1x = np.array([0.2, 0.5, 0.9, 0.0])
    p, ne = p_correlacion(r, r1x, 0.5, 300)
    assert p.shape == ne.shape == (4,)
    for i in range(4):
        pi, nei = p_correlacion(r[i], r1x[i], 0.5, 300)
        assert p[i] == pytest.approx(pi) and ne[i] == pytest.approx(nei)
    assert p[0] == pytest.approx(1.0)


@pytest.mark.lento
def test_correlacion_series_independientes_falsas_alarmas_cerca_de_5_por_ciento():
    # Guía §13 "Correlación": ≈ 5 % con tamaño efectivo (≈ 22 % con el p ingenuo).
    # Tolerancia fijada por B3: entre 2 % y 8 % sobre 1000 pares (ρ = 0.9, 480 meses).
    reps = 1000
    pares = [series_independientes(generador(i), n=N, rho=0.9) for i in range(reps)]
    x = np.stack([a for a, _ in pares])
    y = np.stack([b for _, b in pares])
    xc = x - x.mean(axis=1, keepdims=True)
    yc = y - y.mean(axis=1, keepdims=True)
    r = (xc * yc).sum(1) / np.sqrt((xc**2).sum(1) * (yc**2).sum(1))
    p, ne = p_correlacion(r, r1(x), r1(y), N)
    tasa = np.mean(p < ALFA)
    assert 0.02 <= tasa <= 0.08, tasa
    p_ingenua, _ = p_correlacion(r, 0.0, 0.0, N)
    assert np.mean(p_ingenua < ALFA) > 2 * tasa
    assert (ne <= N).all() and (ne >= NEFF_PISO).all()


# --- quitar_enso (C9, C10, C12) ---------------------------------------------


def test_quitar_enso_devuelve_resultado_inmutable():
    _, a = _caso()
    res = quitar_enso(a, _caso()[0].indice)
    assert isinstance(res, ResultadoEnso)
    assert res.indicativo is True
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.rezago = 0


def test_limpia_tiene_largo_n_y_nan_en_los_primeros_rezago_meses():
    s, a = _caso(rezago=3)
    res = quitar_enso(a, s.indice)
    assert res.rezago == 3
    assert res.limpia.shape == (N,)
    assert np.isnan(res.limpia[:3]).all()
    assert not np.isnan(res.limpia[3:]).any()


def test_limpia_sin_rezago_no_tiene_nan():
    s, a = _caso(rezago=0)
    res = quitar_enso(a, s.indice)
    assert res.rezago == 0
    assert not np.isnan(res.limpia).any()


def test_limpia_resta_gamma_por_el_indice_centrado_y_conserva_la_tendencia():
    s, a = _caso(rezago=2)
    res = quitar_enso(a, s.indice)
    ell = res.rezago
    e = s.indice[: N - ell]
    np.testing.assert_allclose(res.limpia[ell:], a[ell:] - res.gamma * (e - e.mean()))
    # Regresión conjunta: la tendencia queda en la serie limpia.
    t = np.arange(N - ell)
    pendiente = np.polyfit(t, res.limpia[ell:], 1)[0] * 120
    assert pendiente == pytest.approx(0.3, abs=0.25)


def test_r_y_p_corresponden_al_rezago_elegido():
    s, a = _caso(rezago=3)
    res = quitar_enso(a, s.indice)
    ell = res.rezago
    e, y = s.indice[: N - ell], a[ell:]
    assert res.r == pytest.approx(np.corrcoef(e, y)[0, 1])
    p, ne = p_correlacion(res.r, r1(e), r1(y), N - ell)
    assert res.p == pytest.approx(p)
    assert res.n_efectivo == pytest.approx(ne)
    assert NEFF_PISO <= res.n_efectivo <= N - ell
    assert res.p < ALFA


@pytest.mark.lento
def test_recupera_rezago_3_en_al_menos_99_por_ciento():
    # Guía §13 "Recuperación": rezago correcto en ≥ 99 % con rezago verdadero de 3 meses.
    reps = 200
    aciertos = 0
    for i in range(reps):
        s, a = _caso(repeticion=i, rezago=3)
        aciertos += quitar_enso(a, s.indice).rezago == 3
    assert aciertos / reps >= 0.99


@pytest.mark.parametrize("rezago", range(REZAGO_MAX + 1))
def test_recupera_cada_rezago_de_0_a_6(rezago):
    s, a = _caso(repeticion=rezago, rezago=rezago)
    assert quitar_enso(a, s.indice).rezago == rezago


@pytest.mark.lento
def test_gamma_recuperado_cerca_del_verdadero():
    # Tolerancia fijada por B3: |γ̂ − γ| < 0.15 en ≥ 95 % y sesgo medio < 0.03 (γ = 1).
    errores = []
    for i in range(200):
        s, a = _caso(repeticion=i, gamma=1.0, rezago=3)
        errores.append(quitar_enso(a, s.indice).gamma - 1.0)
    errores = np.array(errores)
    assert np.mean(np.abs(errores) < 0.15) >= 0.95
    assert abs(errores.mean()) < 0.03


def test_sin_efecto_de_el_nino_gamma_cerca_de_cero():
    s, a = _caso(gamma=0.0, rezago=0)
    assert abs(quitar_enso(a, s.indice).gamma) < 0.2


def test_rezago_max_limita_la_busqueda():
    s, a = _caso(rezago=5)
    assert quitar_enso(a, s.indice, rezago_max=2).rezago <= 2


def test_colinealidad_con_signo():
    s, a = _caso(rezago=0)
    t = np.arange(N)
    sube = s.indice + t / 60.0
    baja = s.indice - t / 60.0
    r_sube = quitar_enso(a, sube)
    r_baja = quitar_enso(a, baja)
    e = sube[: N - r_sube.rezago]
    assert r_sube.colinealidad == pytest.approx(np.corrcoef(e, np.arange(e.size))[0, 1])
    assert r_sube.colinealidad > COLINEALIDAD_MAX
    assert r_baja.colinealidad < -COLINEALIDAD_MAX
    assert r_sube.colineal and r_baja.colineal


def test_colinealidad_baja_sin_tendencia_en_el_indice():
    s, a = _caso()
    res = quitar_enso(a, s.indice)
    assert abs(res.colinealidad) <= 1
    assert res.colineal == (abs(res.colinealidad) > COLINEALIDAD_MAX)


def test_quitar_enso_rechaza_largos_distintos():
    s, a = _caso()
    with pytest.raises(ValueError):
        quitar_enso(a, s.indice[:-1])


def test_quitar_enso_no_modifica_la_entrada():
    s, a = _caso()
    a0, e0 = a.copy(), s.indice.copy()
    quitar_enso(a, s.indice)
    np.testing.assert_array_equal(a, a0)
    np.testing.assert_array_equal(s.indice, e0)
