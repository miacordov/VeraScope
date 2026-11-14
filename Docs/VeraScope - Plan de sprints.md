# VeraScope · Plan de sprints (48 horas)

NASA Space Apps Challenge 2026 · Earth System Trend Detective
Equipo: 3 backend (B1, B2, B3) y 3 frontend (F1, F2, F3) · Basado en el informe técnico v2 y en el reparto de tareas v1 (14-nov-2026).

Este documento ordena el reparto de tareas en **sprints cortos**. Cada sprint tiene un objetivo, lo que hace cada persona, qué le entrega a quién y cómo se sabe que terminó. Las horas son "horas de evento" (hora 0 = arranque).

---

## 0. Cómo usar este plan

- **Un sprint = un bloque de 4 a 8 horas** con un objetivo de integración. Al cerrar cada sprint, lo terminado entra a `main` por PR con CI en verde.
- **Inicio de sprint (10 min, de pie):** cada persona dice qué va a fusionar al cierre y qué espera de otro.
- **Cierre de sprint (15 min):** se prueba el criterio de cierre en un teléfono real y en la web. Si no se cumple, se aplica el orden de recorte (sección 9); **el hito no se mueve**.
- **Handoff = entrega explícita.** Si tu tarea depende de algo de otra persona, la tabla "Entregas entre personas" de cada sprint dice quién, qué y a qué hora. Si a esa hora no llegó, se usa el JSON simulado y se avisa en el canal.
- Las tareas tienen casillas `- [ ]` para que cada persona las marque en su issue de GitHub.

### Quién toca qué (para no pisarse)

