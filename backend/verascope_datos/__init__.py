"""Delega al paquete verascope_datos instalado para evitar namespace package shadowing.

Cuando `backend/` está en sys.path, Python encuentra `backend/verascope_datos/`
como namespace package y sombra el paquete editable. Este archivo convierte la
carpeta en un paquete regular que delega al anidado en `verascope_datos/`.
"""

import importlib.util
import sys
from pathlib import Path

_real_path = Path(__file__).parent / "verascope_datos"

# Cargar el __init__.py del paquete real directamente, sin pasar por el
# sistema de imports (que volvería a este archivo).
_spec = importlib.util.spec_from_file_location(
    "verascope_datos",
    _real_path / "__init__.py",
    submodule_search_locations=[str(_real_path)],
)
_real = importlib.util.module_from_spec(_spec)
sys.modules["verascope_datos"] = _real
_spec.loader.exec_module(_real)

# Copiar todo al módulo actual (el que Python ya creó para este __init__.py)
for _name in dir(_real):
    setattr(sys.modules[__name__], _name, getattr(_real, _name))

__path__ = _real.__path__
__version__ = _real.__version__
