"""Análisis mensual real con caché por celda y respaldo de escenarios simulados."""

import math
from datetime import date

from fastapi import Request
from fastapi.responses import JSONResponse

from app.api import router
from app.api.simulados import escenario_para_celda
from app.api.validacion import LatitudConsulta, LongitudConsulta, rechazar, validar_ventana
from app.contracts import (
    AnalyzeRespuesta,
    Aviso,
    Celda,
    CeldaEscaneo,
    Indice,
    IndiceId,
    MesInusual,
    Tendencia,
    Variable,
    Ventana,
    Veredicto,
    Vinculo,
)
from app.datos import celdas, indices, power_client
from app.datos.power_client import PowerError, PowerLento
from app.estadistica import veredicto
from app.estadistica.celda import TendenciaCelda, analizar_celda
from app.estadistica.constantes import UMBRAL_INUSUAL, ventana_fin
from app.estadistica.teleconexion import celda_mas_cercana


def _meses_ventana(inicio: int, fin: int) -> list[str]:
    return [f"{y}-{m:02d}" for y in range(inicio, fin + 1) for m in range(1, 13)]


def _meses_calendario(meses: list[str]) -> list[int]:
    return [int(m.split("-")[1]) for m in meses]


def _numero(valor):
    return None if valor is None or math.isnan(float(valor)) else round(float(valor), 6)


def _nan_a_none(arr):
    return [_numero(v) for v in arr]


def _cercana(lat: float, lon: float, candidatas) -> CeldaEscaneo | None:
    """Reutiliza la distancia esférica del motor, también al cruzar el Pacífico."""
    if not candidatas:
        return None
    lats, lons = zip(*candidatas)
    i, distancia = celda_mas_cercana(lat, lon, lats, lons)
    return CeldaEscaneo(lat=lats[i], lon=lons[i], distancia_km=round(distancia, 6))


def _cercana_en_cache(cache, variable, lat, lon):
    candidatas = []
    for llave in cache.series.lugares(variable, "celda:"):
        _, lat_c, lon_c = llave.split(":")
        candidatas.append((float(lat_c), float(lon_c)))
    return _cercana(lat, lon, candidatas)


def _tendencia(res: TendenciaCelda, p_ajustado=None) -> Tendencia:
    """Mapea el motor al contrato; ScanMap decide significancia con BH (C14)."""
    sig = (
        res.significativa
        if p_ajustado is None
        else bool(veredicto.significativa(p_ajustado))
    )
    return Tendencia(
        pendiente_decada=_numero(res.pendiente_decada),
        ic_bajo=_numero(res.ic_bajo),
        ic_alto=_numero(res.ic_alto),
        p=_numero(res.p),
        p_ajustado=_numero(p_ajustado),
        significativa=sig,
        direccion=veredicto.direccion(res.pendiente_decada, sig),
        cambio_total=_numero(res.cambio_total),
        cambio_pct_decada=_numero(res.cambio_pct_decada),
        recta=_nan_a_none(res.recta),
    )


