"""Pruebas de app/estadistica/teleconexion.py (guía §10 y §13, issue #6).

Mundo sintético con semilla fija sobre la rejilla real de ScanMap (4235 celdas):
la costa de "Piura" responde a El Niño con signo +, "Indonesia y norte de Australia"
con signo −, una región lejana del Pacífico norte con signo + (mismo efecto) y el
resto es ruido. Las tasas no son resultados de la plataforma.
"""

import time

import numpy as np
import pytest

from app.datos.celdas import rejilla
from app.estadistica.constantes import (
    KM_MIN_DESTINO,
    KM_SEP_DESTINOS,
    MAX_LINEAS_IGUALES,
    MAX_LINEAS_OPUESTAS,
)
from app.estadistica.enso import p_correlacion, r1
from app.estadistica.teleconexion import (
    MENSAJE_SIN_VINCULO,
    MENSAJE_VARIABLE_SIN_LINEAS,
    buscar_lineas,
    celda_mas_cercana,
    haversine_km,
    preparar_matrices,
)
from tests.sinteticas import ar1, generador

N_MESES = 480
PIURA = (-5.0, -80.5)


def _region(lat, lon, lat_min, lat_max, lon_min, lon_max):
    return (lat >= lat_min) & (lat <= lat_max) & (lon >= lon_min) & (lon <= lon_max)


def _mundo(con_senal=True, semilla=0):
    rng = generador(7000 + semilla)
    celdas = np.array(rejilla())
    lat, lon = celdas[:, 0], celdas[:, 1]
    indice = ar1(N_MESES, 0.93, 1.0, rng)
    ruido = np.stack([ar1(N_MESES, 0.3, 1.0, rng) for _ in range(lat.size)])
    signo = np.zeros(lat.size)
    if con_senal:
        signo[_region(lat, lon, -8, -2, -82, -78)] = 1.0  # costa norte del Perú
        signo[_region(lat, lon, -20, 4, 110, 145)] = -1.0  # Indonesia y norte de Australia
        signo[_region(lat, lon, 20, 26, -160, -150)] = 1.0  # región lejana, mismo efecto
    anomalias = ruido + 1.5 * signo[:, None] * indice
    r_enso = np.array([np.corrcoef(a, indice)[0, 1] for a in anomalias])
    p_enso, _ = p_correlacion(r_enso, r1(anomalias), r1(indice), N_MESES)
    fechas = [f"{1981 + k // 12}-{k % 12 + 1:02d}" for k in range(N_MESES)]
    fases = np.where(indice >= 0.5, "nino", np.where(indice <= -0.5, "nina", "neutro"))
    return dict(
        lat=lat,
        lon=lon,
        anomalias=anomalias,
        r_enso=r_enso,
        p_enso=np.asarray(p_enso),
        fechas=fechas,
        fases=list(fases),
        signo=signo,
    )


@pytest.fixture(scope="module")
def mundo():
    return _mundo()


def _buscar(m, origen, variable="PRECTOTCORR", matrices=None):
    matrices = matrices if matrices is not None else preparar_matrices(m["anomalias"])
    return buscar_lineas(
        variable,
        origen,
        matrices,
        m["lat"],
        m["lon"],
        m["r_enso"],
        m["p_enso"],
        m["fechas"],
        m["fases"],
    )


def _origen_piura(m):
    origen, _ = celda_mas_cercana(*PIURA, m["lat"], m["lon"])
    return origen


# ------------------------------------------------------------------ geografía


def test_haversine_distancias_conocidas():
    assert haversine_km(0, 0, 0, 1) == pytest.approx(111.19, abs=0.1)
    assert haversine_km(0, 0, 0, 180) == pytest.approx(np.pi * 6371.0088, rel=1e-6)
    lima_sidney = haversine_km(-12.05, -77.04, -33.87, 151.21)
    assert lima_sidney == pytest.approx(12_740, rel=0.01)


def test_haversine_cruza_180_y_acepta_0_360():
    assert haversine_km(0, 179.5, 0, -179.5) == pytest.approx(haversine_km(0, 0, 0, 1))
    assert haversine_km(-5, -80.5, -5, 279.5) == pytest.approx(0.0, abs=1e-6)
    lats = np.array([0.0, 10.0])
    lons = np.array([-179.0, 170.0])
    np.testing.assert_allclose(
        haversine_km(0.0, 179.0, lats, lons),
        [haversine_km(0, 179, 0, -179), haversine_km(0, 179, 10, 170)],
    )


def test_celda_mas_cercana_informa_la_distancia(mundo):
    i, km = celda_mas_cercana(*PIURA, mundo["lat"], mundo["lon"])
    assert km == pytest.approx(haversine_km(*PIURA, mundo["lat"][i], mundo["lon"][i]))
    assert km == pytest.approx(haversine_km(*PIURA, mundo["lat"], mundo["lon"]).min())
    assert abs(mundo["lat"][i] - PIURA[0]) <= 1 and abs(mundo["lon"][i] - PIURA[1]) <= 1
    _, km_360 = celda_mas_cercana(PIURA[0], PIURA[1] + 360, mundo["lat"], mundo["lon"])
    assert km_360 == pytest.approx(km)


# ------------------------------------------------------------------ matrices


def test_preparar_matrices_z_poblacional_mascara_y_rho(mundo):
    a = mundo["anomalias"].copy()
    a[3, 10] = np.nan  # serie incompleta
    a[4] = 2.0  # serie constante
    m = preparar_matrices(a)
    assert m.z.dtype == np.float32 and m.z.shape == a.shape and m.n == N_MESES
    assert not m.validas[3] and not m.validas[4] and m.validas[0]
    assert np.all(m.z[~m.validas] == 0)
    z0 = (a[0] - a[0].mean()) / a[0].std()
    np.testing.assert_allclose(m.z[0], z0, atol=1e-5)
    assert m.rho1[0] == pytest.approx(r1(a[0]), abs=1e-6)


