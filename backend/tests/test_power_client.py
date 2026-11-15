"""Cliente de NASA POWER (B2): sin red, con una sesión falsa inyectada."""

import math

import numpy as np
import pytest
import requests

from app.datos import power_client as pc

MESES = ["2000-01", "2000-02", "2000-03"]


class Respuesta:
    def __init__(self, estado=200, datos=None):
        self.status_code = estado
        self._datos = datos if datos is not None else json_power()

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code}", response=self)

    def json(self):
        return self._datos


class SesionFalsa:
    """Devuelve, en orden, las respuestas (o lanza las excepciones) que se le dan."""

    def __init__(self, *salidas):
        self.salidas = list(salidas) or [Respuesta()]
        self.llamadas = []

    def get(self, url, params=None, timeout=None):
        self.llamadas.append({"url": url, "params": params, "timeout": timeout})
        salida = self.salidas.pop(0) if len(self.salidas) > 1 else self.salidas[0]
        if isinstance(salida, Exception):
            raise salida
        return salida


def json_power(relleno=-999.0):
    def serie(valores):
        d = {m.replace("-", ""): v for m, v in zip(MESES, valores)}
        d["200013"] = 123.0  # promedio anual: se ignora
        return d

    return {
        "header": {"fill_value": relleno},
        "properties": {
            "parameter": {
                "PRECTOTCORR": serie([1.5, -999.0, 2.5]),
                "T2M": serie([25.0, 26.0, 27.0]),
                "GWETROOT": serie([-999.0, -999.0, -999.0]),
                "GWETTOP": serie([0.4, 0.5, 0.6]),
                "RH2M": serie([70.0, 71.0, 72.0]),
            }
        },
    }


@pytest.fixture
def esperas():
    return []


@pytest.fixture
def cliente_de(esperas):
    def crear(sesion, timeout=pc.TIMEOUT_LOTE, **kw):
        return pc.ClientePower(timeout, pausa=0, sesion=sesion, dormir=esperas.append, **kw)

    return crear


def test_cinco_variables_y_comunidad_ag_en_una_sola_peticion(cliente_de, monkeypatch):
    monkeypatch.delenv("VERASCOPE_POWER_URL", raising=False)
    sesion = SesionFalsa()
    datos = cliente_de(sesion).celda(-5.0, -80.5, 1981, 2024)
    assert datos == json_power()
    assert len(sesion.llamadas) == 1
    params = sesion.llamadas[0]["params"]
    assert pc.VARIABLES_POWER == ("PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M")
    assert params["parameters"] == "PRECTOTCORR,T2M,GWETROOT,GWETTOP,RH2M"
    assert params["community"] == "AG"
    assert (params["latitude"], params["longitude"]) == (-5.0, -80.5)
    assert (params["start"], params["end"], params["format"]) == (1981, 2024, "JSON")
    assert sesion.llamadas[0]["url"] == pc.POWER_URL_POR_DEFECTO


def test_timeout_es_parametro_8_en_vivo_60_en_lote(cliente_de, monkeypatch):
    monkeypatch.delenv("VERASCOPE_POWER_TIMEOUT", raising=False)
    assert pc.TIMEOUT_LOTE == 60
    assert pc.timeout_vivo() == 8
    for timeout in (pc.timeout_vivo(), pc.TIMEOUT_LOTE):
        sesion = SesionFalsa()
        cliente_de(sesion, timeout=timeout).celda(0.0, 0.0, 1981, 2024)
        assert sesion.llamadas[0]["timeout"] == timeout


def test_timeout_vivo_se_lee_del_entorno(monkeypatch):
    monkeypatch.setenv("VERASCOPE_POWER_TIMEOUT", "3.5")
    assert pc.timeout_vivo() == 3.5


def test_url_se_lee_del_entorno_al_llamar(cliente_de, monkeypatch):
    sesion = SesionFalsa()
    cliente = cliente_de(sesion)
    monkeypatch.setenv("VERASCOPE_POWER_URL", "http://falso.local/power")
    cliente.celda(0.0, 0.0, 1981, 2024)
    assert sesion.llamadas[0]["url"] == "http://falso.local/power"


def test_parsear_menos_999_es_nan_y_mes_13_se_ignora():
    v = pc.parsear(json_power(), MESES)
    assert set(v) == set(pc.VARIABLES_POWER)
    assert all(a.dtype == np.float32 and a.size == 3 for a in v.values())
    assert v["PRECTOTCORR"][0] == pytest.approx(1.5)
    assert math.isnan(v["PRECTOTCORR"][1])
    assert np.isnan(v["GWETROOT"]).all()
    assert not (np.concatenate(list(v.values())) <= -998).any()
    assert np.allclose(v["T2M"], [25.0, 26.0, 27.0])
    # El mes "13" es el promedio anual: aunque se pida, no entra en la serie.
    con_13 = pc.parsear(json_power(), ["2000-01", "2000-13"])
    assert con_13["T2M"][0] == pytest.approx(25.0) and math.isnan(con_13["T2M"][1])


