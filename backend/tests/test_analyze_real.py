"""S4–S6: analyze real con índices y respuestas POWER sintéticos, sin red."""

import importlib
import json
from unittest.mock import Mock

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.contracts import AnalyzeRespuesta, ErrorRespuesta
from app.datos import indices, power_client

PARAMETROS = {
    "variable": "PRECTOTCORR",
    "lat": -5,
    "lon": -80.5,
    "inicio": 1981,
    "fin": 2025,
    "indice": "ONI",
}


def _respuesta_power_sintetica(meses):
    """Respuesta POWER sintética: cinco variables y tendencia leve en lluvia."""
    rng = np.random.RandomState(42)
    n = len(meses)
    parametros = {}
    for variable in power_client.VARIABLES_POWER:
        base = np.linspace(3.0, 4.0, n) if variable == "PRECTOTCORR" else np.full(n, 20.0)
        ruido = rng.normal(0, 0.3, n)
        parametros[variable] = {
            mes.replace("-", ""): round(float(valor + error), 4)
            for mes, valor, error in zip(meses, base, ruido)
        }
    return {"properties": {"parameter": parametros}, "header": {"fill_value": -999}}


def _crear_indices_sinteticos(tabla_dir, meses):
    """Escribe índices sintéticos reproducibles sin modificar el generador global."""
    tabla_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(123)
    for nombre in ("ONI", "NINO12"):
        valores = rng.normal(0, 0.5, len(meses)).astype(np.float64)
        np.save(tabla_dir / f"{nombre}.npy", valores)
    (tabla_dir / "meses.json").write_text(json.dumps(meses), encoding="utf-8")


@pytest.fixture
def cliente_real(monkeypatch, tmp_path, sin_red):
    monkeypatch.setenv("VERASCOPE_FIN", "2025")
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path))
    # Igual que `cliente` en conftest.py: main.py lee VERASCOPE_CORS al importarse.
    monkeypatch.setenv("VERASCOPE_CORS", "https://web.example,https://otra.example")
    meses = [f"{anio}-{mes:02d}" for anio in range(1981, 2026) for mes in range(1, 13)]
    _crear_indices_sinteticos(tmp_path / "tabla", meses)
    datos = importlib.import_module("app.datos")
    principal = importlib.import_module("app.main")
    monkeypatch.setattr(datos, "carpeta_datos", lambda: tmp_path)
    monkeypatch.setattr(indices, "carpeta_datos", lambda: tmp_path)
    monkeypatch.setattr(principal, "carpeta_datos", lambda: tmp_path)
    llamada = Mock(return_value=_respuesta_power_sintetica(meses))
    monkeypatch.setattr(principal.ClientePower, "celda", llamada)
    with TestClient(principal.app, backend_options={"loop_factory": lambda: sin_red}) as cliente:
        yield cliente, llamada


def _comprobar_error(respuesta, estado, codigo, mensaje):
    assert respuesta.status_code == estado, respuesta.text
    assert respuesta.json() == {
        "error": {"codigo": codigo, "mensaje": mensaje, "celda_cercana": None}
    }
    ErrorRespuesta.model_validate(respuesta.json())


def test_analyze_respuesta_valida(cliente_real):
    cliente, llamada = cliente_real
    respuesta = cliente.get("/api/v1/analyze", params=PARAMETROS)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert AnalyzeRespuesta.model_validate(datos).model_dump(mode="json") == datos
    assert datos["ventana"]["meses"] == 540
    assert datos["fechas"][0] == "1981-01"
    assert datos["fechas"][-1] == "2025-12"
    assert datos["veredicto"]["origen"] == "individual"
    llamada.assert_called_once_with(-5.0, -80.5, 1981, 2025)


def test_analyze_ambas_tendencias_mismos_meses(cliente_real):
    cliente, llamada = cliente_real
    respuesta = cliente.get("/api/v1/analyze", params=PARAMETROS)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    original = datos["tendencia_original"]["recta"]
    limpia = datos["tendencia_sin_el_nino"]["recta"]
    assert len(original) == len(limpia) == len(datos["fechas"]) == 540
    assert [i for i, valor in enumerate(original) if valor is not None] == [
        i for i, valor in enumerate(limpia) if valor is not None
    ]
    llamada.assert_called_once()


def test_analyze_ventana_corta(cliente_real):
    cliente, llamada = cliente_real
    respuesta = cliente.get("/api/v1/analyze", params={**PARAMETROS, "inicio": 2020, "fin": 2022})
    _comprobar_error(
        respuesta,
        422,
        "ventana_corta",
        "La ventana tiene menos de 10 años. Con tan pocos años, el ruido entre "
        "años impide ver tendencias; elige al menos 10.",
    )
    llamada.assert_not_called()


