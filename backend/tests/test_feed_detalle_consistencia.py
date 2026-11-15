"""Precisión pública feed ↔ analyze sobre datos sintéticos, sin red."""

import importlib
import json
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.datos import indices
from app.datos.celdas import lugar_celda, rejilla
from app.datos.escaneo import escribir_estado
from app.estadistica.celda import analizar_celda


@pytest.fixture
def escaneo_real(monkeypatch, tmp_path, sin_red):
    monkeypatch.setenv("VERASCOPE_SIMULADO", "0")
    monkeypatch.setenv("VERASCOPE_FIN", "2025")
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path))
    monkeypatch.setenv("VERASCOPE_CORS", "https://web.example,https://otra.example")
    meses = [f"{anio}-{mes:02d}" for anio in range(1981, 2026) for mes in range(1, 13)]
    rng = np.random.default_rng(123)
    oni = rng.normal(0, 0.5, len(meses))
    # El casillero guarda float32: el motor recibe exactamente la misma serie.
    serie = (np.linspace(3, 4, len(meses)) + rng.normal(0, 0.3, len(meses))).astype("float32")
    tabla = tmp_path / "tabla"
    tabla.mkdir()
    np.save(tabla / "ONI.npy", oni)
    (tabla / "meses.json").write_text(json.dumps(meses), encoding="utf-8")
    rc = analizar_celda(serie, [int(m[-2:]) for m in meses], oni, "PRECTOTCORR")
    assert rc is not None
    lat, lon = -6.0, -80.0
    fila = {
        **rc.fila_escaneo(),
        "variable": "PRECTOTCORR",
        "celda": rejilla().index((lat, lon)),
        "lat": lat,
        "lon": lon,
        "unidad": "mm/día",
        "pareja": None,
        "veredicto": "cambio_robusto",
        "p_original_ajustado": 0.003456789,
        "p_ajustado": 1.23456789e-9,
    }
    principal = importlib.import_module("app.main")
    monkeypatch.setattr(principal, "carpeta_datos", lambda: tmp_path)
    monkeypatch.setattr(indices, "carpeta_datos", lambda: tmp_path)
    power = Mock(side_effect=AssertionError("No debe consultar POWER"))
    monkeypatch.setattr(principal.ClientePower, "celda", power)
    escribir_estado(tmp_path, "completo", 4235, 4235)
    with TestClient(principal.app, backend_options={"loop_factory": lambda: sin_red}) as cliente:
        principal.app.state.cache.series.guardar(
            "PRECTOTCORR",
            lugar_celda(lat, lon),
            meses[0],
            serie,
            lat=lat,
            lon=lon,
            unidad="mm/día",
            fuente="Serie sintética",
        )
        principal.app.state.escaneo_resultados = pd.DataFrame([fila])
        yield cliente, fila
        power.assert_not_called()


def _feed(cliente, tipo="fuertes"):
    respuesta = cliente.get("/api/v1/scan/feed", params={"tipo": tipo})
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()


def test_feed_y_analyze_comparten_precision_publica(escaneo_real):
    cliente, fila = escaneo_real
    antes = cliente.app.state.escaneo_resultados.copy(deep=True)
    tarjeta = _feed(cliente)["tarjetas"][0]
    respuesta = cliente.get(
        "/api/v1/analyze",
        params={
            "variable": fila["variable"],
            "lat": fila["lat"],
            "lon": fila["lon"],
            "inicio": 1981,
            "fin": 2025,
            "indice": "ONI",
        },
    )
    assert respuesta.status_code == 200, respuesta.text
    detalle = respuesta.json()
    assert detalle["veredicto"]["origen"] == "escaneo"
    assert tarjeta["celda"] == {k: detalle["celda"][k] for k in ("lat", "lon")}
    assert tarjeta["veredicto"] == detalle["veredicto"]["estado"]
    assert fila["p_ajustado"] != round(fila["p_ajustado"], 6)
    for campo in ("p_ajustado", "pendiente_decada", "ic_bajo", "ic_alto"):
        assert tarjeta[campo] == detalle["tendencia_sin_el_nino"][campo]
    assert tarjeta["efecto"] == round(fila["efecto"], 6)
    pd.testing.assert_frame_equal(cliente.app.state.escaneo_resultados, antes)


def test_feed_orden_y_titular_conservan_valores_crudos(escaneo_real):
    cliente, fila = escaneo_real
    filas = [
        {**fila, "celda": 1, "efecto": 1.0000001, "pendiente": -1e-9},
        {
            **fila,
            "celda": 2,
            "efecto": 1.0000002,
            "pendiente": 1e-9,
            "lat": -6.123456789,
            "lon": -80.123456789,
        },
    ]
    cliente.app.state.escaneo_resultados = pd.DataFrame(filas)
    tarjetas = _feed(cliente)["tarjetas"]
    assert [t["id"] for t in tarjetas] == ["PRECTOTCORR-2", "PRECTOTCORR-1"]
    assert [t["pendiente_decada"] for t in tarjetas] == [0, 0]
    assert [t["efecto"] for t in tarjetas] == [1, 1]
    assert "sube" in tarjetas[0]["titular"]
    assert "baja" in tarjetas[1]["titular"]
    assert tarjetas[0]["celda"] == {"lat": -6.123457, "lon": -80.123457}


def test_feed_pares_conservan_signos_y_orden_crudos(escaneo_real):
    cliente, fila = escaneo_real
    filas = []
    for par, efecto, origen in (("a", 1.0000001, 1), ("b", 1.0000002, 3)):
        filas.extend(
            [
                {**fila, "celda": origen, "pareja": par, "efecto": efecto, "pendiente": 1e-9},
                {
                    **fila,
                    "celda": origen + 1,
                    "pareja": par,
                    "efecto": -efecto,
                    "pendiente": -1e-9,
                    "lat": 10.123456789,
                    "lon": 120.123456789,
                },
            ]
        )
    cliente.app.state.escaneo_resultados = pd.DataFrame(filas)
    tarjetas = _feed(cliente, "opuestas")["tarjetas"]
    assert [t["id"] for t in tarjetas] == ["PRECTOTCORR-3", "PRECTOTCORR-1"]
    assert all(
        t["pareja"]
        == {
            "lat": 10.123457,
            "lon": 120.123457,
            "pendiente_decada": 0,
        }
        for t in tarjetas
    )
    assert all(t["titular"] == "La lluvia sube aquí y baja allá" for t in tarjetas)
