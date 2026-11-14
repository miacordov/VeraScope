# VeraScope

**¿Esta variable cambió de forma sostenida en este lugar, o lo que vemos es El Niño?**

Proyecto del **NASA International Space Apps Challenge 2026**, reto *Earth System Trend Detective*. VeraScope
calcula la tendencia de una variable de la Tierra **dos veces**: sobre la serie original y sobre la serie sin la
parte que explica El Niño. De esa comparación sale uno de cuatro veredictos en lenguaje claro: **cambio robusto**,
**sensible a El Niño**, **cambio oculto** o **sin tendencia detectable**.

- **ScanMap:** los hallazgos más fuertes de 4235 celdas del Pacífico tropical, en un clic.
- **Líneas causa → consecuencia:** desde Piura (Perú), la plataforma encuentra sola a Indonesia y al norte de
  Australia, que sufren lo opuesto en los mismos meses de El Niño.
- **Comparador en el tiempo:** reproducción mes a mes desde 1981, dos periodos y meses inusuales.

**Plataformas:** app de React Native (Expo) para iOS y Android, con versión web desde el mismo código.
**Datos:** NASA POWER (MERRA-2, desde 1981) e índices ONI y Niño 1+2 de NOAA CPC.

## Estructura

```
VeraScope/
├── backend/                  # API FastAPI (un solo servicio)                → backend/CLAUDE.md
│   ├── app/                  # api/, contracts/, datos/, estadistica/, catalogo/   (rama chore/contratos)
│   ├── jobs/                 # scanmap.py, precalentar.py, instantaneas.py
│   ├── verascope_datos/      # preparador de datos con panel visual (listo, 13 pruebas)
│   ├── data/                 # la llena el preparador; fuera de Git salvo data/demo/
│   └── tests/
└── frontend/                 # app Expo (iOS, Android y web)                 → frontend/CLAUDE.md
    ├── app/                  # pantallas (Expo Router)                         (rama chore/contratos)
    ├── assets/demo/          # respuestas de las demos para funcionar sin red
    └── src/                  # estado/, shared/, features/
```

**Antes de escribir código, lee la guía de tu área:** [`backend/CLAUDE.md`](backend/CLAUDE.md) o
[`frontend/CLAUDE.md`](frontend/CLAUDE.md). Son también las instrucciones para Claude Code en cada carpeta.
Las reglas C1–C19 y V1–V8 (secciones 2 de cada guía) ya están decididas: no se revierten sin hablarlo.

## Equipo y ramas

Seis personas: **B1, B2, B3** (backend) y **F1, F2, F3** (frontend). Cada rama tiene un **issue con el detalle
de la tarea** (objetivo, archivos, pasos, pruebas y criterio de terminado). Ramas cortas sobre `main`: viven
horas, no días.

