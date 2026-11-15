"""Pruebas de app/estadistica/anomalias.py (cálculo C3 y orden decidido en L13).

Todas las series son sintéticas con semilla fija (tests/sinteticas.py); ninguna toca la red.
"""

import numpy as np
import pytest

from app.datos.validacion import rellenar_huecos
from app.estadistica.anomalias import anomalias, estandarizar, preparar
from app.estadistica.constantes import MAX_HUECO
from tests.sinteticas import FALTANTE_POWER, con_huecos, generador, serie

N = 480


def _serie(repeticion=0, n=N, mes_inicial=1):
    return serie(generador(repeticion), n=n, beta_dec=0.3, gamma=1.0, mes_inicial=mes_inicial)


# --- anomalias (C3) ---------------------------------------------------------


def test_anomalias_restan_la_climatologia_de_cada_mes_calendario():
    s = _serie(mes_inicial=4)
    a = anomalias(s.valores, s.meses_calendario)
    assert a.shape == s.valores.shape
    for k in range(1, 13):
        sel = s.meses_calendario == k
        esperado = s.valores[sel] - s.valores[sel].mean()
        np.testing.assert_allclose(a[sel], esperado)
        # Cada mes calendario queda con media cero.
        assert abs(a[sel].mean()) < 1e-12


def test_anomalias_quitan_el_ciclo_estacional():
    s = _serie()
    a = anomalias(s.valores, s.meses_calendario)
    medias = [a[s.meses_calendario == k].mean() for k in range(1, 13)]
    np.testing.assert_allclose(medias, 0.0, atol=1e-12)


def test_climatologia_solo_con_los_meses_recibidos():
    # La climatología sale de la ventana que llega, no de un periodo fijo:
    # recortar la serie cambia la climatología y por lo tanto las anomalías.
    s = _serie()
    completa = anomalias(s.valores, s.meses_calendario)
    corta = anomalias(s.valores[240:], s.meses_calendario[240:])
    for k in range(1, 13):
        sel = s.meses_calendario[240:] == k
        clima = s.valores[240:][sel].mean()
        np.testing.assert_allclose(corta[sel], s.valores[240:][sel] - clima)
    assert not np.allclose(corta, completa[240:])


def test_climatologia_ignora_faltantes_y_los_conserva():
    s = _serie()
    v = con_huecos(s.valores, 13, 2)
    a = anomalias(v, s.meses_calendario)
    assert np.isnan(a[13:15]).all()
    for k in (2, 3):  # meses 14 y 15 → febrero y marzo
        sel = s.meses_calendario == k
        clima = np.nanmean(v[sel])
        ok = sel & ~np.isnan(v)
        np.testing.assert_allclose(a[ok], v[ok] - clima)


def test_anomalias_vectorizadas_por_filas():
    filas = np.stack([_serie(i).valores for i in range(3)])
    meses = _serie().meses_calendario
    juntas = anomalias(filas, meses)
    for i in range(3):
        np.testing.assert_allclose(juntas[i], anomalias(filas[i], meses))


def test_anomalias_rechazan_largos_distintos():
    with pytest.raises(ValueError):
        anomalias(np.ones(24), np.arange(23) % 12 + 1)


# --- estandarizar (serie_z) -------------------------------------------------


def test_estandarizar_da_media_cero_y_desviacion_poblacional_uno():
    s = _serie()
    z = estandarizar(anomalias(s.valores, s.meses_calendario))
    assert abs(z.mean()) < 1e-12
    assert z.std(ddof=0) == pytest.approx(1.0)


def test_estandarizar_serie_constante_da_nan():
    assert np.isnan(estandarizar(np.ones(12))).all()


def test_estandarizar_vectorizado_por_filas():
    filas = np.stack([_serie(i).valores for i in range(3)])
    juntas = estandarizar(filas)
    for i in range(3):
        np.testing.assert_allclose(juntas[i], estandarizar(filas[i]))


# --- preparar (orden L13: anomalías y después relleno) ----------------------


def test_preparar_sin_huecos_es_igual_a_las_anomalias():
    s = _serie()
    np.testing.assert_allclose(
        preparar(s.valores, s.meses_calendario), anomalias(s.valores, s.meses_calendario)
    )


def test_preparar_aplica_anomalias_y_despues_relleno():
    s = _serie()
    v = con_huecos(s.valores, 100, MAX_HUECO)
    p = preparar(v, s.meses_calendario)
    assert p is not None and not np.isnan(p).any()
    np.testing.assert_allclose(p, rellenar_huecos(anomalias(v, s.meses_calendario)))
    # El orden inverso mete datos interpolados en la climatología y da otros números.
    inverso = anomalias(rellenar_huecos(v), s.meses_calendario)
    assert not np.allclose(p, inverso)


def test_preparar_trata_el_relleno_de_power_como_faltante():
    s = _serie()
    con_nan = preparar(con_huecos(s.valores, 50, 1), s.meses_calendario)
    con_999 = preparar(con_huecos(s.valores, 50, 1, FALTANTE_POWER), s.meses_calendario)
    np.testing.assert_allclose(con_999, con_nan)


def test_preparar_devuelve_none_con_hueco_largo():
    s = _serie()
    v = con_huecos(s.valores, 100, MAX_HUECO + 1)
    assert preparar(v, s.meses_calendario) is None


def test_preparar_devuelve_none_con_mucho_faltante():
    s = _serie()
    v = s.valores.copy()
    v[::5] = np.nan  # 20 % faltante en huecos de un mes
    assert preparar(v, s.meses_calendario) is None


def test_preparar_no_modifica_la_entrada():
    s = _serie()
    v = con_huecos(s.valores, 10, 1)
    copia = v.copy()
    preparar(v, s.meses_calendario)
    np.testing.assert_array_equal(v, copia)
