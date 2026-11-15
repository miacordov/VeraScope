"""Precalentamiento: descarga de una en una las celdas de las demos y ~50 ciudades.

    cd backend
    python -m jobs.precalentar                          # usa VERASCOPE_DATOS o backend/data
    python -m jobs.precalentar --datos /data             # carpeta explícita
    python -m jobs.precalentar --pausa 2.0               # pausa entre peticiones (por defecto 1 s)

Reutiliza el casillero (nivel 1 de la caché): si la celda ya tiene serie guardada,
no la pide otra vez a POWER. Nunca dispara dos peticiones en paralelo.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from app.datos import carpeta_datos
from app.datos.cache import Cache
from app.datos.celdas import celda, lugar_celda
from app.datos.power_client import (
    VARIABLES_POWER,
    ClientePower,
    PowerError,
    PowerLento,
    parsear,
    timeout_vivo,
)
from app.estadistica.constantes import ventana_fin

logger = logging.getLogger(__name__)

# ── Celdas de las demos ──────────────────────────────────────────────────────

DEMOS = [
    ("efecto-espejo (Piura)", -5.0, -80.5),
    ("senal-o-ruido", -6.0, -80.0),
]

# ── ~50 ciudades conocidas (lat, lon) ────────────────────────────────────────
# Ciudades costeras o continentales donde El Niño deja huella clara, distribuidas
# por los trópicos y subtrópicos. Coordenadas aproximadas al centro urbano.

CIUDADES = [
    ("Lima", -12.05, -77.05),
    ("Guayaquil", -2.2, -79.9),
    ("Quito", -0.2, -78.5),
    ("Bogotá", 4.6, -74.1),
    ("Santiago", -33.45, -70.65),
    ("Buenos Aires", -34.6, -58.45),
    ("São Paulo", -23.55, -46.65),
    ("Río de Janeiro", -22.9, -43.2),
    ("Recife", -8.05, -34.9),
    ("Ciudad de México", 19.4, -99.15),
    ("La Habana", 23.1, -82.35),
    ("San Juan", 18.45, -66.1),
    ("Miami", 25.75, -80.2),
    ("Los Ángeles", 34.05, -118.25),
    ("San Francisco", 37.75, -122.45),
    ("Houston", 29.75, -95.35),
    ("Nueva Orleans", 30.0, -90.05),
    ("Yakarta", -6.2, 106.85),
    ("Manila", 14.6, 120.95),
    ("Bangkok", 13.75, 100.5),
    ("Hanói", 21.0, 105.85),
    ("Singapur", 1.3, 103.85),
    ("Sídney", -33.85, 151.2),
    ("Melbourne", -37.8, 144.95),
    ("Darwin", -12.45, 130.85),
    ("Perth", -31.95, 115.85),
    ("Auckland", -36.85, 174.75),
    ("Bombay", 19.05, 72.85),
    ("Chennai", 13.05, 80.25),
    ("Colombo", 6.9, 79.85),
    ("Nairobi", -1.3, 36.8),
    ("Dar es Salaam", -6.8, 39.3),
    ("Maputo", -25.95, 32.6),
    ("Ciudad del Cabo", -33.9, 18.4),
    ("Dakar", 14.7, -17.45),
    ("Lagos", 6.45, 3.4),
    ("Accra", 5.55, -0.2),
    ("El Cairo", 30.05, 31.25),
    ("Tokio", 35.7, 139.75),
    ("Shanghái", 31.2, 121.45),
    ("Hong Kong", 22.3, 114.15),
    ("Taipéi", 25.05, 121.5),
    ("Seúl", 37.55, 127.0),
    ("Madrid", 40.4, -3.7),
    ("Lisboa", 38.7, -9.15),
    ("Roma", 41.9, 12.5),
    ("Atenas", 37.95, 23.7),
    ("Estambul", 41.0, 29.0),
    ("Honolulú", 21.3, -157.85),
    ("Panamá", 9.0, -79.5),
]


def _meses_ventana(inicio: int, fin: int) -> list[str]:
    return [f"{y}-{m:02d}" for y in range(inicio, fin + 1) for m in range(1, 13)]


def precalentar(
    datos=None,
    pausa: float = 1.0,
    dormir=time.sleep,
):
    """Descarga las celdas de las demos y las ciudades, de una en una.

    Devuelve (descargadas, omitidas, fallos).
    """
    carpeta = datos or carpeta_datos()
    cache = Cache(carpeta)
    cliente = ClientePower(timeout=timeout_vivo(), pausa=pausa, dormir=dormir)
    fin = ventana_fin()
    meses = _meses_ventana(1981, fin)

    todas = [(nombre, lat, lon) for nombre, lat, lon in DEMOS]
    todas.extend(CIUDADES)

    descargadas = 0
    omitidas = 0
    fallos = 0

    for nombre, lat_raw, lon_raw in todas:
        lat_q, lon_q = celda(lat_raw, lon_raw)
        llave = lugar_celda(lat_q, lon_q)

        # Si ya tiene al menos una variable, no repetir
        if cache.series.existe(VARIABLES_POWER[0], llave):
            logger.info("omitida %s (%+.2f, %+.2f) — ya en caché", nombre, lat_q, lon_q)
            omitidas += 1
            continue

        logger.info("descargando %s (%+.2f, %+.2f)…", nombre, lat_q, lon_q)
        try:
            respuesta = cliente.celda(lat_q, lon_q, 1981, fin)
            series = parsear(respuesta, meses)
            for codigo in VARIABLES_POWER:
                cache.series.guardar(
                    codigo,
                    llave,
                    meses[0],
                    series[codigo],
                    lat=lat_q,
                    lon=lon_q,
                )
            descargadas += 1
            logger.info("guardada %s (%+.2f, %+.2f)", nombre, lat_q, lon_q)
        except (PowerLento, PowerError) as e:
            logger.warning("fallo %s (%+.2f, %+.2f): %s", nombre, lat_q, lon_q, e)
            cache.series.fallo("precalentar", llave, str(e))
            fallos += 1

    cache.cerrar()
    logger.info(
        "precalentamiento terminado: %d descargadas, %d omitidas, %d fallos",
        descargadas,
        omitidas,
        fallos,
    )
    return descargadas, omitidas, fallos


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m jobs.precalentar",
        description="Descarga las celdas de las demos y ~50 ciudades conocidas.",
    )
    parser.add_argument("--datos", default=None, help="Carpeta de datos (default: VERASCOPE_DATOS)")
    parser.add_argument(
        "--pausa",
        type=float,
        default=1.0,
        help="Segundos entre peticiones (default: 1)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    descargadas, omitidas, fallos = precalentar(datos=args.datos, pausa=args.pausa)
    print(f"\nResultado: {descargadas} descargadas, {omitidas} omitidas, {fallos} fallos.")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
