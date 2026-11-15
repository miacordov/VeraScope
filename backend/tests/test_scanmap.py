"""Pruebas de jobs/scanmap.py y app/datos/escaneo.py (guía §9 y §12; issue #5)."""

import json

import pandas as pd
import pytest

from app.contracts import Escaneo
from app.datos.celdas import rejilla
from app.datos.escaneo import ARCHIVO_ESTADO, escribir_estado, leer_estado
from tests.mundo_escaneo import CELDAS_CON_DATOS, armar_mundo

COLUMNAS_GUIA = {
    "variable",
    "celda",
    "lat",
    "lon",
    "pendiente_original",
    "p_original",
    "pendiente",
    "ic_bajo",
    "ic_alto",
    "p",
    "p_original_ajustado",
    "p_ajustado",
    "rezago",
    "r_enso",
    "p_enso",
    "colinealidad",
    "efecto",
    "meses",
    "veredicto",
    "unidad",
    "pareja",
    "ventana",
}


# ------------------------------------------------------------ estado del escaneo


def test_sin_nada_el_escaneo_esta_en_curso(tmp_path):
    estado = leer_estado(tmp_path)
    assert estado == {"estado": "en_curso", "celdas_listas": 0, "celdas_total": len(rejilla())}
    Escaneo.model_validate(estado)


def test_escribe_y_lee_el_estado(tmp_path):
    escribir_estado(tmp_path, "en_curso", 120, 4235)
    assert leer_estado(tmp_path) == {
        "estado": "en_curso",
        "celdas_listas": 120,
        "celdas_total": 4235,
    }
    escribir_estado(tmp_path, "completo", 4235, 4235)
    assert leer_estado(tmp_path)["estado"] == "completo"
    assert not list(tmp_path.glob("*.tmp"))  # escritura atómica: no quedan temporales


def test_paquete_instalado_sin_estado_cuenta_como_completo(tmp_path):
    (tmp_path / "resultados.parquet").write_bytes(b"x")
    total = len(rejilla())
    assert leer_estado(tmp_path) == {
        "estado": "completo",
        "celdas_listas": total,
        "celdas_total": total,
    }


def test_estado_ilegible_cuenta_como_en_curso(tmp_path):
    (tmp_path / ARCHIVO_ESTADO).write_text("{no es json")
    assert leer_estado(tmp_path)["estado"] == "en_curso"


@pytest.mark.parametrize("malo", ["terminado", ""])
def test_no_escribe_estados_fuera_del_contrato(tmp_path, malo):
    with pytest.raises(ValueError):
        escribir_estado(tmp_path, malo, 0, 1)


# ------------------------------------------------------------------- el job


@pytest.fixture
def rutas(tmp_path, monkeypatch):
    pytest.importorskip("verascope_datos.calcular")
    return armar_mundo(tmp_path, monkeypatch)


def test_correr_arma_la_tabla_calcula_y_marca_completo(rutas):
    from jobs.scanmap import correr

    df = correr(rutas.base, procesos=1)
    assert (rutas.tabla / "meses.json").exists() and (rutas.tabla / "PRECTOTCORR.npy").exists()
    assert COLUMNAS_GUIA <= set(df.columns)
    leido = pd.read_parquet(rutas.resultados)
    assert leido.shape == df.shape
    from verascope_datos import config

    estado = json.loads((rutas.base / ARCHIVO_ESTADO).read_text())
    assert estado == {
        "estado": "completo",
        "celdas_listas": CELDAS_CON_DATOS,
        "celdas_total": len(config.rejilla()),  # la rejilla del preparador (paso 8° aquí)
    }


def test_mientras_calcula_el_estado_es_en_curso(rutas, monkeypatch):
    from jobs import scanmap

    vistos = []
    original = scanmap.calcular.calcular_resultados

    def espia(r, procesos=None, avance=None):
        vistos.append(leer_estado(r.base)["estado"])
        avance(7)
        vistos.append(leer_estado(r.base))
        return original(r, procesos=procesos, avance=avance)

    monkeypatch.setattr(scanmap.calcular, "calcular_resultados", espia)
    scanmap.correr(rutas.base, procesos=1)
    assert vistos[0] == "en_curso"
    assert vistos[1]["estado"] == "en_curso" and vistos[1]["celdas_listas"] == 1  # 7 series / 5
    assert leer_estado(rutas.base)["estado"] == "completo"


def test_si_el_calculo_falla_el_estado_queda_en_curso(rutas, monkeypatch):
    from jobs import scanmap

    def roto(*a, **k):
        raise RuntimeError("se cortó")

    monkeypatch.setattr(scanmap.calcular, "calcular_resultados", roto)
    with pytest.raises(RuntimeError):
        scanmap.correr(rutas.base, procesos=1)
    assert leer_estado(rutas.base)["estado"] == "en_curso"


def test_no_rearma_la_tabla_si_ya_existe_salvo_que_se_pida(rutas, monkeypatch):
    from jobs import scanmap

    scanmap.correr(rutas.base, procesos=1)
    llamadas = []
    monkeypatch.setattr(scanmap.calcular, "armar_tabla", lambda r, avance=None: llamadas.append(1))
    scanmap.correr(rutas.base, procesos=1)
    assert llamadas == []
    scanmap.correr(rutas.base, procesos=1, rearmar_tabla=True)
    assert llamadas == [1]


def test_cli_corre_el_job(rutas, capsys):
    from jobs.scanmap import main

    assert main(["--datos", str(rutas.base), "--procesos", "1"]) == 0
    salida = capsys.readouterr().out
    assert "completo" in salida and str(CELDAS_CON_DATOS) in salida
