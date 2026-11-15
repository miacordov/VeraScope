# Issue #7 · be/scan-feed-api

Owner: B1 · Branch: `be/scan-feed-api` · Status: in progress · Delivery: sliced commits, PR toward `main`

## Specs

S1. `GET /api/v1/scan/feed?tipo=fuertes|opuestas|ocultas&pagina=N` — 20 tarjetas por página. `fuertes`: veredicto `cambio_robusto`, orden por |efecto|. `opuestas`: una tarjeta por par, con `pareja`. `ocultas`: veredicto `cambio_oculto`. Id estable `{variable}-{celda}`. Campos: `p_ajustado`, `ic_bajo`, `ic_alto`, `efecto`, `unidad`.
S2. Titulares por plantilla desde `catalogo/titulares.json`, nunca con un modelo de lenguaje. Sujeto con artículo por variable.
S3. Escaneo incompleto: `scan/feed` responde 200 con `escaneo.estado = "en_curso"`, avance y sin tarjetas; `scan/layer` responde 503 `escaneo_en_curso`.
S4. `GET /api/v1/scan/layer?variable=…` — columnas paralelas (lat, lon, veredicto, pendiente_decada, efecto), 4235 valores, `null` donde no hay serie válida. GZip.
S5. `salud`, `variables`, `glosario` y `demos/{id}` desde catálogo. `variables.json` se genera desde el preparador.
S6. Lo que dice el feed es exactamente lo que muestra el detalle (`analyze` con `origen = "escaneo"`).

## Tasks

- [ ] T1 · S1, S2, S3 · scan.py: feed real con titulares y estado del escaneo · worker · commit: (humano)
- [ ] T2 · S4, S3 · scan.py: layer real con columnas paralelas · inline · commit: (humano)
- [ ] T3 · S5 · catalogo.py: salud, variables, glosario, demos reales · inline · commit: (humano)
- [ ] T4 · S2 · catalogo/titulares.json: plantillas de titulares por variable · inline · commit: (humano)
- [ ] T5 · S1-S6 · pruebas: feed, layer, contrato, rendimiento · worker · commit: (humano)

## Log

L1 (pedido original, literal): "verifica y empecemos de nuevo con el issue #7"
L2: Base: main actualizado con PR #30 (issue #3) mergeado, 497 tests verde, ruff limpio.
L3: Orden de trabajo: T4 → T1 → T2 → T3 → T5.
