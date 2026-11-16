"""T5 · S1–S4, S6: rutas reales sobre filas sintéticas del productor, sin red."""

from pathlib import Path
from statistics import median
from time import perf_counter

import pandas as pd
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.exceptions import HTTPException

from app.api import router
from app.contracts import (
    ErrorRespuesta,
    FeedRespuesta,
    GlosarioRespuesta,
    LayerRespuesta,
    VariablesRespuesta,
)
from app.datos.celdas import rejilla
from app.datos.escaneo import escribir_estado


def _cargar_catalogos() -> dict:
    """Carga los catálogos editoriales (variables y glosario) desde JSON."""
    carpeta = Path(__file__).resolve().parents[1] / "app" / "catalogo"
    return {
        "variables": VariablesRespuesta.model_validate_json(
            (carpeta / "variables.json").read_text("utf-8")
        ),
        "glosario": GlosarioRespuesta.model_validate_json(
            (carpeta / "glosario.json").read_text("utf-8")
        ),
    }


@pytest.fixture
def api_real(tmp_path, sin_red, monkeypatch):
    """Sin lifespan, POWER ni caché: conserva rutas y validación HTTP reales."""
    # main lee CORS al importarse; respetar la configuración de conftest.
    monkeypatch.setenv("VERASCOPE_CORS", "https://web.example,https://otra.example")
    from app.main import error_http, registrar_peticion

    app = FastAPI()
    app.middleware("http")(registrar_peticion)
    app.state._resultados_mtime = None
    app.include_router(router)
    app.add_exception_handler(HTTPException, error_http)
    app.state.datos = tmp_path
    app.state.escaneo_resultados = None
    catalogos = _cargar_catalogos()
    app.state.catalogo_variables = catalogos["variables"]
    app.state.catalogo_glosario = catalogos["glosario"]
    with TestClient(app, backend_options={"loop_factory": lambda: sin_red}) as cliente:
        yield cliente


def fila(celda=0, variable="PRECTOTCORR", **cambios):
    """Esquema de resultados.parquet; ningún valor representa una observación real."""
    lat, lon = rejilla()[celda]
    return {
        "variable": variable,
        "celda": celda,
        "lat": lat,
        "lon": lon,
        "pendiente_original": 0.6,
        "p_original": 0.001,
        "pendiente": 0.23456789,
        "ic_bajo": 0.12345678,
        "ic_alto": 0.34567891,
        "p": 0.002,
        "p_original_ajustado": 0.003,
        "p_ajustado": 0.00456789,
        "rezago": 2,
        "r_enso": 0.4,
        "p_enso": 0.01,
        "colinealidad": 0.1,
        "efecto": -1.23456789,
        "meses": 540,
        "veredicto": "cambio_robusto",
        "unidad": "mm/día",
        "pareja": None,
        "ventana": "1981-2025",
        **cambios,
    }


def preparar(cliente, filas, estado="completo"):
    cliente.app.state.escaneo_resultados = pd.DataFrame(filas)
    escribir_estado(cliente.app.state.datos, estado, 137 if estado == "en_curso" else 4235, 4235)


def consultar_feed(cliente, tipo="fuertes", pagina=0):
    respuesta = cliente.get("/api/v1/scan/feed", params={"tipo": tipo, "pagina": pagina})
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert FeedRespuesta.model_validate(datos).model_dump(mode="json") == datos
    return datos


@pytest.mark.parametrize("tipo", ["fuertes", "ocultas", "opuestas"])
@pytest.mark.parametrize("hay_resultados", [False, True])
def test_feed_incompleto_expone_avance_real_sin_tarjetas(api_real, tipo, hay_resultados):
    preparar(api_real, [fila()], "en_curso")
    if not hay_resultados:
        api_real.app.state.escaneo_resultados = None
    assert consultar_feed(api_real, tipo) == {
        "tipo": tipo,
        "pagina": 0,
        "por_pagina": 20,
        "total": 0,
        "escaneo": {"estado": "en_curso", "celdas_listas": 137, "celdas_total": 4235},
        "tarjetas": [],
    }


