"""Pruebas del generador de series sintéticas.

Si el generador miente, las pruebas del motor también.
"""

import numpy as np
import pytest

from tests.sinteticas import (
    FALTANTE_POWER,
    ar1,
    con_huecos,
    generador,
    serie,
    series_independientes,
)


def test_misma_semilla_misma_serie():
    a = serie(generador(3), beta_dec=0.5, gamma=1.0, rezago=3)
    b = serie(generador(3), beta_dec=0.5, gamma=1.0, rezago=3)
    np.testing.assert_array_equal(a.valores, b.valores)
    np.testing.assert_array_equal(a.indice, b.indice)


def test_repeticiones_distintas_dan_series_distintas():
    a = serie(generador(0)).valores
    b = serie(generador(1)).valores
    assert not np.allclose(a, b)


def test_formas_y_meses_calendario():
    s = serie(generador(0), n=240, mes_inicial=11)
    assert s.valores.shape == s.indice.shape == s.meses_calendario.shape == (240,)
    assert list(s.meses_calendario[:4]) == [11, 12, 1, 2]
    assert np.isfinite(s.valores).all() and np.isfinite(s.indice).all()


def test_ar1_tiene_la_autocorrelacion_pedida():
    x = ar1(20000, 0.93, 1.0, generador(0))
    r1 = np.corrcoef(x[:-1], x[1:])[0, 1]
    assert r1 == pytest.approx(0.93, abs=0.01)
    assert x.std() == pytest.approx(1.0, abs=0.1)


def test_ar1_rechaza_rho_fuera_de_rango():
    with pytest.raises(ValueError):
        ar1(10, 1.0, 1.0, generador(0))


def test_parametros_verdaderos_se_recuperan_por_minimos_cuadrados():
    """Con el rezago verdadero, una regresión conjunta recupera β y γ: el generador es coherente."""
    s = serie(generador(0), n=6000, beta_dec=0.5, gamma=1.5, rezago=3, amplitud_estacional=0.0)
    n, L = s.valores.size, s.rezago
    t = np.arange(n - L)
    X = np.column_stack([np.ones(n - L), t, s.indice[: n - L]])
    _, beta_mes, gamma = np.linalg.lstsq(X, s.valores[L:], rcond=None)[0]
    assert beta_mes * 120 == pytest.approx(0.5, abs=0.05)
    assert gamma == pytest.approx(1.5, abs=0.05)


def test_alineacion_del_rezago():
    """El motor empareja a[ℓ:] con E[:n−ℓ]: la componente de El Niño debe cumplir eso exacto."""
    s = serie(generador(1), gamma=2.0, rezago=3)
    np.testing.assert_allclose(s.componente_enso[3:], 2.0 * s.indice[:-3])


def test_series_independientes_no_correlacionadas():
    x, y = series_independientes(generador(0), n=20000, rho=0.5)
    assert abs(np.corrcoef(x, y)[0, 1]) < 0.05


def test_con_huecos_no_modifica_la_original():
    v = np.arange(10.0)
    h = con_huecos(v, 2, 3, relleno=FALTANTE_POWER)
    assert list(h[2:5]) == [-999.0] * 3
    assert np.isnan(con_huecos(v, 0, 1)[0])
    assert list(v) == list(np.arange(10.0))
    with pytest.raises(ValueError):
        con_huecos(v, 8, 3)
