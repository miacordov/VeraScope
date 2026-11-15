"""Pruebas de app/estadistica/celda.py: `analizar_celda`, la implementación única (guía §7–§8).

Series sintéticas con semilla fija (tests/sinteticas.py); ninguna toca la red. Las cifras
son de simulaciones y no se citan como resultados de la plataforma.

No se compara contra el motor viejo del preparador: el método cambió (mismos meses para las
dos tendencias, L13; varianza de L14; `VERSION_METODO = 2`). En su lugar se comprueba que
cada número sale de las funciones de `app.estadistica` sobre los mismos meses.
"""

import dataclasses
import json
import time

import numpy as np
import pytest

from app.estadistica.anomalias import estandarizar, preparar
from app.estadistica.celda import ResultadoCelda, analizar_celda
from app.estadistica.constantes import ALFA, MIN_MESES
from app.estadistica.enso import quitar_enso
from app.estadistica.fdr import benjamini_hochberg
from app.estadistica.tendencia import cambio_pct_decada, cambio_total, recta, tendencia
from app.estadistica.veredicto import estado
from tests.sinteticas import ar1, con_huecos, generador, serie

N = 540
COLUMNAS_ESCANEO = {
    "pendiente_original",
    "p_original",
    "pendiente",
    "ic_bajo",
    "ic_alto",
    "p",
    "rezago",
    "r_enso",
    "p_enso",
    "colinealidad",
    "efecto",
    "meses",
    "n_efectivo",
}


def _calendario(n=N):
    return np.arange(n) % 12 + 1


def _con_indice_con_rampa(semilla, pendiente_indice, beta_dec, n=N):
    """Índice con rampa propia: la tendencia viaja con El Niño (o lo contrario).

    valor_t = 10 + ciclo + β·t + 1.5·E_t + ruido, con E_t = AR(1) + rampa.
    """
    rng = generador(semilla)
    t = np.arange(n)
    cal = _calendario(n)
    e = ar1(n, 0.9, 1.0, rng) + pendiente_indice * t / n
    v = 10 + np.sin(2 * np.pi * (cal - 1) / 12) + beta_dec / 120 * t + 1.5 * e
    return v + ar1(n, 0.3, 1.0, rng), cal, e


def _caso(nombre):
    if nombre == "cambio_robusto":
        s = serie(generador(100), n=N, beta_dec=0.6, gamma=0.8, rezago=2)
        return s.valores + 10, s.meses_calendario, s.indice
    if nombre == "sensible_a_el_nino":
        # La rampa viene solo del índice: al quitar El Niño no queda tendencia.
        return _con_indice_con_rampa(200, pendiente_indice=2.0, beta_dec=0.0)
    if nombre == "cambio_oculto":
        # El índice baja y la variable sube: en la serie original se compensan.
        return _con_indice_con_rampa(300, pendiente_indice=-2.0, beta_dec=0.6)
    s = serie(generador(400), n=N, beta_dec=0.0, gamma=1.0, rezago=3)
    return s.valores + 10, s.meses_calendario, s.indice


# ------------------------------------------------------------------ veredicto


@pytest.mark.parametrize(
    "esperado", ["cambio_robusto", "sensible_a_el_nino", "cambio_oculto", "sin_tendencia"]
)
def test_veredicto_en_casos_claros(esperado):
    v, cal, e = _caso(esperado)
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    assert isinstance(res, ResultadoCelda)
    assert res.veredicto == esperado
    assert res.tendencia_original.significativa == (res.tendencia_original.p < ALFA)
    assert res.tendencia_sin_el_nino.significativa == (res.tendencia_sin_el_nino.p < ALFA)


def test_recupera_el_rezago_conocido():
    s = serie(generador(100), n=N, beta_dec=0.6, gamma=0.8, rezago=2)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "RH2M")
    assert res.vinculo_el_nino.rezago_meses == 2
    assert res.vinculo_el_nino.r > 0
    assert res.vinculo_el_nino.indicativo is True
    assert res.vinculo_el_nino.n_efectivo > 0


