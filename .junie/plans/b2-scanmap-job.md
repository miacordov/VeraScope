---
sessionId: session-261115-172513-xnnl
---

# Technical Design

## Overview

El esqueleto de B2 ya está implementado: `jobs/scanmap.py` orquesta el escaneo, `verascope_datos/calcular.py` calcula con BH FDR, pares opuestos y escribe `resultados.parquet`. Las pruebas de backend (548) pasan. **Lo que falta son correcciones y documentación para que todo funcione end-to-end.**

## Current State

### Lo que ya existe y funciona
- `jobs/scanmap.py` (79 líneas): `correr()` → `armar_tabla()` → `calcular_resultados()` → estado `completo`
- `verascope_datos/calcular.py` (108 líneas): usa `analizar_celda` del motor único, BH en dos familias, pares opuestos > 1500 km, parquet con las columnas de §6
- `verascope_datos/cli.py`: comandos `indices`, `power`, `calcular`, `demos`, `empaquetar`, `instalar`, `panel`
- `app/datos/escaneo.py`: estado `en_curso`/`completo` con escritura atómica
- Pruebas: `test_scanmap.py` (157 líneas), `test_consistencia_escaneo.py` (105 líneas), `test_fdr.py` (88 líneas), `test_pares.py` (159 líneas)
- `backend/pytest -q` → 548 passed, 3 skipped ✓

### Lo que está roto
- **Preparador tests (13 pruebas):** fallan al importar. La carpeta `backend/verascope_datos/` (sin `__init__.py`) se interpreta como namespace package y sombra el paquete editable. pytest añade `backend/verascope_datos/` a `sys.path` al cargar los tests, y Python encuentra esa carpeta vacía antes que el `__init__.py` del paquete instalado.

### Lo que falta
- Conectar `verascope-datos calcular` CLI con `jobs/scanmap.py` (actualmente el CLI llama a `calcular_resultados` directamente; el issue pide que usen la misma implementación)
- `--minimo-celdas N` en `calcular` para generar resultados parciales
- Documentación de operación: cómo empaquetar, subir a GitHub release, instalar en el servidor
- Verificar servicios reales (GLDAS × 8, NDVI) y documentar la decisión en `README.md`

## Key Issues to Fix

1. **Namespace package shadowing** — `backend/verascope_datos/` sin `__init__.py` rompe las pruebas del preparador
2. **CLI `calcular` vs `jobs/scanmap.py`** — dos caminos al mismo motor; unificar
3. **`--minimo-celdas`** — falta en el CLI para escaneos parciales
4. **Documentación** — falta guía de empaquetado y despliegue con datos reales

# Delivery Steps

### ✓ Step 1: Fix preparador test imports and unify CLI with scanmap job
Corregir el namespace package shadowing que rompe las 13 pruebas del preparador y unificar `verascope-datos calcular` con `jobs/scanmap.py`.

- Crear `backend/verascope_datos/tests/conftest.py` que remueve la carpeta shadowing de `sys.path` antes de importar `verascope_datos`
- Verificar que `cd backend/verascope_datos && pytest tests -q` pase las 13 pruebas
- Unificar `cmd_calcular` en `cli.py` para que llame a `jobs.scanmap.correr()` en lugar de `calcular_resultados()` directamente — una sola implementación
- Agregar `--minimo-celdas N` al comando `calcular` del CLI para generar resultados parciales (filtra las primeras N celdas de la rejilla)
- Verificar `pytest -q` en backend (548+) y en preparador (13) en verde

### ✓ Step 2: Add scanmap state tracking and partial scan support
Hacer que el estado del escaneo se actualice correctamente durante un escaneo parcial y que la API lo lea.

- En `jobs/scanmap.py`, soportar `--minimo-celdas N`: filtrar la rejilla a las primeras N celdas antes de armar `tabla/` y calcular
- Asegurar que `escribir_estado` se llama con `celdas_total` correcto (N si es parcial, 4235 si es completo)
- Verificar que `leer_estado` en `app/datos/escaneo.py` funciona con resultados parciales
- Agregar prueba de escaneo parcial en `test_scanmap.py`

### ✓ Step 3: Document packaging, GitHub release and server deployment
Documentar el flujo completo de empaquetado, subida a GitHub release e instalación en el servidor.

- Actualizar `backend/verascope_datos/README.md` con:
  - Cómo correr `verascope-datos empaquetar` y subir el `.tar.gz` a un release de GitHub
  - Cómo correr `verascope-datos instalar <paquete> --datos /data` en el servidor
  - Cómo verificar con `verascope-datos estado` que la instalación es correcta
- Documentar la decisión sobre GLDAS (× 8) y NDVI de AppEEARS en `README.md`: si los datos están disponibles o no, y qué variables se ofrecen
- Verificar que `render.yaml` y `start-render.sh` usan `verascope-datos instalar` o el paquete del repo correctamente