"""Elección de la carpeta de datos: $VERASCOPE_DATOS manda; si no, backend/data del repo; si no, ./datos."""
import json
from pathlib import Path

from verascope_datos import cli, config


def test_variable_de_entorno_manda(monkeypatch, tmp_path):
    monkeypatch.setenv("VERASCOPE_DATOS", str(tmp_path / "otra"))
    assert config.carpeta_datos_por_defecto() == tmp_path / "otra"


def test_sin_variable_usa_backend_data(monkeypatch):
    monkeypatch.delenv("VERASCOPE_DATOS", raising=False)
    backend = Path(config.__file__).resolve().parents[2]
    esperado = backend / "data" if (backend / "verascope_datos").is_dir() and (backend / "data").is_dir() else Path("datos")
    assert config.carpeta_datos_por_defecto() == esperado


def test_catalogo_json_sale_de_variables_py(tmp_path):
    destino = tmp_path / "variables.json"
    cli.main(["--datos", str(tmp_path / "d"), "variables", "--json", str(destino)])
    catalogo = json.loads(destino.read_text(encoding="utf-8"))
    assert [v["id"] for v in catalogo] == [f"V{i}" for i in range(1, 14)]
    assert {"codigo", "nombre", "unidad", "capa", "fuente", "desde", "nota"} <= set(catalogo[0])