| Rol | Carpetas y archivos propios | Ramas (issue) |
|---|---|---|
| B1 | `backend/app/main.py`, `app/api/`, `app/contracts/`, `app/datos/cache.py`, `app/catalogo/`, `jobs/precalentar.py`, `jobs/instantaneas.py`, `backend/Dockerfile`, `.github/workflows/backend.yml` | `chore/contratos` (#1), `be/api-cache-despliegue` (#3), `be/scan-feed-api` (#7), `be/instantaneas-demo` (#8) |
| B2 | `app/datos/` (power_client, celdas, validacion, indices), `jobs/scanmap.py`, `backend/verascope_datos/`, `backend/data/` | `be/datos-power` (#2), `be/scanmap-job` (#5) |
| B3 | `app/estadistica/`, `app/api/teleconnect.py` y `compare_periods.py` (con B1), `backend/tests/` | `be/motor-enso` (#4), `be/teleconexion-periodos` (#6) |
| F1 | esqueleto `frontend/`, `src/features/map/`, `variable-picker/`, `teleconnection-lines/`, `src/estado/store.ts`, `src/shared/geo.ts`, `tema.ts`, `src/shared/api/`, `app/espacio.tsx`, `assets/geo/`, `.github/workflows/frontend.yml` | `chore/contratos` (#1), `fe/mapa-celda` (#9), `fe/lineas-mosaico` (#13) |
| F2 | `src/features/series-charts/`, `enso-toggle/`, `time-comparator/`, `src/estado/queryClient.ts`, `eas.json`, `app.json` | `fe/graficos-enso` (#10), `fe/distribucion` (#12), `fe/tiempo-comparador` (#14) |
| F3 | `src/features/verdict-card/`, `scan-feed/`, `guided-tours/`, `glossary/`, `src/shared/components/`, `src/shared/format.ts`, `app/_layout.tsx`, `app/index.tsx`, `app/glosario.tsx`, `assets/demo/` |  `fe/veredicto-feed` (#11), `fe/demos-glosario` (#15) |

Archivos compartidos con un solo dueño: **contratos** (B1; aprueban B1 + F1), **`store.ts`** (F1; aprueban F1 + F2 + F3), **`constantes.py`** (lo crea B1, lo revisa B3).

---

## 1. Vista general

| Sprint | Horas | Nombre | Cierra con |
|---|---|---|---|
| S-pre | antes | Preparación | Decisiones tomadas, cuentas listas, issues asignados |
| S0 | 0–6 | Cimientos | **Hito 6:** URL HTTPS + app recibe `analyze` simulado |
| S1 | 6–13 | Piezas base | Datos POWER y motor con pruebas; mapa y gráfico con simulado |
| S2 | 13–20 | Flujo real | **Hito 20:** toque en el mapa → veredicto con datos reales |
| S3 | 20–28 | Diferenciadores I | Teleconexión, feed y tiempo funcionando en `main` |
| S4 | 28–36 | Diferenciadores II y demos | **Hito 36:** las dos demos completas (congelamiento) |
| S5 | 36–44 | Sin red y pulido | APK y web finales, demos sin red, solo `fix/…` |
| S6 | 44–48 | Entrega | Entregables enviados, etiqueta `v1.0-entrega` |

Línea de tiempo por persona (ramas):

```
hora      0    6    12   18   24   30   36   42   48
B1   [contratos][api-cache-despliegue ][scan-feed][...][instantaneas][entrega]
B2   [prueba][datos-power][scanmap-job ][satelites/demos][  apoyo   ]
B3   [prep  ][ motor-enso    ][teleconexion-periodos][demos][ apoyo ]
F1   [contratos/esqueleto][mapa-celda][   lineas-mosaico   ][ fix ]
F2   [apoyo][distribucion][graficos-enso][tiempo-comparador][distribucion final]
F3   [marca ][     veredicto-feed            ][demos-glosario][pulido/entrega]
```

---

## S-pre · Preparación (antes del evento)

**Objetivo:** llegar a la hora 0 sin decisiones abiertas que frenen a nadie.

| Tarea | Dueño |
|---|---|
| - [ ] Completar la tabla "Quién es quién" (persona ↔ rol ↔ usuario de GitHub) | Todos |
| - [ ] Asignar los issues #1–#15 en GitHub y proteger `main` (revisión + CI obligatorios) | miacordov |
| - [ ] Averiguar entregables de la sede y hora de cierre | B1 (con todos) |
| - [ ] Decidir cuándo corre la descarga de las 4235 celdas (hora 8 o antes) | B2 propone, todos deciden |
| - [ ] Cuenta de Apple Developer (TestFlight) o iOS solo con Expo Go | F2 propone, todos deciden |
| - [ ] Cuenta de Expo creada (`eas login`) | F2 |
| - [ ] Cuenta de NASA Earthdata (solo en el panel o en variables de entorno) | B2 |
| - [ ] Elegir hosting HTTPS para la API y hosting estático para la web | B1 / F2 |
| - [ ] Cada persona lee su guía (`backend/CLAUDE.md` o `frontend/CLAUDE.md`) y su issue | Todos |
| - [ ] Conseguir logo y hoja de marca (`VeraScope-logo-mision.zip`, `VeraScope-hoja-de-marca-mision.png`) | F3 |

---

## S0 · Cimientos (horas 0–6) → Hito 6

**Objetivo:** contrato aprobado, backend simulado desplegado con HTTPS, app en un teléfono real recibiendo un `analyze` simulado. A partir de aquí **todos trabajan contra el contrato**, no contra el código del otro.

### Backend

**B1 · `chore/contratos` (#1)**
- [ ] `backend/pyproject.toml` (Python 3.11, FastAPI, Pydantic v2, uvicorn, numpy, pandas, scipy ≥ 1.11, pymannkendall, pyarrow, requests; extra dev: pytest, ruff).
- [ ] Árbol `backend/app/` (api, contracts, datos, estadistica, catalogo), `jobs/`, `tests/`.
- [ ] Modelos Pydantic de todas las rutas y del error estándar, con las enumeraciones exactas (sección 17 de la guía).
- [ ] `estadistica/constantes.py` con todas las constantes y `VERSION_METODO = 1`.
- [ ] JSON simulados de cada ruta en `catalogo/simulado/` + prueba que los valida contra los modelos.
- [ ] `main.py`: `/api/v1`, GZip, CORS solo web (`VERASCOPE_CORS`), modo `VERASCOPE_SIMULADO=1`, ruta salud.
- [ ] `Dockerfile` ligero + `.dockerignore` (excluye `verascope_datos/`, `data/`, `tests/`).
- [ ] CI `.github/workflows/backend.yml`: `ruff check`, `ruff format --check`, `pytest -q`.
- [ ] Desplegar modo simulado con HTTPS y anotar la URL en el README.
- [ ] Medir latencia de NASA POWER con 20 celdas (una por segundo); tabla en el PR.

**B2 · comprobaciones (inicia `be/datos-power` #2 en la hora 2)**
- [ ] Abrir el panel (`abrir-panel.sh` / `Abrir-panel.bat`) y correr la Prueba rápida (índices NOAA + 3 demos POWER).
- [ ] Último año completo de MERRA-2 en POWER con una consulta real → fija `VERASCOPE_FIN`.
- [ ] Verificar con dos consultas vecinas que `0.5·round(x/0.5)` cae en la misma celda que POWER.
- [ ] Comprobar: celda oceánica → `-999` en GWETROOT; PRECTOTCORR mensual en mm/día; aparece el mes `"13"`.
- [ ] Hora 2–6: empezar `celdas.py` (cuantización única, 0..360 ↔ −180..180, rejilla 4235, llave `lugar_celda`).

**B3 · preparación**
- [ ] Leer `motor.py` del preparador y las 5 diferencias conocidas (sección 7 de la guía backend).
- [ ] Series sintéticas con semilla fija para las pruebas.
- [ ] Revisar con B1 `constantes.py`.

### Frontend

**F1 · `chore/contratos` (#1)**
- [ ] Hora 0: app con Expo SDK 57 (Expo Router, TypeScript estricto); abrirla en teléfono real con Expo Go. Si falla: plan B (expo-dev-client o APK) y avisar.
- [ ] `npx expo install` de todo el stack (incluye react-native-web, react-dom, @expo/metro-runtime, persistencia AsyncStorage) + `npx expo install --check`.
- [ ] Scripts: `test`, `lint`, `tipos` (desde `/openapi.json`), `demo:copiar`.
- [ ] `store.ts` (sección 7), `tema.ts`, `geo.ts`, cliente único en `shared/api/`, fixtures desde los JSON simulados.
- [ ] Pantallas mínimas (`_layout`, `index`, `espacio`, `glosario`) con banda "Datos simulados"; `espacio.tsx` muestra un `analyze` simulado.
- [ ] CI `.github/workflows/frontend.yml`: `npm ci`, `tsc --noEmit`, `npm run test`, `npx expo export -p web`.
- [ ] Hora 0: confirmar con el equipo "una sola base con Expo" y la versión de Expo Go en tiendas.
- [ ] Hora 3: empezar `fe/mapa-celda` (#9).

**F2 · apoyo al esqueleto**
- [ ] `eas login`; revisar con F1 que el esqueleto compile en web.
- [ ] `queryClient.ts` mínimo para el hito.

**F3 · marca y navegación**
- [ ] Logo y hoja de marca en `assets/` (no redibujar el logo).
- [ ] Revisar con F1 `_layout.tsx` (Inter con pantalla de arranque, barra de estado, áreas seguras).
- [ ] Leer la sección 11 de la guía (estados de error) y preparar los textos.

### Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| ~2 | B1 → F1 | Modelos Pydantic y JSON simulados (para tipos y fixtures) |
| ~3 | B1 → B3 | `constantes.py` para revisar |
| ~5 | B1 + F1 | Aprobación conjunta del contrato (`chore/contratos` a `main`) |
| 6 | B1 → todos | URL HTTPS del modo simulado |

### Criterio de cierre (Hito 6)
- [ ] URL pública con HTTPS responde `analyze` simulado.
- [ ] La app, en un teléfono real y en la web, muestra esa respuesta.
- [ ] CI backend y frontend en verde en `main`.

---

## S1 · Piezas base (horas 6–13)

**Objetivo:** cada pieza funciona sola contra el contrato: datos de POWER limpios, motor estadístico probado, mapa con celda, gráfico e interruptor con datos simulados, primer APK en camino.

### Backend

**B1 · `be/api-cache-despliegue` (#3)**
- [ ] `datos/cache.py`: nivel 1 = casillero SQLite del preparador (`backend/data/casillero.sqlite`, llave `lugar_celda`); nivel 2 = resultados con llave celda + variable + ventana + índice + `VERSION_METODO`.
- [ ] Cerrojo por celda (dos peticiones a una celda nueva → una sola llamada a POWER).
- [ ] Esqueleto de la ruta `analyze` real (validar → cuantizar → caché → POWER 8 s → motor → guardar → origen) usando *stubs* de B2/B3 hasta que lleguen.
- [ ] Errores en español sencillo; `power_lento` con `celda_cercana`.
- [ ] Log de una línea por petición (`t_total_ms`, acierto/fallo de caché).
- [ ] Despliegue continuo desde `main`; volumen `VERASCOPE_DATOS=/data`.

**B2 · `be/datos-power` (#2) → cierra hora 12**
- [ ] `celdas.py` terminado, con regla de empates x.25/x.75.
- [ ] `power_client.py`: 5 variables en una petición; timeout parámetro (8 s vivo / 60 s lote); `-999 → NaN`; ignora mes `"13"`; espera creciente ante 429.
- [ ] `validacion.py`: huecos ≤ 2 meses se interpolan; > 10 % faltante o hueco > 2 se descarta; mínimo 120 meses; aviso bajo 240; suelo sobre mar → `sin_datos_tierra`.
- [ ] `indices.py`: ONI y Niño 1+2 locales; fases nino/nina/neutro; Niño 1+2 desde 1982; recorte al último mes con índice.
- [ ] Una sola implementación compartida con el preparador.
- [ ] Pruebas sin red (cuantización, geografía, calidad, ventana, cliente con servidor falso).
- [ ] **Hora 8:** lanzar descarga completa en segundo plano (`verascope-datos power`, ~71 min, demos primero). Vigilarla.
- [ ] Hora 12: PR de `be/datos-power` a `main`; empezar `be/scanmap-job` (#5).

**B3 · `be/motor-enso` (#4)**
- [ ] `anomalias.py` (climatología dentro de la ventana).
- [ ] `enso.py`: rezago 0–6, regresión conjunta con tendencia, serie sin El Niño, `n_efectivo`, colinealidad.
- [ ] `tendencia.py`: Theil-Sen a mano, Mann-Kendall Hamed-Rao 12 rezagos, IC con la misma varianza que el p-valor, cambio total, cambio % (nunca en temperatura), recta.
- [ ] `veredicto.py` (cuatro estados y avisos) y `fdr.py` (Benjamini-Hochberg).
- [ ] Pruebas: recuperación, sin tendencia, coherencia IC ↔ p (0 % contradicciones), falsos positivos, potencia, correlación con tamaño efectivo, mismos meses, rendimiento.

### Frontend

**F1 · `fe/mapa-celda` (#9)**
- [ ] Costas Natural Earth 110m en `assets/geo/tierra.json`; proyección equirrectangular centrada en el Pacífico (vista 90–330).
- [ ] Polígonos dibujados con desplazamiento 0 y +360 (sin rayas); puntos con lon360.
- [ ] Toque → celda cuantizada → rectángulo visible (≥ ~12 px); manda la celda que devuelve la API.
- [ ] Gestos (arrastrar, pellizcar, tocar), rueda en web, botones ＋/−, Restablecer vista; accesos a Piura, Borneo y norte de Australia.
- [ ] Selector de variable (desde `/variables`), ventana (< 10 años no se envía) e índice (Niño 1+2 deshabilitado hasta que B3 decida).

**F2 · `fe/distribucion` (#12) primero, luego `fe/graficos-enso` (#10)**
- [ ] `eas.json` con perfil `preview` (APK) y `expo.android.package`.
- [ ] `EXPO_PUBLIC_API_URL` a la URL HTTPS (nunca `http://`).
- [ ] Primer APK: `eas build -p android --profile preview`; instalarlo en teléfono real.
- [ ] Primera web con `npx expo export -p web` en hosting estático; pasar el origen a B1 (CORS).
- [ ] Anotar tiempos de cola de EAS.
- [ ] Empezar `GraficoSerie` (react-native-svg + d3; los `null` son huecos).

**F3 · `fe/veredicto-feed` (#11), parte veredicto**
- [ ] Tarjeta: "Tendencia aparente" con interruptor apagado; insignia de cuatro estados con interruptor encendido.
- [ ] Pendiente por década con IC y unidad; cambio % solo si viene; p-valor ("corregido por muchas pruebas" si viene del escaneo); vínculo con El Niño (indicativo); avisos tal cual; fuente; insignia "análisis individual".
- [ ] Veredicto por texto + icono + forma; anuncio a lectores de pantalla.
- [ ] `format.ts`: un solo formateador `es-PE`, siempre con unidad.

### Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| 8 | B2 → todos | Descarga completa arrancada (aviso en el canal) |
| ~10 | F2 → B1 | Origen de la web publicada para `VERASCOPE_CORS` |
| 12 | B2 → B1 | `power_client`, `celdas`, `validacion`, `indices` en `main` |
| 13 | B3 → B1, B2 | API pública del motor (firma de funciones) aunque el PR siga abierto |

### Criterio de cierre (hora 13)
- [ ] `be/datos-power` fusionado con pruebas en verde.
- [ ] Motor con pruebas obligatorias corriendo (PR abierto o fusionado).
- [ ] Mapa con toque → celda funcionando sobre simulado, en teléfono y web.
- [ ] Primer APK instalado o, como mínimo, build en cola.

---

## S2 · Flujo real (horas 13–20) → Hito 20

**Objetivo:** unir datos + motor + API + app. Un toque en el mapa devuelve un veredicto calculado con datos reales de POWER. Mientras tanto, ScanMap se calcula en segundo plano.

### Backend

**B1 · cierra `be/api-cache-despliegue` (#3) → hora 20**
- [ ] Conectar `analyze` con el cliente de B2 y el motor de B3 (quitar *stubs*).
- [ ] Carga en memoria al arrancar (catálogo, índices, `tabla/`, `resultados.parquet`) y recarga del parquet si cambia.
- [ ] Instalar el paquete de datos de B2 en el servidor (`verascope-datos instalar … --datos /data`).
- [ ] `jobs/precalentar.py`: celdas de las demos y ~50 ciudades, de una en una, con pausas.
- [ ] Confirmar con F1 el hito 20.

**B2 · `be/scanmap-job` (#5) → cierra hora 20**
- [ ] `jobs/scanmap.py`: armar `tabla/` y calcular celda × variable **con el motor de B3** (no con copia), en paralelo.
- [ ] `verascope-datos calcular` usa ese mismo motor.
- [ ] Benjamini-Hochberg en dos familias de 21 175 pruebas; ranking por tamaño del efecto; pares opuestos > 1500 km.
- [ ] `resultados.parquet` con exactamente las columnas del contrato; estado del escaneo (`en_curso` / `completo`).
- [ ] Prueba de consistencia escaneo ↔ vivo (con B3).
- [ ] `verascope-datos empaquetar` y subir el `.tar.gz` a un release de GitHub (nunca al repo); pasarlo a B1 y al equipo.

**B3 · cierra `be/motor-enso` (#4) → hora 18; empieza `be/teleconexion-periodos` (#6)**
- [ ] Resolver las 5 diferencias del preparador (mismos meses en ambas tendencias, orden calidad ↔ anomalías, BH en `p_enso` por escrito, `n_efectivo`).
- [ ] El preparador importa este motor (o se borra su copia): prohibido mantener dos.
- [ ] Hora 18: PR a `main`.
- [ ] Hora 18–20: matrices precalculadas por variable para `teleconexion.py`.
- [ ] **Hora 20: decidir Niño 1+2** como índice alternativo (Piura r = 0,30 vs 0,18 con ONI) y avisar a F1.

### Frontend

**F1 · cierra `fe/mapa-celda` (#9) → hora 14**
- [ ] Diseño adaptable de `espacio.tsx` (teléfono con hoja inferior, tableta, web/laptop).
- [ ] Antes de hora 14: medir rendimiento en un Android de gama baja (decide si el mosaico se recorta).
- [ ] Antes de hora 14: proponer con captura los colores de La Niña y de la línea de mismo efecto (aprueba F2 o F3).
- [ ] Hora 14–20: cambiar el cliente de simulado a la API real y probar con B1; preparar estructura de `teleconnection-lines/`.

**F2 · `fe/graficos-enso` (#10) → cierra hora 20**
- [ ] Panel Causa (índice con franjas El Niño / La Niña con trama), Consecuencia (`serie_z` de celda y destino), Realidad (original o sin El Niño, recta y meses inusuales).
- [ ] Ejes sincronizados con `mesVisible`; lectura con dedo/cursor (contexto de React, no el store).
- [ ] Interruptor "Quitar El Niño" accesible: cambia gráfico y veredicto sin red, con frase de rezago.
- [ ] `queryClient.ts` completo: llaves, `staleTime: Infinity`, persistencia AsyncStorage con buster, sin reintentar `power_lento`, esqueletos al cargar.
- [ ] Pruebas: interruptor sin red (10 veces, 0 llamadas), una llamada por análisis, huecos en los `null`.

**F3 · `fe/veredicto-feed` (#11), parte inicio y errores**
- [ ] Página de Inicio: frase de VeraScope, Investigar, Escanear, acceso a las dos demos, "Usar demo sin conexión".
- [ ] Estados de error de la sección 11 (`power_lento` con botón de celda cercana, `sin_datos_tierra`, error de red).
- [ ] Conectar la tarjeta al interruptor de F2 (vía store, aprobado por F1 + F2 + F3).
- [ ] Empezar el feed de ScanMap contra el JSON simulado de `scan/feed`.

### Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| 14 | F1 → F2/F3 | Captura con colores propuestos para aprobar |
| 18 | B3 → B1, B2 | Motor en `main` (B2 lo usa en ScanMap; B1 en `analyze`) |
| ~19 | B2 → B1 | Release con el paquete de datos `.tar.gz` |
| 20 | B3 → F1 | Decisión Niño 1+2 (habilitar o no el selector) |
| 20 | B1 + F1 | Prueba conjunta del hito |

### Criterio de cierre (Hito 20)
- [ ] Toque en el mapa (teléfono y web) → veredicto mensual calculado con datos reales de POWER.
- [ ] El interruptor cambia gráfico y veredicto sin red.
- [ ] ScanMap calculado o en curso con estado visible.
- [ ] Si no se cumple: se recorta según la sección 9, el hito no se mueve.

---

## S3 · Diferenciadores I (horas 20–28)

**Objetivo:** que existan las funciones que hacen única a VeraScope: líneas causa → consecuencia, feed de ScanMap y reproducción en el tiempo.

### Backend

**B1 · `be/scan-feed-api` (#7)**
- [ ] Ruta `scan/feed` (pestañas fuertes, opuestas, ocultas; 20 por página; id estable; `en_curso` con 200).
- [ ] Ruta `scan/layer` (columnas paralelas, `null` sin serie, GZip; 503 `escaneo_en_curso`).
- [ ] Rutas `variables`, `glosario` y `demos/{id}` desde `catalogo/`.
- [ ] `catalogo/variables.json` con `verascope-datos variables --json` + definiciones en español sencillo de las 5 variables.
- [ ] `catalogo/glosario.json` y `catalogo/titulares.json` (plantillas, nunca con modelo de lenguaje).

**B2 · datos de apoyo**
- [ ] `verascope-datos satelites` (V8–V12 para las 3 demos) con cuenta Earthdata.
- [ ] Verificar escorrentía de GLDAS (× 8) y capa NDVI de AppEEARS con servicios reales; decisión escrita en `backend/verascope_datos/README.md`.
- [ ] Revisar los resultados del escaneo (valores raros, celdas vacías) y avisar a B3.

**B3 · `be/teleconexion-periodos` (#6)**
- [ ] `teleconexion.py`: correlación en una operación, tamaño efectivo, BH, condición de causa común, destinos > 1500 km y separados > 1000 km, máx. 3 opuestas + 2 iguales, `meses_coincidencia`, `mensaje_vacio`.
- [ ] Ruta `teleconnect` (con B1); 503 sin escaneo; T2M responde sin líneas con su mensaje.
- [ ] Pruebas: mundo sintético (líneas desde "Piura" caen en Indonesia y norte de Australia), haversine y cruce de ±180°, rendimiento < 50 ms.

### Frontend

**F1 · `fe/lineas-mosaico` (#13)**
- [ ] Arco celda → destino cruzando el Pacífico: opuesto continua y roja, mismo efecto punteada.
- [ ] Se encienden solo en meses de coincidencia al reproducir; franja "Efecto opuesto · r · km · meses a la vez".
- [ ] Zona táctil ancha, `elegirDestino`, lista accesible en texto, `mensaje_vacio`, aviso de escaneo en curso.

**F2 · `fe/tiempo-comparador` (#14), parte tiempo**
- [ ] Reproducir/Pausa y barra de tiempo accesible; ~30 s por tiempo transcurrido; actualiza `mesVisible` solo al cambiar de mes; nunca recalcula.
- [ ] Prueba con temporizadores falsos: reproducción sin red.

**F3 · cierra `fe/veredicto-feed` (#11) → hora 28**
- [ ] Feed: botón Escanear, tres pestañas, FlatList paginada, titular tal como llega, tocar tarjeta → detalle, "Escaneo en curso" con avance.
- [ ] Conectar a `scan/feed` real cuando B1 lo fusione.
- [ ] Hora 24: empezar `fe/demos-glosario` (#15): ejecutor de guiones con Anterior / Siguiente / Salir.

### Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| ~24 | B1 → F3 | `scan/feed`, `glosario`, `demos/{id}` en `main` |
| ~25 | B3 → F1 | `teleconnect` en `main` (antes: JSON simulado) |
| ~26 | B1 → F1 | `scan/layer` en `main` |
| 28 | F2 → F1 | `mesVisible` animado (para encender las líneas) |

### Criterio de cierre (hora 28)
- [ ] Desde Piura salen líneas reales hacia el otro lado del Pacífico.
- [ ] Reproducción en el tiempo enciende las líneas en los meses de coincidencia.
- [ ] Feed de ScanMap lista hallazgos reales y abre el detalle.

---

## S4 · Diferenciadores II y demos (horas 28–36) → Hito 36 (congelamiento)

**Objetivo:** terminar lo que falta, ajustar las demos a los datos reales y congelar funciones.

### Backend

**B1 · cierra `be/scan-feed-api` (#7) y prepara congelamiento**
- [ ] Guiones `catalogo/demos/efecto-espejo.json` y `senal-o-ruido.json` (con F3 y B3).
- [ ] `VERASCOPE_CORS` con el origen final de la web (de F2).
- [ ] Hora 36: etiqueta `v1.0-freeze` y rama `release/demo`.

**B2 · respaldo de demos**
- [ ] `verascope-datos demos` → respaldo JSON de las 3 demos en `backend/data/demo/` (sí va a Git).
- [ ] Mantener en verde las 13 pruebas del preparador.
- [ ] Apoyar a B1/B3 con correcciones del escaneo.

**B3 · cierra `be/teleconexion-periodos` (#6) → hora 30; demos**
- [ ] `periodos.py`: diferencia entre periodos (original y sin El Niño, descriptiva) y meses inusuales (|z| > 2) con su fase.
- [ ] Ruta `compare-periods` (con B1).
- [ ] Hora 30–36: con datos reales, revisar hacia dónde apuntan las líneas de Piura y qué veredicto sale; ajustar con F3 el guion de la demo 1 **a los datos**.
- [ ] Elegir con F3 la celda de la demo 2 (temperatura).
- [ ] Si los datos contradicen los informes, decirlo al equipo.

### Frontend

**F1 · cierra `fe/lineas-mosaico` (#13) → hora 32**
- [ ] Mosaico de ScanMap en pocos `Path` agrupados; medir en teléfono modesto (si no alcanza, se recorta y se avisa).
- [ ] Captura de la línea de Piura cruzando el Pacífico con datos reales.
- [ ] Hora 32–36: corregir lo que salga del ensayo de demos; revisar PR de F3.

**F2 · cierra `fe/tiempo-comparador` (#14) → hora 32**
- [ ] "Antes y después": periodos editables, `compare-periods`, diferencia original y sin El Niño, meses inusuales en El Niño, nota descriptiva.
- [ ] Hora 30 (solo si sobra tiempo): decidir franja de CO₂ de Mauna Loa como contexto, sin correlacionarla.

**F3 · cierra `fe/demos-glosario` (#15) → hora 36**
- [ ] Todas las acciones del contrato en el ejecutor de guiones.
- [ ] Demo 1 "El efecto espejo de El Niño" (núcleo) y Demo 2 "¿Señal real o ruido climático?".
- [ ] Modo sin red: respuestas en `assets/demo/` (con `npm run demo:copiar`) y banda "Sin conexión · mostrando la demo guardada en la app".
- [ ] Página de glosario (desde `/glosario`), enlaces desde la tarjeta y créditos (Natural Earth, NASA POWER, NOAA CPC).
- [ ] Ensayar en proyector y en teléfono a plena luz; si el tema oscuro se ve lavado, ajustar tokens con F1.

### Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| 30 | B3 → F2 | `compare-periods` en `main` |
| ~33 | B3 + F3 → B1 | Guion final demo 1 y celda demo 2 |
| ~34 | B1 → F3 | Primera tanda de respuestas de demo regeneradas |
| 36 | B1 → todos | `v1.0-freeze` y `release/demo` abiertas |

### Criterio de cierre (Hito 36)
- [ ] Las dos demos corren completas en teléfono y web, con y sin red.
- [ ] Todo lo del núcleo está en `main`: análisis mensual con y sin El Niño, interruptor, línea de Piura hacia Indonesia y Australia, reproducción en el tiempo, demo 1.
- [ ] Desde aquí **solo ramas `fix/…` hacia `release/demo`**.

---

## S5 · Sin red y pulido (horas 36–44)

**Objetivo:** que nada dependa de la red de la sede ni de la NASA el día de la demo.

| Rol | Tareas |
|---|---|
| B1 · `be/instantaneas-demo` (#8) | - [ ] `jobs/instantaneas.py`: respuestas en `backend/data/demo/respuestas/` (analyze de Piura y destinos, analyze demo 2 completa y de 10 años, teleconnect, compare-periods, demos). <br> - [ ] Regenerarlas si cambia contrato, `VERSION_METODO` o un guion. <br> - [ ] Precalentamiento final: no pedir nada nuevo a la NASA el día de la demo. |
| B2 | - [ ] Verificar el paquete de datos en el servidor y en la laptop de la demo. <br> - [ ] Verificar referencias de fuentes de datos (con B3). <br> - [ ] Correcciones `fix/…` del backend. |
| B3 | - [ ] Verificar referencias bibliográficas (se citaron de memoria). <br> - [ ] Empezar a redactar la descripción del proyecto. <br> - [ ] Correcciones `fix/…` del motor. |
| F1 | - [ ] Correcciones `fix/…` del mapa y las líneas. <br> - [ ] Revisar rendimiento final en teléfono modesto. |
| F2 · `fe/distribucion` (#12) | - [ ] APK y web finales con demos empaquetadas (`npm run demo:copiar`). <br> - [ ] Probarlos en modo avión y con red desconectada. <br> - [ ] Enlaces de descarga del APK y de la web en el README. |
| F3 | - [ ] Copiar las respuestas que regenera B1 a `assets/demo/`. <br> - [ ] Revisión final de textos (español sencillo, sin redacción causal, unidades y fuentes visibles). <br> - [ ] Revisión de accesibilidad en todas las pantallas. |

**Entregas:** B1 → F3 respuestas regeneradas (~40) · F3 → F2 `assets/demo/` final (~41) · F2 → todos APK y web finales (~43).

**Criterio de cierre (hora 44):** APK y web finales funcionan en modo avión; README con enlaces.

---

## S6 · Entrega (horas 44–48)

| Tarea | Dueño |
|---|---|
| - [ ] Ensayo con la red desconectada: servidor (API y web en la misma laptop) | B1 |
| - [ ] Ensayo con la red desconectada: app (teléfono y navegador de la laptop) | F3 |
| - [ ] Descripción del proyecto para la entrega | B3 redacta, F3 revisa |
| - [ ] Video de la demo | F3 graba, F2 edita |
| - [ ] README final, URL de la API y de la web, etiqueta `v1.0-entrega` | B1 |
| - [ ] Enviar los entregables antes de la hora de cierre de la sede | B1 (con todos) |
| - [ ] Apoyo libre a quien vaya atrasado | B2, F1 |

---

## 7. Turnos de descanso (propuesta)

48 horas de reloj ≈ 30 horas efectivas por persona. Siempre queda **al menos una persona de backend y una de frontend despiertas**, y ScanMap corre solo mientras tanto. Ajústenlo en la primera reunión.

| Bloque | Descansan | Quedan despiertos |
|---|---|---|
| Horas 14–18 | B2 (la descarga corre sola), F2 (tras el primer APK) | B1, B3 · F1, F3 |
| Horas 21–25 | B3, F1 | B1, B2 · F2, F3 |
| Horas 25–29 | B1, F3 | B2, B3 · F1, F2 |
| Horas 32–35 | F2 | todo el backend · F1, F3 |
| Horas 37–41 | B2, B3, F1 | B1 · F2, F3 |
| Horas 41–44 | B1, F3 | B2, B3 · F1, F2 |

Comidas: 30 min escalonados, nunca dos personas del mismo par de entrega (por ejemplo B1 y F1 cerca de un hito) a la vez.

---

## 8. Revisión cruzada de PR

| Autor | Revisa | Suplente |
|---|---|---|
| B1 | B2 | B3 |
| B2 | B3 | B1 |
| B3 | B1 | B2 |
| F1 | F2 | F3 |
| F2 | F3 | F1 |
| F3 | F1 | F2 |

Cambio de contrato: lo aprueban B1 + F1. Cambio de `store.ts`: F1 + F2 + F3. Si el revisor está descansando (sección 7), revisa el suplente.

---

## 9. Reglas para no enredarnos

1. **Contrato primero.** Nadie toca la carpeta del otro lado (`backend/` ↔ `frontend/`) sin avisar: casi siempre es un cambio de contrato.
2. **Ramas cortas.** `git pull --rebase origin main` y fusionar al menos cada 4–6 horas, con CI en verde.
3. **Si te falta algo de otro, no esperes:** usa el JSON simulado y sigue.
4. **Una sola implementación** de la cuantización, del cliente POWER y del motor: el preparador importa, no copia.
5. Commits chicos en español con prefijo `feat:`, `fix:`, `docs:`, `chore:` o `test:`.
6. Nada de `push --force` a `main`, saltarse la revisión o desactivar pruebas.
7. Datos fuera de Git (salvo `backend/data/demo/` y `frontend/assets/demo/`); credenciales de NASA nunca en un archivo.
8. El frontend nunca calcula estadística: muestra lo que manda la API.
9. Honestidad: "ocurren a la vez y ambos responden a El Niño"; nunca "uno causa el otro". "Sin tendencia detectable" es un hallazgo válido.
10. Desde la hora 36 solo entran `fix/…` hacia `release/demo`.

### Orden de recorte si hay atraso (no se mueve el hito)

1. Vistas diaria y anual del gráfico.
2. Tooltips del glosario (queda la página).
3. Líneas de "mismo efecto" (quedan las de efecto opuesto).
4. Mosaico de ScanMap en el mapa (queda el feed en lista). Primero si el mapa va lento en un teléfono modesto.
5. Pestañas de señales opuestas y cambios ocultos (feed reducido a 10 hallazgos precalculados).
6. Comparación por periodos (queda la reproducción).

**Nunca se recorta:** análisis mensual con y sin El Niño, el interruptor, la línea de Piura hacia Indonesia y Australia, la reproducción en el tiempo y la demo 1.
