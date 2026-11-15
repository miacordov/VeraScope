# Issue #3 · be/api-cache-despliegue

Owner: B1 · Branch: `be/api-cache-despliegue` · Status: in progress · Delivery: sliced commits, PR toward `main`

## Specs

S1. Caché nivel 1 (series): reutilizar `verascope_datos.almacen.Casillero` (SQLite WAL, float32, llave `lugar_celda`). Archivo: `backend/data/casillero.sqlite`.
S2. Caché nivel 2 (resultados): llave = celda + variable + ventana + índice + `VERSION_METODO`. No caduca salvo al subir `VERSION_METODO`.
S3. Cerrojo por celda: dos peticiones simultáneas a la misma celda nueva → una sola llamada a POWER.
S4. `analyze.py` real: validar (variable de las 5, años en [1981, VERASCOPE_FIN], ventana ≥ 10) → cuantizar → nivel 2 → nivel 1 → POWER timeout 8s → `analizar_celda` (B3) → guardar. Si la celda está en rejilla con ventana por defecto e índice ONI, sobrescribir veredicto y `p_ajustado` con los del escaneo (`origen = "escaneo"`); si no, `origen = "individual"`.
S5. Respuesta exacta del contrato `AnalyzeRespuesta`: fechas, series, rectas, vínculo, colinealidad, avisos, meses_inusuales, descarga.
S6. Errores en español con cuerpo estándar: `ventana_corta`, `fuera_de_rango`, `sin_datos_tierra`, `power_lento` con `celda_cercana`.
S7. `main.py` al arrancar: cargar catálogo, índices, `tabla/`, `celdas.npy`, `meses.json` y `resultados.parquet`. Recargar `resultados.parquet` si cambia su fecha en disco.
S8. Log de una línea por petición con `t_total_ms` y acierto/fallo de caché.
S9. `jobs/precalentar.py`: descargar de una en una, con pausas, celdas de demos y ~50 ciudades conocidas. Reutiliza el casillero; nunca repite la misma celda.
S10. Despliegue: healthcheck `/api/v1/salud`, HTTPS, CI/CD. Bloqueado: falta proveedor y autorización de cuenta.

## Tasks

- [ ] T1 · S1, S2, S3 · cache.py (dos niveles + cerrojo) · inline · commit: (humano)
- [ ] T2 · S4, S5, S6 · analyze.py real + respuesta contrato + errores · worker · commit: (humano)
- [ ] T3 · S7, S8 · main.py carga al arrancar + log con caché · inline · commit: (humano)
- [ ] T4 · S9 · jobs/precalentar.py · inline · commit: (humano)
- [ ] T5 · S10 · despliegue HTTPS + healthcheck · bloqueada: falta proveedor · commit: (humano)
- [ ] T6 · S1–S6 · pruebas: caché, cerrojo, analyze, rendimiento · inline · commit: (humano)

## Log

L1 (pedido original, literal): "arranquemos" — el usuario aceptó empezar la issue #3 tras revisar la lista de tareas.
L2: Orden de trabajo: T1 → T2 → T3 → T4 → T6. T5 bloqueada.
L3: Piezas de B2 y B3 ya están en main y mergeadas en la rama.
