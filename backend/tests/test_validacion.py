"""Pruebas de app/datos/validacion.py: calidad y ventana (sección 13, filas Calidad y Ventana)."""

import numpy as np
import pytest

from app.datos.validacion import (
    Calidad,
    limpiar,
    rellenar_huecos,
    validar_serie,
    validar_ventana,
)
from app.estadistica.constantes import (
    AVISO_POTENCIA_MESES,
    MAX_FALTANTE,
    MAX_HUECO,
    MIN_MESES,
)
from tests.sinteticas import FALTANTE_POWER, con_huecos, generador, serie

N = 480


def _valores(n=N, repeticion=0):
    return serie(generador(repeticion), n=n, beta_dec=0.3).valores


# --- -999 y rellenos --------------------------------------------------------


def test_limpiar_pasa_menos_999_a_nan_y_no_toca_lo_demas():
    v = np.array([1.5, FALTANTE_POWER, -12.0, -999.0, 0.0])
    limpio = limpiar(v)
    assert np.isnan(limpio[[1, 3]]).all()
    assert limpio[[0, 2, 4]].tolist() == [1.5, -12.0, 0.0]
    assert v[1] == FALTANTE_POWER  # no modifica la entrada


def test_validar_serie_enmascara_menos_999_antes_de_interpolar():
    v = con_huecos(_valores(), 100, 1, relleno=FALTANTE_POWER)
    cal = validar_serie(v, "T2M")
    assert cal.motivo is None
    assert not (cal.valores <= -998).any()
    assert np.isfinite(cal.valores).all()
    assert cal.valores[100] == pytest.approx((v[99] + v[101]) / 2)
    assert cal.faltante == pytest.approx(1 / N)


# --- Huecos -------------------------------------------------------------------


@pytest.mark.parametrize("largo", [1, MAX_HUECO])
def test_huecos_de_uno_y_dos_meses_se_interpolan(largo):
    original = _valores()
    v = con_huecos(original, 200, largo)
    cal = validar_serie(v, "PRECTOTCORR")
    assert isinstance(cal, Calidad)
    assert cal.motivo is None
    esperado = np.interp(np.arange(200, 200 + largo), [199, 200 + largo], v[[199, 200 + largo]])
    assert np.allclose(cal.valores[200 : 200 + largo], esperado)
    assert np.array_equal(
        np.delete(cal.valores, range(200, 200 + largo)),
        np.delete(original, range(200, 200 + largo)),
    )


def test_hueco_de_tres_meses_descarta_la_serie():
    v = con_huecos(_valores(), 200, MAX_HUECO + 1)
    cal = validar_serie(v, "RH2M")
    assert cal.valores is None
    assert cal.motivo == "hueco_largo"
    assert rellenar_huecos(v) is None


def test_mas_de_diez_por_ciento_faltante_descarta_aunque_los_huecos_sean_cortos():
    v = _valores()
    # Huecos de 1 mes cada 9 meses: ningún hueco largo, pero > 10 % faltante.
    v[::9] = np.nan
    assert np.isnan(v).mean() > MAX_FALTANTE
    cal = validar_serie(v, "T2M")
    assert cal.valores is None
    assert cal.motivo == "faltante_excesivo"
    assert cal.faltante == pytest.approx(np.isnan(v).mean())


def test_exactamente_diez_por_ciento_faltante_en_huecos_cortos_se_acepta():
    v = _valores()
    v[::10] = np.nan  # 48 de 480 = 10 %
    assert np.isnan(v).mean() == pytest.approx(MAX_FALTANTE)
    cal = validar_serie(v, "T2M")
    assert cal.motivo is None
    assert np.isfinite(cal.valores).all()


def test_rellenar_huecos_sin_faltantes_devuelve_copia_igual():
    v = _valores()
    r = rellenar_huecos(v)
    assert r is not v
    assert np.array_equal(r, v)


# --- Desviación nula ----------------------------------------------------------


def test_serie_constante_se_descarta_por_desviacion_nula():
    cal = validar_serie(np.full(N, 25.0), "T2M")
    assert cal.valores is None
    assert cal.motivo == "serie_constante"


# --- Suelo sobre el mar (docs/comprobaciones-b2.md) -----------------------------


def test_gwetroot_todo_menos_999_es_sin_datos_tierra():
    cal = validar_serie(np.full(N, FALTANTE_POWER), "GWETROOT")
    assert cal.valores is None
    assert cal.motivo == "sin_datos_tierra"
    assert cal.faltante == 1.0


def test_gwettop_constante_en_uno_es_sin_datos_tierra():
    cal = validar_serie(np.full(N, 1.0), "GWETTOP")
    assert cal.valores is None
    assert cal.motivo == "sin_datos_tierra"


def test_temperatura_constante_no_se_trata_como_mar():
    cal = validar_serie(np.full(N, 1.0), "T2M")
    assert cal.motivo == "serie_constante"


def test_temperatura_toda_faltante_no_se_trata_como_mar():
    cal = validar_serie(np.full(N, FALTANTE_POWER), "T2M")
    assert cal.motivo == "faltante_excesivo"


def test_humedad_del_suelo_en_tierra_se_acepta():
    v = np.clip(0.5 + 0.1 * _valores(), 0, 1)
    cal = validar_serie(v, "GWETROOT")
    assert cal.motivo is None
    assert np.array_equal(cal.valores, v)


# --- Ventana (9, 10 y 19 años) --------------------------------------------------


def test_ventana_de_nueve_anos_se_rechaza():
    assert validar_ventana(9 * 12) == "ventana_corta"
    cal = validar_serie(_valores(9 * 12), "T2M")
    assert cal.valores is None
    assert cal.motivo == "ventana_corta"


def test_ventana_de_diez_anos_se_acepta_con_aviso():
    assert validar_ventana(MIN_MESES) is None
    cal = validar_serie(_valores(10 * 12), "T2M")
    assert cal.motivo is None
    assert cal.valores.size == MIN_MESES
    assert cal.aviso_potencia is True


def test_ventana_de_diecinueve_anos_se_acepta_con_aviso_de_potencia():
    assert validar_ventana(19 * 12) is None
    cal = validar_serie(_valores(19 * 12), "T2M")
    assert cal.motivo is None
    assert cal.aviso_potencia is True


def test_ventana_de_veinte_anos_no_lleva_aviso():
    assert validar_ventana(AVISO_POTENCIA_MESES) is None
    cal = validar_serie(_valores(AVISO_POTENCIA_MESES), "T2M")
    assert cal.motivo is None
    assert cal.aviso_potencia is False


# --- Una sola implementación ----------------------------------------------------


def test_modulo_no_importa_fastapi():
    import ast

    import app.datos.validacion as validacion

    with open(validacion.__file__, encoding="utf-8") as f:
        arbol = ast.parse(f.read())
    modulos = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos.update(a.name.split(".")[0] for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            modulos.add(nodo.module.split(".")[0])
    assert "fastapi" not in modulos


def test_el_preparador_usa_la_misma_rellenar_huecos():
    motor = pytest.importorskip("verascope_datos.motor")
    assert motor.rellenar_huecos is rellenar_huecos
