# CLAUDE.md · VeraScope · BACKEND

> **Para quién es:** el Claude Code que trabaja en `backend/`. Este archivo va en **`backend/CLAUDE.md`**. Su gemelo, `frontend/CLAUDE.md`, trae las mismas reglas del proyecto (secciones 1–3) y el mismo contrato de la API (sección 17). Si cambias una regla compartida, avisa al humano para que se actualice **en los dos**.
> **Cómo se mantiene:** si un comando, una ruta o una regla de aquí deja de ser cierta, corrígela **en el mismo PR** que la cambió. Un archivo desactualizado es peor que no tener ninguno.

**Mapa del archivo:** 0 Quién eres · 1 Qué es VeraScope · 2 Reglas que no se deshacen · 3 Cómo hablamos de la ciencia · 4 Stack y comandos · 5 Estructura y dueños · 6 Datos y caché · 7 El preparador de datos · 8 Motor estadístico · 9 ScanMap · 10 Teleconexión · 11 Periodos · 12 La API · 13 Pruebas · 14 Despliegue · 15 Qué hacer y qué no · 16 Definición de "terminado" · 17 Contrato de la API · 18 Equipo, ramas y calendario.

## 0. Quién eres y cómo trabajar

- Eres el **Claude Code del backend** de VeraScope. Construyes y mantienes **un solo servicio FastAPI** (tres paquetes: Datos, Estadística, Catálogo, más la capa de API) y sus pruebas, el job de ScanMap, **el preparador de datos (`verascope-datos`) integrado en el repositorio**, las **respuestas de las demos para la app sin red** y los datos que la API lee. Tu API la consumen una **app de React Native (iOS y Android)** y una **web** que salen de la misma base de código.
- **Tu carpeta es `backend/`** (y `backend/data/demo/`, la instantánea y las `respuestas/` de las demos, que sí van en Git). **No tocas `frontend/`.** Si una tarea te obliga a hacerlo, detente y avisa: casi seguro es un cambio de contrato.
- **Para saber qué te toca**, mira la rama (`git branch --show-current`) y la tabla de ramas de la sección 18: la rama dice qué tarea es y de quién (B1, B2 o B3).
- **Al empezar una sesión:** lee `git status`, `git log -5 --oneline`, corre `pytest -q` y confirma que partes de verde. Si hay algo rojo que no es tuyo, dilo antes de empezar.
- **Con el humano:** español sencillo, sin jerga; explica **qué hiciste y qué falta** en pocas líneas. Antes de un cambio grande, propón el plan en 3–5 líneas y espera el visto bueno. **Pregunta antes de:** cambiar un contrato, una constante estadística, una regla de la sección 2, o agregar una dependencia.
- **Si algo no está en este archivo, no lo inventes:** pregunta, o busca en los informes del equipo (técnico y estadístico). Si los datos reales contradicen lo que dicen los informes, **dilo**; no lo escondas.
- Trabajas contra un reloj de 48 horas con ~30 h efectivas por persona. **Prioriza el núcleo** (sección 18: "nunca se recorta") y no te desvíes a propuestas opcionales.

## 1. Qué es VeraScope

- Proyecto del **NASA International Space Apps Challenge 2026**, reto **Earth System Trend Detective**: encontrar tendencias de largo plazo en datos de la Tierra y separarlas del ruido de **ENSO** (El Niño y La Niña).
- **Idea central:** cada tendencia se calcula **dos veces**, sobre la serie original y sobre la serie **sin la parte explicada por El Niño**. El veredicto sale de comparar las dos.
- **Caso estrella (la demo):** en El Niño llueve de más en Piura (Perú) y hay sequía en Indonesia y el norte de Australia, **a la vez**. El mapa une Piura con esas regiones con una línea que cruza el Pacífico, y la línea se enciende en los meses en que ambos lados sufren juntos.
- **Dos caminos, una sola vista de detalle:** *Investigar* (el usuario elige variable, celda y ventana) y *Escanear* (ScanMap: un feed de hallazgos ya calculados sobre 4235 celdas × 5 variables). Los dos terminan en la misma vista con **los mismos números**.
- **Plataformas (versión 2 del informe):** una **app de React Native (Expo) para iOS y Android**, con **versión web que sale de la misma base de código** (React Native for Web). El teléfono es la pantalla principal; la web en laptop o proyector se usa para presentar. Las demos funcionan **sin red** con respuestas empaquetadas dentro de la app.
- **Los datos se preparan aparte:** el software **`verascope-datos`** (con panel visual) descarga las series, calcula el escaneo de ScanMap, respalda las demos y empaqueta todo. La API **solo lee** lo que ese software deja en disco; la app **nunca** llama a NASA ni a NOAA.
- **Equipo:** 6 personas (B1, B2, B3 en backend; F1, F2, F3 en frontend), 48 horas, unas 30 horas efectivas por persona.
- **Idioma:** todo lo que ve el usuario va **en español sencillo, sin jerga**. Los comentarios de código, mensajes de commit y documentos también en español. Los identificadores de código siguen el árbol del repositorio (carpetas del backend en español, features del frontend en inglés).

Documentos de referencia del equipo (están fuera del repositorio; pídelos si los necesitas): *Informe técnico del proyecto, **versión 2** (14 nov 2026, 50 págs.: app móvil y web, más el capítulo del software de datos; reemplaza a la versión 1)*, *Informe estadístico* (30 págs.), *Fallas del plan actual y soluciones* y *Plan de implementación* (estos dos, del plan original, quedan superados donde contradigan al informe técnico v2). **Si este archivo y un informe se contradicen, manda el informe técnico, salvo lo indicado en "Decisiones posteriores a los informes".**

## 2. Reglas que no se deshacen (correcciones C1–C19)

El plan original tenía errores que un jurado técnico habría detectado. Estas correcciones ya están decididas. **No las "mejores" ni las reviertas** aunque parezca más simple o más rápido; si crees que alguna está mal, avisa al humano antes de tocar nada.

| # | Tema | Regla final (la que se construye) |
|---|---|---|
| C1 | Fuentes | **NASA POWER es la única fuente en vivo.** AppEEARS, Giovanni y los archivos de GES DISC nunca se llaman desde la API. |
| C2 | Catálogo | Solo 5 variables de POWER, rotuladas **"MERRA-2 vía NASA POWER"**: `PRECTOTCORR`, `T2M`, `GWETROOT`, `GWETTOP`, `RH2M`. GPM, GLDAS y MODIS no vienen de POWER: no se anuncian como si lo fueran. |
| C3 | Geometría | Se analiza una **celda de 0.5°**. Nada de polígonos ni radios. El mapa dibuja el **rectángulo** de la celda, no un punto. |
| C4 | Caché | **Dos niveles en disco, sin caducidad** (series y resultados), con llave sobre la **celda cuantizada**. Nada de Redis. |
| C5 | Ventana | Por defecto **1981 → último año completo de MERRA-2**. Mínimo **10 años** (120 meses). Aviso de poca potencia bajo **20 años** (240 meses). |
| C6 | Resolución | **Solo análisis mensual.** Lo diario y lo anual, como mucho, son vistas del gráfico sin veredicto (y son lo primero que se recorta). |
| C7 | ENSO | Tendencia **con y sin El Niño**: el índice se quita por **regresión conjunta con la tendencia**, rezago de 0 a 6 meses. Hamed-Rao solo corrige la varianza, no la pendiente. |
| C8 | Intervalo | El intervalo de confianza usa **la misma varianza corregida** que el p-valor. Así el intervalo excluye el cero **si y solo si** p < 0.05. |
| C9 | Veredicto | **Cuatro estados:** cambio robusto, sensible a El Niño, cambio oculto, sin tendencia detectable. La dirección (sube o baja) sale del signo de la pendiente. |
| C10 | Correlación con ENSO | Rezago de 0 a 6 meses y significancia con **tamaño efectivo de muestra** (Bretherton 1999). Nunca el p-valor ingenuo. |
| C11 | Atribución | El ONI lo publica el **Climate Prediction Center de NOAA**, no la NASA. |
| C12 | Arquitectura | **Un servicio FastAPI con tres paquetes** (Datos, Estadística, Catálogo) y una capa de API, más el frontend: **dos piezas desplegables** (la API y la web estática; la app nativa sale como APK). Nada de microservicios, gateway ni Redis. |
| C13 | Cronograma | **Despliegue en la hora 6** (con datos simulados), flujo real en la hora 20, congelamiento en la hora 36, entregables en 44–48. |
| C14 | Capacidad | Se planifica con **~30 horas efectivas por persona**, no 48. |
| C15 | Comparador | El comparador es **en el tiempo, de una misma región**. La segunda región la encuentran las líneas causa → consecuencia; el usuario no elige "dos zonas". |
| C16 | Dirección del fenómeno | **El Niño = lluvia extrema en Piura y sequía en Indonesia y norte de Australia** (La Niña, al revés). Eso es lo que la demo narra. |
| C17 | Efecto invernadero | Se muestra **la tendencia que queda al quitar El Niño** y **no se atribuyen causas**. POWER no mide CO₂ ni contaminantes. El CO₂ de Mauna Loa, si entra, es solo una franja de contexto, **sin correlacionarlo con nada**. |
| C18 | Escaneo masivo | **Benjamini-Hochberg** sobre las 21 175 pruebas de ScanMap, en dos familias (original y sin El Niño). Sin esto saldrían ~1000 falsos hallazgos. |
| C19 | Demos | Recorrido simple que **fija el estado por código**. Glosario como **página**; los tooltips solo si sobra tiempo. Sin reproductor de recorridos a medida. |

**Cambios de la versión 2 del informe (V1–V8).** No son correcciones del plan original (por eso C1–C19 no cambian): son decisiones de plataforma y herramientas, también ya tomadas.

| # | Tema | Regla final (la que se construye) |
|---|---|---|
| V1 | Plataforma | App de **React Native con Expo** (SDK 57, fijo) para iOS y Android; **la web sale del mismo código** con React Native for Web. Ya no hay web aparte con Vite. |
| V2 | Mapa | **Mapa propio en SVG** centrado en el Pacífico, con las costas dentro de la app. Ya no hay Leaflet ni teselas de OpenStreetMap. |
| V3 | Gráficos | Componente propio con `react-native-svg` y d3. Ya no hay Recharts. |
| V4 | Estilos y pruebas | `StyleSheet` con tokens de tema; **Jest** (`jest-expo`). Ya no hay Tailwind ni Vitest. |
| V5 | Entrega | Web estática (`expo export -p web`), **APK con EAS Build**, Expo Go en desarrollo; iOS en iPhone real sin Expo Go exige cuenta de Apple Developer. La API **con HTTPS** desde la hora 6. |
| V6 | Demo sin red | Respuestas completas de las demos **empaquetadas dentro de la app** (las genera el backend), además de la instantánea del servidor. |
| V7 | Datos | El software **`verascope-datos`** (panel visual, reanudable, con pruebas) hace la descarga, el escaneo y el paquete. Ver `backend/CLAUDE.md`, sección 7. |
| V8 | Pantallas | El **teléfono** es la pantalla principal; la web en laptop o proyector se usa para presentar. |