| Rama | Issue | Dueño | Horas | Qué se hace |
|---|---|---|---|---|
| `chore/contratos` | [#1](https://github.com/miacordov/VeraScope/issues/1) | B1 + F1 | 0–6 | Contratos Pydantic, tipos TS, esqueletos de API y app, despliegue simulado con HTTPS |
| `be/datos-power` | [#2](https://github.com/miacordov/VeraScope/issues/2) | B2 | 2–12 | Cliente de POWER, cuantización, validación, índices de NOAA |
| `be/api-cache-despliegue` | [#3](https://github.com/miacordov/VeraScope/issues/3) | B1 | 4–20 | Ruta `analyze`, caché de dos niveles, despliegue, precalentamiento |
| `be/motor-enso` | [#4](https://github.com/miacordov/VeraScope/issues/4) | B3 | 6–18 | Motor estadístico: anomalías, tendencia, quitar El Niño, veredicto |
| `be/scanmap-job` | [#5](https://github.com/miacordov/VeraScope/issues/5) | B2 | 8–20 | Integrar el preparador; escaneo de 4235 celdas, FDR, ranking y pares |
| `be/teleconexion-periodos` | [#6](https://github.com/miacordov/VeraScope/issues/6) | B3 | 18–30 | Rutas `teleconnect` y `compare-periods`, meses inusuales |
| `be/scan-feed-api` | [#7](https://github.com/miacordov/VeraScope/issues/7) | B1 | 20–30 | Rutas del feed y del mosaico de ScanMap |
| `be/instantaneas-demo` | [#8](https://github.com/miacordov/VeraScope/issues/8) | B1 | 36–42 | Respuestas de las demos para la app sin red |
| `fe/mapa-celda` | [#9](https://github.com/miacordov/VeraScope/issues/9) | F1 | 3–14 | Mapa del Pacífico en SVG, celda, selector de variable y ventana |
| `fe/graficos-enso` | [#10](https://github.com/miacordov/VeraScope/issues/10) | F2 | 6–20 | Panel Causa · Consecuencia · Realidad e interruptor de El Niño |
| `fe/veredicto-feed` | [#11](https://github.com/miacordov/VeraScope/issues/11) | F3 | 6–28 | Tarjeta de veredicto y feed de ScanMap |
| `fe/distribucion` | [#12](https://github.com/miacordov/VeraScope/issues/12) | F2 | 6–14 y 36–44 | Primer APK (EAS) y exportación web; luego las finales |
| `fe/lineas-mosaico` | [#13](https://github.com/miacordov/VeraScope/issues/13) | F1 | 20–32 | Líneas causa → consecuencia y mosaico |
| `fe/tiempo-comparador` | [#14](https://github.com/miacordov/VeraScope/issues/14) | F2 | 20–32 | Reproducción, periodos y meses inusuales |
| `fe/demos-glosario` | [#15](https://github.com/miacordov/VeraScope/issues/15) | F3 | 24–36 | Las dos demos guiadas y el glosario |
| `release/demo` | — | Todos | 36–48 | Se abre en el congelamiento (`v1.0-freeze`); solo ramas `fix/…` |

**Hitos:** hora 6, URL pública con HTTPS y la app recibe un `analyze` simulado · hora 20, un toque en el mapa
devuelve un veredicto con datos reales · hora 36, las dos demos corren completas (congelamiento).

### Cómo trabajar

```bash
git switch main && git pull --rebase origin main
git switch <tu-rama>               # p. ej. be/motor-enso
git pull --rebase origin main      # al menos cada 4–6 horas
# … commits chicos: feat: / fix: / docs: / chore: / test:  (en español)
git push -u origin <tu-rama>       # y abre el PR hacia main, enlazando tu issue ("Cierra #N")
```

- Todo PR lo aprueba **otra persona de tu área**; un cambio de contrato, **una de backend y una de frontend**.
- CI en verde para fusionar. Nada de `push --force` a `main` ni pruebas desactivadas.
- Si tu tarea te obliga a tocar la carpeta del otro lado (`backend/` ↔ `frontend/`), **detente y avisa**:
  casi seguro es un cambio de contrato.

## Datos

Los datos los prepara **una sola persona** con el preparador de `backend/verascope_datos/`; el resto del equipo
instala el paquete que esa persona comparte. Todo queda en `backend/data/`, que es lo que lee la API.

**Abrir el panel:** doble clic en `backend/verascope_datos/Abrir-panel.bat` (Windows) o
`Abrir-panel.command` (Mac), o `backend/verascope_datos/abrir-panel.sh` (Linux). La primera vez se instala solo
(Python 3.10 o más nuevo e internet). El panel corre solo en tu computadora (`127.0.0.1`). Pulsa
**Prueba rápida** y, si sale bien, **Hacer todo**.

| Paso | Comando | Qué hace |
|---|---|---|
| 1 | `verascope-datos indices` | ONI, Niño 1+2 y CO₂ de NOAA |
| 2 | `verascope-datos power` | NASA POWER V1–V5: primero las 3 demos, luego las 4235 celdas (~71 min). `--solo-demos` para probar |
| 3 | `verascope-datos satelites` | GPM, GLDAS y MODIS (V8–V12) para las demos; pide cuenta de NASA Earthdata |
| 4 | `verascope-datos calcular` | Tendencias con y sin El Niño, FDR y veredicto por celda → `resultados.parquet` |
| 5 | `verascope-datos demos` | Respaldo JSON de Piura, Borneo y el norte de Australia |
| 6 | `verascope-datos empaquetar` | Un `.tar.gz` para el equipo (nunca va a Git) |

Instalar el paquete del equipo: `pip install -e backend/verascope_datos` y
`verascope-datos instalar verascope-datos-AAAAMMDD.tar.gz` (o súbelo desde el panel). Verifica cada archivo.

Las credenciales de NASA Earthdata van por variables de entorno (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`),
`~/.netrc` o el panel (solo en memoria). **Nunca en un archivo del repo.**

**Pendiente de verificar con los servicios reales:** la conversión × 8 de la escorrentía de GLDAS (V10) y el
nombre de la capa NDVI de AppEEARS (V12). Detalle en [`backend/verascope_datos/README.md`](backend/verascope_datos/README.md).

## Honestidad científica

La plataforma **detecta tendencias y coincidencias; no atribuye causas**. Las líneas dicen *"ocurren a la vez y
ambos responden a El Niño"*, nunca que uno causa el otro. Cada dato muestra su fuente, unidad, celda y periodo.
"Sin tendencia detectable" es un hallazgo válido.
