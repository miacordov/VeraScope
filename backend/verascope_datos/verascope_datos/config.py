"""Configuración del proyecto. Todo lo que el equipo podría querer cambiar está aquí."""
import datetime as _dt
import os
from dataclasses import dataclass, field
from pathlib import Path

# Ventana de años: desde 1981 (inicio de POWER/MERRA-2) hasta el último año completo.
ANIO_INICIO = 1981
ANIO_FIN = int(os.environ.get("VERASCOPE_FIN", _dt.date.today().year - 1))

# Rejilla de ScanMap: 34°S–34°N, de 90°E a 30°O, paso de 2° (35 × 121 = 4235 celdas)
REJILLA_LAT = (-34, 34)
REJILLA_LON_0_360 = (90, 330)
REJILLA_PASO = 2.0

# Celda de análisis en vivo (malla de POWER)
CELDA = 0.5

# NASA POWER
POWER_URL = os.environ.get("VERASCOPE_POWER_URL", "https://power.larc.nasa.gov/api/temporal/monthly/point")
POWER_PAUSA_S = 1.0          # ~1 petición por segundo: POWER puede bloquear a quien insiste
POWER_TIMEOUT_S = 60


@dataclass(frozen=True)
class Lugar:
    id: str
    nombre: str
    lat: float
    lon: float


# Lugares de las demos: se descargan primero y alimentan la capa precalculada (V8–V12).
LUGARES_DEMO = (
    Lugar("piura", "Piura (Perú)", -5.2, -80.6),
    Lugar("borneo", "Borneo (Indonesia)", -2.0, 116.0),
    Lugar("norte_australia", "Norte de Australia", -14.0, 132.0),
)


@dataclass
class Rutas:
    base: Path

    @property
    def casillero(self): return self.base / "casillero.sqlite"
    @property
    def tabla(self): return self.base / "tabla"
    @property
    def resultados(self): return self.base / "resultados.parquet"
    @property
    def demos(self): return self.base / "demo"
    @property
    def crudo(self): return self.base / "crudo"
    @property
    def paquetes(self): return self.base / "paquetes"

    def crear(self):
        for p in (self.base, self.tabla, self.demos, self.crudo, self.paquetes):
            p.mkdir(parents=True, exist_ok=True)
        return self


def carpeta_datos_por_defecto() -> Path:
    """$VERASCOPE_DATOS; si no está, backend/data del repo VeraScope (la misma que lee la API); si no, ./datos."""
    if os.environ.get("VERASCOPE_DATOS"):
        return Path(os.environ["VERASCOPE_DATOS"])
    backend = Path(__file__).resolve().parents[2]       # <repo>/backend/verascope_datos/verascope_datos/config.py
    if (backend / "verascope_datos").is_dir() and (backend / "data").is_dir():
        return backend / "data"
    return Path("datos")


def rutas(base=None) -> Rutas:
    return Rutas(Path(base) if base else carpeta_datos_por_defecto()).crear()


def cuantizar(valor, paso=CELDA):
    return round(round(valor / paso) * paso, 4)


def rejilla(paso=None):
    """Celdas de ScanMap como (lat, lon) con lon en −180..180."""
    import numpy as np
    paso = paso or REJILLA_PASO
    lats = np.arange(REJILLA_LAT[0], REJILLA_LAT[1] + 1e-9, paso)
    lons = np.arange(REJILLA_LON_0_360[0], REJILLA_LON_0_360[1] + 1e-9, paso)
    return [(float(a), float(o - 360 if o > 180 else o)) for a in lats for o in lons]


def meses(inicio=ANIO_INICIO, fin=None):
    fin = fin or ANIO_FIN
    return [f"{y}-{m:02d}" for y in range(inicio, fin + 1) for m in range(1, 13)]
