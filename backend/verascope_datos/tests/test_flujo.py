"""Prueba de punta a punta sin red: índices → POWER (con cortes) → satélites → cálculo → demos → paquete → instalar."""
import json
import tarfile

import numpy as np
import pandas as pd
import pytest

from verascope_datos import cli, config
from verascope_datos.almacen import Casillero
from verascope_datos.fuentes.power import parsear
from verascope_datos.variables import VARIABLES

from . import simulados


@pytest.fixture(scope="module")
def entorno(tmp_path_factory):
    base = tmp_path_factory.mktemp("vs")
    config.ANIO_FIN = 2024
    simulados.textos_noaa(base / "noaa")
    simulados.archivos_satelite(base / "sat")
    return base


def correr(entorno, *args, cliente=None):
    datos = entorno / "datos"
    if cliente is not None:                      # inyecta el POWER falso
        original = cli.cmd_power
        cli.cmd_power = lambda a, r: original(a, r, cliente=cliente)
        try:
            cli.main(["--datos", str(datos), "--fin", "2024", *args])
        finally:
            cli.cmd_power = original
    else:
        cli.main(["--datos", str(datos), "--fin", "2024", *args])
    return config.rutas(datos)


def test_parsear_power_ignora_mes_13_y_relleno():
    meses = config.meses(2000, 2001)
    d = simulados.PowerFalso().celda(-34.0, 0.0)          # océano: humedad del suelo con −999
    v = parsear(d, meses)
    assert v["PRECTOTCORR"].size == 24 and np.isfinite(v["PRECTOTCORR"]).all()
    assert np.isnan(v["GWETROOT"]).all()


def test_flujo_completo(entorno):
    r = correr(entorno, "indices", "--carpeta", str(entorno / "noaa"))
    cas = Casillero(r.casillero)
    assert all(cas.existe(c, "indice") for c in ("ONI", "NINO12", "CO2"))
    cas.cerrar()

    # POWER con un corte cada 7 llamadas y en varias corridas: debe retomar sin repetir
    falso = simulados.PowerFalso(fallar_cada=7)
    correr(entorno, "power", "--paso", "8", "--pausa", "0", "--limite", "40", cliente=falso)
    primera = falso.llamadas
    correr(entorno, "power", "--paso", "8", "--pausa", "0", cliente=falso)
    correr(entorno, "power", "--paso", "8", "--pausa", "0", cliente=simulados.PowerFalso())
    cas = Casillero(r.casillero)
    total = len(config.rejilla(8)) + len(config.LUGARES_DEMO)
    assert len(cas.lugares("PRECTOTCORR")) == total
    assert len(cas.lugares("PRECTOTCORR", "demo:")) == 3
    assert primera == 40 and not [f for f in cas.fallos() if f[0] == "power"]
    cas.cerrar()

    correr(entorno, "satelites", "--archivos-locales", str(entorno / "sat"))
    cas = Casillero(r.casillero)
    for cod in ("IMERG", "GLDAS_EVAP", "GLDAS_ESCORRENTIA", "GLDAS_SUELO", "NDVI"):
        assert len(cas.lugares(cod, "demo:")) == 3, cod
    meses = config.meses()
    piura = cas.leer_alineada("IMERG", "demo:piura", meses)
    borneo = cas.leer_alineada("IMERG", "demo:borneo", meses)
    ok = np.isfinite(piura) & np.isfinite(borneo)
    assert ok.sum() == 24 and np.corrcoef(piura[ok], borneo[ok])[0, 1] < -0.9   # efecto espejo
    ndvi = cas.leer_alineada("NDVI", "demo:borneo", meses)
    assert np.nanmax(ndvi) <= 1.0 and np.nanmin(ndvi) >= -0.2                  # factor 0.0001 aplicado
    cas.cerrar()

    correr(entorno, "calcular", "--paso", "8", "--procesos", "2")
    df = pd.read_parquet(r.resultados)
    t2m = df[df.variable == "T2M"]
    assert (t2m.veredicto == "cambio_robusto").mean() > 0.9                    # calentamiento simulado
    assert set(df.variable) == {"PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M"}
    assert (r.tabla / "T2M.npy").exists() and np.load(r.tabla / "T2M.npy").shape[1] == len(meses)

    correr(entorno, "demos")
    doc = json.loads((r.demos / "piura.json").read_text())
    assert len(doc["variables"]) == 13 and len(doc["variables"]["PRECTOTCORR"]["valores"]) == len(meses)

    correr(entorno, "empaquetar")
    paquete = next(r.paquetes.glob("*.tar.gz"))
    with tarfile.open(paquete) as tar:
        nombres = tar.getnames()
    assert "casillero.sqlite" in nombres and "manifiesto.json" in nombres

    otro = entorno / "otro_integrante"
    cli.main(["--datos", str(otro), "instalar", str(paquete)])
    assert (otro / "resultados.parquet").exists()
    correr(entorno, "estado")


def test_catalogo_tiene_13_variables():
    assert [v.id for v in VARIABLES] == [f"V{k}" for k in range(1, 14)]