**Reglas estadísticas que se desprenden de lo anterior (ambos lados las respetan):**

- Mann-Kendall *original* (sin corrección) está **prohibido**: 60.5 % de falsos positivos en las simulaciones. Se usa Hamed-Rao con 12 rezagos.
- `scipy.stats.theilslopes` **no se usa para el intervalo** (usa la varianza sin corregir y contradice el p-valor). El intervalo se calcula a mano, de las pendientes ordenadas (C8).
- `scipy.stats.pearsonr` **no se usa para el p-valor** de una correlación con El Niño ni entre celdas: se usa el tamaño efectivo.
- `pymannkendall.seasonal_test` no se usa: las anomalías mensuales ya quitan el ciclo estacional.
- "Sin tendencia detectable" es un **hallazgo válido**, no un error ni un estado vacío.
- Nunca se recalcula Theil-Sen por cada cuadro de la reproducción: la tendencia se calcula una vez con la serie completa.

## 3. Cómo hablamos de la ciencia (honestidad)

- **Correlación no es causa.** Las líneas dicen: *"ocurren a la vez y ambos responden a El Niño"*. **Nunca** "uno causa el otro" ni "El Niño causó esto".
- La plataforma **detecta tendencias y coincidencias; no atribuye causas**. Una tendencia de fondo en la temperatura *es coherente con* el calentamiento global, pero **no se afirma que lo pruebe**.
- **Cada dato muestra su fuente, unidad, celda y periodo:** "MERRA-2 vía NASA POWER", "ONI, NOAA CPC", fecha de descarga. Si es análisis fuera de la rejilla de ScanMap, se rotula **"análisis individual"**.
- **No se inventan números.** Ni en la interfaz, ni en las demos, ni en los titulares. Todo número viene de la API o de un archivo de datos real; los datos simulados siempre se rotulan como simulados.
- Si la respuesta de Piura no es lineal (lluvia que responde sobre todo a eventos extremos), **la tarjeta lo dice**. Para Piura se ofrece también el índice **Niño 1+2** (Niños costeros como el de 2017, que el ONI casi no registra).
- **MERRA-2 no registra las lluvias del Niño de 1983 en Piura** (marzo de 1983: 2.5 mm/día, casi la media de marzo, 2.0; en 1998 llega a 16.2). Es una limitación del modelo en la costa peruana a inicios de los 80: **no uses 1983 como ejemplo de lluvia extrema**; usa 1998 o 2017. (Revisión de anomalías de B2, 15-nov-2026.)
- El umbral mensual de El Niño (índice ≥ 0.5) y La Niña (≤ −0.5) es una **simplificación**; NOAA exige cinco estaciones seguidas. Se indica en el glosario.
- Las cifras de simulaciones (falsos positivos, potencia) son **de series sintéticas**, no de datos reales. No las presentes como resultados sobre datos reales.
- Las referencias de literatura de los informes se citaron **de memoria** y hay que verificarlas antes de la entrega.

## 4. Stack, comandos y variables de entorno

**Stack:** Python 3.11 · FastAPI + Pydantic v2 + uvicorn · numpy · pandas · scipy ≥ 1.11 (probado con 1.18) · pymannkendall · pyarrow · requests · sqlite3 (estándar) · pytest. `pyhomogeneity` solo si entra la prueba de Pettitt (C19, propuesta).
**No van en la imagen de la API:** xarray, earthaccess, netCDF4 (son del preparador de datos), ni `statsmodels` (scipy ya trae Benjamini-Hochberg: `scipy.stats.false_discovery_control(p, method="bh")`).

```bash
cd backend
pip install -e ".[dev]"                     # dependencias de la API + pytest, ruff
uvicorn app.main:app --reload --port 8000   # API en local
VERASCOPE_SIMULADO=1 uvicorn app.main:app   # API con respuestas simuladas (sin datos ni red)
pytest -q                                   # pruebas del motor y de la API (sin red)
pytest -q -m lento                          # pruebas de rendimiento
ruff check . && ruff format --check .       # estilo
python -m jobs.precalentar                  # descarga celdas de las demos y ~50 ciudades (una a una)
python -m jobs.scanmap                      # escaneo de 4235 celdas (usa lo que ya está en el casillero)
python -m jobs.instantaneas                 # respuestas de las demos para la app sin red → data/demo/respuestas/
verascope-datos panel                       # panel visual del preparador de datos (sección 7)
```

> Si un comando de arriba no coincide con lo que hay en el repositorio, **corrige esta sección en el mismo PR**; no improvises otro flujo.

| Variable | Para qué | Por defecto |
|---|---|---|
| `VERASCOPE_DATOS` | Carpeta de datos (casillero, tabla, resultados, demos) | `backend/data` |
| `VERASCOPE_FIN` | Último año de la ventana (último año completo de MERRA-2) | año actual − 1 |
| `VERASCOPE_POWER_URL` | URL de POWER (las pruebas la apuntan a un servidor falso) | endpoint mensual por punto de POWER |
| `VERASCOPE_POWER_TIMEOUT` | Espera máxima en vivo, en segundos | `8` |
| `VERASCOPE_SIMULADO` | `1` = responde con JSON simulados | `0` |
| `VERASCOPE_CORS` | Orígenes de la **versión web** permitidos, separados por coma (las apps nativas no usan CORS) | `http://localhost:8081` (servidor de desarrollo de Expo para web) |

**HTTPS:** las apps nativas bloquean las conexiones sin cifrar. Publica la API detrás de TLS (el proxy o el hosting) **desde la hora 6**. En desarrollo, el teléfono con Expo Go alcanza la API por la IP de la laptop (`--host 0.0.0.0` en `uvicorn`).

No hay secretos en el repositorio. Las credenciales de Earthdata solo las usa el preparador de datos, en la máquina de quien lo corre, **nunca** en la imagen de la API.

## 5. Estructura de `backend/` y dueños

```
backend/
├── Dockerfile
├── pyproject.toml
├── app/
│   ├── main.py                  # arranque y carga en memoria de ScanMap          [B1]
│   ├── api/                     # rutas /api/v1                                   [B1]
│   │   ├── analyze.py
│   │   ├── scan.py              # feed y mosaico
│   │   ├── teleconnect.py
│   │   ├── compare_periods.py
│   │   └── catalogo.py          # variables, glosario, demos, salud
│   ├── contracts/               # modelos Pydantic compartidos               [B1, revisan todos]
│   ├── datos/                                                                   [B2]
│   │   ├── power_client.py      # una petición por celda, cinco variables
│   │   ├── celdas.py            # cuantización a 0.5° y rejilla de 2°
│   │   ├── validacion.py        # 10 años, faltantes −999, cobertura
│   │   ├── indices.py           # ONI y Niño 1+2 de NOAA CPC
│   │   └── cache.py             # dos niveles en disco                            [B1]
│   ├── estadistica/                                                             [B3]
│   │   ├── constantes.py        # TODOS los umbrales, en un solo lugar
│   │   ├── anomalias.py
│   │   ├── tendencia.py         # Theil-Sen, Hamed-Rao, intervalo coherente
│   │   ├── enso.py              # regresión conjunta, rezago, n efectivo
│   │   ├── veredicto.py         # cuatro estados y avisos
│   │   ├── fdr.py               # Benjamini-Hochberg
│   │   ├── teleconexion.py      # destinos de las líneas
│   │   └── periodos.py          # comparación por periodos y meses inusuales
│   └── catalogo/                                                                [B1]
│       ├── variables.json
│       ├── glosario.json
│       ├── titulares.json       # plantillas del feed (sin modelo de lenguaje)
│       ├── demos/               # efecto-espejo.json, senal-o-ruido.json
│       └── simulado/            # respuestas simuladas para la hora 6
├── verascope_datos/             # preparador de datos con panel visual (sección 7)        [B2]
├── jobs/
│   ├── scanmap.py               # escaneo offline de 4235 celdas                    [B2]
│   ├── precalentar.py           # celdas de las demos y de 50 ciudades             [B1]
│   └── instantaneas.py          # respuestas de las demos para la app sin red       [B1]
├── data/                        # fuera de Git, salvo data/demo/ (incluye demo/respuestas/)
└── tests/                       # pruebas del motor con series sintéticas           [B3]
```

**Los límites entre los tres paquetes son sagrados** (separarlos después sería un cambio de despliegue, no de diseño):
- `datos/` no importa de `estadistica/`, ni al revés. Solo la capa `api/` los compone.
- `estadistica/` es **puro**: recibe arreglos de numpy, devuelve resultados; no lee disco ni red.
- `catalogo/` son archivos JSON que mantiene quien los consume. No hay servicio de catálogo.

## 6. Datos: POWER, celdas, calidad, índices y caché

### Reglas de NASA POWER

- **Una petición por celda trae las 5 variables**, de 1981 al último año completo (`parameters=PRECTOTCORR,T2M,GWETROOT,GWETTOP,RH2M`, `community=AG`, endpoint mensual por punto, hasta 20 parámetros por petición). Cambiar de variable en la misma celda **no** cuesta otra petición.
- **Cuantiza antes de todo:** `lat_c = 0.5 * round(lat / 0.5)`, igual para `lon`. Los toques o clics a 100 m de distancia deben dar **la misma llave**. Hay 259 200 celdas posibles en el planeta. **Una sola función** (`datos/celdas.py`) hace esta cuantización; ojo con los empates exactos (`x.25`, `x.75`): el `round` de Python redondea al par (5.25 → 5.0) y el `Math.round` de JavaScript (también en el teléfono) hacia arriba (5.25 → 5.5). **Define una regla, pruébala, y recuerda que la celda que devuelve la API es la autoridad**: la app dibuja la que le llega.
- **Nunca repitas una petición a la misma ubicación:** POWER puede bloquear la IP. La caché por celda es también la forma de cumplir esa regla. Peticiones de fondo: **~1 por segundo**, con espera creciente ante errores y ante `429`.
- **Un cerrojo por celda:** si llegan dos peticiones a la misma celda nueva a la vez, sale **una** petición y las dos esperan.
- **En vivo, espera máxima de 8 s** (`VERASCOPE_POWER_TIMEOUT`). Pasado ese tiempo: error `power_lento` (504) con la **celda en caché más cercana** en `celda_cercana`. (El preparador usa 60 s porque corre en lote; el cliente debe recibir el timeout como parámetro.)
- Valores `-999` = faltante. La clave de mes `"13"` es el promedio anual: **se ignora**. Rellena `NaN`, nunca dejes `-999` en un arreglo.
- La ventana **termina en el último año completo de MERRA-2**: POWER completa los meses recientes con GEOS FP-IT (otro modelo) y eso puede inclinar la pendiente.
- Las demos y las fichas deben decir **"MERRA-2 vía NASA POWER"** y la fecha de descarga.

### Control de calidad (C2), antes de calcular nada