def test_analyze_fuera_de_rango(cliente_real):
    cliente, llamada = cliente_real
    respuesta = cliente.get("/api/v1/analyze", params={**PARAMETROS, "inicio": 1970, "fin": 1980})
    _comprobar_error(
        respuesta,
        422,
        "fuera_de_rango",
        "Elige años desde 1981 hasta el último año completo, en orden.",
    )
    llamada.assert_not_called()


def test_analyze_power_lento(cliente_real):
    cliente, llamada = cliente_real
    llamada.side_effect = power_client.PowerLento("Espera simulada agotada")
    respuesta = cliente.get("/api/v1/analyze", params=PARAMETROS)
    _comprobar_error(
        respuesta,
        504,
        "power_lento",
        "NASA POWER tardó demasiado en responder. "
        "Inténtalo más tarde o elige una celda con datos guardados.",
    )
    llamada.assert_called_once_with(-5.0, -80.5, 1981, 2025)


def test_analyze_sin_datos_tierra(cliente_real):
    cliente, llamada = cliente_real
    for serie in llamada.return_value["properties"]["parameter"].values():
        for mes in serie:
            serie[mes] = -999
    respuesta = cliente.get("/api/v1/analyze", params=PARAMETROS)
    _comprobar_error(
        respuesta,
        422,
        "sin_datos_tierra",
        "Esta celda no tiene suficientes datos válidos para analizar. "
        "Para humedad del suelo, elige una celda sobre tierra.",
    )
    llamada.assert_called_once_with(-5.0, -80.5, 1981, 2025)


def test_meses_inusuales_usan_la_fase_del_indice_rezagado(cliente_real):
    """Cálculo C17: |z| > 2 con la fase del índice en t − ℓ*; los primeros ℓ* no cuentan."""
    cliente, _ = cliente_real
    datos = cliente.get("/api/v1/analyze", params=PARAMETROS).json()
    rezago = datos["vinculo_el_nino"]["rezago_meses"]
    posicion = {mes: i for i, mes in enumerate(datos["fechas"])}
    esperados = [
        (mes, datos["fase"][i - rezago])
        for i, (mes, z) in enumerate(zip(datos["fechas"], datos["serie_z"]))
        if i >= rezago and z is not None and abs(z) > 2
    ]
    obtenidos = [(m["fecha"], m["fase"]) for m in datos["meses_inusuales"]]
    assert obtenidos == esperados
    assert all(posicion[m] >= rezago for m, _ in obtenidos)


def _codigos(datos):
    return [a["codigo"] for a in datos["avisos"]]


def test_analyze_avisa_respuesta_no_lineal_en_la_lluvia_de_piura(cliente_real):
    cliente, _ = cliente_real
    datos = cliente.get("/api/v1/analyze", params=PARAMETROS).json()
    assert "respuesta_no_lineal" in _codigos(datos)
    AnalyzeRespuesta.model_validate(datos)


def test_analyze_no_avisa_respuesta_no_lineal_fuera_de_la_lluvia(cliente_real):
    cliente, _ = cliente_real
    datos = cliente.get("/api/v1/analyze", params={**PARAMETROS, "variable": "T2M"}).json()
    assert "respuesta_no_lineal" not in _codigos(datos)


def test_analyze_agrega_nino_costero_con_oni_y_no_con_nino12(cliente_real, monkeypatch):
    analyze = importlib.import_module("app.api.analyze")
    llamadas = []

    def falso(lat, lon, anomalias, oni, nino12):
        llamadas.append((len(anomalias), len(oni), len(nino12)))
        return ("nino_costero", "texto de prueba")

    monkeypatch.setattr(analyze, "aviso_nino_costero", falso)
    cliente, _ = cliente_real
    datos = cliente.get("/api/v1/analyze", params=PARAMETROS).json()
    assert "nino_costero" in _codigos(datos)
    n = len(datos["fechas"])
    assert llamadas == [(n, n, n)]  # serie, ONI y Niño 1+2 alineados a la ventana

    datos = cliente.get("/api/v1/analyze", params={**PARAMETROS, "indice": "NINO12"}).json()
    assert "nino_costero" not in _codigos(datos)
    assert len(llamadas) == 1


def test_analyze_sin_nino12_responde_sin_el_aviso_costero(cliente_real, tmp_path):
    (tmp_path / "tabla" / "NINO12.npy").unlink()  # el aviso es complementario: no rompe analyze
    cliente, _ = cliente_real
    respuesta = cliente.get("/api/v1/analyze", params=PARAMETROS)
    assert respuesta.status_code == 200, respuesta.text
    assert "nino_costero" not in _codigos(respuesta.json())
