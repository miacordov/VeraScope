"""Configuración y exportaciones del catálogo del preparador, sin red."""
import json
from dataclasses import asdict
from pathlib import Path

import pytest
from verascope_datos.variables import VARIABLES

from verascope_datos import cli, config

PUBLICO = Path(__file__).resolve().parents[2] / "app" / "catalogo" / "variables.json"


@pytest.fixture(autouse=True)
def consola_sin_saltos(monkeypatch):
    monkeypatch.setattr(cli.con, "width", 1000)


def test_variable_de_entorno_manda(monkeypatch, tmp_path):
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path / "otra"))
    assert config.carpeta_datos_por_defecto() == tmp_path / "otra"


def test_sin_variable_usa_backend_data(monkeypatch):
    monkeypatch.delenv("VERASCOPE_DATOS", raising=False)
    backend = Path(config.__file__).resolve().parents[2]
    en_repo = (backend / "verascope_datos").is_dir() and (backend / "data").is_dir()
    esperado = backend / "data" if en_repo else Path("datos")
    assert config.carpeta_datos_por_defecto() == esperado


@pytest.mark.parametrize("pantalla", [False, True])
def test_catalogo_json_sale_de_variables_py(tmp_path, capsys, pantalla):
    destino = tmp_path / "variables.json"
    salida = "-" if pantalla else str(destino)
    assert cli.main(["--datos", str(tmp_path / "d"), "variables", "--json", salida]) is None
    captura = capsys.readouterr()
    assert captura.err == ""
    if pantalla:
        texto = captura.out
    else:
        assert captura.out == f"✔ Catálogo escrito en {destino}\n"
        texto = destino.read_text(encoding="utf-8")
    catalogo = json.loads(texto)
    assert set(catalogo) == {"variables", "indices"}
    assert [v["id"] for v in catalogo["variables"]] == [
        "PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M",
    ]
    assert [v["id"] for v in catalogo["indices"]] == ["ONI", "NINO12"]
    for v in catalogo["variables"] + catalogo["indices"]:
        assert set(v) == {"id", "nombre", "definicion", "unidad", "fuente"}
        assert all(isinstance(valor, str) and valor for valor in v.values())
    assert catalogo == json.loads(PUBLICO.read_text(encoding="utf-8"))
    # El contrato se prueba cuando está disponible el entorno del backend.
    contracts = pytest.importorskip("app.contracts")
    assert contracts.VariablesRespuesta.model_validate(catalogo).model_dump(mode="json") == catalogo


@pytest.mark.parametrize("pantalla", [False, True])
def test_catalogo_json_completo_conserva_exportacion_tecnica(tmp_path, capsys, pantalla):
    destino = tmp_path / "completo.json"
    salida = "-" if pantalla else str(destino)
    assert cli.main([
        "--datos", str(tmp_path / "d"), "variables", "--json-completo", salida,
    ]) is None
    captura = capsys.readouterr()
    assert captura.err == ""
    if pantalla:
        texto = captura.out
    else:
        assert captura.out == f"✔ Catálogo escrito en {destino}\n"
        texto = destino.read_text(encoding="utf-8")
    catalogo = json.loads(texto)
    assert [v["id"] for v in catalogo] == [f"V{i}" for i in range(1, 14)]
    assert catalogo == [asdict(v) for v in VARIABLES]
    assert {"codigo", "nombre", "unidad", "capa", "fuente", "desde", "nota"} <= set(catalogo[0])


def test_variables_sin_exportar_conserva_tabla(tmp_path, capsys):
    assert cli.main(["--datos", str(tmp_path), "variables"]) is None
    captura = capsys.readouterr()
    assert captura.err == ""
    assert "Las 13 variables de VeraScope" in captura.out
    for v in VARIABLES:
        assert v.id in captura.out


def test_ayuda_describe_ambas_exportaciones(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["variables", "--ayuda"])
    assert exc.value.code == 0
    captura = capsys.readouterr()
    assert captura.err == ""
    assert "--json ARCHIVO" in captura.out
    assert "--json-completo ARCHIVO" in captura.out
    assert "5 variables y 2 índices" in captura.out
    assert "13 variables" in captura.out
