"""Catálogo de las 13 variables de VeraScope (ver el informe estadístico, sección 4)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Variable:
    id: str            # V1..V13
    codigo: str        # nombre en la fuente
    nombre: str        # nombre en la interfaz
    unidad: str
    capa: str          # "vivo", "indice", "precalculada", "contexto"
    fuente: str
    desde: int         # primer año con datos
    nota: str = ""
    definicion: str = ""


VARIABLES = (
    Variable("V1", "PRECTOTCORR", "Lluvia", "mm/día", "vivo", "MERRA-2 vía NASA POWER", 1981,
             definicion="Precipitación que llega a la superficie, como promedio mensual."),
    Variable("V2", "T2M", "Temperatura del aire a 2 m", "°C", "vivo",
             "MERRA-2 vía NASA POWER", 1981,
             definicion=("Temperatura del aire a dos metros sobre la superficie; "
                         "no se expresa como cambio porcentual.")),
    Variable("V3", "GWETROOT", "Humedad del suelo, zona de raíces", "0 a 1", "vivo",
             "MERRA-2 vía NASA POWER", 1981,
             definicion=("Agua disponible para las raíces en los primeros 100 cm de suelo, "
                         "entre 0 y 1. No se interpreta sobre el mar.")),
    Variable("V4", "GWETTOP", "Humedad del suelo, superficie", "0 a 1", "vivo",
             "MERRA-2 vía NASA POWER", 1981,
             definicion=("Humedad de los primeros centímetros de suelo, entre 0 y 1. "
                         "No se interpreta sobre el mar.")),
    Variable("V5", "RH2M", "Humedad relativa a 2 m", "%", "vivo", "MERRA-2 vía NASA POWER", 1981,
             definicion=("Vapor de agua del aire frente al máximo posible a esa temperatura, "
                         "entre 0 y 100 %.")),
    Variable("V6", "ONI", "Índice Oceánico de El Niño", "°C", "indice", "ONI, NOAA CPC", 1950,
             "Anomalía Niño 3.4, media móvil de 3 meses, asignada al mes central",
             definicion=("Anomalía de temperatura en Niño 3.4, promediada en tres meses "
                         "y asignada al mes central.")),
    Variable("V7", "NINO12", "Niño 1+2", "°C", "indice", "Niño 1+2, NOAA CPC", 1982,
             "Anomalía mensual de temperatura del mar frente a Ecuador y el norte del Perú",
             definicion=("Anomalía mensual frente a la costa de Perú y Ecuador, "
                         "disponible desde 1982.")),
    Variable("V8", "IMERG", "Lluvia satelital (GPM IMERG)", "mm/día", "precalculada", "NASA GES DISC · GPM_3IMERGM v07", 1998,
             "Llega en mm/h; se multiplica por 24"),
    Variable("V9", "GLDAS_EVAP", "Evapotranspiración (GLDAS)", "mm/día", "precalculada", "NASA GES DISC · GLDAS_NOAH025_M v2.1", 2000,
             "Evap_tavg llega en kg m⁻² s⁻¹; se multiplica por 86 400"),
    Variable("V10", "GLDAS_ESCORRENTIA", "Escorrentía (GLDAS)", "mm/día", "precalculada", "NASA GES DISC · GLDAS_NOAH025_M v2.1", 2000,
             "Qs_acc + Qsb_acc, acumulados de 3 h; se multiplica por 8 (verificar en la guía de GLDAS)"),
    Variable("V11", "GLDAS_SUELO", "Humedad del suelo 0–10 cm (GLDAS)", "mm", "precalculada", "NASA GES DISC · GLDAS_NOAH025_M v2.1", 2000,
             "SoilMoi0_10cm_inst en kg m⁻² equivale a mm de agua"),
    Variable("V12", "NDVI", "Índice de vegetación (MODIS)", "adimensional", "precalculada", "NASA LP DAAC · MOD13A3 v061 vía AppEEARS", 2000,
             "Factor de escala 0.0001"),
    Variable("V13", "CO2", "CO₂ atmosférico (Mauna Loa)", "ppm", "contexto", "NOAA GML", 1958,
             "Solo contexto: no se correlaciona con nada"),
)

POR_CODIGO = {v.codigo: v for v in VARIABLES}
POWER = [v.codigo for v in VARIABLES if v.capa == "vivo"]
INDICES = ["ONI", "NINO12"]
SATELITE = [v.codigo for v in VARIABLES if v.capa == "precalculada"]


def catalogo_api() -> dict[str, list[dict[str, str]]]:
    """Proyecta el catálogo público sin incluir satélites ni variables de contexto."""
    def entrada(v: Variable) -> dict[str, str]:
        return {
            "id": v.codigo,
            "nombre": v.nombre,
            "definicion": v.definicion,
            "unidad": v.unidad,
            "fuente": v.fuente,
        }

    return {
        "variables": [entrada(v) for v in VARIABLES if v.capa == "vivo"],
        "indices": [entrada(POR_CODIGO[codigo]) for codigo in INDICES],
    }
