"""Pruebas de app/estadistica/tendencia.py (cálculos C4–C7, sección 13 de la guía).

Todas las series son sintéticas con semilla fija (tests/sinteticas.py): sus tasas no
son resultados de la plataforma. Tolerancias fijadas por B3 al escribir la prueba:

- Sin tendencia (ruido AR(1) ρ = 0.3, 480 meses, 300 repeticiones): tasa de
  "significativo" entre 1 % y 10 % (nominal 5 %; ±~4 desviaciones binomiales).
- Falsos positivos de referencia (índice AR(1) ρ = 0.93, 240 meses, sin tendencia,
  300 repeticiones): Mann-Kendall corregido tras quitar el índice ≤ 10 % y por debajo de la
  serie original. El índice se quita aquí con el índice verdadero (rezago 0) por
  regresión conjunta, solo como andamio de la prueba: la prueba con enso.py es de
  quien escribe enso.py.
- Recuperación (β = 0.5 por década, ruido blanco y AR(1) ρ = 0.3 y 0.6, 300
  repeticiones): el IC contiene β en ≥ 95 % de las repeticiones.
- Potencia (β = 0.5 desviaciones por década, 480 meses, 200 repeticiones): ≥ 80 %.
"""

import time

import numpy as np
import pytest

from app.estadistica.constantes import ALFA, ESCALA_DECADA, RHO_MAX_AR1
from app.estadistica.tendencia import (
    ResultadoTendencia,
    cambio_pct_decada,
    cambio_total,
    mann_kendall_corregido,
    recta,
    rho_ar1,
    tendencia,
    theil_sen,
)
from tests.sinteticas import ar1, generador, serie

# Repeticiones por lote, con generadores distintos para cada prueba.
_BASE_RECUPERACION = 1000
_BASE_SIN_TENDENCIA = 2000
_BASE_AR1_FUERTE = 3000
_BASE_POTENCIA = 4000
_BASE_COHERENCIA = 5000


def _ruido_ar1(i, n=480, rho=0.3):
    return ar1(n, rho, 1.0, generador(i))


# ---------------------------------------------------------------- C4 Theil-Sen


def test_theil_sen_pendientes_ordenadas_y_mediana_a_mano():
    y = np.array([1.0, 3.0, 2.0, 5.0])
    pendientes, mediana = theil_sen(y)
    # Pares (i<j): (3-1)/1, (2-1)/2, (5-1)/3, (2-3)/1, (5-3)/2, (5-2)/1
    esperadas = np.sort([2.0, 0.5, 4 / 3, -1.0, 1.0, 3.0])
    np.testing.assert_allclose(pendientes, esperadas)
    assert mediana == pytest.approx(np.median(esperadas))


def test_theil_sen_recta_exacta():
    y = 2.5 + 0.1 * np.arange(50)
    pendientes, mediana = theil_sen(y)
    assert pendientes.size == 50 * 49 // 2
    assert mediana == pytest.approx(0.1)


# ------------------------------------------- C5–C6 Mann-Kendall con AR(1)


def _var0(n):
    return n * (n - 1) * (2 * n + 5) / 18


def _rho_esperado(y):
    """ρ₁ de los residuos de Theil-Sen con la corrección de sesgo de Marriott-Pope."""
    _, b = theil_sen(y)
    e = y - b * np.arange(y.size)
    e = e - e.mean()
    rho = (e[:-1] * e[1:]).sum() / (e * e).sum()
    rho = rho + (1 + 4 * rho) / y.size
    return min(max(rho, 0.0), RHO_MAX_AR1)


def test_mann_kendall_s_y_varianza_ar1_a_mano():
    y = _ruido_ar1(7, n=240) + 0.02 * np.arange(240)
    s, var_s, z, p = mann_kendall_corregido(y)
    i, j = np.triu_indices(240, 1)
    assert s == pytest.approx(np.sign(y[j] - y[i]).sum())
    rho = _rho_esperado(y)
    assert var_s == pytest.approx(_var0(240) * (1 + rho) / (1 - rho))
    assert z == pytest.approx((s - np.sign(s)) / np.sqrt(var_s))
    from scipy.stats import norm

    assert p == pytest.approx(2 * norm.sf(abs(z)))


def test_rho_ar1_corrige_el_sesgo_y_se_acota():
    y = _ruido_ar1(8, n=240, rho=0.5)
    assert rho_ar1(y) == pytest.approx(_rho_esperado(y))
    onda_lenta = np.sin(2 * np.pi * np.arange(240) / 400)  # ρ̂ ≈ 1 tras quitar la recta
    assert rho_ar1(onda_lenta) == pytest.approx(RHO_MAX_AR1)