def test_r_en_float32_coincide_con_float64(mundo):
    m = preparar_matrices(mundo["anomalias"])
    o = _origen_piura(mundo)
    a = mundo["anomalias"]
    z64 = (a - a.mean(1, keepdims=True)) / a.std(1, keepdims=True)
    r64 = z64 @ z64[o] / N_MESES
    r32 = m.z.astype(np.float64) @ m.z[o].astype(np.float64) / N_MESES
    np.testing.assert_allclose(r32, r64, atol=1e-5)


# ------------------------------------------------------------------ líneas


def test_lineas_opuestas_desde_piura_caen_en_indonesia_y_australia(mundo):
    res = _buscar(mundo, _origen_piura(mundo))
    opuestas = [li for li in res.lineas if li.tipo == "opuesto"]
    assert len(opuestas) == MAX_LINEAS_OPUESTAS
    for li in opuestas:
        assert _region(li.lat, li.lon, -20, 4, 110, 145)
        assert li.r < 0 and li.p_ajustado < 0.05
        assert np.sign(li.r_el_nino_origen) != np.sign(li.r_el_nino_destino)
    assert res.mensaje_vacio is None


def test_lineas_de_mismo_efecto_caen_en_la_region_lejana(mundo):
    res = _buscar(mundo, _origen_piura(mundo))
    iguales = [li for li in res.lineas if li.tipo == "mismo"]
    assert 1 <= len(iguales) <= MAX_LINEAS_IGUALES
    for li in iguales:
        assert _region(li.lat, li.lon, 20, 26, -160, -150)
        assert li.r > 0
        assert np.sign(li.r_el_nino_origen) == np.sign(li.r_el_nino_destino)


def test_distancias_minimas_y_orden_por_r(mundo):
    o = _origen_piura(mundo)
    res = _buscar(mundo, o)
    assert len(res.lineas) <= MAX_LINEAS_OPUESTAS + MAX_LINEAS_IGUALES
    for li in res.lineas:
        assert li.distancia_km > KM_MIN_DESTINO
        assert li.distancia_km == pytest.approx(
            haversine_km(mundo["lat"][o], mundo["lon"][o], li.lat, li.lon)
        )
    for k, a in enumerate(res.lineas):
        for b in res.lineas[k + 1 :]:
            assert haversine_km(a.lat, a.lon, b.lat, b.lon) > KM_SEP_DESTINOS
    for tipo in ("opuesto", "mismo"):
        rs = [abs(li.r) for li in res.lineas if li.tipo == tipo]
        assert rs == sorted(rs, reverse=True)


def test_meses_de_coincidencia_con_la_fase_del_propio_mes(mundo):
    o = _origen_piura(mundo)
    m = preparar_matrices(mundo["anomalias"])
    res = _buscar(mundo, o, matrices=m)
    li = next(x for x in res.lineas if x.tipo == "opuesto")
    j = int(np.flatnonzero((mundo["lat"] == li.lat) & (mundo["lon"] == li.lon))[0])
    zi, zj = m.z[o], m.z[j]
    esperados = np.flatnonzero(((zi > 1) & (zj < -1)) | ((zi < -1) & (zj > 1)))
    assert [fecha for fecha, _ in li.meses_coincidencia] == [mundo["fechas"][k] for k in esperados]
    assert [fase for _, fase in li.meses_coincidencia] == [mundo["fases"][k] for k in esperados]
    assert len(esperados) > 0


def test_ruido_puro_da_lista_vacia_con_mensaje():
    m = _mundo(con_senal=False, semilla=1)
    res = _buscar(m, _origen_piura(m))
    assert res.lineas == []
    assert res.mensaje_vacio == MENSAJE_SIN_VINCULO


def test_origen_sin_respuesta_a_el_nino_no_tiene_lineas(mundo):
    sin_senal = np.flatnonzero(
        (mundo["signo"] == 0) & (mundo["p_enso"] > 0.5) & (mundo["lat"] > 28)
    )
    res = _buscar(mundo, int(sin_senal[0]))
    assert res.lineas == [] and res.mensaje_vacio == MENSAJE_SIN_VINCULO


def test_origen_con_serie_invalida_no_tiene_lineas(mundo):
    a = mundo["anomalias"].copy()
    o = _origen_piura(mundo)
    a[o, 0] = np.nan
    res = _buscar(mundo, o, matrices=preparar_matrices(a))
    assert res.lineas == [] and res.mensaje_vacio == MENSAJE_SIN_VINCULO


def test_temperatura_responde_vacio_con_su_mensaje(mundo):
    res = _buscar(mundo, _origen_piura(mundo), variable="T2M")
    assert res.lineas == []
    assert res.mensaje_vacio == MENSAJE_VARIABLE_SIN_LINEAS


def test_lineas_validan_contra_el_contrato(mundo):
    from app.contracts import Linea

    res = _buscar(mundo, _origen_piura(mundo))
    for li in res.lineas:
        Linea.model_validate(li.como_contrato())


@pytest.mark.lento
def test_rendimiento_busqueda(mundo):
    m = preparar_matrices(mundo["anomalias"])
    o = _origen_piura(mundo)
    _buscar(mundo, o, matrices=m)
    inicio = time.perf_counter()
    for _ in range(10):
        _buscar(mundo, o, matrices=m)
    assert (time.perf_counter() - inicio) / 10 < 0.050
