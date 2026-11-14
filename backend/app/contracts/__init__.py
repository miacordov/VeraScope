"""Contrato público de la API mensual, compartido con el frontend."""

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Modelo(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Variable(StrEnum):
    LLUVIA = "PRECTOTCORR"
    TEMPERATURA = "T2M"
    RAICES = "GWETROOT"
    SUPERFICIE = "GWETTOP"
    HUMEDAD = "RH2M"


class IndiceId(StrEnum):
    ONI = "ONI"
    NINO12 = "NINO12"


class EstadoVeredicto(StrEnum):
    ROBUSTO = "cambio_robusto"
    SENSIBLE = "sensible_a_el_nino"
    OCULTO = "cambio_oculto"
    SIN_TENDENCIA = "sin_tendencia"


class Direccion(StrEnum):
    SUBE = "sube"
    BAJA = "baja"
    PLANA = "plana"


class Fase(StrEnum):
    NINO = "nino"
    NINA = "nina"
    NEUTRO = "neutro"


class OrigenVeredicto(StrEnum):
    ESCANEO = "escaneo"
    INDIVIDUAL = "individual"


class TipoLinea(StrEnum):
    OPUESTO = "opuesto"
    MISMO = "mismo"


class CodigoAviso(StrEnum):
    COLINEALIDAD = "colinealidad"
    POTENCIA = "potencia_baja"
    NO_LINEAL = "respuesta_no_lineal"
    COSTERO = "nino_costero"
    REJILLA = "fuera_de_rejilla"
    MUESTRA = "muestra_efectiva_baja"


class CodigoError(StrEnum):
    VENTANA = "ventana_corta"
    RANGO = "fuera_de_rango"
    TIERRA = "sin_datos_tierra"
    LENTO = "power_lento"
    POWER = "power_error"
    ESCANEO = "escaneo_en_curso"


class TipoFeed(StrEnum):
    FUERTES = "fuertes"
    OPUESTAS = "opuestas"
    OCULTAS = "ocultas"


Mes = Annotated[str, Field(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
Latitud = Annotated[float, Field(ge=-90, le=90)]
Longitud = Annotated[float, Field(ge=-180, le=180)]
Probabilidad = Annotated[float, Field(ge=0, le=1)]
Serie = list[float | None]


class Coordenadas(Modelo):
    lat: Latitud
    lon: Longitud


class CeldaEscaneo(Coordenadas):
    distancia_km: float


class Celda(Coordenadas):
    lado_grados: float
    en_rejilla: bool
    celda_escaneo: CeldaEscaneo | None


class Escaneo(Modelo):
    estado: Literal["en_curso", "completo"]
    celdas_listas: int
    celdas_total: int


class SaludRespuesta(Modelo):
    simulado: bool
    ventana_fin: int
    version_metodo: int
    escaneo: Escaneo


class DefinicionVariable(Modelo):
    id: Variable
    nombre: str
    definicion: str
    unidad: str
    fuente: str


class Indice(Modelo):
    id: IndiceId
    nombre: str
    fuente: str


class DefinicionIndice(Indice):
    definicion: str
    unidad: str


class VariablesRespuesta(Modelo):
    variables: list[DefinicionVariable]
    indices: list[DefinicionIndice]


class Termino(Modelo):
    termino: str
    definicion: str


class GlosarioRespuesta(Modelo):
    terminos: list[Termino]


class Ventana(Modelo):
    inicio: Mes
    fin: Mes
    meses: int
    meses_analizados: int


class Tendencia(Modelo):
    pendiente_decada: float
    ic_bajo: float
    ic_alto: float
    p: Probabilidad
    p_ajustado: Probabilidad | None
    significativa: bool
    direccion: Direccion
    cambio_total: float | None
    cambio_pct_decada: float | None
    recta: Serie


class Veredicto(Modelo):
    estado: EstadoVeredicto
    origen: OrigenVeredicto


class Vinculo(Modelo):
    rezago_meses: Annotated[int, Field(ge=0, le=6)]
    r: Annotated[float, Field(ge=-1, le=1)]
    p: Probabilidad
    n_efectivo: float
    significativo: bool
    indicativo: bool


class Aviso(Modelo):
    codigo: CodigoAviso
    texto: str


class MesInusual(Modelo):
    fecha: Mes
    z: float
    fase: Fase


class AnalyzeRespuesta(Modelo):
    variable: Variable
    nombre: str
    unidad: str
    fuente: str
    descarga: str
    celda: Celda
    ventana: Ventana
    indice: Indice
    fechas: list[Mes]
    serie_original: Serie
    serie_sin_el_nino: Serie
    serie_z: Serie
    indice_valores: Serie
    fase: list[Fase]
    tendencia_original: Tendencia
    tendencia_sin_el_nino: Tendencia
    veredicto: Veredicto
    vinculo_el_nino: Vinculo
    colinealidad: float
    avisos: list[Aviso]
    meses_inusuales: list[MesInusual]
    prueba_t: None
    cambio_brusco: None

    @model_validator(mode="after")
    def validar_longitudes(self):
        """Todas las series y rectas se alinean con el mismo calendario."""
        n = len(self.fechas)
        series = (
            self.serie_original,
            self.serie_sin_el_nino,
            self.serie_z,
            self.indice_valores,
            self.fase,
            self.tendencia_original.recta,
            self.tendencia_sin_el_nino.recta,
        )
        if self.ventana.meses != n or any(len(serie) != n for serie in series):
            raise ValueError(
                "Las series y rectas deben tener la misma longitud que fechas y meses."
            )
        return self


class OrigenTeleconexion(Coordenadas):
    distancia_a_clic_km: float
    r_el_nino: float


class Coincidencia(Modelo):
    fecha: Mes
    fase: Fase


class Linea(Coordenadas):
    tipo: TipoLinea
    r: float
    p_ajustado: Probabilidad
    distancia_km: float
    r_el_nino_origen: float
    r_el_nino_destino: float
    meses_coincidencia: list[Coincidencia]


class TeleconnectRespuesta(Modelo):
    variable: Variable
    origen: OrigenTeleconexion
    lineas: list[Linea]
    mensaje_vacio: str | None


class Periodo(Modelo):
    anios: tuple[int, int]
    media_original: float
    media_sin_el_nino: float
    meses_inusuales: int
    meses_inusuales_en_el_nino: int


class ComparePeriodsRespuesta(Modelo):
    p1: Periodo
    p2: Periodo
    delta_original: float
    delta_sin_el_nino: float
    nota: str


class Pareja(Coordenadas):
    pendiente_decada: float


class Tarjeta(Modelo):
    id: str
    titular: str
    variable: Variable
    unidad: str
    celda: Coordenadas
    veredicto: EstadoVeredicto
    pendiente_decada: float
    ic_bajo: float
    ic_alto: float
    p_ajustado: Probabilidad
    efecto: float
    pareja: Pareja | None = None


class FeedRespuesta(Modelo):
    tipo: TipoFeed
    pagina: int
    por_pagina: int
    total: int
    escaneo: Escaneo
    tarjetas: list[Tarjeta]


class LayerRespuesta(Modelo):
    variable: Variable
    paso_grados: float
    lat: list[Latitud]
    lon: list[Longitud]
    veredicto: list[EstadoVeredicto | None]
    pendiente_decada: Serie
    efecto: Serie

    @model_validator(mode="after")
    def validar_columnas(self):
        """Cada posición representa la misma celda en todas las columnas."""
        columnas = (self.lon, self.veredicto, self.pendiente_decada, self.efecto)
        if any(len(columna) != len(self.lat) for columna in columnas):
            raise ValueError("Las columnas del mosaico deben tener la misma longitud.")
        return self


class Accion(Modelo):
    model_config = ConfigDict(extra="forbid", strict=True)


class SeleccionarVariable(Accion):
    tipo: Literal["seleccionar_variable"]
    variable: Literal["PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M"]


class SeleccionarCelda(Accion):
    tipo: Literal["seleccionar_celda"]
    lat: Latitud
    lon: Longitud


class FijarVentana(Accion):
    tipo: Literal["fijar_ventana"]
    inicio: int
    fin: int


class QuitarElNino(Accion):
    tipo: Literal["quitar_el_nino"]
    valor: bool


class Reproducir(Accion):
    tipo: Literal["reproducir"]


class Detener(Accion):
    tipo: Literal["detener"]


class IrAlMes(Accion):
    tipo: Literal["ir_al_mes"]
    fecha: Mes


class IrADestino(Accion):
    tipo: Literal["ir_a_destino"]
    lat: Latitud
    lon: Longitud


class MostrarPeriodos(Accion):
    tipo: Literal["mostrar_periodos"]


AccionDemo = Annotated[
    SeleccionarVariable
    | SeleccionarCelda
    | FijarVentana
    | QuitarElNino
    | Reproducir
    | Detener
    | IrAlMes
    | IrADestino
    | MostrarPeriodos,
    Field(discriminator="tipo"),
]


class PasoDemo(Modelo):
    n: int
    texto: str
    acciones: list[AccionDemo]


class DemoRespuesta(Modelo):
    id: Literal["efecto-espejo", "senal-o-ruido"]
    titulo: str
    variable: Variable
    celda: Coordenadas
    pasos: list[PasoDemo]


class ErrorDetalle(Modelo):
    codigo: CodigoError
    mensaje: str
    celda_cercana: Coordenadas | None


class ErrorRespuesta(Modelo):
    error: ErrorDetalle