1. `-999` y rellenos → faltante.
2. Huecos de **hasta 2 meses seguidos** → interpolación lineal.
3. Más de **10 %** faltante, o un hueco mayor a 2 meses → la serie se **descarta**.
4. Ventana de **al menos 120 meses**. Entre 120 y 239 meses, se avisa de potencia baja.
5. Desviación estándar nula → se descarta.
6. **Humedad del suelo (`GWETROOT`, `GWETTOP`) sobre el mar:** sin sentido; esas celdas se descartan por la regla 3 y la API responde `sin_datos_tierra` con una explicación en español.

### Catálogo de las 5 variables (alimenta `catalogo/variables.json`; B1 escribe las definiciones en español sencillo)

| Código | En la interfaz | Unidad | Qué mide | Respuesta esperada a El Niño | Cuidados |
|---|---|---|---|---|---|
| `PRECTOTCORR` | Lluvia | mm/día (promedio mensual) | Precipitación total (líquida y sólida) que llega a la superficie | Costa norte del Perú: aumento fuerte en eventos intensos (1982–83, 1997–98), de enero a abril, **no proporcional** al índice. Indonesia y norte de Australia: disminución, más marcada en la estación seca | Distribución asimétrica y con muchos ceros en la costa árida (Theil-Sen es preferible a la media); cambio porcentual sobre la climatología de la celda |
| `T2M` | Temperatura del aire a 2 m | °C | Temperatura del aire sobre la superficie | Calentamiento en la costa peruana durante los eventos. Es donde más se espera que la tendencia de fondo sobreviva al quitar El Niño | **No se reporta cambio porcentual** (el cero de Celsius es arbitrario) |
| `GWETROOT` | Humedad del suelo, zona de raíces | 0 a 1 (saturación relativa, capa 0–100 cm) | Agua disponible para las raíces; integra varios meses de lluvia | Sigue a la lluvia con meses de rezago; baja en Indonesia y norte de Australia. Suele elegir rezagos mayores | Sin sentido sobre el océano (se descarta); autocorrelación muy alta (pesa más la corrección de Hamed-Rao); acotada entre 0 y 1 |
| `GWETTOP` | Humedad del suelo, superficie | 0 a 1 | Humedad de los primeros centímetros; responde rápido | Igual que la anterior, con menos rezago | Mismas restricciones |
| `RH2M` | Humedad relativa a 2 m | % | Vapor de agua del aire frente al máximo posible a esa temperatura | Aumenta en la costa norte del Perú con la lluvia; si el aire se calienta sin más vapor, baja | Acotada entre 0 y 100 %; interpretar junto a `T2M` |

El **cambio porcentual por década** solo se informa en variables con cero natural y promedio positivo (lluvia y humedades); nunca en temperatura. Las definiciones de la interfaz **no se escriben a mano en el frontend**: salen de este catálogo.

### Índices de El Niño

- **ONI** (Niño 3.4, media móvil de 3 meses, asignada al mes central) y **Niño 1+2** (anomalía mensual, para Niños costeros): ambos de **NOAA CPC**, descargados **antes** del evento y servidos como archivos locales. Nunca se piden en vivo.
- El ONI tiene autocorrelación mensual > 0.9: toda correlación con él se evalúa con **tamaño efectivo** de muestra.
- Fase de un mes: `nino` si índice ≥ 0.5, `nina` si ≤ −0.5, `neutro` en otro caso (simplificación declarada).
- **Niño 1+2 empieza en 1982** (el ONI, mucho antes): con ese índice la ventana arranca en 1982-01 y la interfaz debe decirlo.
- Si al final de la ventana falta el último trimestre del índice, la ventana efectiva se recorta al último mes con índice. Escaneo y análisis en vivo deben aplicar **la misma regla**.

### Caché de dos niveles (en disco, no caduca, sobrevive a reinicios)

| Nivel | Qué guarda | Llave | Caducidad |
|---|---|---|---|
| 1 · Series | Respuesta de POWER con las 5 variables (1981 → `VERASCOPE_FIN`) | celda cuantizada | Nunca (los años cerrados no cambian) |
| 2 · Resultados | Veredicto, pendientes, intervalos, diagnósticos | celda + variable + ventana + índice + `VERSION_METODO` | Nunca, salvo cambio de `VERSION_METODO` |

- El nivel 1 **es el casillero SQLite del preparador** (`casillero.sqlite`, modo WAL, un bloque binario `float32` por variable y lugar; llave de lugar `celda:{lat:+.2f}:{lon:+.2f}`). Usa su misma función `lugar_celda` para que el preparador y la API compartan entradas.
- Sube `VERSION_METODO` (en `estadistica/constantes.py`) **cada vez que cambie un cálculo**, para invalidar el nivel 2.
- Como el nivel 1 siempre guarda la serie completa, cualquier ventana de análisis es una **rebanada** de esa serie.

### Carpeta `data/` (la llena el preparador; la API solo la lee)

```
backend/data/
├── casillero.sqlite       # nivel 1: todas las series (V1–V13)
├── resultados.parquet     # ScanMap: una fila por celda y variable
├── escaneo.json           # estado del escaneo (en_curso | completo); lo escribe jobs/scanmap.py, lo lee app/datos/escaneo.py
├── tabla/                 # matrices celdas × meses (float32, valores crudos con NaN)
│   ├── PRECTOTCORR.npy  T2M.npy  GWETROOT.npy  GWETTOP.npy  RH2M.npy
│   ├── ONI.npy  NINO12.npy  CO2.npy
│   ├── celdas.npy         # (4235, 2) = [lat, lon], lon en −180..180
│   └── meses.json         # ["1981-01", …]
├── demo/                  # SÍ se sube a Git: respaldo JSON de Piura, Borneo y norte de Australia
│   └── respuestas/        # respuestas de la API de las demos (las genera jobs/instantaneas.py; las copia la app)
├── crudo/                 # respuestas originales (no se sube)
└── paquetes/              # tar.gz para compartir con el equipo (no se sube)
```

`resultados.parquet` — columnas: `variable` (código POWER), `celda` (fila en `celdas.npy`), `lat`, `lon`, `pendiente_original`, `p_original`, `pendiente` (de la serie **sin El Niño**, por década), `ic_bajo`, `ic_alto`, `p`, `p_original_ajustado`, `p_ajustado` (ambos BH), `rezago`, `r_enso`, `p_enso`, `colinealidad`, `efecto` (pendiente por década ÷ desviación estándar), `meses`, `veredicto` (`cambio_robusto` \| `sensible_a_el_nino` \| `cambio_oculto` \| `sin_tendencia`), `unidad`, `pareja` (id de par opuesto o `None`), `ventana`.

La API carga todo esto **en memoria al arrancar** (≈ 50–100 MB) y **nunca llama a la NASA** para nada que ya esté en caché. Si `resultados.parquet` cambia en disco (por ejemplo, el escaneo terminó), recárgalo al notar el cambio de fecha del archivo, sin reiniciar.

## 7. El preparador de datos (`verascope-datos`)

Es la herramienta **local** (con panel visual) que descarga y arma `data/`: índices de NOAA, POWER (demos primero y luego la rejilla), satélites (GPM, GLDAS, MODIS, solo para las demos), cálculo del escaneo, respaldo de demos y paquete `.tar.gz` para el equipo. Está integrado en el repositorio en **`backend/verascope_datos/`** (paquete propio con su `pyproject.toml`, pruebas y lanzadores; **no** entra en la imagen de la API).

- **Una sola implementación del motor.** La fuente de verdad es `backend/app/estadistica/`. El `motor.py` del preparador es la **semilla ya probada** (13 pruebas en verde): B3 la reparte en los módulos del árbol, y el preparador pasa a **importarla** (o se borra su copia). **Prohibido mantener dos copias** que puedan divergir: el escaneo y el análisis en vivo tienen que dar el mismo número.
- Dentro del repo, el preparador usa **`backend/data` por defecto** (orden: `--datos` → `$VERASCOPE_DATOS` → `backend/data` → `./datos`); los lanzadores también. Instálalo con `pip install -e backend/verascope_datos` y prueba con `cd backend/verascope_datos && pytest tests`.
- Comandos útiles: `verascope-datos panel` (visual), `estado`, `power --solo-demos` (primera prueba, segundos), `power`, `calcular`, `demos`, `empaquetar`, `instalar paquete.tar.gz` (verifica la integridad de cada archivo).
- **No lo toques salvo para integrarlo o arreglar un fallo.** Mantén sus pruebas en verde (`pytest` sin red, con datos simulados).
- Para desplegar los datos: `verascope-datos empaquetar` → release de GitHub o carpeta compartida → en el servidor, `verascope-datos instalar … --datos /data`.
- Los datos de satélite (V8–V12) y el CO₂ (V13) **no entran al flujo en vivo ni al selector de variables**: solo alimentan fichas informativas de la demo 1 y el contraste entre fuentes (propuestas P9).
- **Cómo opera (para no romperlo):** el panel es un servidor de la biblioteca estándar que escucha **solo en `127.0.0.1`**, exige la cabecera `X-Token` y revisa el `Host`. **No lo expongas a la red, no le quites esas comprobaciones y no lo metas en la imagen de la API.** Cada paso corre en un **proceso aparte** (se detiene con SIGINT sin dejar archivos a medias) y es **reanudable**: el casillero (SQLite en modo WAL) guarda cada serie al llegar, y al volver a correr sigue donde se quedó y reintenta solo lo que falló. El paquete `.tar.gz` (~50 MB) guarda la suma **SHA-256** de cada archivo y `instalar` la comprueba. Las credenciales de Earthdata (`EARTHDATA_USERNAME`, `EARTHDATA_PASSWORD`, solo para V8–V12) viven en memoria mientras el panel está abierto y **nunca** se guardan en el repositorio.
- **Pendiente de verificar con los servicios reales** (las 10 pruebas usan archivos simulados con el formato de NASA y NOAA; desde donde se escribió no había acceso a sus servidores): la escorrentía de GLDAS (V10, `Qs_acc + Qsb_acc` × 8, acumulados de 3 h) y el nombre de la capa de NDVI en AppEEARS (V12, `CMG_0.05_Deg_Monthly_NDVI`, de MOD13C2.061). Revísalo en la **primera corrida real** y deja la decisión escrita.

**Las 13 variables del preparador (`variables.py`):**

| Id | Código | Capa | Fuente | Desde |
|---|---|---|---|---|
| V1–V5 | `PRECTOTCORR`, `T2M`, `GWETROOT`, `GWETTOP`, `RH2M` | **En vivo** (las únicas que sirve la API) | NASA POWER (MERRA-2) | 1981 |
| V6, V7 | `ONI`, `NINO12` | Índice | NOAA CPC | 1950, 1982 |
| V8 | `IMERG` (lluvia satelital, mm/día; llega en mm/h, × 24) | Precalculada (solo 3 lugares de las demos) | NASA GES DISC · GPM_3IMERGM v07 | 1998 |
| V9–V11 | `GLDAS_EVAP` (× 86 400), `GLDAS_ESCORRENTIA` (× 8, **por verificar**), `GLDAS_SUELO` (mm) | Precalculada (idem) | NASA GES DISC · GLDAS_NOAH025_M v2.1 | 2000 |
| V12 | `NDVI` (factor 0.0001) | Precalculada (idem) | NASA LP DAAC · MOD13C2 v061 vía AppEEARS | 2000 |
| V13 | `CO2` (ppm) | Contexto (franja aparte; no se correlaciona con nada) | NOAA GML | 1958 |

