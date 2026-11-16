"""Genera respuestas reales de la API para las demos sin red.

    python -m jobs.instantaneas

Arranca la API en memoria con TestClient, llama a las rutas de las demos
y guarda los JSON en data/demo/respuestas/. El frontend los copia a
assets/demo/ con `npm run demo:copiar`.
"""

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient

# Forzar modo real
os.environ["VERASCOPE_SIMULADO"] = "0"

from app.main import app  # noqa: E402
from app.contracts import (  # noqa: E402
    AnalyzeRespuesta,
    ComparePeriodsRespuesta,
    DemoRespuesta,
    TeleconnectRespuesta,
)

DESTINO = Path(__file__).resolve().parents[1] / "data" / "demo" / "respuestas"

# Celdas de las demos (cuantizadas a la rejilla de paso 2)
PIURA = {"lat": -6.0, "lon": -80.0}
NORTE_AUSTRALIA = {"lat": -14.0, "lon": 132.0}

# Configuración de las demos
DEMOS = {
    "efecto-espejo": {
        "variable": "PRECTOTCORR",
        "celda": PIURA,
        "destinos": [NORTE_AUSTRALIA],
    },
    "senal-o-ruido": {
        "variable": "T2M",
        "celda": PIURA,
        "ventanas": [(1981, 2025), (1981, 1990)],
    },
}


def nombre_archivo(ruta: str, variable: str, lat: float, lon: float, extra: str = "") -> str:
    """Nombre estable: analyze_PRECTOTCORR_-6.0_-80.0.json"""
    base = f"{ruta}_{variable}_{lat}_{lon}"
    if extra:
        base += f"_{extra}"
    return f"{base}.json"


def guardar(nombre: str, datos: dict, modelo):
    """Valida contra el modelo Pydantic y guarda el JSON."""
    # Validar
    modelo.model_validate(datos)
    
    # Guardar
    ruta = DESTINO / nombre
    ruta.write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  ✓ {nombre}")


def generar_analyze(cliente: TestClient, variable: str, lat: float, lon: float, inicio: int = 1981, fin: int = 2025):
    """Genera respuesta de /analyze."""
    params = {
        "variable": variable,
        "lat": lat,
        "lon": lon,
        "inicio": inicio,
        "fin": fin,
        "indice": "ONI",
    }
    respuesta = cliente.get("/api/v1/analyze", params=params)
    if respuesta.status_code != 200:
        print(f"  ✗ analyze {variable} ({lat}, {lon}): {respuesta.status_code}")
        print(f"    {respuesta.text[:200]}")
        return None
    
    extra = "" if (inicio == 1981 and fin == 2025) else f"{inicio}-{fin}"
    nombre = nombre_archivo("analyze", variable, lat, lon, extra)
    guardar(nombre, respuesta.json(), AnalyzeRespuesta)
    return respuesta.json()


def generar_teleconnect(cliente: TestClient, variable: str, lat: float, lon: float):
    """Genera respuesta de /teleconnect."""
    params = {"variable": variable, "lat": lat, "lon": lon}
    respuesta = cliente.get("/api/v1/teleconnect", params=params)
    if respuesta.status_code != 200:
        print(f"  ✗ teleconnect {variable} ({lat}, {lon}): {respuesta.status_code}")
        return None
    
    nombre = nombre_archivo("teleconnect", variable, lat, lon)
    guardar(nombre, respuesta.json(), TeleconnectRespuesta)
    return respuesta.json()


def generar_compare_periods(cliente: TestClient, variable: str, lat: float, lon: float,
                            p1_inicio: int = 1981, p1_fin: int = 2001,
                            p2_inicio: int = 2003, p2_fin: int = 2025):
    """Genera respuesta de /compare-periods."""
    params = {
        "variable": variable, "lat": lat, "lon": lon,
        "p1_inicio": p1_inicio, "p1_fin": p1_fin,
        "p2_inicio": p2_inicio, "p2_fin": p2_fin,
    }
    respuesta = cliente.get("/api/v1/compare-periods", params=params)
    if respuesta.status_code != 200:
        print(f"  \u2717 compare-periods {variable} ({lat}, {lon}): {respuesta.status_code}")
        return None
    
    nombre = nombre_archivo("compare-periods", variable, lat, lon)
    guardar(nombre, respuesta.json(), ComparePeriodsRespuesta)
    return respuesta.json()


def generar_demo(cliente: TestClient, demo_id: str):
    """Genera respuesta de /demos/{id}."""
    respuesta = cliente.get(f"/api/v1/demos/{demo_id}")
    if respuesta.status_code != 200:
        print(f"  ✗ demos/{demo_id}: {respuesta.status_code}")
        return None
    
    nombre = f"demos_{demo_id}.json"
    guardar(nombre, respuesta.json(), DemoRespuesta)
    return respuesta.json()


def main():
    print("Generando respuestas de las demos...\n")
    
    # Crear carpeta destino
    DESTINO.mkdir(parents=True, exist_ok=True)
    
    with TestClient(app) as cliente:
        # Verificar que estamos en modo real
        salud = cliente.get("/api/v1/salud").json()
        if salud.get("simulado"):
            print("✗ Error: la API está en modo simulado")
            return 1
        print(f"API en modo real, ventana hasta {salud['ventana_fin']}\n")
        
        # Demo 1: efecto-espejo
        print("Demo 1: efecto-espejo")
        cfg = DEMOS["efecto-espejo"]
        celda = cfg["celda"]
        
        # Analyze de Piura
        generar_analyze(cliente, cfg["variable"], celda["lat"], celda["lon"])
        
        # Teleconnect de Piura
        tc = generar_teleconnect(cliente, cfg["variable"], celda["lat"], celda["lon"])
        
        # Analyze de los destinos del teleconnect
        if tc and tc.get("destinos"):
            for destino in tc["destinos"][:3]:  # máximo 3 destinos
                generar_analyze(
                    cliente,
                    cfg["variable"],
                    destino["lat"],
                    destino["lon"],
                )
        
        # Guion de la demo
        generar_demo(cliente, "efecto-espejo")
        
        # Demo 2: senal-o-ruido
        print("\nDemo 2: senal-o-ruido")
        cfg = DEMOS["senal-o-ruido"]
        celda = cfg["celda"]
        
        # Analyze con ventanas diferentes
        for inicio, fin in cfg["ventanas"]:
            generar_analyze(cliente, cfg["variable"], celda["lat"], celda["lon"], inicio, fin)
        
        # Compare-periods
        generar_compare_periods(cliente, cfg["variable"], celda["lat"], celda["lon"])
        
        # Guion de la demo
        generar_demo(cliente, "senal-o-ruido")
    
    print(f"\n✓ Respuestas guardadas en {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
