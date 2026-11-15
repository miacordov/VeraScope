"""Pruebas de app/datos/indices.py: ONI y Niño 1+2 locales, fases y recorte de ventana."""

import json
import math

import numpy as np
import pytest

from app.datos import indices
from app.estadistica.constantes import UMBRAL_FASE

ONI_TEXTO = """SEAS  YR   TOTAL   ANOM
DJF 1982  26.50   0.10
JFM 1982  26.70  -0.20
FMA 1982  27.00   0.55
NDJ 1982  27.10   1.20
"""

SSTOI_TEXTO = """ YR   MON  NINO1+2  ANOM   NINO3    ANOM   NINO4    ANOM NINO3.4    ANOM
1981   12  24.10   9.99  25.80  0.00  28.30  0.00  26.70  0.00
1982    1  24.10   0.30  25.80  0.00  28.30  0.00  26.70  0.00
1982    2  24.10  -0.70  25.80  0.00  28.30  0.00  26.70  0.00
1982    3  24.10   1.10  25.80  0.00  28.30  0.00  26.70  0.00
"""


def _meses(desde_anio, hasta_anio):
    return [f"{a}-{m:02d}" for a in range(desde_anio, hasta_anio + 1) for m in range(1, 13)]


# --- ONI: temporada de 3 meses al mes central -------------------------------


def test_oni_asigna_cada_temporada_a_su_mes_central():
    meses = ["1982-01", "1982-02", "1982-03", "1982-04", "1982-12"]
    serie = indices.parsear_oni(ONI_TEXTO, meses)
    assert serie.dtype == np.float32
    # DJF → enero, JFM → febrero, FMA → marzo, NDJ → diciembre.
    assert serie[0] == pytest.approx(0.10)
    assert serie[1] == pytest.approx(-0.20)
    assert serie[2] == pytest.approx(0.55)
    assert math.isnan(serie[3])
    assert serie[4] == pytest.approx(1.20)


def test_oni_ignora_encabezado_y_lineas_rotas():
    texto = ONI_TEXTO + "DJF 19x2 26.0 abc\nlinea suelta\n"
    serie = indices.parsear_oni(texto, ["1982-01"])
    assert serie[0] == pytest.approx(0.10)


# --- Niño 1+2: empieza en 1982-01 ------------------------------------------


def test_nino12_empieza_en_1982():
    assert indices.INICIO_NINO12 == "1982-01"
    meses = ["1981-11", "1981-12", "1982-01", "1982-02", "1982-03"]
    serie = indices.parsear_nino12(SSTOI_TEXTO, meses)
    assert serie.dtype == np.float32
    assert math.isnan(serie[0])
    # Aunque el texto traiga 1981-12, antes de 1982-01 no hay Niño 1+2.
    assert math.isnan(serie[1])
    assert serie[2] == pytest.approx(0.30)
    assert serie[3] == pytest.approx(-0.70)
    assert serie[4] == pytest.approx(1.10)


# --- Fases ------------------------------------------------------------------


def test_umbral_de_fase_viene_de_constantes():
    assert UMBRAL_FASE == 0.5


@pytest.mark.parametrize(
    "valor, esperada",
    [
        (0.5, "nino"),
        (np.float32(0.5), "nino"),
        (1.8, "nino"),
        (-0.5, "nina"),
        (np.float32(-0.5), "nina"),
        (-2.0, "nina"),
        (0.49, "neutro"),
        (-0.49, "neutro"),
        (0.0, "neutro"),
    ],
)
def test_fase_en_los_bordes(valor, esperada):
    assert indices.fase(valor) == esperada


def test_fase_sin_indice_es_error():
    with pytest.raises(ValueError, match="sin índice"):
        indices.fase(float("nan"))


def test_fases_de_una_serie():
    serie = np.array([0.5, -0.5, 0.49, -0.49, 1.0], dtype=np.float32)
    assert indices.fases(serie) == ["nino", "nina", "neutro", "neutro", "nino"]


# --- Ventana y recorte al último mes con índice ------------------------------


def test_ventana_valida_va_del_primer_al_ultimo_mes_con_indice():
    indice = np.array([np.nan, 0.1, 0.2, np.nan, 0.3, np.nan, np.nan])
    assert indices.ventana_valida(indice) == (1, 5)