**Diferencias conocidas entre el `motor.py` del preparador y los informes (B3 las resuelve al moverlo a `estadistica/`):**

| # | Hoy en el preparador | Lo que debe hacer |
|---|---|---|
| 1 | `analizar()` calcula la tendencia **original** sobre toda la serie y la **sin El Niño** sobre `n − rezago` meses: ventanas distintas. | Ambas sobre **los mismos meses** (`a[rezago:]`), como en la implementación de referencia de *Fallas del plan*. |
| 2 | Hace anomalías y **después** rellena huecos. El informe dice control de calidad → anomalías. | Elegir un orden, dejarlo escrito en el código y usar el **mismo** en escaneo y en vivo. (El de hoy evita meter datos inventados en la climatología.) |
| 3 | `p_enso` (respuesta de cada celda al índice) se guarda **sin** corregir por comparaciones múltiples. | Recomendado: corregirlo con BH (4235 pruebas por variable) antes de usarlo como condición de "causa común". Decide B3 y deja la decisión escrita. |
| 4 | `quitar_enso` devuelve `p_r` pero no `n_efectivo`. | Devolver también `n_efectivo` (lo muestra la tarjeta). |
| 5 | Timeout de POWER de 60 s. | Parámetro; 8 s en la API en vivo. |

## 8. Motor estadístico (`app/estadistica/`)

**Un solo análisis, mensual.** Una función compuesta (`analizar_celda`) recibe la serie mensual, los meses calendario y el índice, y devuelve todo lo de una celda. **La usan por igual** la ruta `analyze`, el job de ScanMap y el preparador. Si el escaneo y el análisis en vivo pudieran dar números distintos para una misma celda, es un bug.

### Pipeline por celda y variable (los "C#" de esta tabla son los **cálculos** del informe estadístico)

| Paso | Cálculo | Qué hace | Cómo (librería) |
|---|---|---|---|
| C2 | Control de calidad | Reglas de la sección 6 | `numpy`, `pandas.Series.interpolate(limit=2)` |
| C3 | Anomalías mensuales | Resta la climatología de cada mes calendario **dentro de la ventana** | `numpy` / `pandas.groupby.transform` |
| C9 | Rezago | `ℓ* = argmax_ℓ∈0..6 \|corr(a_t, E_{t−ℓ})\|`. Su significancia se informa como **indicativa** (elegir el máximo de 7 la infla) | `numpy.corrcoef` en bucle de 7 |
| C10 | Quitar El Niño | Regresión **conjunta** `a_t = α + β·t + γ·E_{t−ℓ} + ε`; serie limpia `r_t = a_t − γ̂·(E_{t−ℓ} − Ē)`. γ se estima **en el mismo ajuste que β** (si se estimara solo contra el índice, la tendencia se le atribuiría a El Niño) | `numpy.column_stack` + `numpy.linalg.lstsq` |
| C4 | Pendiente | **Theil-Sen**: mediana de las pendientes entre todos los pares de meses; se expresa **por década** (`× 120`) | `numpy.triu_indices` + `median` (no `scipy.theilslopes`) |
| C5–C6 | Significancia | **Mann-Kendall con Hamed-Rao, 12 rezagos**; `p = 2·(1 − Φ(\|Z\|))` con `Z = (S − sgn S)/√Var′(S)`. Si `var_s` no es positiva, usa la varianza sin corregir | `pymannkendall.hamed_rao_modification_test(y, lag=12)` |
| C7 | Intervalo coherente | `C = z₁₋α/₂·√Var′(S)`; IC 95 % = pendiente de orden `(N−C)/2` a la de orden `(N+C)/2 + 1`, sobre las N pendientes **ordenadas**, acotado a `[1, N]`. **Excluye el 0 si y solo si p < 0.05** | `numpy.sort`, `scipy.stats.norm` |
| C11 | Vínculo con El Niño | `n_e = n·(1 − ρ₁ρ₂)/(1 + ρ₁ρ₂)`; `t = r·√((n_e−2)/(1−r²)) ~ t(n_e−2)` | `numpy.corrcoef`, `scipy.stats.t.sf` |
| C12 | Diagnósticos | Colinealidad `\|corr(E_{t−ℓ}, t)\| > 0.3`; potencia (< 240 meses); respuesta no lineal en la costa norte del Perú | `numpy` |
| C13 | Veredicto | Con `p_orig` y `p_sin` (los **ajustados por BH** si la celda está en ScanMap): ambos significativos → `cambio_robusto`; solo el original → `sensible_a_el_nino`; solo el sin El Niño → `cambio_oculto`; ninguno → `sin_tendencia`. Dirección = signo de la pendiente de la serie sin El Niño | lógica propia, sin librería |
| C14 | FDR | Benjamini-Hochberg, `q = 0.05`, **en dos familias** de 21 175 pruebas (original y sin El Niño) | `scipy.stats.false_discovery_control(p, method="bh")` |

> **Nota de nomenclatura:** el informe técnico numera las correcciones al plan original como C1–C19 (sección 2 de este archivo); el informe estadístico numera los **cálculos** C1–C20 (tabla de arriba). Cuando cites un número en un commit o comentario, escribe **"cálculo C8"** o **"corrección C8"** para no confundirlos. El intervalo coherente es la *corrección* C8 y el *cálculo* C7.

### Constantes (todas en `estadistica/constantes.py`; nada de números mágicos sueltos)

| Constante | Valor | Constante | Valor |
|---|---|---|---|
| `ALFA` | 0.05 | `FDR_Q` | 0.05 |
| `REZAGO_MAX` | 6 | `LAG_HAMED_RAO` | 12 |
| `MIN_MESES` | 120 | `AVISO_POTENCIA_MESES` | 240 |
| `MAX_HUECO` / `MAX_FALTANTE` | 2 meses / 0.10 | `ESCALA_DECADA` | 120 |
| `UMBRAL_FASE` | 0.5 | `COLINEALIDAD_MAX` | 0.3 |
| `UMBRAL_INUSUAL` (\|z\|) | 2 | `UMBRAL_COINCIDENCIA` (\|z\|) | 1 |
| `KM_MIN_DESTINO` | 1500 | `KM_SEP_DESTINOS` | 1000 |
| `MAX_LINEAS_OPUESTAS` / `MAX_LINEAS_IGUALES` | 3 / 2 | `PERIODOS_DEFECTO` | (1981, 2001) y (2003, fin) |
| `NEFF_MIN_PRUEBA_T` | 10 | `NEFF_PISO` | 3 |
| `VERSION_METODO` | entero; **súbelo al cambiar cualquier cálculo** | `GRILLA_PASO` / `CELDA` | 2.0° / 0.5° |

### Reglas del motor

- **Mismos meses para las dos tendencias** (desde `ℓ*`). La serie sin El Niño tiene `null` en los primeros `ℓ*` meses; el resto del código y el contrato lo asumen.
- **Alineación del índice:** `a[ℓ:]` se empareja con `E[:n−ℓ]`. La serie y el índice deben llegar **alineados mes a mes y sin faltantes**.
- El motor es **puro y vectorizable**; no hay bucles por celda dentro de `estadistica/` (el job los paraleliza por fuera, con `spawn`).
- **Prohibido:** `scipy.stats.theilslopes` para el intervalo, `pymannkendall.original_test`, `pymannkendall.seasonal_test`, `scipy.stats.pearsonr` para el p-valor, p-valores sin corrección de autocorrelación en cualquier correlación entre series mensuales.
- **Análisis solo mensual.** No agregues rutas ni parámetros de resolución diaria/anual.
- Cada función lleva un docstring con su cálculo (`C#`), supuestos y para qué variables aplica.
- **Propuestas (solo si sobra tiempo, nunca antes de la hora 20 y nunca a costa del núcleo; cada una necesita sus pruebas antes de entrar):** prueba t corregida de Santer (C8, `n_e ≥ 10` o no se informa), asimetría de la respuesta a El Niño (C12), frecuencia de episodios extremos con prueba binomial (C18, `scipy.stats.binomtest`), Pettitt (C19, `pyhomogeneity`), contraste entre fuentes (C20). Cuando una entra, su campo del contrato deja de ser `null`.

## 9. ScanMap (`jobs/scanmap.py`, B2)

- **Rejilla:** 34°S–34°N, 90°E–30°O, paso 2° → 35 × 121 = **4235 celdas** × 5 variables = **21 175 series**.
- **Orden:** primero las **celdas de las demos** (Piura, Borneo, norte de Australia), para que la demo funcione aunque el escaneo no termine. Luego el resto, una petición por celda, ~1/s ≈ **71 minutos de red**, ~8 minutos de cálculo.
- **Reanudable:** lo ya guardado en el casillero no se vuelve a pedir; los fallos se registran y se reintentan en la corrida siguiente. Se puede cortar en cualquier momento.
- **Resultado:** `resultados.parquet` + `tabla/*.npy`, con las columnas de la sección 6. Veredicto de cada celda a partir de los p-valores **ya corregidos por BH**. Mientras no termine el cálculo, la API informa `escaneo.estado = "en_curso"` (el feed muestra "escaneo en curso", **no** una lista vacía).
- **Ranking:** por **tamaño del efecto** (`pendiente por década ÷ desviación estándar de la serie`), para comparar variables con unidades distintas.
- **Señales opuestas:** por variable, empareja tendencias **significativas de signo contrario** separadas **> 1500 km** (cada celda en un solo par).
- **Consistencia feed ↔ detalle:** el escaneo usa **las mismas funciones** que el análisis en vivo y escribe en **la misma caché de resultados**. Cuando una celda está en la rejilla (y la ventana es la del escaneo con ONI), `analyze` devuelve el veredicto del escaneo con su `p_ajustado` y `origen = "escaneo"`. Fuera de eso, `origen = "individual"`.
- Corre en segundo plano **desde la hora 8**, mientras el equipo sigue trabajando. Con `calcular --minimo-celdas N` del preparador se puede calcular un resultado parcial para probar rutas antes de que termine la descarga.

## 10. Teleconexión (`estadistica/teleconexion.py`, B3)

Dada una celda de origen *i*, encuentra **sola** las regiones lejanas que sufren lo opuesto (o lo mismo) en los mismos meses **y** responden a El Niño.

