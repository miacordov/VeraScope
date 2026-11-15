"""VeraScope · Cargador de datos: baja, ordena, calcula y empaqueta las 13 variables del proyecto."""

import sys
from pathlib import Path

__version__ = "1.1.0"

# Una sola implementación compartida: el preparador importa los módulos de
# `app.datos` del backend (cliente de POWER, validación e índices). Integrado en
# el repositorio, `backend/` está dos carpetas arriba de este paquete.
try:
    import app.datos  # noqa: F401
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