def test_direccion_sigue_el_signo_de_cada_pendiente():
    v, cal, e = _caso("cambio_oculto")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    assert res.tendencia_sin_el_nino.direccion == "sube"
    assert res.tendencia_original.direccion == "plana"


# ------------------------------------------------------- mismos meses (C-regla)


@pytest.mark.parametrize("rezago", [0, 3, 6])
def test_las_dos_tendencias_usan_los_mismos_n_menos_rezago_meses(rezago):
    s = serie(generador(500 + rezago), n=N, beta_dec=0.3, gamma=1.2, rezago=rezago)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "GWETTOP")
    ell = res.rezago
    assert ell == rezago
    assert res.meses == N
    assert res.meses_analizados == N - ell
    a = preparar(s.valores, s.meses_calendario)
    en = quitar_enso(a, s.indice)
    orig = tendencia(a[ell:])
    sin = tendencia(en.limpia[ell:])
    assert orig.n == sin.n == N - ell
    assert res.tendencia_original.pendiente_decada == pytest.approx(orig.pendiente_decada)
    assert res.tendencia_original.p == pytest.approx(orig.p)
    # La pendiente sin El Niño coincide con tendencia(limpia[ℓ:]).
    assert res.tendencia_sin_el_nino.pendiente_decada == pytest.approx(sin.pendiente_decada)
    assert res.tendencia_sin_el_nino.ic_bajo == pytest.approx(sin.ic_bajo)
    assert res.tendencia_sin_el_nino.ic_alto == pytest.approx(sin.ic_alto)
    assert res.tendencia_sin_el_nino.p == pytest.approx(sin.p)


def test_series_tienen_largo_n_y_nan_antes_del_rezago():
    s = serie(generador(600), n=N, beta_dec=0.3, gamma=1.0, rezago=4)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "PRECTOTCORR")
    ell = res.rezago
    assert ell == 4
    for serie_ in (res.serie_original, res.serie_sin_el_nino, res.serie_z):
        assert len(serie_) == N
    assert np.isnan(res.serie_sin_el_nino[:ell]).all()
    assert np.isfinite(res.serie_sin_el_nino[ell:]).all()
    assert np.isfinite(res.serie_original).all()
    a = preparar(s.valores, s.meses_calendario)
    np.testing.assert_allclose(res.serie_original, a)
    np.testing.assert_allclose(res.serie_z, estandarizar(a))


def test_rectas_con_none_antes_del_rezago():
    s = serie(generador(601), n=N, beta_dec=0.3, gamma=1.0, rezago=5)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "PRECTOTCORR")
    ell = res.rezago
    assert ell == 5
    a = preparar(s.valores, s.meses_calendario)
    esperada = recta(tendencia(a[ell:]), N, ell)
    for t in (res.tendencia_original, res.tendencia_sin_el_nino):
        assert len(t.recta) == N
        assert t.recta[:ell] == [None] * ell
        assert all(x is not None for x in t.recta[ell:])
    assert res.tendencia_original.recta == pytest.approx(esperada)


def test_cambio_total_sobre_los_meses_analizados():
    s = serie(generador(602), n=N, beta_dec=0.5, gamma=1.0, rezago=2)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "RH2M")
    a = preparar(s.valores, s.meses_calendario)
    orig = tendencia(a[res.rezago :])
    assert res.tendencia_original.cambio_total == pytest.approx(
        cambio_total(orig.pendiente_mes, N - res.rezago)
    )


# ------------------------------------------------------------ cambio porcentual


def test_cambio_pct_nunca_en_temperatura():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(v, cal, e, "T2M")
    assert res.tendencia_original.cambio_pct_decada is None
    assert res.tendencia_sin_el_nino.cambio_pct_decada is None


