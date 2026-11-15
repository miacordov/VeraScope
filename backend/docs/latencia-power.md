# Latencia de NASA POWER (20 celdas)

Medida el 2026-11-14T20:08:49 desde la laptop del equipo (no desde la sede). Endpoint mensual por punto, `parameters=PRECTOTCORR,T2M,GWETROOT,GWETTOP,RH2M`, `community=AG`, 1981–2025, una petición por segundo, timeout 60 s.

| # | lat | lon | HTTP | segundos | KB |
|---:|---:|---:|---:|---:|---:|
| 1 | -6.0 | -79.5 | 200 | 1.74 | 41.5 |
| 2 | -3.5 | -80.0 | 200 | 1.51 | 41.6 |
| 3 | -8.0 | -79.0 | 200 | 0.78 | 41.4 |
| 4 | -17.0 | -71.0 | 200 | 0.96 | 41.6 |
| 5 | -33.5 | -70.5 | 200 | 1.26 | 41.6 |
| 6 | 4.5 | -74.0 | 200 | 1.14 | 41.7 |
| 7 | 9.0 | -79.5 | 200 | 1.30 | 41.7 |
| 8 | 19.5 | -99.0 | 200 | 1.27 | 41.6 |
| 9 | 21.0 | -157.5 | 200 | 2.55 | 41.7 |
| 10 | -17.5 | 178.0 | 200 | 1.67 | 41.7 |
| 11 | -6.0 | 106.5 | 200 | 5.12 | 41.7 |
| 12 | 1.5 | 103.5 | 200 | 1.83 | 41.7 |
| 13 | 14.5 | 121.0 | 200 | 5.61 | 41.8 |
| 14 | -27.5 | 153.0 | 200 | 8.83 | 41.6 |
| 15 | -33.5 | 151.0 | 200 | 1.14 | 41.6 |
| 16 | -23.5 | 133.5 | 200 | 1.16 | 41.5 |
| 17 | -8.5 | 115.0 | 200 | 0.95 | 41.7 |
| 18 | 3.0 | 113.5 | 200 | 1.22 | 41.9 |
| 19 | 10.5 | 106.5 | 200 | 1.19 | 41.6 |
| 20 | 0.0 | -150.0 | 200 | 2.59 | 42.3 |

**Resumen:** 20/20 respuestas 200 · mínimo 0.78 s · mediana 1.29 s · media 2.19 s · p90 5.12 s · máximo 8.83 s.

**Lectura:** la mayoría responde en 1–2 s, pero hay colas de 5–9 s. Con `VERASCOPE_POWER_TIMEOUT=8` una de las 20 (5 %) habría terminado en `power_lento` (504): el precalentamiento de celdas y la caché son necesarios. Repetir la medición desde la sede antes de prometer cifras.