@router.get("/analyze", response_model=AnalyzeRespuesta)
def analyze(
    request: Request,
    variable: Variable,
    lat: LatitudConsulta,
    lon: LongitudConsulta,
    inicio: int,
    fin: int,
    indice: IndiceId = IndiceId.ONI,
):
    """Analiza una celda mensual con y sin El Niño; reutiliza datos ya descargados.

    Ejemplo: PRECTOTCORR, Piura (-5, -80.5), 1981–1990, ONI.
    En modo simulado solo se sirven las combinaciones con un JSON local.
    """
    validar_ventana(inicio, fin)
    estado = request.app.state
    if estado.simulado:
        return escenario_para_celda(
            request, "analyze", variable, lat, lon, inicio=inicio, fin=fin, indice=indice
        )

    lat_q, lon_q = celdas.celda(lat, lon)
    llave = celdas.lugar_celda(lat_q, lon_q)
    rejilla = celdas.rejilla()
    en_rejilla = (lat_q, lon_q) in set(rejilla)
    cache = estado.cache
    with cache.cerrojo(llave):
        guardado = cache.resultados.leer(variable, lat_q, lon_q, inicio, fin, indice)
        if guardado is not None:
            return AnalyzeRespuesta.model_validate(guardado)

        _, serie = cache.series.leer(variable, llave)
        if serie is None:
            estado.power.timeout = power_client.timeout_vivo()
            try:
                respuesta = estado.power.celda(lat_q, lon_q, 1981, ventana_fin())
            except PowerLento:
                cercana = _cercana_en_cache(cache, variable, lat_q, lon_q)
                # El modelo de error compartido solo acepta coordenadas; se conserva
                # aquí la distancia de la alternativa sin cambiar aquel contrato.
                return JSONResponse(
                    status_code=504,
                    content={"error": {
                        "codigo": "power_lento",
                        "mensaje": "NASA POWER tardó demasiado en responder. "
                        "Inténtalo más tarde o elige una celda con datos guardados.",
                        "celda_cercana": cercana.model_dump() if cercana else None,
                    }},
                )
            except PowerError:
                return JSONResponse(
                    status_code=502,
                    content={"error": {
                        "codigo": "power_error",
                        "mensaje": "No se pudieron obtener los datos de NASA POWER. "
                        "Inténtalo más tarde.",
                        "celda_cercana": None,
                    }},
                )
            meses_completos = _meses_ventana(1981, ventana_fin())
            descargadas = power_client.parsear(respuesta, meses_completos)
            for codigo in power_client.VARIABLES_POWER:
                ficha = estado.variables[codigo]
                cache.series.guardar(
                    codigo, llave, meses_completos[0], descargadas[codigo],
                    lat=lat_q, lon=lon_q, unidad=ficha["unidad"], fuente=ficha["fuente"],
                )

        meses = _meses_ventana(inicio, fin)
        serie = cache.series.leer_alineada(variable, llave, meses)
        _, indice_arr = indices.cargar_indice(indice, estado.datos, meses)
        meses, serie, indice_arr = indices.recortar(meses, serie, indice_arr)
        if not meses:
            rechazar(
                "fuera_de_rango",
                "No hay índice de El Niño disponible en esta ventana. Elige otros años.",
            )
        rc = analizar_celda(serie, _meses_calendario(meses), indice_arr, variable)
        if rc is None:
            rechazar(
                "sin_datos_tierra",
                "Esta celda no tiene suficientes datos válidos para analizar. "
                "Para humedad del suelo, elige una celda sobre tierra.",
            )

        origen = "individual"
        estado_veredicto = rc.veredicto
        p_original = p_sin = None
        escaneo = estado.escaneo_resultados
        if en_rejilla and inicio == 1981 and fin == ventana_fin() and indice == IndiceId.ONI:
            if escaneo is not None:
                filas = escaneo.loc[
                    (escaneo["lat"] == lat_q)
                    & (escaneo["lon"] == lon_q)
                    & (escaneo["variable"] == variable)
                ]
                if not filas.empty:
                    fila = filas.iloc[0]
                    p_original = float(fila["p_original_ajustado"])
                    p_sin = float(fila["p_ajustado"])
                    if math.isfinite(p_original) and math.isfinite(p_sin):
                        estado_veredicto = fila["veredicto"]
                        origen = "escaneo"
                    else:
                        p_original = p_sin = None

        fases = indices.fases(indice_arr)
        ficha = estado.variables[variable]
        vinculo = rc.vinculo_el_nino
        resultado = AnalyzeRespuesta(
            variable=variable, nombre=ficha["nombre"], unidad=ficha["unidad"],
            fuente=ficha["fuente"], descarga=date.today().isoformat(),
            celda=Celda(
                lat=lat_q, lon=lon_q, lado_grados=celdas.PASO_CELDA,
                en_rejilla=en_rejilla, celda_escaneo=_cercana(lat_q, lon_q, rejilla),
            ),
            ventana=Ventana(
                inicio=meses[0], fin=meses[-1], meses=len(meses),
                meses_analizados=rc.meses_analizados,
            ),
            indice=Indice(
                id=indice,
                nombre="Índice Oceánico de El Niño" if indice == IndiceId.ONI else "Niño 1+2",
                fuente="ONI, NOAA CPC" if indice == IndiceId.ONI else "Niño 1+2, NOAA CPC",
            ),
            fechas=meses,
            serie_original=_nan_a_none(rc.serie_original),
            serie_sin_el_nino=_nan_a_none(rc.serie_sin_el_nino),
            serie_z=_nan_a_none(rc.serie_z), indice_valores=_nan_a_none(indice_arr),
            fase=fases,
            tendencia_original=_tendencia(rc.tendencia_original, p_original),
            tendencia_sin_el_nino=_tendencia(rc.tendencia_sin_el_nino, p_sin),
            veredicto=Veredicto(estado=estado_veredicto, origen=origen),
            vinculo_el_nino=Vinculo(
                rezago_meses=vinculo.rezago_meses, r=_numero(vinculo.r),
                p=_numero(vinculo.p), n_efectivo=_numero(vinculo.n_efectivo),
                significativo=vinculo.significativo, indicativo=vinculo.indicativo,
            ),
            colinealidad=_numero(rc.colinealidad),
            avisos=[Aviso(codigo=c, texto=t) for c, t in rc.avisos],
            meses_inusuales=[
                MesInusual(fecha=mes, z=_numero(z), fase=fase)
                for mes, z, fase in zip(meses, rc.serie_z, fases)
                if abs(float(z)) > UMBRAL_INUSUAL
            ],
            prueba_t=None, cambio_brusco=None,
        )
        cache.resultados.guardar(
            variable, lat_q, lon_q, inicio, fin, indice, resultado.model_dump(mode="json")
        )
        return resultado