def test_varianza_usada_nunca_menor_que_la_sin_corregir():
    """Con autocorrelación negativa o nula, ρ se acota en 0: la corrección nunca achica."""
    alterna = np.array([(-1.0) ** k for k in range(200)]) + 0.001 * np.arange(200)
    assert rho_ar1(alterna) == 0.0
    for i in range(60):
        y = _ruido_ar1(_BASE_SIN_TENDENCIA + i, n=240, rho=0.0)
        _, var_s, _, _ = mann_kendall_corregido(y)
        assert var_s >= _var0(y.size)
        assert tendencia(y).var_s >= _var0(y.size)


def test_pendiente_dada_evita_recalcular_theil_sen():
    y = _ruido_ar1(11, n=200) + 0.01 * np.arange(200)
    _, b = theil_sen(y)
    assert mann_kendall_corregido(y, pendiente_mes=b) == pytest.approx(mann_kendall_corregido(y))


# ------------------------------------------------------------ C7 y resultado


def test_resultado_campos_y_unidades():
    y = _ruido_ar1(3, n=300) + 0.01 * np.arange(300)
    res = tendencia(y)
    assert isinstance(res, ResultadoTendencia)
    _, mediana = theil_sen(y)
    assert res.n == 300
    assert res.pendiente_mes == pytest.approx(mediana)
    assert res.pendiente_decada == pytest.approx(mediana * ESCALA_DECADA)
    assert res.ic_bajo <= res.pendiente_decada <= res.ic_alto
    assert res.intercepto == pytest.approx(np.median(y - mediana * np.arange(300)))
    with pytest.raises(AttributeError):
        res.p = 0.5  # inmutable


def test_ic_por_rangos_con_la_misma_varianza_que_el_p():
    y = _ruido_ar1(5, n=240) + 0.01 * np.arange(240)
    from scipy.stats import norm

    pendientes, _ = theil_sen(y)
    _, var_s, _, _ = mann_kendall_corregido(y)
    N = pendientes.size
    C = norm.ppf(1 - ALFA / 2) * np.sqrt(var_s)
    bajo = pendientes[int(max(round((N - C) / 2) - 1, 0))]
    alto = pendientes[int(min(round((N + C) / 2), N - 1))]
    res = tendencia(y)
    assert res.ic_bajo == pytest.approx(bajo * ESCALA_DECADA)
    assert res.ic_alto == pytest.approx(alto * ESCALA_DECADA)


def test_coherencia_ic_y_p_sin_contradicciones():
    """Corrección C8: el IC excluye el 0 si y solo si p < 0.05 (0 % de contradicciones)."""
    contradicciones = []
    for i in range(300):
        rng = generador(_BASE_COHERENCIA + i)
        beta = (0.0, 0.05, 0.1, 0.2, 0.4)[i % 5]
        rho = (0.0, 0.3, 0.6, 0.9)[i % 4]
        n = (120, 240, 480)[i % 3]
        y = ar1(n, rho, 1.0, rng) + beta / ESCALA_DECADA * np.arange(n)
        res = tendencia(y)
        excluye = res.ic_bajo > 0 or res.ic_alto < 0
        if excluye != (res.p < ALFA):
            contradicciones.append((i, res))
    assert contradicciones == []


@pytest.mark.parametrize("rho", [0.0, 0.3, 0.6])
def test_recuperacion_ic_contiene_pendiente_verdadera(rho):
    """El IC contiene la pendiente verdadera en ≥ 95 % de las repeticiones (guía §13).

    Con ruido blanco y con ruido AR(1) ρ = 0,3 y 0,6, 480 meses, 300 repeticiones.
    Con Hamed-Rao de pymannkendall la cobertura con AR(1) se quedaba en 92–93 %;
    la varianza AR(1) con corrección de sesgo (VERSION_METODO = 3) la lleva al 95 %.
    """
    beta = 0.5
    aciertos = 0
    total = 300
    for i in range(total):
        s = serie(
            generador(_BASE_RECUPERACION + i),
            n=480,
            beta_dec=beta,
            rho_ruido=rho,
            amplitud_estacional=0.0,
        )
        res = tendencia(s.valores)
        aciertos += res.ic_bajo <= beta <= res.ic_alto
    assert aciertos / total >= 0.95


def test_sin_tendencia_tasa_cercana_a_cinco_por_ciento():
    total = 300
    rechazos = sum(tendencia(_ruido_ar1(_BASE_SIN_TENDENCIA + i)).p < ALFA for i in range(total))
    assert 0.01 <= rechazos / total <= 0.10


