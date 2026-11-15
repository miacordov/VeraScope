"""Issue #6: rutas teleconnect y compare-periods con datos reales, sin red.

Mundo sintético de 7 celdas: la lluvia de "Piura" sube con El Niño, la de "Indonesia" y
"norte de Australia" baja, una vecina de Piura (a < 1500 km) también baja, y el resto es
ruido. `resultados.parquet` trae el vínculo con El Niño de cada celda.
"""

import importlib
import json
import time
from unittest.mock import Mock

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from app.contracts import AnalyzeRespuesta, ComparePeriodsRespuesta, TeleconnectRespuesta
from app.datos import indices, power_client
from app.estadistica.constantes import KM_MIN_DESTINO, KM_SEP_DESTINOS
from app.estadistica.teleconexion import haversine_km

MESES = [f"{anio}-{mes:02d}" for anio in range(1981, 2026) for mes in range(1, 13)]
N = len(MESES)

PIURA = (-6.0, -80.0)
INDONESIA = (-2.0, 116.0)
AUSTRALIA = (-14.0, 132.0)
VECINA = (-8.0, -78.0)  # a unos 300 km de Piura: nunca puede ser destino
RUIDO = [(20.0, -150.0), (-30.0, -40.0), (10.0, 60.0)]

# (celda, respuesta de la lluvia al índice)
RUIDO_OCEANO = 4  # fila de RUIDO[0], en medio del Pacífico

MUNDO = [(PIURA, 1.0), (INDONESIA, -1.0), (AUSTRALIA, -1.0), (VECINA, -1.0)] + [
    (c, 0.0) for c in RUIDO
]


def _oni(rng) -> np.ndarray:
    """AR(1) con ρ = 0.9, parecido al ONI."""
    x = np.zeros(N)
    for t in range(1, N):
        x[t] = 0.9 * x[t - 1] + rng.normal(0, 0.3)
    return x


def _mundo(tmp_path, ruido_puro: bool = False, con_escaneo: bool = True):
    """Escribe `tabla/` y `resultados.parquet` como los deja el preparador."""
    rng = np.random.default_rng(7)
    oni = _oni(rng)
    estacional = np.tile(np.sin(np.arange(12) / 12 * 2 * np.pi), N // 12)
    tabla = tmp_path / "tabla"
    tabla.mkdir(parents=True)
    celdas = np.array([c for c, _ in MUNDO], dtype=float)
    np.save(tabla / "celdas.npy", celdas)
    (tabla / "meses.json").write_text(json.dumps(MESES), encoding="utf-8")
    np.save(tabla / "ONI.npy", oni.astype(np.float32))
    np.save(tabla / "NINO12.npy", oni.astype(np.float32))

    filas = []
    for variable in ("PRECTOTCORR", "GWETROOT", "GWETTOP", "RH2M", "T2M"):
        matriz = np.empty((len(MUNDO), N))
        for i, (_, respuesta) in enumerate(MUNDO):
            k = 0.0 if ruido_puro else respuesta
            matriz[i] = 5 + estacional + k * oni + rng.normal(0, 0.4, N)
        if variable == "GWETROOT":
            matriz[RUIDO_OCEANO] = np.nan  # humedad del suelo sobre el mar
        np.save(tabla / f"{variable}.npy", matriz.astype(np.float32))
        for i, ((lat, lon), respuesta) in enumerate(MUNDO):
            responde = respuesta != 0.0 and not ruido_puro
            filas.append(
                {
                    "variable": variable,
                    "celda": i,
                    "lat": lat,
                    "lon": lon,
                    "r_enso": 0.8 * respuesta if responde else 0.02,
                    "p_enso": 1e-8 if responde else 0.8,
                    "p_original_ajustado": np.nan,
                    "p_ajustado": np.nan,
                    "veredicto": "sin_tendencia",
                }
            )
    if con_escaneo:
        pd.DataFrame(filas).to_parquet(tmp_path / "resultados.parquet")
    return oni


def _respuesta_power(meses):
    rng = np.random.RandomState(42)
    parametros = {
        variable: {mes.replace("-", ""): round(float(20 + rng.normal(0, 0.3)), 4) for mes in meses}
        for variable in power_client.VARIABLES_POWER
    }
    return {"properties": {"parameter": parametros}, "header": {"fill_value": -999}}


def _cliente(monkeypatch, tmp_path, sin_red):
    monkeypatch.setenv("VERASCOPE_SIMULADO", "0")
    monkeypatch.setenv("VERASCOPE_FIN", "2025")
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path))
    monkeypatch.setenv("VERASCOPE_CORS", "https://web.example,https://otra.example")
    datos = importlib.import_module("app.datos")
    principal = importlib.import_module("app.main")
    for modulo in (datos, indices, principal):
        monkeypatch.setattr(modulo, "carpeta_datos", lambda: tmp_path)
    llamada = Mock(return_value=_respuesta_power(MESES))
    monkeypatch.setattr(principal.ClientePower, "celda", llamada)
    return TestClient(principal.app, backend_options={"loop_factory": lambda: sin_red})