def test_ventana_valida_sin_indice_es_vacia():
    assert indices.ventana_valida(np.full(4, np.nan)) == (0, 0)


def test_recortar_al_ultimo_mes_con_indice():
    meses = ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
    serie = np.arange(6, dtype=float)
    indice = np.array([0.1, 0.2, 0.3, 0.4, np.nan, np.nan])
    m, s, i = indices.recortar(meses, serie, indice)
    assert m == ["2024-07", "2024-08", "2024-09", "2024-10"]
    np.testing.assert_array_equal(s, [0, 1, 2, 3])
    np.testing.assert_array_equal(i, [0.1, 0.2, 0.3, 0.4])


def test_recortar_con_nino12_arranca_en_1982():
    meses = _meses(1981, 1982)
    nino12 = indices.parsear_nino12(SSTOI_TEXTO, meses)
    serie = np.arange(len(meses), dtype=float)
    m, s, i = indices.recortar(meses, serie, nino12)
    assert m == ["1982-01", "1982-02", "1982-03"]
    np.testing.assert_array_equal(s, [12, 13, 14])
    assert np.isfinite(i).all()


def test_recortar_misma_regla_que_ventana_valida():
    meses = _meses(2000, 2001)
    indice = np.full(len(meses), np.nan)
    indice[3:20] = 0.2
    a, b = indices.ventana_valida(indice)
    m, s, i = indices.recortar(meses, np.zeros(len(meses)), indice)
    assert m == meses[a:b]
    assert len(s) == len(i) == b - a


def test_recortar_exige_largos_iguales():
    with pytest.raises(ValueError):
        indices.recortar(["2000-01"], np.zeros(2), np.zeros(2))


# --- Archivos locales -------------------------------------------------------


@pytest.fixture
def datos(tmp_path, monkeypatch):
    tabla = tmp_path / "tabla"
    tabla.mkdir()
    meses = ["1981-12", "1982-01", "1982-02", "1982-03"]
    (tabla / "meses.json").write_text(json.dumps(meses))
    np.save(tabla / "ONI.npy", np.array([0.4, 0.5, -0.6, np.nan], dtype=np.float32))
    np.save(tabla / "NINO12.npy", np.array([np.nan, 0.3, -0.7, 1.1], dtype=np.float32))
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path))
    return tmp_path


def test_cargar_indice_lee_la_tabla_local(datos):
    meses, valores = indices.cargar_indice("ONI")
    assert meses == ["1981-12", "1982-01", "1982-02", "1982-03"]
    assert valores.dtype == float
    np.testing.assert_allclose(valores[:3], [0.4, 0.5, -0.6], rtol=1e-6)
    assert math.isnan(valores[3])


def test_cargar_indice_carpeta_explicita_y_meses_pedidos(datos, monkeypatch):
    monkeypatch.setenv("VERASCOPE_DATOS", str(datos / "otra"))
    meses, valores = indices.cargar_indice(
        "NINO12", carpeta=datos, meses=["1982-02", "1982-03", "1982-04"]
    )
    assert meses == ["1982-02", "1982-03", "1982-04"]
    np.testing.assert_allclose(valores[:2], [-0.7, 1.1], rtol=1e-6)
    assert math.isnan(valores[2])


def test_cargar_indice_desconocido(datos):
    with pytest.raises(ValueError, match="Índice desconocido"):
        indices.cargar_indice("SOI")


def test_cargar_indice_sin_archivo(tmp_path):
    with pytest.raises(FileNotFoundError, match="indices"):
        indices.cargar_indice("ONI", carpeta=tmp_path)


def test_indices_no_usa_fastapi_ni_red():
    fuente = indices.__file__
    with open(fuente, encoding="utf-8") as f:
        texto = f.read()
    assert "fastapi" not in texto
    assert "requests" not in texto
    assert "http" not in texto


# --- Una sola implementación con el preparador ------------------------------


def test_preparador_usa_los_parsers_del_backend():
    noaa = pytest.importorskip("verascope_datos.fuentes.noaa")
    assert noaa.parsear_oni is indices.parsear_oni
    assert noaa.parsear_nino12 is indices.parsear_nino12
    assert noaa.TEMPORADAS is indices.TEMPORADAS


def test_preparador_usa_la_ventana_del_backend():
    calcular = pytest.importorskip("verascope_datos.calcular")
    assert calcular.ventana_valida is indices.ventana_valida
