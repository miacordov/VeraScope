"""Índices de El Niño de VeraScope: ONI y Niño 1+2, siempre desde archivos locales.

Reglas (backend/CLAUDE.md, sección 6):
- Ambos índices los publica el Climate Prediction Center de NOAA (ONI, NOAA CPC).
  Se bajan ANTES con el preparador (``verascope-datos indices``) y aquí solo se leen;
  este módulo nunca los pide en vivo.
- ONI: media móvil de 3 meses asignada a su mes central (DJF → enero).
- Niño 1+2: anomalía mensual; empieza en 1982-01 (antes no hay valor).
- Fase de un mes: ``nino`` si índice ≥ UMBRAL_FASE, ``nina`` si ≤ −UMBRAL_FASE,
  ``neutro`` en otro caso (simplificación declarada).
- La ventana efectiva va del primer al último mes con índice; escaneo y análisis
  en vivo usan esta misma regla (``ventana_valida`` / ``recortar``).

Es la implementación única: el preparador (``verascope_datos``) importa de aquí.
"""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

import numpy as np

from app.datos import carpeta_datos
from app.estadistica.constantes import UMBRAL_FASE

Fase = Literal["nino", "nina", "neutro"]

INDICES = ("ONI", "NINO12")
INICIO_NINO12 = "1982-01"
TEMPORADAS = ["DJF", "JFM", "FMA", "MAM", "AMJ", "MJJ", "JJA", "JAS", "ASO", "SON", "OND", "NDJ"]


def _a_serie(tabla: dict[str, float], meses: Sequence[str]) -> np.ndarray:
    return np.array([tabla.get(m, np.nan) for m in meses], dtype=np.float32)


def parsear_oni(texto: str, meses: Sequence[str]) -> np.ndarray:
    """Columnas SEAS YR TOTAL ANOM. Cada temporada de 3 meses va a su mes central (DJF → enero)."""
    t = {}
    for linea in texto.splitlines():
        p = linea.split()
        if len(p) >= 4 and p[0] in TEMPORADAS:
            try:
                t[f"{int(p[1])}-{TEMPORADAS.index(p[0]) + 1:02d}"] = float(p[3])
            except ValueError:
                continue
    return _a_serie(t, meses)


def parsear_nino12(texto: str, meses: Sequence[str]) -> np.ndarray:
    """sstoi.indices: YR MON NINO1+2 ANOM ... Se usa la anomalía de Niño 1+2, desde 1982-01."""
    t = {}
    for linea in texto.splitlines():
        p = linea.split()
        if len(p) >= 4 and p[0].isdigit() and p[1].isdigit():
            try:
                mes = f"{int(p[0])}-{int(p[1]):02d}"
                if mes >= INICIO_NINO12:
                    t[mes] = float(p[3])
            except ValueError:
                continue
    return _a_serie(t, meses)


def fase(valor: float) -> Fase:
    """Fase de El Niño de un mes según el índice."""
    v = float(valor)
    if math.isnan(v):
        raise ValueError("Mes sin índice de El Niño: no tiene fase; recorta la ventana primero.")
    if v >= UMBRAL_FASE:
        return "nino"
    if v <= -UMBRAL_FASE:
        return "nina"
    return "neutro"


def fases(indice: Sequence[float] | np.ndarray) -> list[Fase]:
    """Fase de cada mes de una serie de índice (sin meses faltantes)."""
    return [fase(v) for v in np.asarray(indice, dtype=float)]


def ventana_valida(indice):
    """Meses con índice de El Niño disponible (al final puede faltar el último trimestre)."""
    ok = np.where(np.isfinite(indice))[0]
    return (int(ok[0]), int(ok[-1]) + 1) if ok.size else (0, 0)


def recortar(meses: Sequence[str], serie, indice):
    """Recorta meses, serie e índice a la ventana con índice (misma regla que el escaneo)."""
    serie = np.asarray(serie)
    indice = np.asarray(indice)
    if not (len(meses) == len(serie) == len(indice)):
        raise ValueError("Los meses, la serie y el índice deben tener el mismo largo.")
    a, b = ventana_valida(indice)
    return list(meses[a:b]), serie[a:b], indice[a:b]


def cargar_indice(
    nombre: str, carpeta: Path | str | None = None, meses: Sequence[str] | None = None
) -> tuple[list[str], np.ndarray]:
    """Lee un índice local de ``tabla/`` (lo deja ahí el preparador) y lo devuelve por mes.

    Sin ``meses`` devuelve los de ``tabla/meses.json``; con ``meses`` alinea el índice a
    esos meses (NaN donde no hay valor).
    """
    nombre = str(nombre)
    if nombre not in INDICES:
        raise ValueError(f"Índice desconocido: {nombre}. Usa ONI o NINO12.")
    tabla = Path(carpeta) if carpeta is not None else carpeta_datos()
    tabla = tabla / "tabla"
    archivo, lista = tabla / f"{nombre}.npy", tabla / "meses.json"
    if not archivo.exists() or not lista.exists():
        raise FileNotFoundError(
            f"Falta el índice {nombre} en {tabla}: corre primero el comando 'indices' "
            "del preparador."
        )
    propios = json.loads(lista.read_text(encoding="utf-8"))
    valores = np.load(archivo).astype(float)
    if meses is None:
        return list(propios), valores
    por_mes = dict(zip(propios, valores))
    pedidos = list(meses)
    return pedidos, np.array([por_mes.get(m, np.nan) for m in pedidos], dtype=float)
