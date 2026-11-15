"""Mundo chico para probar el escaneo: casillero con series sintéticas sobre una rejilla gruesa.

Usa el preparador (`verascope_datos`) tal cual: `Casillero.guardar` para las series y
`config.REJILLA_PASO` / `config.ANIO_FIN` para achicar la rejilla y la ventana. Las
pruebas que lo usan se omiten si el preparador no está instalado.
"""

import numpy as np

from tests.sinteticas import ar1, generador, serie

PASO = 8.0
ANIO_FIN = 2000  # 1981–2000 = 240 meses
N_MESES = 240
CELDAS_CON_DATOS = 12  # las primeras celdas de la rejilla gruesa; el resto queda vacío


def armar_mundo(tmp_path, monkeypatch):
    """Devuelve las `rutas` del preparador con un casillero sintético ya guardado."""
    from verascope_datos.almacen import Casillero, lugar_celda
    from verascope_datos.variables import POWER

    from verascope_datos import config

    monkeypatch.setattr(config, "REJILLA_PASO", PASO)
    monkeypatch.setattr(config, "ANIO_FIN", ANIO_FIN)
    rutas = config.rutas(tmp_path / "datos")
    oni = ar1(N_MESES, 0.93, 1.0, generador(9000))
    cas = Casillero(rutas.casillero)
    cas.guardar("ONI", "indice", "1981-01", oni.astype(np.float32))
    for k, (lat, lon) in enumerate(config.rejilla()[:CELDAS_CON_DATOS]):
        for j, cod in enumerate(POWER):
            s = serie(
                generador(9100 + 10 * k + j),
                n=N_MESES,
                beta_dec=0.3 * (k % 4) - 0.4,
                gamma=(k % 3 - 1) * 0.8,
                rezago=k % 4,
            )
            valores = s.valores + 20 + (k + 1) * 0.5 * oni
            if k == 5 and cod == "T2M":
                valores[100:103] = np.nan  # un hueco de 3 meses: la serie se descarta
            cas.guardar(cod, lugar_celda(lat, lon), "1981-01", valores.astype(np.float32), lat, lon)
    cas.cerrar()
    return rutas