def test_fuertes_orden_absoluto_empates_ids_y_paginacion(api_real):
    filas = [fila(i, efecto=(-1) ** i * (30 - i // 2)) for i in range(25)]
    filas += [fila(40, "T2M", efecto=30, unidad="°C")]
    filas += [fila(41, veredicto="cambio_oculto", efecto=100)]
    filas += [fila(42, veredicto="sensible_a_el_nino", efecto=100)]
    filas += [fila(43, veredicto="sin_tendencia", efecto=100)]
    preparar(api_real, list(reversed(filas)))
    antes = api_real.app.state.escaneo_resultados.copy(deep=True)
    paginas = [consultar_feed(api_real, pagina=p) for p in range(3)]
    assert [len(p["tarjetas"]) for p in paginas] == [20, 6, 0]
    assert all(p["total"] == 26 and p["por_pagina"] == 20 for p in paginas)
    tarjetas = paginas[0]["tarjetas"] + paginas[1]["tarjetas"]
    esperadas = sorted(filas[:26], key=lambda f: (-abs(f["efecto"]), f["variable"], f["celda"]))
    assert [t["id"] for t in tarjetas] == [f"{f['variable']}-{f['celda']}" for f in esperadas]
    assert {t["veredicto"] for t in tarjetas} == {"cambio_robusto"}
    assert tarjetas[0]["titular"] == ("La lluvia sube de forma sostenida, aun quitando El Niño")
    pd.testing.assert_frame_equal(api_real.app.state.escaneo_resultados, antes)
    assert consultar_feed(api_real) == paginas[0]


def test_ocultas_solo_veredicto_y_titulares_por_signo(api_real):
    preparar(
        api_real,
        [
            fila(1, veredicto="cambio_oculto", efecto=2),
            fila(
                2, "GWETROOT", veredicto="cambio_oculto", pendiente=-0.2, efecto=-3, unidad="0 a 1"
            ),
            fila(3),
            fila(4, veredicto="sin_tendencia"),
        ],
    )
    datos = consultar_feed(api_real, "ocultas")
    assert datos["total"] == 2
    assert [t["veredicto"] for t in datos["tarjetas"]] == ["cambio_oculto"] * 2
    assert [t["titular"] for t in datos["tarjetas"]] == [
        "El Niño ocultaba que la humedad del suelo en la zona de raíces baja",
        "El Niño ocultaba que la lluvia sube",
    ]


def test_opuestas_una_por_par_origen_positivo_y_destino_negativo(api_real):
    preparar(
        api_real,
        [
            fila(8, pareja="par-b", pendiente=-0.8, efecto=-5),
            fila(2, pareja="par-b", pendiente=0.2, efecto=1),
            fila(9, pareja="par-a", pendiente=-0.9, efecto=-5),
            fila(3, pareja="par-a", pendiente=0.3, efecto=2),
        ],
    )
    datos = consultar_feed(api_real, "opuestas")
    assert datos["total"] == 2
    assert [t["id"] for t in datos["tarjetas"]] == ["PRECTOTCORR-3", "PRECTOTCORR-2"]
    destinos = [fila(9, pendiente=-0.9), fila(8, pendiente=-0.8)]
    for tarjeta, destino in zip(datos["tarjetas"], destinos):
        assert tarjeta["pendiente_decada"] > 0
        assert tarjeta["pareja"] == {
            "lat": destino["lat"],
            "lon": destino["lon"],
            "pendiente_decada": destino["pendiente"],
        }
        assert tarjeta["titular"] == "La lluvia sube aquí y baja allá"


@pytest.mark.parametrize(
    "miembros",
    [
        [fila(0, pareja="x")],
        [fila(0, pareja="x"), fila(1, pareja="x"), fila(2, pareja="x", pendiente=-1)],
        [fila(0, pareja="x"), fila(1, "T2M", pareja="x", pendiente=-1)],
        [fila(0, pareja="x"), fila(0, pareja="x", pendiente=-1)],
        [fila(0, pareja="x"), fila(1, pareja="x", pendiente=0)],
        [fila(0, pareja="x"), fila(1, pareja="x", pendiente=1)],
        [fila(0, pareja="x"), fila(1, pareja="x", pendiente=-1, efecto=float("nan"))],
        [fila(0, pareja=None), fila(1, pareja="", pendiente=-1)],
    ],
)
def test_opuestas_omite_pares_malformados_y_huerfanos(api_real, miembros):
    preparar(api_real, miembros)
    datos = consultar_feed(api_real, "opuestas")
    assert datos["total"] == 0
    assert datos["tarjetas"] == []


def test_s6_proyeccion_publica_redondeada_como_analyze(api_real):
    # Feed y analyze exponen la misma autoridad del escaneo con la precisión
    # pública de seis decimales; el DataFrame conserva su precisión interna.
    original = fila(1820)
    preparar(api_real, [original])
    tarjeta = consultar_feed(api_real)["tarjetas"][0]
    for campo, columna in {
        "pendiente_decada": "pendiente",
        "ic_bajo": "ic_bajo",
        "ic_alto": "ic_alto",
        "p_ajustado": "p_ajustado",
        "efecto": "efecto",
    }.items():
        assert tarjeta[campo] == round(float(original[columna]), 6)
    for campo in ("veredicto", "unidad", "variable"):
        assert tarjeta[campo] == original[campo]
    assert tarjeta["celda"] == {
        "lat": round(float(original["lat"]), 6),
        "lon": round(float(original["lon"]), 6),
    }
    assert tarjeta["id"] == "PRECTOTCORR-1820"


@pytest.mark.parametrize("estado,resultados", [("en_curso", True), ("completo", False)])
def test_layer_incompleto_o_sin_resultados_error_estandar(api_real, estado, resultados):
    preparar(api_real, [fila()], estado)
    if not resultados:
        api_real.app.state.escaneo_resultados = None
    respuesta = api_real.get("/api/v1/scan/layer", params={"variable": "PRECTOTCORR"})
    assert respuesta.status_code == 503
    assert respuesta.json() == {
        "error": {
            "codigo": "escaneo_en_curso",
            "mensaje": "El escaneo sigue en curso. Vuelve a intentarlo más tarde.",
            "celda_cercana": None,
        }
    }
    ErrorRespuesta.model_validate(respuesta.json())


@pytest.mark.parametrize("variable,unidad", [("PRECTOTCORR", "mm/día"), ("GWETROOT", "0 a 1")])
def test_layer_rejilla_oficial_valores_y_mar_nulo(api_real, variable, unidad):
    # Piura y Borneo, sobre tierra; (0, -140), océano, no tiene fila válida.
    tierra = [rejilla().index((-6.0, -80.0)), rejilla().index((0.0, 114.0))]
    filas = [
        fila(i, variable, unidad=unidad, pendiente=i / 10000, efecto=-i / 1000) for i in tierra
    ]
    preparar(api_real, list(reversed(filas)) + [fila(10, "T2M", unidad="°C")])
    respuesta = api_real.get("/api/v1/scan/layer", params={"variable": variable})
    assert respuesta.status_code == 200, respuesta.text
    datos = respuesta.json()
    assert LayerRespuesta.model_validate(datos).model_dump(mode="json") == datos
    assert datos["variable"] == variable
    assert datos["paso_grados"] == 2
    for campo in ("lat", "lon", "veredicto", "pendiente_decada", "efecto"):
        assert len(datos[campo]) == 4235
    assert list(zip(datos["lat"], datos["lon"])) == rejilla()
    assert (datos["lat"][0], datos["lon"][0]) == (-34, 90)
    assert (datos["lat"][-1], datos["lon"][-1]) == (34, -30)
    por_celda = {f["celda"]: f for f in filas}
    columnas = [
        ("veredicto", "veredicto"),
        ("pendiente_decada", "pendiente"),
        ("efecto", "efecto"),
    ]
    for i in range(4235):
        for campo, columna in columnas:
            assert datos[campo][i] == (por_celda[i][columna] if i in por_celda else None)
    mar = rejilla().index((0.0, -140.0))
    assert all(datos[c][mar] is None for c in ("veredicto", "pendiente_decada", "efecto"))


@pytest.mark.parametrize("actualizacion", ["reemplazo", "recarga"])
def test_feed_cache_invalida_resultados(api_real, monkeypatch, actualizacion):
    from app.api import scan

    seleccionar = scan._seleccionar_tarjetas
    llamadas = []
    lecturas = []
    leer_texto = Path.read_text

    def contar_seleccion(resultados, tipo, titulares):
        llamadas.append(tipo)
        return seleccionar(resultados, tipo, titulares)

    def contar_lectura(ruta, *args, **kwargs):
        if ruta.name == "titulares.json":
            lecturas.append(ruta)
        return leer_texto(ruta, *args, **kwargs)

    monkeypatch.setattr(scan, "_seleccionar_tarjetas", contar_seleccion)
    monkeypatch.setattr(Path, "read_text", contar_lectura)

    def filas(inicio):
        return [
            fila(inicio),
            fila(inicio + 1, veredicto="cambio_oculto"),
            fila(inicio + 2, pareja="par", pendiente=1),
            fila(inicio + 3, pareja="par", pendiente=-1),
        ]

    preparar(api_real, filas(0))
    anteriores = {}
    for tipo in ("fuertes", "ocultas", "opuestas"):
        anteriores[tipo] = consultar_feed(api_real, tipo)
        assert consultar_feed(api_real, tipo) == anteriores[tipo]
        assert consultar_feed(api_real, tipo, pagina=1)["tarjetas"] == []
    assert len(llamadas) == 3
    assert len(lecturas) == 1

    nuevos = pd.DataFrame(filas(10))
    if actualizacion == "reemplazo":
        api_real.app.state.escaneo_resultados = nuevos
    else:
        nuevos.to_parquet(api_real.app.state.datos / "resultados.parquet")
    for tipo in anteriores:
        actualizado = consultar_feed(api_real, tipo)
        assert actualizado["total"] == anteriores[tipo]["total"]
        assert actualizado["tarjetas"] != anteriores[tipo]["tarjetas"]
        assert all(int(t["id"].rsplit("-", 1)[1]) >= 10 for t in actualizado["tarjetas"])
        assert consultar_feed(api_real, tipo) == actualizado
    assert len(llamadas) == 6
    assert len(lecturas) == 1

    preparar(api_real, filas(20), "en_curso")
    for tipo in anteriores:
        incompleto = consultar_feed(api_real, tipo)
        assert incompleto["total"] == 0 and incompleto["tarjetas"] == []
        assert incompleto["escaneo"]["celdas_listas"] == 137
    assert len(llamadas) == 6
    escribir_estado(api_real.app.state.datos, "completo", 4235, 4235)
    for tipo in anteriores:
        assert consultar_feed(api_real, tipo)["total"] == anteriores[tipo]["total"]
    assert len(llamadas) == 9
    assert len(lecturas) == 1


@pytest.mark.lento
def test_feed_real_mediana_menor_20_ms(api_real):
    # Construcción de fixtures, estado y catálogo fuera del cronómetro.
    # Rejilla completa × cinco variables; 400 hallazgos robustos sintéticos.
    plantilla = fila()
    base = [
        {
            **plantilla,
            "celda": i,
            "lat": lat,
            "lon": lon,
            "veredicto": "cambio_robusto" if i < 80 else "sin_tendencia",
        }
        for i, (lat, lon) in enumerate(rejilla())
    ]
    bloques = []
    for variable in ("PRECTOTCORR", "T2M", "GWETROOT", "GWETTOP", "RH2M"):
        bloque = pd.DataFrame(base)
        bloque["variable"] = variable
        bloques.append(bloque)
    resultados = pd.concat(bloques, ignore_index=True)
    assert len(resultados) == 21175
    assert resultados.groupby("variable").size().tolist() == [4235] * 5
    assert (resultados["veredicto"] == "cambio_robusto").sum() == 400
    preparar(api_real, [])
    api_real.app.state.escaneo_resultados = resultados

    def ejecutar():
        # HTTP público completo: middleware, disco, ruta y validación de respuesta.
        respuesta = api_real.get("/api/v1/scan/feed", params={"tipo": "fuertes", "pagina": 0})
        assert respuesta.status_code == 200, respuesta.text
        return respuesta

    esperado = consultar_feed(api_real)  # Construcción inicial fuera del cronómetro.
    for _ in range(10):
        ejecutar()
    # Plan fijo, sin reintentos ni descarte de muestras. Con 50 ejecuciones
    # una pausa aislada de 50 ms añade 1 ms al promedio del lote, no 10 ms
    # como ocurría con lotes de cinco. La mediana de nueve lotes tolera
    # pausas ocasionales, pero sigue fallando ante lentitud sostenida.
    tiempos = []
    por_lote = 50
    muestras = 9
    for _ in range(muestras):
        inicio = perf_counter()
        for _ in range(por_lote):
            resultado = ejecutar()
        tiempos.append((perf_counter() - inicio) * 1000 / por_lote)
    validado = FeedRespuesta.model_validate_json(resultado.content)
    assert validado.total == 400
    assert len(validado.tarjetas) == 20
    assert validado.model_dump(mode="json") == esperado == consultar_feed(api_real)
    mediana = median(tiempos)
    print(
        f"feed HTTP real (pared): mediana={mediana:.3f} ms/ejecución; "
        f"{muestras} lotes × {por_lote}; 10 calentamientos; "
        f"21175 filas; 400 hallazgos; tiempos={tiempos}"
    )
    assert mediana < 20, f"Feed HTTP real: mediana {mediana:.3f} ms >= 20 ms; {tiempos}"
