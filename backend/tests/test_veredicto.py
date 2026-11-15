"""Veredicto de cuatro estados, dirección y avisos (cálculos C12 y C13)."""

import numpy as np
import pytest

from app.contracts import CodigoAviso, Direccion, EstadoVeredicto
from app.estadistica import veredicto
from app.estadistica.constantes import (
    ALFA,
    AVISO_POTENCIA_MESES,
    COLINEALIDAD_MAX,
    NEFF_MIN_PRUEBA_T,
)

TABLA = [
    (True, True, "cambio_robusto"),
    (True, False, "sensible_a_el_nino"),
    (False, True, "cambio_oculto"),
    (False, False, "sin_tendencia"),
]

# Valores tranquilos: ningún aviso salta con ellos.
SIN_AVISO = {"meses_analizados": 540, "colinealidad": 0.1, "n_efectivo": 50.0}


@pytest.mark.parametrize(("orig", "sin", "esperado"), TABLA)
def test_estado_escalar_tabla_completa(orig, sin, esperado):
    resultado = veredicto.estado(orig, sin)
    assert resultado == esperado
    assert type(resultado) is str
    assert resultado in {e.value for e in EstadoVeredicto}


def test_estado_vectorizado_tabla_completa():
    orig = np.array([fila[0] for fila in TABLA])
    sin = np.array([fila[1] for fila in TABLA])
    resultado = veredicto.estado(orig, sin)
    assert isinstance(resultado, np.ndarray)
    assert resultado.tolist() == [fila[2] for fila in TABLA]


def test_estados_iguales_al_contrato():
    assert set(veredicto.ESTADOS) == {e.value for e in EstadoVeredicto}


@pytest.mark.parametrize(("orig", "sin", "esperado"), TABLA)
def test_paridad_estado_con_el_preparador(orig, sin, esperado):
    motor = pytest.importorskip("verascope_datos.motor")
    assert veredicto.estado(orig, sin) == motor.veredicto(orig, sin) == esperado


def test_significativa_usa_alfa_estricto_y_nan_no_es_significativo():
    assert ALFA == 0.05
    assert veredicto.significativa(0.049) is True
    assert veredicto.significativa(0.05) is False
    assert veredicto.significativa(float("nan")) is False
    assert veredicto.significativa(0.08, alfa=0.1) is True
    resultado = veredicto.significativa(np.array([0.01, 0.05, np.nan, 0.2]))
    assert resultado.tolist() == [True, False, False, False]


@pytest.mark.parametrize(
    ("pendiente", "sig", "esperado"),
    [
        (0.3, True, "sube"),
        (-0.3, True, "baja"),
        (0.3, False, "plana"),
        (-0.3, False, "plana"),
        (0.0, True, "plana"),
        (float("nan"), True, "plana"),
    ],
)
def test_direccion_escalar(pendiente, sig, esperado):
    resultado = veredicto.direccion(pendiente, sig)
    assert resultado == esperado
    assert type(resultado) is str
    assert resultado in {d.value for d in Direccion}


def test_direccion_vectorizada():
    resultado = veredicto.direccion(
        np.array([0.3, -0.3, 0.3, -0.3]), np.array([True, True, False, False])
    )
    assert resultado.tolist() == ["sube", "baja", "plana", "plana"]


def test_sin_avisos_con_valores_tranquilos():
    assert veredicto.avisos(**SIN_AVISO) == []


@pytest.mark.parametrize(("valor", "salta"), [(0.3, False), (0.31, True), (-0.31, True)])
def test_aviso_colinealidad_en_su_limite(valor, salta):
    assert COLINEALIDAD_MAX == 0.3
    codigos = [c for c, _ in veredicto.avisos(**{**SIN_AVISO, "colinealidad": valor})]
    assert codigos == (["colinealidad"] if salta else [])


@pytest.mark.parametrize(("meses", "salta"), [(239, True), (240, False)])
def test_aviso_potencia_en_su_limite(meses, salta):
    assert AVISO_POTENCIA_MESES == 240
    codigos = [c for c, _ in veredicto.avisos(**{**SIN_AVISO, "meses_analizados": meses})]
    assert codigos == (["potencia_baja"] if salta else [])


@pytest.mark.parametrize(
    ("n_e", "salta"), [(NEFF_MIN_PRUEBA_T - 0.1, True), (float(NEFF_MIN_PRUEBA_T), False)]
)
def test_aviso_muestra_efectiva_en_su_limite(n_e, salta):
    codigos = [c for c, _ in veredicto.avisos(**{**SIN_AVISO, "n_efectivo": n_e})]
    assert codigos == (["muestra_efectiva_baja"] if salta else [])


def test_avisos_valores_ausentes_no_inventan_avisos():
    assert veredicto.avisos(540, float("nan"), float("nan")) == []
    assert veredicto.avisos(540, None, None) == []


def test_avisos_todos_juntos_codigos_del_contrato_y_textos_honestos():
    lista = veredicto.avisos(meses_analizados=200, colinealidad=-0.5, n_efectivo=4.0)
    codigos = [c for c, _ in lista]
    assert codigos == ["colinealidad", "potencia_baja", "muestra_efectiva_baja"]
    contrato = {a.value for a in CodigoAviso}
    for codigo, texto in lista:
        assert codigo in contrato
        assert type(codigo) is str and isinstance(texto, str) and texto.strip()
        minusculas = texto.lower()
        for prohibida in ("causa", "causó", "provoca", "provocó", "debido a"):
            assert prohibida not in minusculas


def test_no_implementa_avisos_sin_regla_numerica():
    # L13: respuesta_no_lineal, nino_costero y fuera_de_rejilla no salen de aquí.
    lista = veredicto.avisos(meses_analizados=10, colinealidad=0.99, n_efectivo=0.0)
    codigos = {c for c, _ in lista}
    assert not codigos & {"respuesta_no_lineal", "nino_costero", "fuera_de_rejilla"}


def test_docstrings_citan_el_calculo():
    assert "C13" in veredicto.estado.__doc__
    assert "C13" in veredicto.direccion.__doc__
    assert "C13" in veredicto.significativa.__doc__
    assert "C12" in veredicto.avisos.__doc__
