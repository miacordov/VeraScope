"""Integración de datos del backend; B2 aporta sus implementaciones."""

import os
from pathlib import Path

_POR_DEFECTO = Path(__file__).resolve().parents[2] / "data"


def carpeta_datos() -> Path:
    """Carpeta de datos de la API: `$VERASCOPE_DATOS` o, si no está, `backend/data`."""
    valor = os.environ.get("VERASCOPE_DATOS", "").strip()
    return Path(valor) if valor else _POR_DEFECTO
