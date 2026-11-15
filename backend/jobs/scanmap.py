"""Escaneo de ScanMap: 4235 celdas × 5 variables (guía §9; issue #5).

    cd backend
    python -m jobs.scanmap                     # usa VERASCOPE_DATOS o backend/data
    python -m jobs.scanmap --datos /data --procesos 4
    python -m jobs.scanmap --rearmar-tabla     # vuelve a armar tabla/ desde el casillero

No duplica nada: arma `tabla/` y calcula con el preparador (`verascope_datos.calcular`),
que a su vez usa el motor único de `app/estadistica/` (la misma `analizar_celda` que
`analyze`). Este job agrega el **estado del escaneo** que lee la API: `en_curso`
mientras calcula (con un avance aproximado de celdas listas) y `completo` al terminar.
Si el cálculo se corta, el estado queda en `en_curso` y basta con volver a correrlo.
"""

from __future__ import annotations

import argparse
import sys

try:
    from verascope_datos.variables import POWER

    from verascope_datos import calcular, config
except ImportError as error:  # pragma: no cover - mensaje para quien lo corre a mano
    raise SystemExit(
        "Falta el preparador de datos. Instálalo con: pip install -e verascope_datos"
    ) from error

from app.datos.escaneo import COMPLETO, EN_CURSO, escribir_estado


def correr(datos=None, procesos: int | None = None, rearmar_tabla: bool = False):
    """Arma `tabla/` si falta (o si se pide), calcula `resultados.parquet` y marca el estado.

    Devuelve el `DataFrame` de resultados. `celdas_listas` avanza con las series
    calculadas ÷ 5 variables (aproximado: sobre el mar falta la humedad del suelo) y al
    final es el número de celdas con al menos una serie válida.
    """
    rutas = config.rutas(datos)
    total = len(config.rejilla())
    escribir_estado(rutas.base, EN_CURSO, 0, total)
    if rearmar_tabla or not (rutas.tabla / "meses.json").exists():
        calcular.armar_tabla(rutas)

    series_listas = 0

    def avance(n_series: int) -> None:
        nonlocal series_listas
        series_listas += int(n_series)
        escribir_estado(rutas.base, EN_CURSO, min(total, series_listas // len(POWER)), total)

    df = calcular.calcular_resultados(rutas, procesos=procesos, avance=avance)
    escribir_estado(rutas.base, COMPLETO, int(df.celda.nunique()), total)
    return df


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m jobs.scanmap", description="Escaneo de ScanMap sobre la rejilla."
    )
    parser.add_argument(
        "--datos", help="carpeta de datos (por defecto, VERASCOPE_DATOS o backend/data)"
    )
    parser.add_argument("--procesos", type=int, default=None, help="procesos en paralelo")
    parser.add_argument(
        "--rearmar-tabla", action="store_true", help="vuelve a armar tabla/ desde el casillero"
    )
    args = parser.parse_args(argv)
    df = correr(args.datos, procesos=args.procesos, rearmar_tabla=args.rearmar_tabla)
    print(
        f"Escaneo completo: {df.celda.nunique()} celdas con datos, {len(df)} series, "
        f"{(df.veredicto != 'sin_tendencia').sum()} con tendencia."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
