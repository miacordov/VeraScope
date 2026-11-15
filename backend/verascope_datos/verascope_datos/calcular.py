"""Paso 3: arma la tabla gigante, corre el motor sobre cada celda y escribe la lista de resultados."""
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd

from app.datos.indices import ventana_valida  # misma regla de ventana que el backend
from app.estadistica.celda import analizar_celda  # el mismo motor que la API en vivo
from app.estadistica.constantes import ALFA, MIN_MESES
from app.estadistica.fdr import benjamini_hochberg
from app.estadistica.veredicto import estado, significativa

from . import config
from .almacen import Casillero, lugar_celda
from .variables import INDICES, POWER, POR_CODIGO


def armar_tabla(rutas, avance=None):
    """La tabla gigante: una matriz celdas × meses (float32) por variable, más índices y metadatos."""
    meses = config.meses(); celdas = config.rejilla()
    cas = Casillero(rutas.casillero)
    for cod in POWER:
        M = np.full((len(celdas), len(meses)), np.nan, dtype=np.float32)
        for k, (la, lo) in enumerate(celdas):
            M[k] = cas.leer_alineada(cod, lugar_celda(la, lo), meses)
        np.save(rutas.tabla / f"{cod}.npy", M)
        if avance:
            avance(cod)
    for cod in INDICES + ["CO2"]:
        np.save(rutas.tabla / f"{cod}.npy", cas.leer_alineada(cod, "indice", meses))
    np.save(rutas.tabla / "celdas.npy", np.array(celdas, dtype=np.float32))
    (rutas.tabla / "meses.json").write_text(json.dumps(meses))
    cas.cerrar()
    return len(celdas), len(meses)


def _trabajo(args):
    cod, filas, oni, cal, desde = args
    out = []
    for k, fila in filas:
        r = analizar_celda(fila, cal, oni, cod)
        if r is not None:
            out.append({**r.fila_escaneo(), "variable": cod, "celda": k})
    return out


def calcular_resultados(rutas, procesos=None, avance=None, minimo_celdas=0):
    meses = json.loads((rutas.tabla / "meses.json").read_text())
    celdas = np.load(rutas.tabla / "celdas.npy")
    oni = np.load(rutas.tabla / "ONI.npy").astype(float)
    a, b = ventana_valida(oni)
    if b - a < MIN_MESES:
        raise RuntimeError("El índice ONI no cubre al menos 10 años de la ventana: corre primero el comando 'indices'.")
    cal = np.array([int(m[5:7]) for m in meses])[a:b]
    filas = []
    for cod in POWER:
        f = rutas.tabla / f"{cod}.npy"
        if not f.exists():
            continue
        M = np.load(f).astype(float)[:, a:b]
        lote = [(k, M[k]) for k in range(M.shape[0]) if np.isfinite(M[k]).mean() > 0.9]
        tam = max(1, len(lote) // (8 * (procesos or 4)) or 1)
        filas += [(cod, lote[i:i + tam], oni[a:b], cal, meses[a]) for i in range(0, len(lote), tam)]
    res = []
    with ProcessPoolExecutor(max_workers=procesos, mp_context=multiprocessing.get_context("spawn")) as ex:
        for args, parte in zip(filas, ex.map(_trabajo, filas)):
            res += parte
            if avance:
                avance(len(args[1]))
    if not res:
        raise RuntimeError("No hay series completas para calcular: corre primero el comando 'power'.")
    df = pd.DataFrame(res)
    df["lat"] = celdas[df.celda, 0]; df["lon"] = celdas[df.celda, 1]
    # BH (cálculo C14) en dos familias: tendencia original y sin El Niño.
    df["p_original_ajustado"] = benjamini_hochberg(df.p_original.to_numpy())
    df["p_ajustado"] = benjamini_hochberg(df.p.to_numpy())
    # Decisión de B3 (L13, diferencia 3): p_enso también se corrige, una familia por variable.
    df["p_enso_ajustado"] = df.groupby("variable").p_enso.transform(lambda p: benjamini_hochberg(p.to_numpy()))
    df["veredicto"] = estado(significativa(df.p_original_ajustado.to_numpy(), ALFA),
                             significativa(df.p_ajustado.to_numpy(), ALFA)).tolist()
    df["unidad"] = [POR_CODIGO[c].unidad for c in df.variable]
    df["pareja"] = None
    _pares(df)
    df["ventana"] = f"{meses[a]} a {meses[b - 1]}"
    df.to_parquet(rutas.resultados, index=False)
    return df


def _pares(df, min_km=1500, max_pares=30):
    """Señales opuestas: tendencias significativas de signo contrario separadas más de 1500 km."""
    R = 6371.0
    sig = df.veredicto.isin(["cambio_robusto", "cambio_oculto"])
    for cod, g in df[sig].groupby("variable"):
        pos = g[g.pendiente > 0].sort_values("efecto", ascending=False)
        neg = g[g.pendiente < 0].sort_values("efecto")
        usados, k = set(), 0
        for ia, x in pos.iterrows():
            if k >= max_pares:
                break
            la1, lo1, la2, lo2 = map(np.radians, (x.lat, x.lon, neg.lat.values, neg.lon.values))
            d = 2 * R * np.arcsin(np.sqrt(np.sin((la2 - la1) / 2) ** 2 + np.cos(la1) * np.cos(la2) * np.sin((lo2 - lo1) / 2) ** 2))
            for ib, dist in zip(neg.index, d):
                if ib not in usados and dist > min_km:
                    df.loc[[ia, ib], "pareja"] = f"{cod}-{k}"; usados.add(ib); k += 1
                    break