def test_parsear_respeta_fill_value_del_encabezado():
    datos = json_power(relleno=-99.0)
    datos["properties"]["parameter"]["T2M"]["200002"] = -99.0
    assert math.isnan(pc.parsear(datos, MESES)["T2M"][1])


def test_429_espera_creciente_y_luego_responde(cliente_de, esperas):
    sesion = SesionFalsa(Respuesta(429), Respuesta(429), Respuesta(200))
    assert cliente_de(sesion).celda(0.0, 0.0, 1981, 2024) == json_power()
    assert len(sesion.llamadas) == 3
    assert len(esperas) == 2 and esperas[0] > 0 and esperas[1] > esperas[0]


def test_5xx_se_reintenta(cliente_de, esperas):
    sesion = SesionFalsa(Respuesta(503), Respuesta(200))
    assert cliente_de(sesion).celda(0.0, 0.0, 1981, 2024) == json_power()
    assert len(sesion.llamadas) == 2 and len(esperas) == 1


def test_timeout_es_power_lento(cliente_de):
    sesion = SesionFalsa(requests.Timeout("lento"))
    with pytest.raises(pc.PowerLento) as e:
        cliente_de(sesion, timeout=8).celda(0.0, 0.0, 1981, 2024)
    assert len(sesion.llamadas) == 1
    assert "8" in str(e.value) and "POWER" in str(e.value)


def test_reintentos_agotados_es_power_error(cliente_de, esperas):
    sesion = SesionFalsa(Respuesta(429))
    with pytest.raises(pc.PowerError) as e:
        cliente_de(sesion, intentos=3).celda(0.0, 0.0, 1981, 2024)
    assert len(sesion.llamadas) == 3
    assert esperas == sorted(esperas) and len(esperas) == 2
    assert "POWER" in str(e.value) and "3 intentos" in str(e.value)
    assert not issubclass(pc.PowerLento, pc.PowerError)


def test_pausa_de_un_segundo_entre_peticiones(esperas):
    assert pc.ClientePower(pc.TIMEOUT_LOTE).pausa == 1.0
    sesion = SesionFalsa()
    cliente = pc.ClientePower(60, pausa=1.0, sesion=sesion, dormir=esperas.append)
    cliente.celda(0.0, 0.0, 1981, 2024)
    cliente.celda(0.5, 0.0, 1981, 2024)
    assert len(esperas) == 1 and 0 < esperas[0] <= 1.0


def test_guarda_respuesta_cruda_comprimida(cliente_de, tmp_path):
    cliente_de(SesionFalsa(), crudo=tmp_path).celda(-5.0, -80.5, 1981, 2024)
    assert [f.name for f in tmp_path.iterdir()] == ["power_-05.00_-080.50.json.gz"]


def test_no_importa_fastapi():
    import ast
    import inspect

    arbol = ast.parse(inspect.getsource(pc))
    nombres = {
        a.name if isinstance(n, ast.Import) else n.module
        for n in ast.walk(arbol)
        if isinstance(n, (ast.Import, ast.ImportFrom))
        for a in (n.names if isinstance(n, ast.Import) else [n])
    }
    assert not any(str(x).startswith(("fastapi", "app.api", "app.estadistica")) for x in nombres)


def test_preparador_usa_la_misma_implementacion():
    pytest.importorskip("verascope_datos")
    from verascope_datos.fuentes import power

    assert power.parsear is pc.parsear
    assert issubclass(power.ClientePower, pc.ClientePower)
    assert power.PowerError is pc.PowerError and power.PowerLento is pc.PowerLento


def test_preparador_conserva_su_firma_de_lote(monkeypatch):
    pytest.importorskip("verascope_datos")
    from verascope_datos.fuentes import power

    monkeypatch.setattr(power.config, "ANIO_FIN", 2020)  # lo que hace `--fin 2020`
    sesion = SesionFalsa()
    cliente = power.ClientePower(pausa=0, sesion=sesion)
    cliente.celda(-5.0, -80.5)
    llamada = sesion.llamadas[0]
    assert llamada["timeout"] == pc.TIMEOUT_LOTE
    assert (llamada["params"]["start"], llamada["params"]["end"]) == (1981, 2020)


def test_preparador_no_reintenta_cuando_power_se_pasa_del_timeout():
    power = pytest.importorskip("verascope_datos.fuentes.power")
    llamadas = []

    class SesionLenta:
        def get(self, *args, **kwargs):
            llamadas.append(kwargs.get("timeout"))
            raise requests.Timeout("lento")

    cliente = power.ClientePower(pausa=0, sesion=SesionLenta(), dormir=lambda s: None)
    with pytest.raises(power.PowerLento, match="Inténtalo más tarde"):
        cliente.celda(-5.0, -80.5)
    assert llamadas == [60]
