"""Feed y mosaico de resultados precalculados, con fixtures en modo simulado."""

import json
from math import isfinite
from pathlib import Path
from weakref import ref

from fastapi import HTTPException, Query, Request

from app.api import router
from app.api.simulados import escenario
from app.api.validacion import exigir_seleccion
from app.contracts import (
    EstadoVeredicto,
    FeedRespuesta,
    LayerRespuesta,
    Pareja,
    Tarjeta,
    TipoFeed,
    Variable,
)
from app.datos.celdas import lon_a_180, rejilla
from app.datos.escaneo import leer_estado


def _numero(valor):
    """Precisión pública de analyze; nunca se usa para ordenar o decidir signos."""
    try:
        numero = float(valor)
    except (TypeError, ValueError, OverflowError):
        return None
    return round(numero, 6) if isfinite(numero) else None


def _tarjeta(fila: dict, tipo: TipoFeed, titulares: dict) -> Tarjeta | None:
    """Mapea una fila válida sin sustituir datos ausentes o no finitos."""
    try:
        variable = Variable(fila["variable"])
        numeros = {
            campo: float(fila[campo])
            for campo in (
                "celda", "lat", "lon", "pendiente", "ic_bajo", "ic_alto", "p_ajustado", "efecto"
            )
        }
        if not all(isfinite(valor) for valor in numeros.values()):
            return None
        if not numeros["celda"].is_integer() or numeros["celda"] < 0:
            return None
        sujeto = titulares["sujetos"][variable]
        if tipo == TipoFeed.OPUESTAS:
            plantilla = titulares["plantillas"]["opuestas"]
        else:
            # El catálogo no narra una dirección para una pendiente nula.
            if numeros["pendiente"] == 0:
                return None
            direccion = "sube" if numeros["pendiente"] > 0 else "baja"
            plantilla = titulares["plantillas"][fila["veredicto"]][direccion]
        return Tarjeta(
            id=f"{variable}-{int(numeros['celda'])}",
            titular=plantilla.format(sujeto=sujeto, sujeto_min=sujeto[:1].lower() + sujeto[1:]),
            variable=variable,
            unidad=fila["unidad"],
            celda={"lat": _numero(numeros["lat"]), "lon": _numero(numeros["lon"])},
            veredicto=fila["veredicto"],
            pendiente_decada=_numero(numeros["pendiente"]),
            ic_bajo=_numero(numeros["ic_bajo"]),
            ic_alto=_numero(numeros["ic_alto"]),
            p_ajustado=_numero(numeros["p_ajustado"]),
            efecto=_numero(numeros["efecto"]),
        )
    except (KeyError, TypeError, ValueError, OverflowError):
        return None


def _seleccionar_tarjetas(resultados, tipo: TipoFeed, titulares: dict) -> list[Tarjeta]:
    """Filtra y ordena sin modificar el DataFrame compartido del escaneo."""
    if tipo != TipoFeed.OPUESTAS:
        veredicto = "cambio_robusto" if tipo == TipoFeed.FUERTES else "cambio_oculto"
        # Filtrar en pandas antes de materializar las 21 175 filas en Python.
        columnas = (
            "variable", "celda", "lat", "lon", "pendiente", "ic_bajo", "ic_alto",
            "p_ajustado", "efecto", "veredicto", "unidad",
        )
        seleccion = resultados.loc[resultados["veredicto"] == veredicto].reindex(
            columns=columnas
        )
        # Una conversión de la selección estrecha, no un iterador pandas por
        # cada columna del esquema del productor (incluidas las irrelevantes).
        filas = (dict(zip(columnas, valores)) for valores in seleccion.to_numpy().tolist())
        tarjetas = [
            (float(fila["efecto"]), tarjeta)
            for fila in filas
            if fila.get("veredicto") == veredicto
            if (tarjeta := _tarjeta(fila, tipo, titulares)) is not None
        ]
        return [
            tarjeta for _, tarjeta in sorted(
                tarjetas,
                key=lambda par: (
                    -abs(par[0]), par[1].variable, int(par[1].id.rsplit("-", 1)[1])
                ),
            )
        ]

    # El productor asigna ids de texto; agrupar antes de validar evita que un
    # grupo malformado de tres filas se convierta artificialmente en un par.
    grupos = {}
    for fila in resultados.to_dict(orient="records"):
        pareja = fila.get("pareja")
        if isinstance(pareja, str) and pareja:
            grupos.setdefault(pareja, []).append(fila)
    pares = []
    for pareja, miembros in grupos.items():
        if len(miembros) != 2:
            continue
        primera, segunda = (_tarjeta(fila, tipo, titulares) for fila in miembros)
        if primera is None or segunda is None or primera.variable != segunda.variable:
            continue
        if primera.id == segunda.id:
            continue
        (fila_positiva, positiva), (fila_negativa, negativa) = sorted(
            zip(miembros, (primera, segunda)), key=lambda par: -float(par[0]["pendiente"])
        )
        if not (float(fila_positiva["pendiente"]) > 0 > float(fila_negativa["pendiente"])):
            continue
        positiva.pareja = Pareja(
            lat=negativa.celda.lat,
            lon=negativa.celda.lon,
            pendiente_decada=negativa.pendiente_decada,
        )
        efecto = max(abs(float(fila["efecto"])) for fila in miembros)
        pares.append((-efecto, pareja, positiva))
    return [tarjeta for _, _, tarjeta in sorted(pares, key=lambda par: (par[0], par[1]))]


