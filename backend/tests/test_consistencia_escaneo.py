"""Consistencia escaneo ↔ vivo (guía §13; B3).

`analyze` de una celda de la rejilla debe dar **los mismos** pendiente, intervalo y
veredicto que su fila de `resultados.parquet`. Aquí "vivo" es lo que hace la ruta:
leer la serie de la celda del casillero, recortarla a la ventana con índice
(`indices.ventana_valida`) y llamar a `analizar_celda`. El escaneo es
`jobs.scanmap.correr` sobre el mismo casillero.
"""

import numpy as np
import pytest

from app.datos.indices import ventana_valida
from app.estadistica.celda import analizar_celda
from app.estadistica.constantes import ALFA
from app.estadistica.veredicto import estado, significativa
from tests.mundo_escaneo import CELDAS_CON_DATOS, armar_mundo

pytest.importorskip("verascope_datos.calcular")

CAMPOS = (
    "pendiente_original",
    "p_original",
    "pendiente",
    "ic_bajo",
    "ic_alto",
    "p",
    "rezago",
    "r_enso",
    "p_enso",
    "n_efectivo",
    "colinealidad",
    "efecto",
    "meses",
)


@pytest.fixture(scope="module")
def escaneo(tmp_path_factory):
    monkeypatch = pytest.MonkeyPatch()
    try:
        rutas = armar_mundo(tmp_path_factory.mktemp("consistencia"), monkeypatch)
        from jobs.scanmap import correr

        df = correr(rutas.base, procesos=1)
        yield rutas, df
    finally:
        monkeypatch.undo()


def _vivo(rutas, variable, lat, lon):
    from verascope_datos.almacen import Casillero, lugar_celda

    from verascope_datos import config

    meses = config.meses(fin=2000)
    cas = Casillero(rutas.casillero)
    try:
        valores = cas.leer_alineada(variable, lugar_celda(lat, lon), meses)
        oni = cas.leer_alineada("ONI", "indice", meses).astype(float)
    finally:
        cas.cerrar()
    a, b = ventana_valida(oni)
    cal = np.array([int(m[5:7]) for m in meses])[a:b]
    return analizar_celda(valores.astype(float)[a:b], cal, oni[a:b], variable)


def test_el_escaneo_cubre_las_celdas_con_datos(escaneo):
    _, df = escaneo
    assert df.celda.nunique() == CELDAS_CON_DATOS
    assert len(df) == CELDAS_CON_DATOS * 5 - 1  # la serie con hueco de 3 meses se descarta


def test_analyze_da_los_mismos_numeros_que_el_escaneo(escaneo):
    rutas, df = escaneo
    for fila in df.itertuples():
        vivo = _vivo(rutas, fila.variable, fila.lat, fila.lon)
        assert vivo is not None, (fila.variable, fila.lat, fila.lon)
        esperado = vivo.fila_escaneo()
        for campo in CAMPOS:
            assert getattr(fila, campo) == pytest.approx(esperado[campo], rel=1e-12, abs=1e-12), (
                campo,
                fila.variable,
                fila.lat,
                fila.lon,
            )


def test_el_veredicto_del_escaneo_sale_de_los_p_ajustados(escaneo):
    _, df = escaneo
    esperado = estado(
        significativa(df.p_original_ajustado.to_numpy(), ALFA),
        significativa(df.p_ajustado.to_numpy(), ALFA),
    )
    assert df.veredicto.tolist() == list(esperado)


def test_la_serie_descartada_en_el_escaneo_tambien_se_descarta_en_vivo(escaneo):
    rutas, df = escaneo
    from verascope_datos import config

    lat, lon = config.rejilla(8.0)[5]
    assert df[(df.variable == "T2M") & (df.lat == lat) & (df.lon == lon)].empty
    assert _vivo(rutas, "T2M", lat, lon) is None