1. Con las anomalías **estandarizadas** (`Z`, matriz 4235 × n, serie **original**, desviación estándar poblacional) la correlación con todas las celdas se obtiene en una operación: `r = Z @ Z[i] / n`. Solo entran celdas válidas (serie completa tras el control de calidad).
2. Cada `r_j` se evalúa con **tamaño efectivo** (`n_e` con `ρ₁` de ambas series; piso `NEFF_PISO`). Los p-valores de **todas las candidatas** (válidas, a más de 1500 km, con `p_enso` finito) se corrigen con **BH**.
3. **Causa común:** origen y destino responden de forma significativa al índice (`p_enso < 0.05`), con **signos opuestos** de `r_enso` para una línea de efecto opuesto (`r_j < 0`) y **signos iguales** para una de mismo efecto (`r_j > 0`).
4. **Sin vecinos:** destino a **> 1500 km** del origen (distancia de círculo máximo, haversine vectorizada; cuida el cruce de ±180°). Los destinos elegidos distan **> 1000 km entre sí**. Se eligen por |r| descendente.
5. Máximo **3 opuestas y 2 iguales**. Para cada línea, `meses_coincidencia`: meses en que `z_i > 1` y `z_j < −1` (o al revés) para efecto opuesto, o ambos del mismo lado para mismo efecto, con la **fase de El Niño de ese mes** (índice del propio mes, sin rezago, como dice el informe estadístico; los meses inusuales, en cambio, usan el índice en `t − ℓ*`).
6. Si no hay ninguna que cumpla: lista vacía y `mensaje_vacio` ("no se encontró un vínculo que cumpla los criterios"). **Eso también es un resultado.**
7. Si el clic no está en la rejilla, el origen es la **celda de ScanMap más cercana** y se informa la distancia.
8. El informe lo aplica a **V1, V3, V4 y V5** con el ONI. Para `T2M` (que el informe no lista) la ruta responde **200 con `lineas: []`** y un `mensaje_vacio` que dice que no se buscan líneas para esa variable; el frontend lo muestra tal cual. Si el equipo decide incluir la temperatura, se actualiza aquí y en el contrato.

**Lo que mide y lo que no:** mide variabilidad compartida (dos lugares que se mueven en espejo), **no** que sus tendencias sean opuestas (eso lo hacen los pares de ScanMap) y **no** causalidad. Presupuesto: ~8 ms por búsqueda sobre la rejilla completa. Precalcula en el arranque, por variable, `Z`, la máscara de celdas válidas y `ρ₁` de cada celda (con `float32` si la memoria aprieta; comprueba que `r` coincide con `float64` a 1e-5).

## 11. Periodos y meses inusuales (`estadistica/periodos.py`, B3)

- **Comparación entre periodos (C16):** `Δ = ā_P2 − ā_P1` sobre la serie original **y** sobre la serie sin El Niño. Por defecto 1981–2001 frente a 2003 → fin. **Es descriptiva:** no hay prueba de diferencia de medias (habría que corregir autocorrelación y el desbalance de fases entre periodos; la significancia la da la tendencia). Si `Δ_sin` conserva signo y magnitud de `Δ`, el cambio no se debe a que un periodo tuvo más Niños.
- **Meses inusuales (C17):** `|z_t| > 2`; cada uno se etiqueta con la fase del índice en `t − ℓ*` (`nino`, `nina`, `neutro`). Se devuelven en `analyze` y se cuentan por periodo en `compare-periods`.
- Una celda con ≥ 10 años: el mínimo vale también para cada periodo comparado; si no, error `ventana_corta`.

## 12. La API (`app/api/`, B1)

**Arranque (`main.py`):** carga el catálogo JSON; abre el casillero (nivel 1) y la caché de resultados (nivel 2); carga `tabla/`, `celdas.npy`, `meses.json`, índices y `resultados.parquet` en memoria; prepara las matrices de teleconexión. Con `VERASCOPE_SIMULADO=1` solo sirve los JSON de `catalogo/simulado/`.

**Flujo de `analyze`:** validar (variable de las 5, años dentro de `[1981, VERASCOPE_FIN]`, ventana ≥ 10 años) → cuantizar la celda → ¿resultado en nivel 2? devolver → ¿serie en nivel 1? analizar → si no, pedir a POWER (cerrojo por celda, 8 s) y guardar en nivel 1 → `analizar_celda` → guardar en nivel 2 → sobreescribir veredicto y `p_ajustado` con los del escaneo si `origen = "escaneo"`. Rutas síncronas (`def`, no `async def`): FastAPI las corre en un pool de hilos.

**Errores:** siempre el cuerpo estándar del contrato, mensajes **en español sencillo que expliquen qué pasó y qué hacer** ("La ventana tiene menos de 10 años. Con tan pocos años, el ruido entre años impide ver tendencias; elige al menos 10."). No devuelvas trazas ni mensajes técnicos al usuario; regístralos en el log.

**Feed (`scan/feed`):** 20 tarjetas por página; **titulares por plantilla** (`catalogo/titulares.json`), nunca con un modelo de lenguaje. Pestañas: `fuertes` (veredicto `cambio_robusto`, ordenadas por |efecto|), `opuestas` (pares, una tarjeta por par, con `pareja`), `ocultas` (`cambio_oculto`). Plantillas de ejemplo: *"La temperatura sube de forma sostenida, aun quitando El Niño"*, *"La lluvia sube aquí y baja allá"*, *"El Niño ocultaba que la humedad del suelo baja"*. El catálogo trae por variable el sujeto con su artículo ("La lluvia", "La humedad del suelo en la superficie") para que la gramática salga bien. El id de tarjeta es estable (`{variable}-{celda}`).

**Escaneo incompleto:** `scan/feed` responde **200** con `escaneo.estado = "en_curso"` y sin tarjetas; `scan/layer` y `teleconnect` responden **503** `escaneo_en_curso` con un mensaje claro hasta que existan los resultados y las matrices. (El análisis individual de una celda con `analyze` sigue funcionando.)

**Mosaico (`scan/layer`):** arreglos paralelos por celda; `null` donde la celda no tiene serie válida (por ejemplo, humedad del suelo sobre el mar). Es la respuesta más grande (≈ 4235 valores por columna): `GZip` activado.

**Demos (`demos/{id}`):** los guiones viven en `catalogo/demos/*.json`, con celdas **que ya están en caché**. Antes del congelamiento (hora 36), con datos reales, **verifica hacia dónde apuntan las líneas y qué veredicto sale, y ajusta el guion a los datos**, no al revés. La instantánea `data/demo/*.json` permite presentar sin red.

**Respuestas empaquetadas para la app sin red (`jobs/instantaneas.py`, B1).** La app de React Native lleva dentro las respuestas de las demos para funcionar sin red. El job arranca la app FastAPI en memoria (sin servidor), llama a **sus propias rutas** contra los datos ya preparados y guarda **tal cual** el JSON de la respuesta (misma forma que el contrato, validada con los modelos Pydantic) en `backend/data/demo/respuestas/`: `analyze` de Piura **y de los destinos de sus líneas** (el panel de consecuencia los necesita) con la ventana por defecto y el índice ONI, `analyze` de la celda de la demo 2 con la ventana por defecto **y con la de 10 años que usa su paso 1**; `teleconnect` de Piura; `compare-periods` de la celda de la demo 2; y `demos/{id}` de las dos demos. Si la celda de la demo 2 todavía no está elegida, el job se detiene con un mensaje claro en vez de inventar una. Nombres de archivo estables, por ejemplo `analyze_PRECTOTCORR_-5.0_-80.5.json`. **Se regeneran cada vez que cambia el contrato, `VERSION_METODO` o el guion de una demo**, y después de que la demo 1 se ajuste a los datos reales (hora 36). Nunca se editan a mano. El frontend las copia con `npm run demo:copiar`; **tú no escribes en `frontend/`**.

**Presupuesto de latencia:** lectura de caché = milisegundos; análisis original + sin El Niño ≈ 14 ms (240 meses) a ≈ 22 ms (516 meses); líneas ≈ 8 ms; celda nueva = lo que tarde POWER (**sin medir**; ver la lista de pendientes). Registra en cada petición `t_total_ms` y si hubo acierto o fallo de caché.

## 13. Pruebas obligatorias (`backend/tests/`, B3 las escribe, todos las respetan)

**Ninguna prueba toca la red.** POWER se simula con un servidor falso (`VERASCOPE_POWER_URL`) o con JSON grabados en `tests/fixtures/`. Las series sintéticas llevan semilla fija. **Una prueba que falla no se desactiva ni se afloja para que pase el CI**: se arregla el código o se discute la regla.

| Prueba | Qué comprueba | Criterio |
|---|---|---|
| Recuperación | Series sintéticas con β, γ y ℓ conocidos | El motor los recupera **dentro de su intervalo en ≥ 95 %** de las repeticiones con ruido sin autocorrelación y **≥ 90 %** con ruido AR(1) (Hamed-Rao corrige de menos con autocorrelación: medido 92–93 %; decisión de equipo, `VERSION_METODO = 2`, que además usa max(varianza corregida, sin corregir)); el rezago correcto en ≥ 99 % (con rezago verdadero de 3 meses) |
| Sin tendencia | Series sin tendencia real, ruido autocorrelacionado | Tasa de "significativo" **cerca de 5 %** (B3 fija la tolerancia al escribir la prueba y la deja anotada); falsos descubrimientos tras BH **< 5 %** |
| Coherencia | En **toda** serie probada | El IC excluye el cero **si y solo si** `p < 0.05` (contradicciones: **0 %**) |
| Falsos positivos de referencia | Índice AR(1) ρ = 0.93, 240 meses, sin tendencia | Hamed-Rao tras quitar el índice **≤ 10 %** (≈ 7.6 % en las simulaciones del equipo; el nominal es 5 %) y claramente por debajo de Hamed-Rao con la serie original (≈ 18.5 %) |
| Potencia | Tendencia de 0.5 desviaciones por década | Mucho mayor sin El Niño que con la serie original (simulaciones: 99.4 % frente a 37.2 %) |
| Correlación | Series independientes | Falsas alarmas **≈ 5 %** con tamaño efectivo (≈ 4.4 % en las simulaciones; ≈ 22 % con el p-valor ingenuo) |
| Mismos meses | Rezago > 0 | Las dos tendencias usan los mismos meses; la serie limpia tiene `null` en los primeros ℓ |
| Calidad | Huecos de 1–2 meses, de 3, > 10 % faltante, serie constante, `-999`, mes `"13"` | Interpola, descarta, descarta, descarta, descarta, enmascara, ignora |
| Ventana | 9 años, 10 años, 19 años | Rechaza con `ventana_corta`; acepta; acepta con aviso `potencia_baja` |
| Cuantización | Dos puntos a 100 m; dos celdas vecinas | Misma llave; llaves distintas |
| Caché | Fallo → acierto → reinicio de proceso | La segunda lectura no llama a POWER; sobrevive al reinicio; subir `VERSION_METODO` invalida el nivel 2 |
| **Consistencia escaneo ↔ vivo** | Rejilla pequeña sintética | `analyze` de una celda de la rejilla da **los mismos** pendiente, intervalo y veredicto que su fila de `resultados.parquet` |
| Teleconexión | Mundo sintético con lluvia ± según región | Las 3 líneas opuestas desde "Piura" caen en la región simulada (Indonesia / norte de Australia); ninguna a < 1500 km; destinos separados > 1000 km; ≤ 3 + 2; con ruido puro: lista vacía y `mensaje_vacio` |
| Geografía | Haversine, cruce de ±180°, longitudes 0..360 ↔ −180..180 | Distancias correctas; la misma celda con ambas convenciones |
| Contrato | Respuestas contra los modelos Pydantic; OpenAPI | Sin campos de más ni de menos; el JSON de simulados valida |
| Rendimiento (`-m lento`) | 540 meses | `analyze` en caliente **< 150 ms** (presupuesto real ≈ 14–22 ms); `teleconnect` **< 50 ms**; feed **< 20 ms** |

