"""Aviso `nino_costero`: Niño 1+2 como índice complementario en la costa norte del Perú.

Decisión de B3 (hora 20, issue #4): el escaneo y el veredicto siguen con el ONI; en la
costa norte del Perú, si Niño 1+2 explica mejor la serie, `analyze` lo avisa y ofrece
ese índice. El aviso no cambia ningún número del veredicto.
"""

import numpy as np
import pytest

from app.contracts import CodigoAviso
from app.estadistica.constantes import ALFA, COSTA_NINO12_LAT, COSTA_NINO12_LON
from app.estadistica.costero import (
    AVISO_COSTERO,
    AVISO_NO_LINEAL,
    aviso_nino_costero,
    aviso_respuesta_no_lineal,
    en_costa_nino12,
)
from app.estadistica.enso import quitar_enso
from tests.sinteticas import ar1, generador

N = 480
PIURA = (-5.0, -80.5)


def _indices(semilla=0):
    rng = generador(5000 + semilla)
    return ar1(N, 0.93, 1.0, rng), ar1(N, 0.85, 1.0, rng)


def _serie(indice, gamma, semilla=0):
    return gamma * indice + ar1(N, 0.3, 1.0, generador(6000 + semilla))


def test_el_codigo_es_el_del_contrato():
    assert AVISO_COSTERO == CodigoAviso.COSTERO.value


def test_piura_esta_en_la_costa_y_lima_jakarta_no():
    assert en_costa_nino12(*PIURA)
    assert en_costa_nino12(-6.0, -80.0)  # celda de ScanMap más cercana a Piura
    assert not en_costa_nino12(-12.0, -77.0)  # Lima
    assert not en_costa_nino12(-6.2, 106.8)  # Yakarta
    lat0, lat1 = COSTA_NINO12_LAT
    lon0, lon1 = COSTA_NINO12_LON
    assert en_costa_nino12(lat0, lon0) and en_costa_nino12(lat1, lon1)  # bordes incluidos


@pytest.mark.parametrize("semilla", range(5))
def test_avisa_si_nino12_explica_mejor_la_serie(semilla):
    oni, n12 = _indices(semilla)
    a = _serie(n12, 0.8, semilla)
    aviso = aviso_nino_costero(*PIURA, a, oni, n12)
    assert aviso is not None
    codigo, texto = aviso
    assert codigo == AVISO_COSTERO
    assert "Niño 1+2" in texto and "ONI" in texto
    r_n12 = quitar_enso(a, n12).r
    assert f"{abs(r_n12):.2f}" in texto  # el número sale del cálculo, no se inventa


@pytest.mark.parametrize("semilla", range(5))
def test_no_avisa_si_el_oni_explica_mejor(semilla):
    oni, n12 = _indices(semilla)
    assert aviso_nino_costero(*PIURA, _serie(oni, 0.8, semilla), oni, n12) is None


def test_no_avisa_fuera_de_la_costa():
    oni, n12 = _indices()
    assert aviso_nino_costero(-6.2, 106.8, _serie(n12, 0.8), oni, n12) is None


def test_no_avisa_si_nino12_no_es_significativo():
    oni, n12 = _indices()
    ruido = ar1(N, 0.3, 1.0, generador(6999))
    assert quitar_enso(ruido, n12).p >= ALFA
    assert aviso_nino_costero(*PIURA, ruido, oni, n12) is None


def test_usa_solo_los_meses_comunes():
    # Niño 1+2 empieza en 1982: los primeros 12 meses llegan como NaN y se descartan.
    oni, n12 = _indices()
    a = _serie(n12, 0.8)
    n12_real = n12.copy()
    n12_real[:12] = np.nan
    a_hueco = a.copy()
    a_hueco[100] = np.nan
    aviso = aviso_nino_costero(*PIURA, a_hueco, oni, n12_real)
    assert aviso is not None
    k = np.isfinite(n12_real) & np.isfinite(a_hueco)
    assert f"{abs(quitar_enso(a[k], n12[k]).r):.2f}" in aviso[1]


def test_no_avisa_sin_meses_suficientes():
    oni, n12 = _indices()
    corto = slice(0, 60)
    assert aviso_nino_costero(*PIURA, _serie(n12, 0.8)[corto], oni[corto], n12[corto]) is None


def test_no_modifica_la_entrada():
    oni, n12 = _indices()
    a = _serie(n12, 0.8)
    copias = [x.copy() for x in (a, oni, n12)]
    aviso_nino_costero(*PIURA, a, oni, n12)
    for original, copia in zip((a, oni, n12), copias):
        np.testing.assert_array_equal(original, copia)


# ------------------------------------------------- respuesta no lineal (C12)


def test_no_lineal_el_codigo_es_el_del_contrato():
    assert AVISO_NO_LINEAL == CodigoAviso.NO_LINEAL.value


def test_no_lineal_avisa_la_lluvia_en_la_costa_norte():
    codigo, texto = aviso_respuesta_no_lineal(*PIURA, "PRECTOTCORR")
    assert codigo == AVISO_NO_LINEAL
    assert "eventos extremos" in texto and "lineal" in texto


@pytest.mark.parametrize("variable", ["T2M", "RH2M", "GWETROOT", "GWETTOP"])
def test_no_lineal_solo_para_la_lluvia(variable):
    assert aviso_respuesta_no_lineal(*PIURA, variable) is None


@pytest.mark.parametrize("lugar", [(-12.0, -77.0), (-6.2, 106.8), (-2.0, 116.0)])
def test_no_lineal_solo_en_la_costa_norte(lugar):
    assert aviso_respuesta_no_lineal(*lugar, "PRECTOTCORR") is None
