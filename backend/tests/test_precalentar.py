"""Celdas de las demos (decisión de B1 y F3, 15-nov-2026).

La demo de Piura usa la celda de ScanMap (−6, −80), no el punto (−5.0, −80.5): así la
tarjeta, el veredicto del escaneo y las líneas de teleconexión salen de la misma celda.
"""

from app.datos.celdas import celda, rejilla
from jobs.precalentar import DEMOS


def test_las_celdas_de_las_demos_estan_en_la_rejilla_de_scanmap():
    malla = set(rejilla())
    for nombre, lat, lon in DEMOS:
        assert celda(lat, lon) in malla, nombre


def test_piura_usa_la_celda_de_scanmap():
    piura = [(lat, lon) for nombre, lat, lon in DEMOS if "Piura" in nombre]
    assert piura == [(-6.0, -80.0)]
