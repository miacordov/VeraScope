# S1 · Backend (B1, B2, B3)

Sprint S1 del backend de VeraScope, un responsable por bloque, avanzando uno por uno.
Guía obligatoria: `backend/CLAUDE.md` (secciones 2, 6, 8, 12, 13, 17). Leer hasta `## Log`.

## Specs

S1. B1 · be/api-cache-despliegue (#3)
- "datos/cache.py: nivel 1 = casillero SQLite del preparador (backend/data/casillero.sqlite, llave lugar_celda); nivel 2 = resultados con llave celda + variable + ventana + índice + VERSION_METODO."
- "Cerrojo por celda (dos peticiones a una celda nueva → una sola llamada a POWER)."
- "Esqueleto de la ruta analyze real (validar → cuantizar → caché → POWER 8 s → motor → guardar → origen) usando stubs de B2/B3 hasta que lleguen."
- "Errores en español sencillo; power_lento con celda_cercana."
- "Log de una línea por petición (t_total_ms, acierto/fallo de caché)."
- "Despliegue continuo desde main; volumen VERASCOPE_DATOS=/data."

S2. B2 · be/datos-power (#2) → cierra hora 12
- "celdas.py terminado, con regla de empates x.25/x.75."
- "power_client.py: 5 variables en una petición; timeout parámetro (8 s vivo / 60 s lote); -999 → NaN; ignora mes \"13\"; espera creciente ante 429."
- "validacion.py: huecos ≤ 2 meses se interpolan; > 10 % faltante o hueco > 2 se descarta; mínimo 120 meses; aviso bajo 240; suelo sobre mar → sin_datos_tierra."
- "indices.py: ONI y Niño 1+2 locales; fases nino/nina/neutro; Niño 1+2 desde 1982; recorte al último mes con índice."
- "Una sola implementación compartida con el preparador."
- "Pruebas sin red (cuantización, geografía, calidad, ventana, cliente con servidor falso)."
- "Hora 8: lanzar descarga completa en segundo plano (verascope-datos power, ~71 min, demos primero). Vigilarla."
- "Hora 12: PR de be/datos-power a main; empezar be/scanmap-job (#5)."

S3. B3 · be/motor-enso (#4)
- "anomalias.py (climatología dentro de la ventana)."
- "enso.py: rezago 0–6, regresión conjunta con tendencia, serie sin El Niño, n_efectivo, colinealidad."
- "tendencia.py: Theil-Sen a mano, Mann-Kendall Hamed-Rao 12 rezagos, IC con la misma varianza que el p-valor, cambio total, cambio % (nunca en temperatura), recta."
- "veredicto.py (cuatro estados y avisos) y fdr.py (Benjamini-Hochberg)."
- "Pruebas: recuperación, sin tendencia, coherencia IC ↔ p (0 % contradicciones), falsos positivos, potencia, correlación con tamaño efectivo, mismos meses, rendimiento."

## Tasks

- [ ] T1 · S1 · pendiente de visto bueno del plan · rama be/api-cache-despliegue · commit: —
- [ ] T2 · S2 · pendiente · rama be/datos-power · commit: —
- [ ] T3 · S3 · pendiente · rama be/motor-enso · commit: —

## Log

L1 (pedido original, literal): "Backend B1 · be/api-cache-despliegue (#3) ... B3 · be/motor-enso (#4) ... avancemos uno por uno" (texto completo en S1–S3).
L2: Previo: chore/verifica-b1 verifica B1 de S0 (184 pruebas, ruff, Docker, latencia en backend/docs/latencia-power.md). Despliegue HTTPS de S0 bloqueado: falta hosting y autorización de cuenta.
L3: Hallazgo B2 S0: POWER usa 0.625° en longitud (MERRA-2 nativo); decisión de equipo pendiente, celdas.py sigue la regla 0.5° de la guía.
L4: Decisión del humano sobre la malla: "Mantener 0.5° y declararlo". celdas.py sigue igual; queda documentado en backend/docs/comprobaciones-b2.md.
L5: Comprobaciones B2 verificadas con POWER real (14-nov-2026): PRECTOTCORR en mm/day, mes 13 presente, GWETROOT -999 en el mar y GWETTOP 1.0. Pendiente: Prueba rápida del panel y latencia desde la sede.
