"""Pruebas de app/datos/celdas.py: cuantización única, longitudes y rejilla."""

import pytest

from app.datos.celdas import (
    PASO_CELDA,
    celda,
    cuantizar,
    lon_a_180,
    lon_a_360,
    lugar_celda,
    rejilla,
)


def test_paso_es_medio_grado():
    assert PASO_CELDA == 0.5


@pytest.mark.parametrize(
    "valor, esperado",
    [
        (-5.1, -5.0),
        (-80.6, -80.5),
        (12.74, 12.5),
        (12.76, 13.0),
        (0.0, 0.0),
    ],
)
def test_cuantizar_redondea_a_medio_grado(valor, esperado):
    assert cuantizar(valor) == esperado


@pytest.mark.parametrize(
    "valor, esperado",
    [
        (5.25, 5.5),  # Python round daría 5.0; JS Math.round da 5.5
        (5.75, 6.0),
        (-5.25, -5.0),  # empate hacia +infinito, igual que Math.round
        (-5.75, -5.5),
    ],
)
def test_cuantizar_empates_como_math_round(valor, esperado):
    assert cuantizar(valor) == esperado


def test_cuantizar_no_devuelve_cero_negativo():
    assert str(cuantizar(-0.1)) == "0.0"


def test_toques_a_100_m_dan_la_misma_llave():
    # ~100 m ≈ 0.0009°
    assert lugar_celda(*celda(-5.1, -80.6)) == lugar_celda(*celda(-5.1009, -80.6009))


@pytest.mark.parametrize(
    "lon, esperado",
    [(0, 0.0), (90, 90.0), (180, 180.0), (-180, 180.0), (270, -90.0), (330, -30.0), (360, 0.0), (-190, 170.0)],
)
def test_lon_a_180(lon, esperado):
    assert lon_a_180(lon) == esperado


@pytest.mark.parametrize(
    "lon, esperado",
    [(0, 0.0), (-30, 330.0), (-180, 180.0), (179.5, 179.5), (-0.5, 359.5)],
)
def test_lon_a_360(lon, esperado):
    assert lon_a_360(lon) == esperado


def test_ida_y_vuelta_de_longitudes():
    for lon in [180.0, -90.5, -0.5, 0.0, 45.0, 179.5]:
        assert lon_a_180(lon_a_360(lon)) == lon


def test_celda_cuantiza_y_normaliza():
    assert celda(-5.1, 279.4) == (-5.0, -80.5)
    assert celda(-5.1, -80.6) == (-5.0, -80.5)
    assert celda(0.1, 179.9) == (0.0, 180.0)
    assert celda(0.1, -179.9) == (0.0, 180.0)


def test_celda_acota_latitud():
    assert celda(95.0, 0.0)[0] == 90.0
    assert celda(-95.0, 0.0)[0] == -90.0


def test_lugar_celda_formato_del_preparador():
    assert lugar_celda(-5.0, -80.5) == "celda:-5.00:-80.50"
    assert lugar_celda(14.0, 132.0) == "celda:+14.00:+132.00"
    assert lugar_celda(-0.0, -0.0) == "celda:+0.00:+0.00"


def test_rejilla_tiene_4235_celdas():
    r = rejilla()
    assert len(r) == 4235 == 35 * 121
    assert len(set(r)) == 4235


def test_rejilla_limites_y_orden():
    r = rejilla()
    lats = sorted({la for la, _ in r})
    assert lats[0] == -34.0 and lats[-1] == 34.0 and len(lats) == 35
    lons360 = sorted({lon_a_360(lo) for _, lo in r})
    assert lons360[0] == 90.0 and lons360[-1] == 330.0 and len(lons360) == 121
    assert all(-180.0 < lo <= 180.0 for _, lo in r)
    assert (-34.0, 180.0) in r
    # orden lat-mayor, igual que config.rejilla() del preparador
    assert r[0] == (-34.0, 90.0)
    assert r[120] == (-34.0, -30.0)
    assert r[121] == (-32.0, 90.0)


def test_rejilla_igual_a_la_del_preparador():
    pytest.importorskip("verascope_datos")
    from verascope_datos import config

    assert rejilla() == [(float(a), float(o)) for a, o in config.rejilla()]


def test_lugar_celda_igual_al_del_preparador():
    pytest.importorskip("verascope_datos")
    from verascope_datos.almacen import lugar_celda as lugar_prep

    for la, lo in rejilla()[::97] + [(-5.0, -80.5)]:
        assert lugar_celda(la, lo) == lugar_prep(la, lo)