@pytest.fixture
def cliente(monkeypatch, tmp_path, sin_red):
    _mundo(tmp_path)
    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        yield c


def _lineas(cliente, variable="PRECTOTCORR", lat=PIURA[0], lon=PIURA[1]):
    respuesta = cliente.get(
        "/api/v1/teleconnect", params={"variable": variable, "lat": lat, "lon": lon}
    )
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert TeleconnectRespuesta.model_validate(datos).model_dump(mode="json") == datos
    return datos


# ── teleconnect ──────────────────────────────────────────────────────────────


def test_las_lineas_opuestas_de_piura_caen_en_indonesia_y_el_norte_de_australia(cliente):
    datos = _lineas(cliente)
    opuestas = {(li["lat"], li["lon"]) for li in datos["lineas"] if li["tipo"] == "opuesto"}
    assert opuestas == {INDONESIA, AUSTRALIA}
    assert datos["mensaje_vacio"] is None
    assert datos["origen"] == {
        "lat": PIURA[0],
        "lon": PIURA[1],
        "distancia_a_clic_km": 0.0,
        "r_el_nino": 0.8,
    }
    for linea in datos["lineas"]:
        assert linea["r"] < 0
        assert linea["r_el_nino_destino"] < 0 < linea["r_el_nino_origen"]
        assert linea["meses_coincidencia"], "una línea real coincide en algunos meses"


def test_ningun_destino_a_menos_de_1500_km_y_destinos_separados(cliente):
    lineas = _lineas(cliente)["lineas"]
    assert VECINA not in {(li["lat"], li["lon"]) for li in lineas}
    assert all(li["distancia_km"] > KM_MIN_DESTINO for li in lineas)
    for a in lineas:
        for b in lineas:
            if a is not b:
                assert haversine_km(a["lat"], a["lon"], b["lat"], b["lon"]) > KM_SEP_DESTINOS
    assert sum(li["tipo"] == "opuesto" for li in lineas) <= 3
    assert sum(li["tipo"] == "mismo" for li in lineas) <= 2


def test_clic_fuera_de_la_rejilla_usa_la_celda_mas_cercana(cliente):
    datos = _lineas(cliente, lat=-5.0, lon=-80.5)
    assert (datos["origen"]["lat"], datos["origen"]["lon"]) == PIURA
    distancia = haversine_km(-5.0, -80.5, *PIURA)
    assert datos["origen"]["distancia_a_clic_km"] == pytest.approx(distancia, abs=1e-3)


def test_longitud_0_360_da_el_mismo_resultado(cliente):
    assert _lineas(cliente, lon=280.0) == _lineas(cliente, lon=-80.0)


def test_temperatura_responde_200_sin_lineas_y_lo_explica(cliente):
    datos = _lineas(cliente, variable="T2M")
    assert datos["lineas"] == []
    assert "temperatura" in datos["mensaje_vacio"]


def test_humedad_del_suelo_sobre_el_mar_responde_sin_datos_tierra(cliente):
    lat, lon = RUIDO[0]
    respuesta = cliente.get(
        "/api/v1/teleconnect", params={"variable": "GWETROOT", "lat": lat, "lon": lon}
    )
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "sin_datos_tierra"


def test_con_ruido_puro_lista_vacia_y_mensaje(monkeypatch, tmp_path, sin_red):
    _mundo(tmp_path, ruido_puro=True)
    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        datos = _lineas(c)
    assert datos["lineas"] == []
    assert datos["mensaje_vacio"] == "No se encontró un vínculo que cumpla los criterios."


def test_sin_escaneo_responde_503_escaneo_en_curso(monkeypatch, tmp_path, sin_red):
    _mundo(tmp_path, con_escaneo=False)
    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        respuesta = c.get(
            "/api/v1/teleconnect", params={"variable": "PRECTOTCORR", "lat": -6, "lon": -80}
        )
    assert respuesta.status_code == 503
    assert respuesta.json()["error"]["codigo"] == "escaneo_en_curso"


def test_sin_tabla_responde_503_escaneo_en_curso(monkeypatch, tmp_path, sin_red):
    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        respuesta = c.get(
            "/api/v1/teleconnect", params={"variable": "PRECTOTCORR", "lat": -6, "lon": -80}
        )
    assert respuesta.status_code == 503
    assert respuesta.json()["error"]["codigo"] == "escaneo_en_curso"


# ── compare-periods ──────────────────────────────────────────────────────────

PERIODOS = {"p1_inicio": 1981, "p1_fin": 2001, "p2_inicio": 2003, "p2_fin": 2025}


def _comparar(cliente, **cambios):
    params = {"variable": "PRECTOTCORR", "lat": -5.0, "lon": -80.5, **PERIODOS, **cambios}
    return cliente.get("/api/v1/compare-periods", params=params)