def cargar_titulares() -> dict:
    """Plantillas inmutables: una carga por aplicación, no por petición."""
    ruta = Path(__file__).resolve().parents[1] / "catalogo" / "titulares.json"
    return json.loads(ruta.read_text(encoding="utf-8"))


def reiniciar_cache_feed(estado, resultados=None):
    """Retiene solo una generación, sin mantener vivo su DataFrame."""
    if resultados is None:
        resultados = estado.escaneo_resultados
    cache = (ref(resultados) if resultados is not None else None, {})
    estado.feed_cache = cache
    return cache


def _tarjetas_cacheadas(estado, resultados, tipo: TipoFeed) -> list[Tarjeta]:
    """Una lista completa por pestaña; nunca guarda respuestas ni páginas."""
    cache = getattr(estado, "feed_cache", None)
    if cache is None or cache[0] is None or cache[0]() is not resultados:
        cache = reiniciar_cache_feed(estado, resultados)
    tarjetas_por_tipo = cache[1]
    if tipo not in tarjetas_por_tipo:
        # También admite aplicaciones pequeñas que no ejecutan lifespan.
        if not hasattr(estado, "feed_titulares"):
            estado.feed_titulares = cargar_titulares()
        tarjetas_por_tipo[tipo] = _seleccionar_tarjetas(
            resultados, tipo, estado.feed_titulares
        )
    return tarjetas_por_tipo[tipo]


def _respuesta_feed(tarjetas: list[Tarjeta], tipo: TipoFeed, pagina: int, estado: dict):
    """Paginación dinámica y contrato de salida sobre las tarjetas derivadas."""
    por_pagina = 20
    inicio = pagina * por_pagina
    return FeedRespuesta(
        tipo=tipo,
        pagina=pagina,
        por_pagina=por_pagina,
        total=len(tarjetas),
        escaneo=estado,
        tarjetas=tarjetas[inicio : inicio + por_pagina],
    )


@router.get("/scan/feed", response_model=FeedRespuesta)
def feed(request: Request, tipo: TipoFeed, pagina: int = Query(default=0, ge=0)):
    if request.app.state.simulado:
        respuesta = escenario(request, "feed")
        respuesta.tipo = tipo
        respuesta.pagina = pagina
        if tipo != TipoFeed.FUERTES or pagina != 0:
            respuesta.tarjetas = []
            if tipo != TipoFeed.FUERTES:
                respuesta.total = 0
        return respuesta

    estado = leer_estado(request.app.state.datos)
    resultados = request.app.state.escaneo_resultados
    if resultados is None:
        estado = {**estado, "estado": "en_curso"}
    if estado["estado"] == "completo":
        tarjetas = _tarjetas_cacheadas(request.app.state, resultados, tipo)
    else:
        # No se cachea el resultado incompleto, ni se reutilizan sus tarjetas.
        reiniciar_cache_feed(request.app.state)
        tarjetas = []
    return _respuesta_feed(tarjetas, tipo, pagina, estado)


@router.get("/scan/layer", response_model=LayerRespuesta)
def layer(request: Request, variable: Variable):
    """Mosaico en el orden de la rejilla; las celdas sin resultado quedan nulas."""
    if request.app.state.simulado:
        respuesta = escenario(request, "layer")
        exigir_seleccion({"variable": variable}, {"variable": respuesta.variable})
        return respuesta

    estado = leer_estado(request.app.state.datos)
    resultados = request.app.state.escaneo_resultados
    if estado["estado"] != "completo" or resultados is None:
        raise HTTPException(
            status_code=503,
            detail={
                "codigo": "escaneo_en_curso",
                "mensaje": "El escaneo sigue en curso. Vuelve a intentarlo más tarde.",
                "celda_cercana": None,
            },
        )

    celdas = rejilla()
    posiciones = set(celdas)
    por_celda = {}
    for fila in resultados.to_dict(orient="records"):
        try:
            if Variable(fila["variable"]) != variable:
                continue
            lat, lon, pendiente, efecto = (
                float(fila[campo]) for campo in ("lat", "lon", "pendiente", "efecto")
            )
            if not all(isfinite(valor) for valor in (lat, lon, pendiente, efecto)):
                continue
            posicion = (lat, lon_a_180(lon))
            veredicto = EstadoVeredicto(fila["veredicto"])
        except (KeyError, TypeError, ValueError, OverflowError):
            continue
        if posicion in posiciones and posicion not in por_celda:
            por_celda[posicion] = (veredicto, pendiente, efecto)

    valores = [por_celda.get(posicion, (None, None, None)) for posicion in celdas]
    return LayerRespuesta(
        variable=variable,
        paso_grados=2.0,
        lat=[lat for lat, _ in celdas],
        lon=[lon for _, lon in celdas],
        veredicto=[veredicto for veredicto, _, _ in valores],
        pendiente_decada=[pendiente for _, pendiente, _ in valores],
        efecto=[efecto for _, _, efecto in valores],
    )