Las simulaciones del informe sirven para **elegir** el método; no dicen nada sobre datos reales. No cites esas cifras como resultado de la plataforma.

## 14. Despliegue y operación (B1)

- **Un contenedor para la API.** El frontend **no** se despliega desde aquí: la web es una carpeta estática (`expo export -p web`, la despliega el frontend) y la app nativa es un APK (EAS Build). Imagen ligera de Python 3.11, solo dependencias de la API. `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 1` (un solo proceso: las matrices viven en memoria y el análisis cuesta milisegundos). La carpeta de datos se monta como volumen (`VERASCOPE_DATOS=/data`).
- **Memoria:** una instancia gratuita típica da 512 MB; tu presupuesto es ≈ 100 MB de matrices + el proceso. **Por eso no hay análisis diario** (ocuparía > 1.8 GB).
- **HTTPS obligatorio** desde la hora 6: las apps nativas bloquean `http://` por defecto (pon la API detrás de TLS en el proxy o el hosting). **CORS** solo para el origen de la **versión web** (`VERASCOPE_CORS`); las apps nativas no lo usan. **Healthcheck** en `/api/v1/salud`.
- **Despliegue en la hora 6 con datos simulados**; cada fusión a `main` se despliega sola. Desde la hora 20, con datos reales.
- Antes del pitch: `jobs/precalentar.py` descarga **de una en una y con pausas** las celdas de las demos y de ~50 ciudades conocidas. El día de la demo no debe hacer falta pedirle nada nuevo a la NASA.
- **Ensayo sin red (horas 44–48):** API y web en la misma laptop, red desconectada, demos servidas desde `data/demo/`; la app en el teléfono con las respuestas empaquetadas (`data/demo/respuestas/`, copiadas a la app).
- Logs de una línea por petición, en español o en claves simples; sin datos personales.

## 15. Qué hacer y qué no (resumen)

**Haz:**
- Empieza cada sesión leyendo la rama (`git branch --show-current`), `git status`, `git log -5 --oneline` y corriendo `pytest -q`. Con la rama sabes qué dueño y qué tarea te toca (tabla de ramas).
- Escribe la prueba **antes o junto con** el código; cita el cálculo (`C#`) en docstrings y commits.
- Pregunta al humano **antes** de cambiar un contrato, una constante o una regla de la sección 2.
- Si los datos reales contradicen un texto de las demos o de los informes, **dilo** y propone ajustar el texto.
- Mantén una sola fuente de cada umbral (`constantes.py`) y una sola copia del motor.

**No hagas:**
- No toques `frontend/`. Si una tarea lo exige, detente: es un cambio de contrato.
- No expongas el panel del preparador a la red ni lo metas en la imagen de la API; no mantengas dos copias del motor estadístico.
- No agregues Redis, colas, servicios, contenedores ni un segundo proceso.
- No llames a POWER ni a ningún servicio externo desde pruebas ni desde rutas que no sean `analyze`; no pidas dos veces la misma celda.
- No subas a Git `data/` (salvo `data/demo/`), credenciales ni archivos de más de unos pocos MB.
- No agregues resolución diaria/anual, polígonos, radios ni variables que POWER no sirva en vivo.
- No "arregles" un resultado incómodo (una tendencia que no sale, una línea que no apunta a donde la demo esperaba): **es un hallazgo**.
- No atribuyas causas en ningún texto que genere la API.

## 16. Definición de "terminado" para un PR del backend

- [ ] `pytest -q` y `ruff` en verde; sin pruebas desactivadas ni aflojadas.
- [ ] Contratos sin cambios, o cambio aprobado por una persona de backend **y** una de frontend, con los tipos de la app regenerables desde `/openapi.json` y **las respuestas empaquetadas de las demos regeneradas** si cambió la forma de alguna.
- [ ] Ningún umbral nuevo fuera de `constantes.py`; `VERSION_METODO` subido si cambió un cálculo.
- [ ] Mensajes de error en español sencillo, con qué pasó y qué hacer.
- [ ] Sin datos ni secretos en el diff. Documentación y este archivo actualizados si cambió una regla o un comando.
- [ ] Revisado por otra persona de backend.

**Comprobaciones tempranas (horas 0–6), antes de confiar en nada:** latencia de POWER con 20 celdas distintas · último año completo de MERRA-2 · alineación de la malla con dos celdas vecinas · una celda oceánica con `GWETROOT` · que `PRECTOTCORR` mensual viene en mm/día y que los demás parámetros están en el listado oficial · que la clave `"13"` aparece y se ignora.

## 17. Contrato de la API (`/api/v1`)

> **Fuente de verdad:** `backend/app/contracts/` (modelos Pydantic) y los tipos espejo del frontend en `frontend/src/shared/api/`. Esta sección es un resumen para que backend y frontend hablen igual. **Si el código y este resumen difieren, manda el código, y quien lo cambió actualiza este archivo en el mismo PR.** Un cambio de contrato lo aprueban **una persona de backend y una de frontend**.
> Los nombres de abajo son la **propuesta inicial** para la rama `chore/contratos` (horas 0–6). Una vez fusionada, ya no se renombra nada sin pasar por la regla anterior.

**Convenciones del JSON:** `snake_case` en español; fechas de mes como `"AAAA-MM"`; longitudes `lon` en **−180..180** (el servidor acepta 0..360 y la normaliza; **el frontend es quien convierte a 0–360 para dibujar**, ver sección del mapa); series con `null` donde no hay dato (nunca `NaN`); unidades siempre explícitas; sin capa de conversión de nombres entre Python y TypeScript.

### Rutas

| Ruta | Entrada | Respuesta |
|---|---|---|
| `GET /api/v1/salud` *(añadida)* | — | Estado del servicio: `simulado`, `ventana_fin`, `version_metodo`, `escaneo` (`estado`, `celdas_listas`, `celdas_total`). |
| `GET /api/v1/variables` | — | Las 5 variables y los índices disponibles (ONI, Niño 1+2), con definición simple, unidad y fuente. |
| `GET /api/v1/glosario` *(añadida)* | — | Términos del glosario (sale de `catalogo/glosario.json`). |
| `GET /api/v1/analyze` | `variable`, `lat`, `lon`, `inicio`, `fin` (años), `indice` (`ONI` por defecto) | Todo lo de una celda: ver forma abajo. **Una sola llamada trae la serie original y la sin El Niño.** |
| `GET /api/v1/teleconnect` | `variable`, `lat`, `lon` | Celda de origen y hasta 5 líneas (3 de efecto opuesto, 2 de mismo efecto). |
| `GET /api/v1/compare-periods` | `variable`, `lat`, `lon`, `p1_inicio`, `p1_fin`, `p2_inicio`, `p2_fin` | Promedios por periodo (original y sin El Niño), diferencias y meses inusuales. |
| `GET /api/v1/scan/feed` | `tipo` (`fuertes` \| `opuestas` \| `ocultas`), `pagina` | Tarjetas del feed (20 por página) y estado del escaneo. |
| `GET /api/v1/scan/layer` | `variable` | Veredicto y pendiente por celda para el mosaico, en **columnas** (arreglos paralelos). |
| `GET /api/v1/demos/{id}` | `id` (`efecto-espejo`, `senal-o-ruido`) | Guion paso a paso de la demo, servido desde archivos locales. |

### Enumeraciones (valores exactos)

- `veredicto.estado`: `"cambio_robusto"` · `"sensible_a_el_nino"` · `"cambio_oculto"` · `"sin_tendencia"`
- `direccion`: `"sube"` · `"baja"` · `"plana"` (solo informativa; la interfaz la dice solo cuando la tendencia es significativa)
- `fase`: `"nino"` (índice ≥ 0.5) · `"nina"` (índice ≤ −0.5) · `"neutro"`
- `veredicto.origen`: `"escaneo"` (celda de la rejilla, ventana por defecto, índice ONI: se lee del escaneo, con p corregido) · `"individual"` (todo lo demás: se rotula "análisis individual")
- `linea.tipo`: `"opuesto"` (roja, continua) · `"mismo"` (punteada)
- `aviso.codigo`: `"colinealidad"` · `"potencia_baja"` · `"respuesta_no_lineal"` · `"nino_costero"` · `"fuera_de_rejilla"` · `"muestra_efectiva_baja"`
  - `nino_costero`: solo con índice ONI, en la costa norte del Perú, si Niño 1+2 tiene `p < ALFA` y |r| mayor que el ONI sobre los mismos meses (`estadistica/costero.py`). No cambia el veredicto.
  - `respuesta_no_lineal`: lluvia (`PRECTOTCORR`) en la misma franja de la costa norte del Perú (C12; `estadistica/costero.py`). No cambia el veredicto.
  - Los dos los agrega `analyze` (`_avisos`) después de los del motor; `nino_costero` solo con índice ONI y se omite si falta `tabla/NINO12.npy`.
- `error.codigo`: `"ventana_corta"` (422) · `"fuera_de_rango"` (422) · `"sin_datos_tierra"` (422; humedad del suelo sobre el mar) · `"power_lento"` (504, trae `celda_cercana`) · `"power_error"` (502) · `"escaneo_en_curso"` (503: `teleconnect` y `scan/layer` mientras no haya resultados del escaneo; `scan/feed` responde 200 con `escaneo.estado = "en_curso"`)

### `analyze` (forma de la respuesta)

