"""Umbrales acordados del motor mensual; no se realizan cálculos aquí."""

import os
from datetime import date

ALFA = 0.05
FDR_Q = 0.05
REZAGO_MAX = 6
LAG_HAMED_RAO = 12
MIN_MESES = 120
AVISO_POTENCIA_MESES = 240
MAX_HUECO = 2
MAX_FALTANTE = 0.10
ESCALA_DECADA = 120
UMBRAL_FASE = 0.5
COLINEALIDAD_MAX = 0.3
UMBRAL_INUSUAL = 2
UMBRAL_COINCIDENCIA = 1
KM_MIN_DESTINO = 1500
KM_SEP_DESTINOS = 1000
MAX_LINEAS_OPUESTAS = 3
MAX_LINEAS_IGUALES = 2
NEFF_MIN_PRUEBA_T = 10
NEFF_PISO = 3
VERSION_METODO = 2
GRILLA_PASO = 2.0
CELDA = 0.5


def ventana_fin() -> int:
    """Último año cerrado configurado, sin consultar fuentes externas."""
    return int(os.environ.get("VERASCOPE_FIN", date.today().year - 1))


def __getattr__(nombre: str):
    # Se resuelve al consultar para no congelar la configuración al importar.
    if nombre == "PERIODOS_DEFECTO":
        return ((1981, 2001), (2003, ventana_fin()))
    raise AttributeError(nombre)