def test_compare_periods_valida_el_contrato_y_trae_la_nota(cliente):
    respuesta = _comparar(cliente)
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert ComparePeriodsRespuesta.model_validate(datos).model_dump(mode="json") == datos
    assert datos["p1"]["anios"] == [1981, 2001]
    assert datos["p2"]["anios"] == [2003, 2025]
    assert datos["nota"] == "Comparación descriptiva: la significancia la da la tendencia."


def test_compare_periods_usa_los_mismos_numeros_que_analyze(cliente):
    datos = _comparar(cliente).json()
    celda = AnalyzeRespuesta.model_validate(
        cliente.get(
            "/api/v1/analyze",
            params={
                "variable": "PRECTOTCORR",
                "lat": -5.0,
                "lon": -80.5,
                "inicio": 1981,
                "fin": 2025,
            },
        ).json()
    )
    anios = np.array([int(f[:4]) for f in celda.fechas])
    for clave, serie in (
        ("media_original", celda.serie_original),
        ("media_sin_el_nino", celda.serie_sin_el_nino),
    ):
        valores = np.array([np.nan if v is None else v for v in serie], dtype=float)
        for periodo, (inicio, fin) in (("p1", (1981, 2001)), ("p2", (2003, 2025))):
            dentro = (anios >= inicio) & (anios <= fin)
            assert datos[periodo][clave] == pytest.approx(float(np.nanmean(valores[dentro])))
    for periodo, (inicio, fin) in (("p1", (1981, 2001)), ("p2", (2003, 2025))):
        en_periodo = [m for m in celda.meses_inusuales if inicio <= int(m.fecha[:4]) <= fin]
        assert datos[periodo]["meses_inusuales"] == len(en_periodo)
        assert datos[periodo]["meses_inusuales_en_el_nino"] == sum(
            m.fase == "nino" for m in en_periodo
        )
    assert datos["delta_original"] == pytest.approx(
        datos["p2"]["media_original"] - datos["p1"]["media_original"]
    )


def test_compare_periods_periodo_de_menos_de_10_anios(cliente):
    respuesta = _comparar(cliente, p2_inicio=2020)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "ventana_corta"


def test_compare_periods_power_lento_se_devuelve_tal_cual(monkeypatch, tmp_path, sin_red):
    _mundo(tmp_path)
    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        principal = importlib.import_module("app.main")
        principal.ClientePower.celda.side_effect = power_client.PowerLento("espera agotada")
        respuesta = _comparar(c)
    assert respuesta.status_code == 504
    assert respuesta.json()["error"]["codigo"] == "power_lento"


# ── rendimiento ──────────────────────────────────────────────────────────────


@pytest.mark.lento
def test_rendimiento_teleconnect_rejilla_completa(monkeypatch, tmp_path, sin_red):
    """Issue #6: `teleconnect` < 50 ms sobre la rejilla real (4235 celdas × 540 meses).

    Mide la ruta completa (HTTP, lectura del escaneo y búsqueda). Las anomalías son
    sintéticas y se ponen en memoria directamente, para no pagar los ~16 s del arranque.
    """
    from app.datos.celdas import rejilla
    from app.estadistica.teleconexion import preparar_matrices

    celdas = np.array(rejilla(), dtype=float)
    rng = np.random.default_rng(11)
    oni = _oni(rng)
    tabla = tmp_path / "tabla"
    tabla.mkdir()
    np.save(tabla / "celdas.npy", celdas)
    (tabla / "meses.json").write_text(json.dumps(MESES), encoding="utf-8")
    np.save(tabla / "ONI.npy", oni.astype(np.float32))

    # Un tercio de las celdas responde a El Niño con signo +, otro tercio con signo −.
    respuesta = rng.choice([-1.0, 0.0, 1.0], size=len(celdas))
    anomalias = respuesta[:, None] * oni[None, :] + rng.normal(0, 0.5, (len(celdas), N))
    pd.DataFrame(
        {
            "variable": "PRECTOTCORR",
            "celda": np.arange(len(celdas)),
            "lat": celdas[:, 0],
            "lon": celdas[:, 1],
            "r_enso": np.where(respuesta == 0, 0.02, 0.8 * respuesta),
            "p_enso": np.where(respuesta == 0, 0.8, 1e-8),
        }
    ).to_parquet(tmp_path / "resultados.parquet")

    with _cliente(monkeypatch, tmp_path, sin_red) as c:
        c.app.state.rejilla.matrices["PRECTOTCORR"] = preparar_matrices(anomalias)
        origen = int(np.flatnonzero(respuesta == 1)[0])
        params = {"variable": "PRECTOTCORR", "lat": celdas[origen, 0], "lon": celdas[origen, 1]}
        primera = c.get("/api/v1/teleconnect", params=params)
        assert primera.status_code == 200, primera.text
        assert primera.json()["lineas"], "el escenario tiene que producir líneas"
        tiempos = []
        for _ in range(10):
            inicio = time.perf_counter()
            assert c.get("/api/v1/teleconnect", params=params).status_code == 200
            tiempos.append(time.perf_counter() - inicio)
    assert np.median(tiempos) < 0.050