```jsonc
{
  "variable": "PRECTOTCORR", "nombre": "Lluvia", "unidad": "mm/día",
  "fuente": "MERRA-2 vía NASA POWER", "descarga": "2026-11-14",          // fecha de descarga de la serie
  "celda": { "lat": -5.0, "lon": -80.5, "lado_grados": 0.5,
             "en_rejilla": false, "celda_escaneo": { "lat": -6.0, "lon": -80.0, "distancia_km": 120 } },
  "ventana": { "inicio": "1981-01", "fin": "2025-12", "meses": 540, "meses_analizados": 537 },
  "indice": { "id": "ONI", "nombre": "Índice Oceánico de El Niño", "fuente": "ONI, NOAA CPC" },

  "fechas":            ["1981-01", "..."],     // todas las series tienen esta misma longitud
  "serie_original":    [0.12, null, "..."],    // anomalías mensuales (misma unidad)
  "serie_sin_el_nino": [null, null, null, "..."],// null los primeros `rezago_meses` meses (no se pueden limpiar)
  "serie_z":           ["..."],                // anomalía original estandarizada (para superponer regiones)
  "indice_valores":    ["..."],                // ONI (o Niño 1+2) alineado mes a mes
  "fase":              ["neutro", "nino", "..."],

  "tendencia_original":    { "pendiente_decada": 0.31, "ic_bajo": 0.10, "ic_alto": 0.52, "p": 0.004,
                             "p_ajustado": null, "significativa": true, "direccion": "sube",
                             "cambio_total": null, "cambio_pct_decada": null, "recta": ["..."] },
  "tendencia_sin_el_nino": { "pendiente_decada": 0.02, "ic_bajo": -0.1, "ic_alto": 0.14, "p": 0.71,
                             "p_ajustado": null, "significativa": false, "direccion": "plana",
                             "cambio_total": null, "cambio_pct_decada": null, "recta": ["..."] },

  "veredicto": { "estado": "sensible_a_el_nino", "origen": "individual" },
  "vinculo_el_nino": { "rezago_meses": 3, "r": 0.62, "p": 0.001, "n_efectivo": 41.2,
                       "significativo": true, "indicativo": true },   // `indicativo`: el rezago se eligió entre 7 (C9)
  "colinealidad": 0.18,                        // corr(índice rezagado, tiempo); aviso si |valor| > 0.3
  "avisos": [ { "codigo": "respuesta_no_lineal", "texto": "…en español sencillo…" } ],
  "meses_inusuales": [ { "fecha": "1998-02", "z": 4.1, "fase": "nino" } ],   // |z| > 2, fase del índice en t − rezago

  "prueba_t": null,          // PROPUESTO (C8): { disponible, p, coincide_con_mann_kendall }
  "cambio_brusco": null      // PROPUESTO (C19): { fecha, p, medias_antes_despues }
}
```

Reglas del contrato `analyze`:
- **Las dos tendencias se calculan sobre exactamente los mismos meses** (desde el mes `rezago_meses` en adelante), de modo que son comparables.
- `p_ajustado` solo viene (no `null`) cuando `veredicto.origen == "escaneo"`; en ese caso `significativa` se decide con `p_ajustado`, y si no, con `p < 0.05`.
- `cambio_pct_decada` solo existe para variables con cero natural (lluvia, humedades); en temperatura es `null`. `cambio_total = pendiente_por_mes × (n − 1)`.
- `recta` tiene la misma longitud que `fechas` (con `null` antes del primer mes analizado) para que el gráfico la dibuje sin calcular nada.
- El frontend **nunca calcula estadística**: ni z, ni tendencias, ni fases, ni veredictos. Solo **elige qué mostrar** de lo recibido.

### `teleconnect`

```jsonc
{ "variable": "PRECTOTCORR",
  "origen": { "lat": -6.0, "lon": -80.0, "distancia_a_clic_km": 120, "r_el_nino": 0.62 },
  "lineas": [ { "tipo": "opuesto", "lat": -18.0, "lon": 142.0, "r": -0.80, "p_ajustado": 1e-9,
                "distancia_km": 14800, "r_el_nino_origen": 0.62, "r_el_nino_destino": -0.55,
                "meses_coincidencia": [ { "fecha": "1998-01", "fase": "nino" } ] } ],
  "mensaje_vacio": null }      // texto cuando no hay líneas: "no se encontró un vínculo que cumpla los criterios"
```

Si la celda clicada no está en la rejilla, el origen es la **celda de ScanMap más cercana** y se informa la distancia. Máximo 3 líneas `opuesto` y 2 `mismo`.

### `compare-periods`, `scan/feed`, `scan/layer`, `demos/{id}`

```jsonc
// compare-periods
{ "p1": { "anios": [1981, 2001], "media_original": 0.1, "media_sin_el_nino": 0.0,
          "meses_inusuales": 12, "meses_inusuales_en_el_nino": 9 },
  "p2": { "anios": [2003, 2025], "...": "..." },
  "delta_original": 0.3, "delta_sin_el_nino": 0.05,
  "nota": "Comparación descriptiva: la significancia la da la tendencia." }

// scan/feed
{ "tipo": "fuertes", "pagina": 0, "por_pagina": 20, "total": 134,
  "escaneo": { "estado": "completo", "celdas_listas": 4235, "celdas_total": 4235 },
  "tarjetas": [ { "id": "T2M-123", "titular": "La temperatura sube de forma sostenida, aun quitando El Niño",
                  "variable": "T2M", "unidad": "°C", "celda": { "lat": -6.0, "lon": -80.0 },
                  "veredicto": "cambio_robusto", "pendiente_decada": 0.25, "ic_bajo": 0.2, "ic_alto": 0.3,
                  "p_ajustado": 1e-6, "efecto": 1.1,
                  "pareja": { "lat": 10.0, "lon": 120.0, "pendiente_decada": -0.04 } } ] }  // `pareja` solo en "opuestas"

// scan/layer  (columnas paralelas; 4235 valores cada una; `null` donde la celda no tiene serie válida)
{ "variable": "T2M", "paso_grados": 2, "lat": ["..."], "lon": ["..."],
  "veredicto": ["cambio_robusto", "..."], "pendiente_decada": ["..."], "efecto": ["..."] }

// demos/{id}
{ "id": "efecto-espejo", "titulo": "El efecto espejo de El Niño", "variable": "PRECTOTCORR",
  "celda": { "lat": -5.0, "lon": -80.5 },
  "pasos": [ { "n": 1, "texto": "Esta es Piura. Mira la lluvia: hay meses que parecen catastróficos.",
               "acciones": [ { "tipo": "seleccionar_celda", "lat": -5.0, "lon": -80.5 },
                             { "tipo": "quitar_el_nino", "valor": false } ] } ] }
```

Vocabulario de `acciones` de las demos (lo ejecuta el frontend contra el estado global): `seleccionar_variable`, `seleccionar_celda`, `fijar_ventana`, `quitar_el_nino`, `reproducir`, `detener`, `ir_al_mes`, `ir_a_destino`, `mostrar_periodos`.

**Error estándar** (todas las rutas): `{ "error": { "codigo": "power_lento", "mensaje": "…en español…", "celda_cercana": { "lat": -5.0, "lon": -80.0 } | null } }`.

**Respuestas empaquetadas para la app sin red (nuevo, versión 2).** El backend (B1, `jobs/instantaneas.py`) llama a sus propias rutas contra los datos ya preparados y guarda **tal cual** las respuestas de `analyze` (ventana por defecto e índice ONI; y la ventana de 10 años de la demo 2), `teleconnect`, `compare-periods` y `demos/{id}` de los lugares de las demos en `backend/data/demo/respuestas/*.json` (va a Git). El frontend las copia con `npm run demo:copiar` a `frontend/assets/demo/` y las valida con los **mismos tipos** del contrato. **Tienen exactamente la forma de las respuestas de la API**; si el contrato cambia, hay que **regenerarlas**. Llevan la fecha de descarga que ya trae `descarga`; la app nunca las presenta como actuales.

**Red y orígenes:** las apps nativas **exigen HTTPS** (bloquean `http://` por defecto): la API se publica con HTTPS desde la hora 6. **CORS** solo hace falta para el origen de la versión web (`VERASCOPE_CORS`); las apps nativas no lo usan.

**Modo simulado:** con `VERASCOPE_SIMULADO=1` el backend responde con los JSON de `backend/app/catalogo/simulado/`, validados contra los mismos modelos Pydantic. Es lo que se despliega en la **hora 6** y lo que el frontend usa para desarrollar sin esperar al motor real. **Todo dato simulado se rotula como simulado en `salud` y en la interfaz.**

## 18. Equipo, ramas, pull requests y calendario

### Quién es dueño de qué

| Persona | Es dueña de |
|---|---|
| **B1** | Capa API y composición (`main.py`, `api/`), `contracts/`, caché de dos niveles (`datos/cache.py`), catálogo y demos en JSON, rutas del feed, despliegue **con HTTPS** desde la hora 6, `jobs/precalentar.py` y **`jobs/instantaneas.py`** (respuestas de las demos para la app sin red). Mide la **latencia de POWER** (20 celdas distintas, horas 0–6). |
| **B2** | Cliente de POWER, cuantización, validación, índices de NOAA (`datos/`), el job de ScanMap (`jobs/scanmap.py`) y la **integración y operación del preparador de datos** (`verascope-datos`: panel, descarga, paquete). Averigua el **último año completo de MERRA-2** (horas 0–6). |
| **B3** | Todo `estadistica/` (anomalías, tendencia, ENSO, veredicto, FDR, teleconexión, periodos), **reparte el `motor.py` del preparador en esos módulos** y escribe **las pruebas del motor** (`tests/`). Decide si entra el índice Niño 1+2 (hora 20). |
| **F1** | Selector de variable y ventana, **mapa del Pacífico propio en SVG con gestos** (celda, mosaico), líneas causa → consecuencia, `app/espacio.tsx`, **`estado/store.ts`**. Comprueba Expo Go y el SDK en la hora 0. |
| **F2** | Panel Causa · Consecuencia · Realidad (**`GraficoSerie` propio en SVG**), interruptor "Quitar El Niño", control de tiempo y comparación por periodos, `estado/queryClient.ts`, y **el primer APK y la exportación web (`fe/distribucion`)**. Decide si entra el CO₂ de Mauna Loa (hora 30, solo si sobra tiempo). |
| **F3** | Tarjeta de veredicto, feed de ScanMap, demos guiadas (incluido el modo sin red), glosario, página de inicio y navegación (`app/_layout.tsx`, `index.tsx`, `glosario.tsx`). |

Los archivos de contratos y el estado global son **compartidos**: los edita su dueño y los revisan todos.

### Ramas (flujo corto sobre `main`)

`main` siempre es desplegable y cada fusión se despliega sola. Cada rama vive **horas, no días**.