def _sin_indice(valores, indice):
    """Andamio: regresión conjunta tendencia + índice (rezago 0) y resta de γ̂·(E − Ē)."""
    e = indice - indice.mean()
    t = np.arange(valores.size)
    x = np.column_stack([np.ones_like(e), t, e])
    gamma = np.linalg.lstsq(x, valores, rcond=None)[0][2]
    return valores - gamma * e


def test_falsos_positivos_ar1_fuerte_no_pasan_de_diez_por_ciento():
    total = 300
    rechazos_original = 0
    rechazos_limpia = 0
    for i in range(total):
        s = serie(
            generador(_BASE_AR1_FUERTE + i),
            n=240,
            gamma=1.0,
            rho_indice=0.93,
            amplitud_estacional=0.0,
        )
        rechazos_original += tendencia(s.valores).p < ALFA
        rechazos_limpia += tendencia(_sin_indice(s.valores, s.indice)).p < ALFA
    assert rechazos_limpia / total <= 0.10
    assert rechazos_limpia < rechazos_original


def test_potencia_razonable():
    total = 200
    detecciones = 0
    for i in range(total):
        s = serie(generador(_BASE_POTENCIA + i), n=480, beta_dec=0.5, amplitud_estacional=0.0)
        res = tendencia(s.valores)
        detecciones += res.p < ALFA and res.pendiente_decada > 0
    assert detecciones / total >= 0.80


def test_paridad_con_motor_del_preparador():
    """Misma pendiente que el motor anterior; IC nunca más estrecho y p nunca menor (L14)."""
    motor = pytest.importorskip("verascope_datos.motor")
    for i in range(20):
        s = serie(generador(9000 + i), n=360, beta_dec=0.1 * (i % 5), gamma=0.8, rezago=2)
        ref = motor.tendencia(s.valores)
        res = tendencia(s.valores)
        assert res.pendiente_decada == pytest.approx(ref["pendiente_dec"], rel=1e-12, abs=1e-12)
        assert res.ic_bajo <= ref["ic"][0]
        assert res.ic_alto >= ref["ic"][1]
        assert res.p >= ref["p"]


# ------------------------------------------------- cambio total y porcentual


def test_cambio_total_es_pendiente_mes_por_n_menos_uno():
    assert cambio_total(0.02, 540) == pytest.approx(0.02 * 539)
    assert cambio_total(-0.5, 120) == pytest.approx(-0.5 * 119)


def test_cambio_pct_nunca_en_temperatura():
    assert cambio_pct_decada(0.3, 25.0, "T2M") is None


@pytest.mark.parametrize("variable", ["PRECTOTCORR", "GWETROOT", "GWETTOP", "RH2M"])
def test_cambio_pct_relativo_a_la_referencia(variable):
    assert cambio_pct_decada(0.2, 4.0, variable) == pytest.approx(5.0)
    assert cambio_pct_decada(-0.1, 0.5, variable) == pytest.approx(-20.0)


@pytest.mark.parametrize("referencia", [0.0, -1.0, float("nan")])
def test_cambio_pct_sin_promedio_positivo_es_none(referencia):
    assert cambio_pct_decada(0.2, referencia, "PRECTOTCORR") is None


# ------------------------------------------------------------------- recta


def test_recta_largo_total_con_none_delante():
    y = 1.0 + 0.05 * np.arange(200) + _ruido_ar1(21, n=200) * 0.1
    res = tendencia(y)
    linea = recta(res, n_total=203, inicio=3)
    assert len(linea) == 203
    assert linea[:3] == [None, None, None]
    assert all(isinstance(v, float) for v in linea[3:])
    t = np.arange(200)
    np.testing.assert_allclose(linea[3:], res.intercepto + res.pendiente_mes * t)


def test_recta_sin_rezago_no_tiene_none():
    res = tendencia(_ruido_ar1(22, n=150))
    linea = recta(res, n_total=150, inicio=0)
    assert len(linea) == 150 and None not in linea


def test_recta_rechaza_largos_incoherentes():
    res = tendencia(_ruido_ar1(23, n=150))
    with pytest.raises(ValueError):
        recta(res, n_total=150, inicio=3)


# ------------------------------------------------------------- rendimiento


@pytest.mark.lento
def test_rendimiento_540_meses():
    y = serie(generador(31), n=540, beta_dec=0.2, amplitud_estacional=0.0).valores
    tendencia(y)  # calentar
    inicio = time.perf_counter()
    tendencia(y)
    tendencia(y)  # original y sin El Niño
    assert (time.perf_counter() - inicio) * 1000 < 150
