"""V1–V5 · NASA POWER: una petición por celda trae las 5 variables, de 1981 al último año completo.

Adaptador fino: la implementación única vive en ``app.datos.power_client`` (la API).
Aquí solo se fijan los valores del lote: timeout de 60 s, pausa de ``config`` y la
ventana de ``config`` (``--fin`` cambia ``config.ANIO_FIN`` en caliente).
"""
from app.datos.power_client import (  # noqa: F401
    TIMEOUT_LOTE,
    VARIABLES_POWER,
    PowerError,
    PowerLento,
    parsear,
)
from app.datos.power_client import ClientePower as _ClientePower

from .. import config


class ClientePower(_ClientePower):
    def __init__(self, pausa=config.POWER_PAUSA_S, intentos=4, sesion=None, crudo=None,
                 timeout=config.POWER_TIMEOUT_S, url=None, **kw):
        super().__init__(timeout, pausa=pausa, intentos=intentos, sesion=sesion, url=url,
                         crudo=crudo, **kw)

    def celda(self, lat, lon, anio_inicio=None, anio_fin=None):
        return super().celda(lat, lon, anio_inicio or config.ANIO_INICIO,
                             anio_fin or config.ANIO_FIN)