def test_cambio_pct_sobre_la_climatologia_bruta_de_la_celda():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    referencia = float(np.mean(v))
    for t in (res.tendencia_original, res.tendencia_sin_el_nino):
        assert t.cambio_pct_decada == pytest.approx(
            cambio_pct_decada(t.pendiente_decada, referencia, "PRECTOTCORR")
        )


def test_cambio_pct_ignora_rellenos_de_power_en_la_referencia():
    v, cal, e = _caso("cambio_robusto")
    v = con_huecos(v, 100, 2, relleno=-999.0)
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    referencia = float(np.mean(np.delete(v, [100, 101])))
    assert res.tendencia_original.cambio_pct_decada == pytest.approx(
        cambio_pct_decada(res.tendencia_original.pendiente_decada, referencia, "PRECTOTCORR")
    )


# ------------------------------------------------------------------- descarte


def test_hueco_largo_descarta():
    v, cal, e = _caso("cambio_robusto")
    assert analizar_celda(con_huecos(v, 50, 3), cal, e, "PRECTOTCORR") is None


def test_hueco_corto_se_interpola_y_se_analiza():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(con_huecos(v, 50, 2, relleno=-999.0), cal, e, "PRECTOTCORR")
    assert res is not None and np.isfinite(res.serie_original).all()


def test_ventana_corta_descarta():
    s = serie(generador(700), n=MIN_MESES - 1, beta_dec=0.5)
    assert analizar_celda(s.valores, s.meses_calendario, s.indice, "T2M") is None


def test_serie_constante_descarta():
    s = serie(generador(701), n=N)
    assert analizar_celda(np.full(N, 3.0), s.meses_calendario, s.indice, "RH2M") is None


# ------------------------------------------------------------- avisos y vínculo


def test_avisos_y_colinealidad():
    v, cal, e = _caso("sensible_a_el_nino")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    en = quitar_enso(preparar(v, cal), e)
    assert res.colinealidad == pytest.approx(en.colinealidad)
    codigos = [c for c, _ in res.avisos]
    assert ("colinealidad" in codigos) == (abs(res.colinealidad) > 0.3)
    assert "potencia_baja" not in codigos


def test_aviso_potencia_baja_con_menos_de_240_meses():
    s = serie(generador(702), n=180, beta_dec=0.5, gamma=1.0, rezago=1)
    res = analizar_celda(s.valores, s.meses_calendario, s.indice, "RH2M")
    assert "potencia_baja" in [c for c, _ in res.avisos]
    assert all(isinstance(t, str) and t for _, t in res.avisos)


def test_vinculo_significativo_con_alfa():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    vin = res.vinculo_el_nino
    assert vin.significativo == (vin.p < ALFA)


def test_resultado_es_inmutable():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    with pytest.raises(dataclasses.FrozenInstanceError):
        res.veredicto = "otro"


# -------------------------------------------------------------- fila de escaneo


def test_fila_escaneo_tiene_las_columnas_de_resultados_parquet():
    v, cal, e = _caso("cambio_robusto")
    res = analizar_celda(v, cal, e, "PRECTOTCORR")
    fila = res.fila_escaneo()
    assert set(fila) == COLUMNAS_ESCANEO
    assert fila["pendiente"] == res.tendencia_sin_el_nino.pendiente_decada
    assert fila["pendiente_original"] == res.tendencia_original.pendiente_decada
    assert fila["p"] == res.tendencia_sin_el_nino.p
    assert fila["p_original"] == res.tendencia_original.p
    assert fila["rezago"] == res.rezago
    assert fila["r_enso"] == res.vinculo_el_nino.r
    assert fila["p_enso"] == res.vinculo_el_nino.p
    assert fila["n_efectivo"] == res.vinculo_el_nino.n_efectivo
    assert fila["meses"] == N
    a = preparar(v, cal)
    assert fila["efecto"] == pytest.approx(fila["pendiente"] / float(np.std(a)))
    # Escalares de Python: se serializan sin sorpresas.
    json.dumps(fila)
    assert isinstance(fila["rezago"], int) and isinstance(fila["meses"], int)