| Rama | Propósito | Dueño | Horas |
|---|---|---|---|
| `chore/contratos` | Contratos Pydantic y tipos TypeScript iniciales; esqueleto del servicio y **de la app Expo** (scripts `tipos`, `test`, `lint`, `demo:copiar`); despliegue simulado con HTTPS | B1 y F1 | 0–6 |
| `be/datos-power` | Cliente de POWER, cuantización, validación e índices | B2 | 2–12 |
| `be/motor-enso` | Anomalías, tendencia con intervalo coherente, quitar El Niño, veredicto | B3 | 6–18 |
| `be/api-cache-despliegue` | Ruta `analyze`, caché de dos niveles, despliegue, precalentamiento | B1 | 4–20 |
| `be/scanmap-job` | Integrar el preparador de datos; rejilla de 2°, escaneo offline, FDR, ranking y pares | B2 | 8–20 |
| `be/teleconexion-periodos` | Rutas `teleconnect` y `compare-periods`, meses inusuales | B3 | 18–30 |
| `be/scan-feed-api` | Rutas del feed y del mosaico | B1 | 20–30 |
| `fe/mapa-celda` | Mapa del Pacífico en SVG (costas, gestos, zoom), rectángulo de la celda, selector de variable y ventana; **medir el rendimiento en un teléfono modesto antes de la hora 14** | F1 | 3–14 |
| `fe/lineas-mosaico` | Líneas causa → consecuencia y mosaico de ScanMap | F1 | 20–32 |
| `fe/graficos-enso` | Panel de gráficos e interruptor de El Niño | F2 | 6–20 |
| `fe/tiempo-comparador` | Reproducción, periodos y meses inusuales | F2 | 20–32 |
| `fe/veredicto-feed` | Tarjeta de veredicto y feed de ScanMap | F3 | 6–28 |
| `fe/demos-glosario` | Las dos demos guiadas y la página de glosario | F3 | 24–36 |
| `fe/distribucion` | **Primer APK con EAS Build y primera exportación web** (antes de la hora 14); luego las versiones finales | F2 | 6–14 y 36–44 |
| `be/instantaneas-demo` | `jobs/instantaneas.py`: respuestas de las demos para la app sin red (`backend/data/demo/respuestas/`) | B1 | 36–42 |
| `release/demo` | Se abre en el congelamiento; solo admite ramas `fix/` | Todos | 36–48 |

### Reglas

1. **Integrar seguido:** cada persona fusiona a `main` **al menos cada 4 a 6 horas**, actualizándose primero con lo último de `main` (`git pull --rebase origin main`).
2. **Revisión cruzada:** todo PR lo aprueba **otra persona de la misma área**. Un cambio de contratos lo aprueban **una de backend y una de frontend**.
3. **CI en verde para fusionar:** pruebas del motor estadístico (backend) + en el frontend `tsc --noEmit`, `jest` y `expo export -p web`.
4. **Congelamiento en la hora 36:** se etiqueta `v1.0-freeze`, se abre `release/demo` y desde ahí **solo entran correcciones** en ramas `fix/…`. La entrega final se etiqueta `v1.0-entrega`.
5. **Datos fuera de Git.** La caché, el casillero y los resultados del escaneo **no se suben**; las únicas excepciones son la instantánea de las demos en `backend/data/demo/` (incluidas las `respuestas/` para la app) y su copia en `frontend/assets/demo/`.
6. **Commits con prefijo:** `feat:`, `fix:`, `docs:`, `chore:` (y `test:` si solo cambian pruebas). Mensaje en español, en presente, corto. Si el cambio toca una regla estadística, cita su número (por ejemplo `fix: intervalo con varianza corregida (C8)`).
7. **No se hace `push --force` a `main`, ni se salta la revisión, ni se desactivan pruebas para que pase el CI.**
8. Si una tarea te obliga a salir de tu carpeta (`backend/` ↔ `frontend/`), **detente y avisa**: probablemente es un cambio de contrato.

### Calendario, hitos y recorte

| Horas | Backend | Frontend |
|---|---|---|
| 0–6 | Contratos, esqueleto con respuestas simuladas, **despliegue con HTTPS**. Medir latencia de POWER con 20 celdas. Poner en marcha el preparador (prueba rápida) y descargar índices de NOAA. | Esqueleto de la app con Expo y **comprobación de Expo Go en un teléfono real**, estado global, mapa en SVG centrado en el Pacífico conectado a la respuesta simulada. |
| 6–20 | Cliente de POWER y caché; motor mensual con y sin El Niño **probado**; ruta `analyze` real. **Desde la hora 8, el preparador descarga y calcula el escaneo en segundo plano** (celdas de las demos primero). | Selector de variable y ventana, rectángulo de la celda, gráfico con interruptor, tarjeta de veredicto. **Primer APK y primera exportación web antes de la hora 14.** |
| 20–36 | Rutas `teleconnect`, `compare-periods`, feed y mosaico; revisar resultados del escaneo. | Líneas, control de tiempo, panel completo, feed y mosaico. |
| 36–44 | Instantánea de las demos **y respuestas empaquetadas para la app**, correcciones, precalentamiento. | Demos guiadas (también sin red), pulido visual, glosario, **APK y web finales**. |
| 44–48 | Entregables del evento (descripción, video, repositorio). **Ensayo con la red desconectada.** | Ídem, con la app en el teléfono y en la web de la laptop. |

**Hitos (son pruebas de integración, no fechas; si no se cumplen a su hora, se recorta alcance, no se mueve el hito):**
- **Hora 6:** URL pública **con HTTPS** y la app (en un teléfono con Expo Go y en la web) recibe una respuesta **simulada** de `analyze`.
- **Hora 20:** un clic en el mapa devuelve un veredicto mensual **calculado con datos reales de POWER**.
- **Hora 36:** las dos demos corren completas; desde aquí solo correcciones.

**Orden de recorte si hay atraso (de lo primero a lo último):**
1. Vistas diaria y anual del gráfico.
2. Tooltips del glosario (queda la página).
3. Líneas de "mismo efecto" (quedan las de efecto opuesto).
4. Mosaico de ScanMap en el mapa (queda el feed en lista). **Es lo primero que se recorta si el mapa en SVG va lento en un teléfono modesto.**
5. Pestañas de señales opuestas y cambios ocultos; el feed se reduce a 10 hallazgos precalculados sobre una región.
6. Comparación por periodos (queda la reproducción).

**NUNCA se recorta (es el núcleo):** el análisis mensual con y sin El Niño, el interruptor, la línea de Piura hacia Indonesia y Australia, la reproducción en el tiempo y la demo 1.

### Decisiones posteriores a los informes

- **Diseño del frontend:** la dirección visual elegida después del informe (fondo grafito oscuro, rojo para El Niño, cian para lluvia, ámbar para sequía, tipografía Inter) **reemplaza** el "fondo claro" y el azul para La Niña mencionados en el informe técnico. Detalle en la sección de lenguaje visual del frontend.
- **App móvil y web (informe técnico v2):** el frontend es **una sola base de código con Expo** para iOS, Android y web. Si el humano prefiere **una web aparte con React** (compartiendo tipos, cliente y estado), es una decisión pendiente (tabla de abajo); mientras no se cambie, manda esta.
- **Fin de la ventana:** los informes hablan de 1981–2023 (516 meses, 43 años) porque estaban escritos con ese último año. **No lo fijes en el código**: la ventana termina en el último año completo de MERRA-2 (`VERASCOPE_FIN`, por defecto año actual − 1) y se confirma en las horas 0–6. Los "516 meses" y los "43 años" de los textos son ejemplos que cambian.
- **El prototipo (`verascope-codigo.zip`)** usa nombres viejos en inglés (`/series`, `/feed`, `raw`, `clean`, `p_adj`…). Sirve para ver ideas, **no para copiar nombres**: manda este contrato.

### Pendiente y sin verificar (no lo des por hecho)

| Tema | Qué falta | Quién |
|---|---|---|
| Entregables de la sede | Qué pide el evento y a qué hora cierra la entrega | Todos, antes del evento |
| Una base de código con Expo (adoptada) o web aparte con React | Confirmarlo con el humano | Todos; propone F1, hora 0 |
| Versión de Expo Go de las tiendas y SDK que se fija | Comprobarlo en un teléfono real (hoy: SDK 57) | F1, hora 0 |
| Rendimiento del mapa SVG con el mosaico en un teléfono modesto | Medirlo; si no alcanza, se recorta el mosaico | F1, antes de la hora 14 |
| Primer APK con EAS Build y primera exportación web | Que salgan sin sorpresas de cuenta o de cola | F2, antes de la hora 14 |
| Cuenta de Apple Developer (TestFlight) o iOS solo con Expo Go y simulador | Decidirlo | Todos, antes del evento |
| Cuándo corre la descarga de las 4235 celdas | Desde la hora 8, como en el plan, o antes si las reglas de la sede lo permiten | B2 y todos, antes del evento |
| Colores de La Niña y de la línea de mismo efecto | Proponer y aprobar con captura de pantalla | F1 propone, otro del frontend aprueba, hora 14 |
| Último año completo de MERRA-2 en POWER | **Verificado (14-nov-2026):** 2025 completo (con mes `13`); 2026 llega hasta septiembre y octubre–noviembre vienen en `-999`. `VERASCOPE_FIN=2025` (= el valor por defecto) | B2, horas 0–6 |
| Latencia real de POWER | Medirla desde la sede con 20 celdas distintas **antes de prometer ninguna cifra** | B1, horas 0–6 |
| Alineación de la malla de 0.5° | **Verificado (14-nov-2026), no coincide del todo:** en latitud, POWER usa celdas de 0.5° centradas en múltiplos de 0.5 (coincide). En longitud usa la malla nativa de MERRA-2, de **0.625°** (centros en −180 + k·0.625): −77.0 y −76.6 devuelven la misma serie, y −76.5 devuelve la de la celda vecina. Por eso dos llaves de 0.5° pueden traer la misma serie, y el rectángulo de 0.5° no es la huella real del dato. **Decidido:** se mantiene la celda de 0.5° (C3) y se declara que en longitud el dato cubre 0.625° (ver `backend/docs/comprobaciones-b2.md`) | B2 propone, todos deciden |
| Humedad del suelo sobre el mar | **Verificado:** en el océano `GWETROOT` llega en `-999`, pero `GWETTOP` llega en `1.0` constante (no `-999`). La regla 5 de C2 (desviación nula) es la que la descarta, no la regla 3 | B2 |
| `PRECTOTCORR` y mes `13` | **Verificado (14-nov-2026):** `PRECTOTCORR` llega en `mm/day` y las llaves incluyen el mes `13` (promedio anual), que el cliente ignora | B2 |
| Prueba rápida del panel del preparador | Correrla y anotar el resultado en `backend/docs/comprobaciones-b2.md` | B2 |
| Niño 1+2 para Piura | **Decidido (15-nov-2026):** el ONI sigue siendo el índice principal (escaneo, veredicto, líneas). Niño 1+2 entra como **complementario**: en la costa norte del Perú (`COSTA_NINO12_LAT` × `COSTA_NINO12_LON`), si su vínculo es significativo y más fuerte que el del ONI, `analyze` emite el aviso `nino_costero` (`estadistica/costero.py`) y ofrece repetir con `indice=NINO12`. Con datos reales, Piura: lluvia r = 0.25 con Niño 1+2 frente a 0.15 con ONI. Conectado en `analyze` junto con `respuesta_no_lineal` | B3 |
| CO₂ de Mauna Loa | Solo si sobra tiempo, como franja de contexto | F2, hora 30 |
| Escorrentía de GLDAS (×8) y capa NDVI de AppEEARS | Confirmar convenciones con los servicios reales (solo afectan al preparador de datos y a fichas informativas de la demo 1) | Quien corra el preparador |
| Referencias bibliográficas | Verificarlas (se citaron de memoria) | Todos, antes de la entrega |
| Dirección real de las líneas y veredicto de la demo 1 | Con datos reales, **ajustar el guion a lo que muestran los datos**, no al revés | B3 + F3, antes de la hora 36 |
