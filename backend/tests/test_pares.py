"""Pares de señales opuestas del escaneo (columna `pareja`; guía §9, issue #5).

Regla: por variable, se emparejan tendencias **significativas** de **signo contrario**
separadas **más de 1500 km**, con **cada celda en un solo par**. El emparejamiento vive
en el preparador (`verascope_datos.calcular._pares`); estas pruebas lo comprueban sobre
tablas sintéticas chicas, recalculando las distancias con nuestra propia haversine.
"""

import numpy as np
import pandas as pd
import pytest

from app.estadistica.constantes import KM_MIN_DESTINO
from app.estadistica.teleconexion import haversine_km
from tests.sinteticas import generador

calcular = pytest.importorskip("verascope_datos.calcular")

SIGNIFICATIVOS = ("cambio_robusto", "cambio_oculto")


def _tabla(filas):
    """Arma la tabla mínima del escaneo que lee `_pares`, con `pareja` vacía."""
    df = pd.DataFrame(
        filas, columns=["variable", "celda", "lat", "lon", "pendiente", "efecto", "veredicto"]
    )
    df["pareja"] = None
    return df


def _mundo(n=400, semilla=0):
    """Mundo aleatorio: celdas por todo el globo, dos variables, signos y veredictos mezclados."""
    rng = generador(7000 + semilla)
    filas = []
    for variable in ("PRECTOTCORR", "T2M"):
        lat = rng.uniform(-60, 70, n)
        lon = rng.uniform(-180, 180, n)
        pendiente = rng.normal(0, 1, n)
        veredicto = rng.choice(
            ["cambio_robusto", "cambio_oculto", "sin_tendencia", "sensible_a_el_nino"], n
        )
        for i in range(n):
            filas.append(
                (variable, i, lat[i], lon[i], pendiente[i], pendiente[i] / 0.5, veredicto[i])
            )
    return _tabla(filas)


def _pares_de(df):
    return {pid: g for pid, g in df.dropna(subset=["pareja"]).groupby("pareja")}


def test_el_umbral_es_el_de_la_guia():
    assert KM_MIN_DESTINO == 1500


@pytest.mark.parametrize("semilla", range(5))
def test_cada_par_cumple_la_regla(semilla):
    df = _mundo(semilla=semilla)
    calcular._pares(df)
    pares = _pares_de(df)
    assert pares, "el mundo aleatorio debería producir pares"
    for pid, g in pares.items():
        assert len(g) == 2, pid
        assert g.variable.nunique() == 1, pid
        assert set(g.veredicto) <= set(SIGNIFICATIVOS), pid
        a, b = g.itertuples()
        assert np.sign(a.pendiente) == -np.sign(b.pendiente) != 0, pid
        assert haversine_km(a.lat, a.lon, b.lat, b.lon) > KM_MIN_DESTINO, pid


@pytest.mark.parametrize("semilla", range(5))
def test_cada_celda_esta_en_un_solo_par(semilla):
    df = _mundo(semilla=semilla)
    calcular._pares(df)
    emparejadas = df.dropna(subset=["pareja"])
    assert not emparejadas.duplicated(["variable", "celda"]).any()
    assert (
        emparejadas.groupby("variable")
        .pareja.nunique()
        .mul(2)
        .eq(emparejadas.groupby("variable").size())
        .all()
    )


def test_no_empareja_vecinas_a_menos_de_1500_km():
    # Lima (−12, −77) y Quito (−0.2, −78.5) están a ~1300 km; Yakarta, a ~19 000 km.
    df = _tabla(
        [
            ("PRECTOTCORR", 0, -12.0, -77.0, 0.5, 2.0, "cambio_robusto"),
            ("PRECTOTCORR", 1, -0.2, -78.5, -0.5, -2.0, "cambio_robusto"),
        ]
    )
    assert haversine_km(-12.0, -77.0, -0.2, -78.5) < KM_MIN_DESTINO
    calcular._pares(df)
    assert df.pareja.isna().all()

    df = _tabla(
        [
            ("PRECTOTCORR", 0, -12.0, -77.0, 0.5, 2.0, "cambio_robusto"),
            ("PRECTOTCORR", 1, -0.2, -78.5, -0.5, -2.0, "cambio_robusto"),
            ("PRECTOTCORR", 2, -6.2, 106.8, -0.4, -1.5, "cambio_oculto"),
        ]
    )
    calcular._pares(df)
    assert df.pareja.tolist()[0] == df.pareja.tolist()[2] is not None
    assert df.pareja.tolist()[1] is None


def test_cruza_el_antimeridiano():
    # 179.5° y −179.5° sobre el ecuador están a ~111 km, no a ~40 000 km.
    df = _tabla(
        [
            ("RH2M", 0, 0.0, 179.5, 0.5, 2.0, "cambio_robusto"),
            ("RH2M", 1, 0.0, -179.5, -0.5, -2.0, "cambio_robusto"),
        ]
    )
    calcular._pares(df)
    assert df.pareja.isna().all()


def test_no_empareja_mismo_signo_ni_no_significativos():
    df = _tabla(
        [
            ("T2M", 0, -12.0, -77.0, 0.5, 2.0, "cambio_robusto"),
            ("T2M", 1, -6.2, 106.8, 0.4, 1.5, "cambio_robusto"),  # mismo signo
            ("T2M", 2, 40.0, 116.0, -0.4, -1.5, "sin_tendencia"),
            ("T2M", 3, 51.5, -0.1, -0.4, -1.5, "sensible_a_el_nino"),
        ]
    )
    calcular._pares(df)
    assert df.pareja.isna().all()


def test_no_mezcla_variables():
    df = _tabla(
        [
            ("PRECTOTCORR", 0, -12.0, -77.0, 0.5, 2.0, "cambio_robusto"),
            ("GWETTOP", 1, -6.2, 106.8, -0.4, -1.5, "cambio_robusto"),
        ]
    )
    calcular._pares(df)
    assert df.pareja.isna().all()


def test_empareja_primero_los_efectos_mas_fuertes():
    df = _tabla(
        [
            ("PRECTOTCORR", 0, -12.0, -77.0, 0.2, 0.5, "cambio_robusto"),
            ("PRECTOTCORR", 1, 30.0, -100.0, 0.9, 3.0, "cambio_robusto"),
            ("PRECTOTCORR", 2, -6.2, 106.8, -0.9, -3.0, "cambio_robusto"),
        ]
    )
    calcular._pares(df)
    # Hay una sola celda negativa: va con la positiva más fuerte, no con la primera fila.
    assert df.pareja[1] is not None and df.pareja[1] == df.pareja[2]
    assert df.pareja[0] is None