def test_docstring_cita_los_calculos():
    for c in ("C3", "C4", "C9", "C10", "C11", "C12", "C13"):
        assert c in analizar_celda.__doc__


# ------------------------------------------------------- preparador redirigido


def test_el_preparador_usa_la_implementacion_unica():
    motor = pytest.importorskip("verascope_datos.motor")
    from app.datos.validacion import rellenar_huecos
    from app.estadistica import anomalias as mod_anomalias
    from app.estadistica import fdr, veredicto

    assert motor.anomalias is mod_anomalias.anomalias
    assert motor.fdr is fdr.benjamini_hochberg
    assert motor.veredicto is veredicto.estado
    assert motor.rellenar_huecos is rellenar_huecos
    assert motor.ALFA == ALFA and motor.MIN_MESES == MIN_MESES
    v, cal, e = _caso("cambio_robusto")
    assert motor.analizar(v, e, cal) == analizar_celda(v, cal, e, "PRECTOTCORR").fila_escaneo()
    assert motor.analizar(con_huecos(v, 0, 3), e, cal) is None


def test_motor_tendencia_conserva_su_forma_de_diccionario():
    motor = pytest.importorskip("verascope_datos.motor")
    s = serie(generador(703), n=360, beta_dec=0.4)
    ref = motor.tendencia(s.valores)
    res = tendencia(s.valores)
    assert ref == {
        "pendiente_dec": res.pendiente_decada,
        "ic": (res.ic_bajo, res.ic_alto),
        "p": res.p,
    }


def test_calcular_agrega_p_enso_ajustado_por_variable(tmp_path):
    pytest.importorskip("verascope_datos.calcular")
    import pandas as pd

    from verascope_datos import calcular, config

    rutas = config.rutas(tmp_path / "datos")
    meses = [f"{1981 + k // 12}-{k % 12 + 1:02d}" for k in range(240)]
    (rutas.tabla / "meses.json").write_text(json.dumps(meses))
    np.save(rutas.tabla / "celdas.npy", np.array([[0, 0], [0, 2], [2, 0], [2, 2]], np.float32))
    oni = ar1(240, 0.9, 1.0, generador(800))
    np.save(rutas.tabla / "ONI.npy", oni)
    for j, cod in enumerate(("PRECTOTCORR", "T2M")):
        filas = []
        for k in range(4):
            s = serie(generador(810 + 10 * j + k), n=240, beta_dec=0.8 * k)
            filas.append(s.valores + 10 + (k + 1) * 0.4 * oni)
        np.save(rutas.tabla / f"{cod}.npy", np.array(filas, np.float32))
    df = calcular.calcular_resultados(rutas, procesos=1)
    assert len(df) == 8
    assert {"p_enso_ajustado", "p_ajustado", "p_original_ajustado", "n_efectivo"} <= set(df)
    for _, g in df.groupby("variable"):
        np.testing.assert_allclose(g.p_enso_ajustado, benjamini_hochberg(g.p_enso.to_numpy()))
    np.testing.assert_allclose(df.p_ajustado, benjamini_hochberg(df.p.to_numpy()))
    np.testing.assert_allclose(df.p_original_ajustado, benjamini_hochberg(df.p_original.to_numpy()))
    esperado = estado(df.p_original_ajustado < ALFA, df.p_ajustado < ALFA)
    assert df.veredicto.tolist() == list(esperado)
    assert pd.read_parquet(rutas.resultados).shape == df.shape


# ----------------------------------------------------------------- rendimiento


@pytest.mark.lento
def test_rendimiento_por_celda_con_540_meses():
    v, cal, e = _caso("cambio_robusto")
    analizar_celda(v, cal, e, "PRECTOTCORR")  # calentamiento
    inicio = time.perf_counter()
    for _ in range(5):
        analizar_celda(v, cal, e, "PRECTOTCORR")
    assert (time.perf_counter() - inicio) / 5 < 0.150
