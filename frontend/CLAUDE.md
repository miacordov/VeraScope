# CLAUDE.md · VeraScope · FRONTEND (app móvil y web)

> **Para quién es:** el Claude Code que trabaja en `frontend/`. Este archivo va en **`frontend/CLAUDE.md`**. Su gemelo, `backend/CLAUDE.md`, trae las mismas reglas del proyecto (secciones 1–3) y el mismo contrato de la API (sección 17). Si cambias una regla compartida, avisa al humano para que se actualice **en los dos**.
> **Cómo se mantiene:** si un comando, una ruta o una regla de aquí deja de ser cierta, corrígela **en el mismo PR** que la cambió. Un archivo desactualizado es peor que no tener ninguno.
> **Versión 2 (14 nov 2026):** el frontend ya no es una web de React con Vite. Es una **app de React Native (Expo)** para iOS y Android; la **versión web sale de la misma base de código** (React Native for Web). Si ves en el repositorio restos de Vite, Leaflet, Recharts, Tailwind o Vitest, son de la versión 1 y hay que sustituirlos (informe técnico v2, cambios V1–V8).

**Mapa del archivo:** 0 Quién eres · 1 Qué es VeraScope · 2 Reglas que no se deshacen · 3 Cómo hablamos de la ciencia · 4 Stack, comandos y entrega · 5 Estructura y dueños · 6 Las seis reglas de oro · 7 Estado global · 8 Datos del servidor y modo sin red · 9 El mapa del Pacífico (SVG) · 10 Las features · 11 Estados de la interfaz · 12 Demos guiadas · 13 Lenguaje visual, textos y accesibilidad · 14 Pruebas · 15 Qué hacer y qué no · 16 Definición de "terminado" · 17 Contrato de la API · 18 Equipo, ramas y calendario.

## 0. Quién eres y cómo trabajar

- Eres el **Claude Code del frontend** de VeraScope. Construyes y mantienes la **app de React Native (Expo) + TypeScript** que muestra el mapa, los gráficos, el veredicto, el feed de ScanMap y las demos guiadas, en **teléfono (iOS y Android) y en web**, con **una sola base de código**.
- **Tu carpeta es `frontend/`.** **No tocas `backend/`** (puedes *leer* `backend/data/demo/respuestas/` para copiar las respuestas de las demos, con `npm run demo:copiar`). Si falta un campo, una ruta o un valor en la API, detente y avisa: es un cambio de contrato (sección 17) y lo aprueban una persona de backend y una de frontend.
- **Para saber qué te toca**, mira la rama (`git branch --show-current`) y la tabla de ramas de la sección 18: la rama dice qué feature es y de quién (F1, F2 o F3).
- **Al empezar una sesión:** lee `git status`, `git log -5 --oneline`, corre `npx tsc --noEmit && npm run test` y confirma que partes de verde. Si hay algo rojo que no es tuyo, dilo antes de empezar.
- **Con el humano:** español sencillo, sin jerga; explica **qué hiciste y qué falta** en pocas líneas. Antes de un cambio grande, propón el plan en 3–5 líneas y espera el visto bueno. **Pregunta antes de:** cambiar el store o un contrato, tocar una regla de la sección 2, agregar una librería o **cambiar de versión de Expo**.
- **Tu trabajo es mostrar bien lo que calcula el backend, no recalcularlo.** Si un número se ve raro, es un tema para hablar con backend, no para "arreglar" en pantalla.
- **Si algo no está en este archivo, no lo inventes:** pregunta, o busca en los informes del equipo (técnico v2 y estadístico). Trabajas contra un reloj de 48 horas con ~30 h efectivas por persona: **prioriza el núcleo** (sección 18: "nunca se recorta").
- **Lo que aquí se dice del mapa, los gestos y la compilación es diseño, no código probado:** nadie ha construido todavía la app de Expo. Donde el texto diga *"se valida en la hora X"*, **valídalo en esa hora y dile al humano qué encontraste**, aunque contradiga lo escrito.

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
| V1 | Plataforma | App de **React Native con Expo** (**SDK 58**, fijo; antes 57, ver sección 4) para iOS y Android; **la web sale del mismo código** con React Native for Web. Ya no hay web aparte con Vite. |
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
- El umbral mensual de El Niño (índice ≥ 0.5) y La Niña (≤ −0.5) es una **simplificación**; NOAA exige cinco estaciones seguidas. Se indica en el glosario.
- Las cifras de simulaciones (falsos positivos, potencia) son **de series sintéticas**, no de datos reales. No las presentes como resultados sobre datos reales.
- Las referencias de literatura de los informes se citaron **de memoria** y hay que verificarlas antes de la entrega.

## 4. Stack, comandos, variables de entorno y entrega

**Stack:** **Expo SDK 58** (React Native 0.88, React 19.3) · TypeScript (modo estricto) · **Expo Router** (rutas por archivos) · **Zustand** (estado global) · **TanStack Query** con persistencia en AsyncStorage (datos del servidor) · **react-native-svg** + **d3-scale / d3-shape / d3-array** (mapa y gráficos, propios) · **react-native-gesture-handler** + **react-native-reanimated** (pellizcar y arrastrar) · `StyleSheet` + `src/shared/tema.ts` (estilos; **sin Tailwind**) · `@expo-google-fonts/inter` (tipografía, **incluida en la app**) · **Jest (`jest-expo`) + Testing Library para React Native** (pruebas) · `openapi-typescript` (tipos del contrato).

**Una sola base de código para tres salidas:** app iOS, app Android y **web** (React Native for Web, que dibuja con React DOM). No hay un segundo proyecto web. *(Alternativa descartada por ahora: una web aparte con React + Vite que comparta tipos, cliente y estado; se decide con el humano en la hora 0; ver sección 18.)*

**No se usan:** Leaflet, `react-native-maps`, MapLibre/Mapbox, WebView con mapas, Skia, Recharts, Plotly, WebGL, Tailwind/NativeWind, Vite ni Vitest. Con series mensuales (~540 puntos) y un mapa propio en SVG alcanza (correcciones C6, V2, V3). **No se agregan librerías de estado, de UI, de gráficos ni de animación sin avisar:** cada dependencia es peso y riesgo en 48 horas.

**Versión de Expo (decisión de la hora 0, 15 nov 2026): se fija el SDK 58** y **no se cambia durante el evento**. El plan original fijaba el 57 porque el 12 de nov Expo Go para el 58 aún no estaba en las tiendas; en la comprobación de la hora 0 (F1, teléfono Android real) la Expo Go de la tienda **ya solo abría el SDK 58** (las tiendas solo traen la última; para el 57 solo queda un APK de Android instalado a mano y nada para iPhone real). Por eso se subió a 58 en `chore/contratos` (cambio de regla: lo aprueban F2, F3 y B1 en el PR). Si en un teléfono no corre, plan B = versión de desarrollo (`expo-dev-client`) o el APK. Instala dependencias **siempre con `npx expo install <paquete>`** (elige la versión que corresponde al SDK) y verifica con `npx expo install --check`.

```bash
cd frontend
npm ci                          # instala exactamente lo del lockfile
npm run dev                     # TODO EN UNO: API simulada (crea backend/.venv la 1.ª vez) + IP local para Expo Go + expo start
npx expo start                  # menú: i (simulador iOS), a (Android), w (web); QR para Expo Go en el teléfono
npx expo start --web            # solo web, normalmente en http://localhost:8081
npx expo export -p web          # sitio estático en dist/  (esto corre el CI)
npx tsc --noEmit                # solo tipos
npm run test                    # Jest (jest-expo), sin red
npm run lint                    # ESLint
npm run tipos                   # regenera src/shared/api/esquema.ts desde http://localhost:8000/openapi.json (openapi-typescript)
npm run fixtures:copiar         # regenera src/shared/api/__fixtures__/*.ts desde ../backend/app/catalogo/simulado/*.json
npm run demo:copiar             # copia ../backend/data/demo/respuestas/*.json a assets/demo/
npx expo install --check        # ¿las versiones coinciden con el SDK?
eas build -p android --profile preview    # APK instalable (hace falta cuenta de Expo y `eas login`)
```

> Si un comando no coincide con lo que hay en el repositorio, **corrige esta sección en el mismo PR**. Los scripts `tipos`, `fixtures:copiar`, `demo:copiar`, `lint` y `test` se crean en `package.json` en la rama `chore/contratos`.
>
> **Notas del esqueleto (`chore/contratos`):** el SDK 58 trae TypeScript 6 y `openapi-typescript` 7 solo acepta TypeScript 5, así que **no es dependencia del proyecto**: `npm run tipos` lo ejecuta con `npx openapi-typescript@7.13.0` (instalación aparte). `esquema.ts` y los fixtures se suben a Git; el CI no los regenera. Los fixtures son módulos `.ts` anotados con los tipos del contrato (un `.json` importado perdería los tipos literales): si el backend cambia un campo, `tsc` falla, y una prueba avisa si se desincronizan de los JSON simulados. Con TypeScript 6, `tsconfig.json` declara `"types": ["jest", "node"]`. En modo simulado el backend solo responde a Piura (−5.0, −80.5), `PRECTOTCORR`, 1981–1990, ONI: el espacio de trabajo ofrece ese ejemplo mientras `salud.simulado` sea verdadero.

| Variable | Para qué | Por defecto |
|---|---|---|
| `EXPO_PUBLIC_API_URL` | URL base de la API (`/api/v1` la agrega el cliente). Se **incrusta al compilar**: hay que definirla al exportar la web y al construir el APK | `http://localhost:8000` |

- **En el teléfono, `localhost` no es tu laptop.** Con Expo Go usa la **IP de la laptop** en la red local (`http://192.168.x.x:8000`) o la URL desplegada. En el emulador de Android la laptop es `http://10.0.2.2:8000`. En el simulador de iOS, `localhost` sí funciona.
- **HTTPS:** las apps nativas **bloquean por defecto las conexiones sin cifrar**. En desarrollo con Expo Go una URL `http://` suele funcionar; en el **APK y en iOS de producción se exige `https://`**. La API se publica con HTTPS desde la hora 6 (backend). Nunca dejes una URL `http://` en un build de entrega.
- Para desarrollar sin esperar al motor real, levanta el backend con `VERASCOPE_SIMULADO=1` (o usa la URL simulada desplegada en la hora 6).
- **`npm run dev` (desde `frontend/`) hace todo eso solo:** prepara `backend/.venv` con Python ≥ 3.11 (uv si está; solo la primera vez o si cambia `pyproject.toml`), arranca la API simulada en `0.0.0.0:8000` con CORS para la web, detecta la IP de la laptop, se la pasa a la app como `EXPO_PUBLIC_API_URL` y abre `expo start` (si el 8081 está ocupado usa el siguiente libre). Ctrl+C apaga los dos. Si ya defines `EXPO_PUBLIC_API_URL` (p. ej. la URL https desplegada), no levanta la API local. Solo ejecuta el backend: no modifica archivos versionados de `backend/`.

**Entrega (tres salidas):**

| Salida | Cómo | Notas |
|---|---|---|
| **Web** | `npx expo export -p web` → `dist/` servido por un hosting estático o nginx. `app.json` → `expo.web.output: "single"` (aplicación de una sola página) | La API necesita CORS para el origen de la web (`VERASCOPE_CORS`, backend) |
| **Android** | `eas build -p android --profile preview` → APK que se instala sin tienda. Durante el desarrollo, Expo Go | El perfil `preview` vive en `eas.json`. `expo.android.package` lo fija F2 al crear el perfil |
| **iOS** | Expo Go o simulador. Un iPhone real **sin Expo Go** (TestFlight) exige una cuenta de **Apple Developer** (de pago) | Decisión pendiente del equipo (sección 18). Si no hay cuenta, iOS se muestra con Expo Go o simulador |

**Primer APK y primera exportación web, antes de la hora 14** (rama `fe/distribucion`, F2). Si EAS Build hace fila o falla algo de la cuenta, se descubre cuando aún hay margen. La web estática y Expo Go quedan como respaldo para presentar.

## 5. Estructura de `frontend/` y dueños

```
frontend/
├── app.json                      # configuración de Expo (web.output: single)
├── eas.json                      # perfiles de EAS Build (preview → APK)
├── .env.example                  # EXPO_PUBLIC_API_URL
├── app/                          # PANTALLAS (Expo Router: un archivo = una ruta)
│   ├── _layout.tsx               # navegación, tipografía, proveedores
│   ├── index.tsx                 # Inicio                                    [F3]
│   ├── espacio.tsx               # Espacio de trabajo                        [F1]
│   └── glosario.tsx              # Glosario                                  [F3]
├── assets/
│   ├── geo/tierra.json           # costas de Natural Earth 110m (dominio público)
│   ├── fonts/                    # (Inter se carga con @expo-google-fonts/inter)
│   └── demo/                     # respuestas de la API para las demos sin red (se copian del backend)
├── scripts/                      # utilidades de build (si hacen falta)
└── src/
    ├── estado/
    │   ├── store.ts              # estado global (Zustand)              [F1, revisan todos]
    │   └── queryClient.ts        # caché de respuestas + persistencia   [F2]
    ├── shared/
    │   ├── api/                  # cliente y tipos (los tipos se GENERAN, no se escriben a mano)
    │   ├── geo.ts                # lon360, lonNormal, cuantización: UN solo lugar
    │   ├── format.ts             # formato de números (es-PE), siempre con unidad
    │   ├── tema.ts               # tokens: paletas clara y oscura, tipografía, espacios
    │   ├── useTema.ts            # useTema() y useEstilos(): colores del modo actual
    │   ├── ProveedorTema.tsx     # modo claro/oscuro (sigue al sistema; guarda la elección)
    │   ├── components/           # insignia de veredicto, etiqueta de fuente
    │   └── ui/                   # botones, tarjetas, alertas, hoja inferior
    └── features/
        ├── variable-picker/      # [F1]
        ├── map/                  # mapa SVG, mosaico, rectángulo de la celda      [F1]
        ├── teleconnection-lines/ # [F1]
        ├── series-charts/        # Causa · Consecuencia · Realidad (GraficoSerie) [F2]
        ├── enso-toggle/          # [F2]
        ├── time-comparator/      # reproducción y periodos                        [F2]
        ├── verdict-card/         # [F3]
        ├── scan-feed/            # [F3]
        ├── guided-tours/         # [F3]
        └── glossary/             # [F3]
```

- **Organización por features:** cada carpeta de `features/` es de una persona. No edites la feature de otra sin avisar; pide el cambio por PR.
- **`app/` (rutas) es delgado:** cada archivo compone features; la lógica vive en `src/`. *(Por eso el estado está en `src/estado/` y no en `app/`: en Expo Router, `app/` son rutas.)*
- Los componentes compartidos (`shared/`) los edita quien los necesita, pero los revisan las tres personas del frontend.
- `shared/api/` **no se escribe a mano**: los tipos se regeneran con `npm run tipos` y se envuelven con funciones del cliente. Si el backend aún no expone un campo, **no lo inventes**: pídelo.
- **Todo es React Native.** Nada de `<div>`, `<span>`, CSS, `document`, `window` ni `localStorage` en código compartido: usa `View`, `Text`, `Pressable`, `StyleSheet`, AsyncStorage. Código solo-web o solo-nativo (`archivo.web.tsx`, `Platform.OS`) únicamente cuando no haya otra salida y **con aviso al humano**.

## 6. Las seis reglas de oro del frontend

1. **Una llamada por análisis.** Elegir una celda dispara `analyze` y `teleconnect` (en paralelo). Todo lo demás se resuelve en el dispositivo. (Cuando hay destino, se pide además `analyze` del destino para la fila "Consecuencia"; queda en caché.)
2. **El interruptor no toca la red.** "Quitar El Niño" solo cambia **qué serie de la respuesta ya recibida** se dibuja y **qué veredicto** se muestra.
3. **Reproducir no recalcula.** El control de tiempo solo **recorta lo visible**. La tendencia viene calculada con la serie completa; dibújala completa.
4. **Lo que dice el feed, lo repite el detalle.** Ningún número se calcula dos veces en lugares distintos. **El frontend nunca calcula estadística**: ni z, ni tendencias, ni fases, ni veredictos, ni porcentajes. Solo elige qué mostrar de lo que llega y le da formato.
5. **Etiquetado honesto.** Cada gráfico y cada tarjeta muestran **unidad, fuente, celda y periodo**. Un resultado sin tendencia se presenta como hallazgo válido.
6. **Lo esencial no depende de internet.** La tipografía, las costas del mapa y las **respuestas de las dos demos van dentro de la app**. Sin red, las demos siguen funcionando (sección 8).

## 7. Estado global (`src/estado/store.ts`, Zustand)

Lo que **se guarda en el store** es solo lo que el usuario (o una demo) decide. **Los datos del servidor viven en TanStack Query, nunca en el store.**

| Campo | Qué guarda | Quién lo cambia |
|---|---|---|
| `variable` | Código de la variable elegida (`PRECTOTCORR` por defecto) | Selector de variable, tarjeta del feed, demo |
| `celda` | Celda de 0.5° cuantizada `{lat, lon}` con `lon` en −180..180, o `null` | Toque en el mapa, tarjeta del feed, demo |
| `ventana` | `{inicio, fin}` en años (por defecto, todo el registro) | Selector de ventana, demo |
| `quitarElNino` | `false` = serie original; `true` = serie sin El Niño | Interruptor, demo |
| `mesVisible` | Mes `"AAAA-MM"` hasta el que se dibuja; `null` = serie completa | Control de tiempo, demo |
| `reproduciendo` | Si el control de tiempo avanza solo | Botón Reproducir, demo |
| `destino` | Celda del otro extremo de la línea, o `null` | Primera línea de efecto opuesto (automático), toque en otra línea, demo |
| `filtroFeed` | Pestaña del feed: `fuertes` \| `opuestas` \| `ocultas` | Pestañas de ScanMap |
| `demo` | Demo en curso y paso, o `null` | Recorrido guiado |
| `indice` *(añadido)* | `ONI` (por defecto) o `NINO12` | Selector de índice (solo si B3 lo habilita) |
| `mosaicoVisible` *(añadido)* | Si se pinta el mosaico de ScanMap | Botón del mapa |

Reglas del store:
- Solo **acciones** (`seleccionarCelda`, `fijarVentana`, `alternarElNino`, `irAlMes`, `reproducir`, `detener`, `elegirDestino`, …) cambian el estado; los componentes no lo mutan.
- Cambiar `celda`, `variable`, `ventana` o `indice` **reinicia** `mesVisible`, `reproduciendo` y `destino`. Cambiar solo `variable` conserva la celda.
- `quitarElNino` **se conserva** al cambiar de celda (la demo lo necesita así).
- Cuando llega `teleconnect` y `destino` es `null`, se asigna la **primera línea de efecto opuesto**; si no hay, queda `null`.
- **El store no se persiste** (al abrir la app se empieza de cero). Lo que sí persiste es la caché de TanStack Query (sección 8).
- Un campo nuevo en el store lo aprueban **F1 y los otros dos del frontend** (el archivo es de F1 y lo revisan todos).
- El **layout** (teléfono vs. pantalla ancha) **no** va al store: sale de `useWindowDimensions()` en cada pantalla (sección 10).

## 8. Datos del servidor (TanStack Query, `queryClient.ts`) y modo sin red

| Consulta | Llave | Notas |
|---|---|---|
| Catálogo | `['variables']`, `['glosario']`, `['salud']` | Al arrancar. `salud` trae `ventana_fin`, `simulado`, `version_metodo` y el estado del escaneo. |
| Análisis | `['analyze', variable, lat, lon, inicio, fin, indice]` | Se dispara al elegir celda con ventana válida (≥ 10 años). |
| Teleconexión | `['teleconnect', variable, lat, lon]` | En paralelo con `analyze`. |
| Destino | `['analyze', variable, destino.lat, destino.lon, …]` | Misma consulta de análisis, sobre la celda de destino. |
| Periodos | `['periodos', variable, lat, lon, p1, p2]` | Solo al abrir "Antes y después". |
| Feed | `['feed', tipo, pagina]` | Paginado de 20. |
| Mosaico | `['layer', variable]` | Solo cuando `mosaicoVisible`. |
| Demo | `['demo', id]` | Al abrir la demo. |

- `staleTime: Infinity` y `gcTime` largo: los datos de años cerrados no cambian, así que **volver a una celda no repite la llamada**. Excepción: `feed` y `salud` cuando `escaneo.estado == "en_curso"` (reconsulta cada cierto tiempo).
- **Persistencia:** la caché se guarda en **AsyncStorage** (`PersistQueryClientProvider` con el persistidor de AsyncStorage de TanStack Query), con `buster = salud.version_metodo` para descartar lo guardado cuando el backend cambie un cálculo. Así, volver a abrir la app no repite llamadas. *(En web también funciona; AsyncStorage usa el almacenamiento del navegador y puede venir vacío: la app debe funcionar igual sin él.)*
- Errores: `power_lento` **no se reintenta** (se muestra el mensaje y la oferta de la celda cercana); los errores de red se reintentan una vez.
- Mientras llega una celda nueva se muestra un **esqueleto**, nunca los datos de la celda anterior bajo la etiqueta de la nueva.
- Las llamadas pasan por **un solo cliente** (`shared/api/`) que antepone `EXPO_PUBLIC_API_URL` y `/api/v1`, usa `AbortController` con un tiempo máximo (~12 s: POWER en vivo espera 8 s), valida el cuerpo de error estándar y lo convierte en un objeto de error con `codigo`, `mensaje` y `celda_cercana`.

### Modo sin red (demos empaquetadas)

El backend genera las respuestas completas de las demos (`analyze` con ventana por defecto e índice ONI, `teleconnect`, `compare-periods` y `demos/{id}`) en `backend/data/demo/respuestas/`; `npm run demo:copiar` las copia a **`assets/demo/`**, que va **dentro de la app** y **en Git**. Tienen **la misma forma** que las respuestas de la API (se validan con los mismos tipos).

- El cliente tiene dos fuentes: `api` y `empaquetada`. Si una llamada falla por **red** (no por un error del contrato) y la consulta **corresponde a un lugar de las demos**, el cliente responde con la respuesta empaquetada y la interfaz muestra la banda **"Sin conexión · mostrando la demo guardada en la app"**. Para cualquier otra celda, el error de red se muestra como error.
- Además, un botón en el Inicio ("Usar demo sin conexión") fuerza la fuente `empaquetada` (sirve para el ensayo de las horas 44–48 y si falla la red de la sede).
- **Nunca mezcles** datos empaquetados con datos de la API en una misma celda, y **nunca los presentes como actuales**: llevan la fecha de descarga que ya traen en `descarga`.
- Si `assets/demo/` está vacío (el backend aún no las generó), la app lo dice y sigue funcionando con la API.

## 9. El mapa del Pacífico (`features/map`, `features/teleconnection-lines`, F1)

**Es el detalle que rompe la demo si se olvida:** Piura está en 80°O (−80°) e Indonesia en 116°E. En un mapa centrado en Greenwich, la línea recta entre ambas cruza África. **El mapa se centra en el Pacífico y todo lo que se dibuja como *punto* usa longitudes de 0 a 360**, así la línea cruza el Pacífico, que es por donde viaja el fenómeno.

**Por qué un mapa propio en SVG** (decisión V2, no la reviertas sin hablar con el humano): Leaflet es de navegador; `react-native-maps` usa los mapas nativos de Apple y de Google (en Android hace falta una clave de Google) y no tiene equivalente directo en la web; MapLibre/Mapbox son código nativo que no corre en Expo Go; una WebView con Leaflet son dos mundos de JavaScript; Skia tiene reportes contradictorios sobre Expo Go. **`react-native-svg` funciona igual en iOS, Android y web, sin red, sin claves y en Expo Go.**

- **Proyección:** equirrectangular. `x = (lon360 − vista.lonMin) / (vista.lonMax − vista.lonMin) · ancho`, `y = (vista.latMax − lat) / (vista.latMax − vista.latMin) · alto`. Vista inicial (**valores de partida; ajústalos probando que se vean Piura, a ~280°, e Indonesia, a ~116°**): `lon 90–330`, `lat −40…40`. Límites del desplazamiento para que no se salga del mundo dibujado.
- **Contrato ↔ mapa:** la API habla en −180..180. Dos funciones y **un solo lugar** donde viven (`shared/geo.ts`): `lon360(lon) = ((lon % 360) + 360) % 360` para **dibujar puntos** (celdas, líneas, marcadores), y `lonNormal(lon) = ((lon + 180) % 360 + 360) % 360 − 180` para **enviar** al servidor lo que devuelve un toque. Nunca hagas esta conversión en otro sitio.
- **Costas (`assets/geo/tierra.json`, Natural Earth 110m, dominio público):** **NO conviertas los polígonos con `lon360`.** Los que cruzan Greenwich (Europa, África) quedarían con vértices en 359° y 1°, y dibujarían una raya de lado a lado. En cambio, **proyecta los polígonos con su longitud original (−180..180) y dibújalos dos veces: con desplazamiento 0 y con desplazamiento +360°**. Así Asia y Oceanía (desplazamiento 0) y las Américas (+360°) quedan continuas en la vista 90–330. Convierte el GeoJSON a trazados SVG **una vez** (`useMemo` o un script en `scripts/`) y no lo recalcules en cada gesto.
- **Clic = celda:** el toque se cuantiza a la malla de 0.5° (`0.5·round(x/0.5)`, en `shared/geo.ts`) **antes** de ir al store, y el mapa dibuja el **rectángulo** de la celda (no un punto). **El servidor es la autoridad:** si la `celda` de la respuesta difiere de la que calculó el dispositivo (por ejemplo en un empate exacto `x.25`, donde el redondeo de JavaScript y el de Python no coinciden), se dibuja la de la respuesta. Si B2 encuentra que la malla real de POWER está desfasada, el rectángulo sigue lo que diga B2.
- **El rectángulo de una celda de 0.5° cabe en menos de un píxel a la escala inicial.** Dibújalo con un **tamaño visual mínimo de ~12 px**, centrado en la celda y con borde de 2 px. Es una ayuda visual: los datos siguen siendo de la celda de 0.5°.
- **Mosaico de ScanMap:** 4235 celdas **agrupadas por color en pocos `<Path>`** (uno por clase de veredicto × signo de la pendiente, más uno apagado para "sin hallazgo"), nunca 4235 elementos. Cada celda es un `M x y h w v h h −w z` dentro del `d` de su grupo. Opacidad **por grupo**, no por celda. Leyenda en texto. Se activa con un botón; el mosaico es lo cuarto que se recorta (sección 18).
- **Gestos (diseño propuesto, F1 lo valida en la hora 14):** `react-native-gesture-handler` (`Gesture.Pan`, `Gesture.Pinch`, `Gesture.Tap`) y `react-native-reanimated`. Durante el gesto se transforma el contenedor del SVG (barato); **al soltar se confirma la vista nueva y se vuelve a dibujar nítido**. En web, la rueda del ratón hace zoom. **Siempre hay alternativas sin gestos:** botones **＋ / −** y un botón de "Restablecer vista" (accesibilidad y teléfonos con un dedo).
- **Accesos directos "Lugares":** Piura, Borneo (Indonesia) y el norte de Australia (los de las demos). Centran la vista; no cambian la celda elegida.
- **Rendimiento:** mide el mapa con el mosaico completo en **un Android de gama baja** (o el emulador más modesto) **antes de la hora 14**. Si no alcanza: menos detalle de costas, mosaico más agrupado o **mosaico recortado** (queda el feed en lista). Dilo al humano, no lo escondas.
- **Atribución:** las costas son de Natural Earth (dominio público; no exige atribución, pero se cita en los créditos del glosario). Ya no se usan teselas de OpenStreetMap.
- **Líneas causa → consecuencia** (de la celda de origen a cada `linea`):
  - `opuesto`: **continua, roja**. `mismo`: **punteada**. La forma (continua/punteada) es la señal; el color refuerza. Se dibujan como un **arco suave** (curva) entre los dos puntos en el espacio `lon360`, así cruzan el Pacífico.
  - Con `mesVisible = null` (control detenido) las líneas se ven siempre (opacidad ~0.8). Al reproducir, cada línea **se enciende** (opacidad 1, trazo más grueso) **solo en los meses de `meses_coincidencia`** y queda **tenue** (≈ 0.15) en los demás.
  - **Al tocar** una línea (en web, también al pasar el cursor): "Efecto opuesto · r = −0.80 · 14 800 km · 23 meses a la vez" (todo viene de la respuesta; en el teléfono se muestra en una franja fija, no en un tooltip).
  - **Zona táctil:** cada línea lleva un trazo transparente más ancho (≥ 24 px) encima para poder tocarla. Tocar la línea o su círculo → `elegirDestino` (el panel de consecuencia pasa a mostrar esa región).
  - **Alternativa accesible:** junto al mapa (o en la hoja inferior), una **lista en texto** de las líneas (tipo, destino, r, distancia), con `accessibilityRole="button"`; activarla hace lo mismo que tocar la línea. Es la forma en que un lector de pantalla usa las líneas.
  - Redacción fija: **"ocurren a la vez y ambos responden a El Niño"**. Nunca "uno causa el otro".
  - Sin líneas: muestra `mensaje_vacio`. No es un error: es un resultado.

## 10. Las features, una por una

**Diseño adaptable (`useWindowDimensions`):** `ancho < 768` = **teléfono** (mapa arriba y una **hoja inferior** deslizable con tarjeta de veredicto, panel y control de tiempo); `768–1023` = **tableta** (hoja más alta o dos columnas); `≥ 1024` = **web/laptop** (mapa, veredicto y feed lado a lado, panel y control de tiempo debajo). **Prioridad de pantallas (decisión V8, el humano puede cambiarla): el teléfono es la pantalla principal; la web en laptop o proyector se usa para presentar.** Ensaya **las dos** antes de la hora 36. La hoja inferior es **propia** (una vista animada con 2–3 alturas); no agregues una librería de hojas sin avisar.

**`variable-picker` (F1).** Tarjetas de las 5 variables (de `/variables`) con nombre cotidiano, definición simple, unidad y fuente. Selector de ventana (años inicial y final, de 1981 a `ventana_fin`), por defecto **todo el registro**. Selector de índice (ONI; Niño 1+2 solo si el backend lo ofrece, y se avisa que empieza en 1982). Ventana de **menos de 10 años: no se envía** y se explica por qué ("Elige al menos 10 años. Con menos, el ruido de un año a otro impide ver tendencias."). Entre 10 y 19 años se envía y el aviso de potencia baja sale en la tarjeta.

**`series-charts` (F2) — panel Causa · Consecuencia · Realidad.** Tres gráficos apilados **con el mismo eje de tiempo**, sincronizados con `mesVisible`, hechos con **un solo componente propio, `GraficoSerie`** (`react-native-svg` + `d3-scale` para los ejes y `d3-shape` `line()` con `.defined(v => v != null)` para que los **`null` sean huecos, no ceros**):
- *Causa:* el índice (ONI o Niño 1+2) con **franjas rojas en los meses de El Niño** y las de La Niña (con trama además de color); líneas de referencia en ±0.5. Usa `fase` de la respuesta.
- *Consecuencia:* `serie_z` de la celda y de `destino` superpuestas, para ver que se mueven en espejo; sombreado en los meses de coincidencia de la línea elegida. La serie del destino sale del `analyze` del destino.
- *Realidad:* la serie **original o sin El Niño** según `quitarElNino` (`serie_original` / `serie_sin_el_nino`) y su **recta de tendencia** (`recta`), con el veredicto al lado. Los meses inusuales (`meses_inusuales`) van marcados con punto y su fase de El Niño.
- Cada gráfico muestra **unidad**, y el panel muestra fuente, celda y periodo. **Sin animaciones de entrada mientras se reproduce.**
- **Lectura con el dedo:** en el teléfono no hay cursor. Al tocar o arrastrar sobre un gráfico, una **línea vertical y una franja fija** muestran fecha, valor, unidad y fase; la posición se comparte entre los tres gráficos (un contexto de React, **no** el store). En web, lo mismo con el cursor.
- Cada gráfico tiene un **resumen en texto** para lectores de pantalla (título + qué muestra + fuente).

**`enso-toggle` (F2).** Interruptor **"Quitar El Niño"** (`Pressable` o `Switch` con `accessibilityRole="switch"` y `accessibilityState={{ checked }}`; en web, teclado con Espacio/Enter). Cambia en el acto el gráfico y el veredicto, **sin red**. Debajo, una línea que explica qué hace: "Quita la parte de la serie que explica El Niño, con X meses de retraso" (X = `vinculo_el_nino.rezago_meses`). Es **el momento central de la demo**: el usuario ve una tendencia alarmante, quita El Niño y el veredicto cambia. Cuida que el cambio se note (transición breve y clara; respeta "reducir movimiento").

**`time-comparator` (F2).**
- *Reproducir:* botón Reproducir/Pausa y una **barra de tiempo propia** (con gestos) con `accessibilityRole="adjustable"` y acciones de aumentar/disminuir. Recorre toda la serie en **~30 s** con `requestAnimationFrame` (el avance depende del **tiempo transcurrido**, no de los cuadros). **Actualiza `mesVisible` solo cuando cambia el mes** (no en cada cuadro). Al llegar al final se detiene y deja `mesVisible = null`. No recalcula nada.
- *Antes y después:* dos periodos (por defecto 1981–2001 y 2003 → fin), editable; llama a `compare-periods` y muestra el promedio y la diferencia **de la serie original y de la sin El Niño** y el conteo de meses inusuales (cuántos en El Niño). Texto fijo: "Comparación descriptiva: la significancia la da la tendencia." Si la diferencia sin El Niño conserva signo y tamaño, se dice que no se debe a que un periodo tuvo más Niños.
- *Meses inusuales:* marcados en el gráfico con su fase.

**`verdict-card` (F3).**
- Con `quitarElNino = false`: **"Tendencia aparente"**, que se lee de `tendencia_original` ("Parece que sube / baja" si es significativa; "Sin tendencia aparente" si no).
- Con `quitarElNino = true`: la **insignia de cuatro estados** (`veredicto.estado`) con su explicación, la dirección y `tendencia_sin_el_nino`.
- Siempre: pendiente **por década** con su **intervalo de 95 %** y **unidad**; `cambio_pct_decada` solo si no es `null`; p-valor (con "corregido por muchas pruebas" cuando `origen = "escaneo"`); vínculo con El Niño ("sigue al índice con 3 meses de retraso, r = 0.62", marcada **indicativa** si lo es); **avisos** (`avisos[].texto`: colinealidad, potencia baja, respuesta no lineal, Niño costero…); la **fuente** en una línea; y la insignia **"análisis individual"** cuando `origen = "individual"`.
- Textos de los estados (en español sencillo): **Cambio robusto** — "La tendencia sigue ahí aunque se quite El Niño." · **Sensible a El Niño** — "Los eventos de El Niño explican la tendencia que parecía haber." · **Cambio oculto** — "El Niño tapaba una tendencia real." · **Sin tendencia detectable** — "Con estos datos no se ve un cambio. Hace falta un registro más largo." (es un hallazgo válido, no un fallo).
- El veredicto se distingue por **texto + icono + forma**; el color solo refuerza. El cambio de veredicto se **anuncia** a los lectores de pantalla (`AccessibilityInfo.announceForAccessibility`).

**`scan-feed` (F3).** Botón **"Escanear"**. Pestañas *Señales fuertes*, *Señales opuestas*, *Cambios ocultos* (`filtroFeed`). Tarjetas en un `FlatList` (de `scan/feed`, 20 por página, carga la siguiente al llegar al final): el **titular tal como llega** (viene de plantilla; no lo reescribas), variable, celda, veredicto, pendiente con intervalo. Tocar una tarjeta: `seleccionarCelda` (+ `variable`; en "opuestas", además el destino = la celda `pareja`) y se pasa a la vista de detalle. Si `escaneo.estado = "en_curso"`: **"Escaneo en curso"** con el avance (`celdas_listas` de `celdas_total`), nunca una lista vacía.

**`guided-tours` (F3).** Ver sección 12.

**`glossary` (F3).** **Página** (`app/glosario.tsx`) con el vocabulario (de `/glosario`); los términos de la tarjeta de veredicto **enlazan** a ella. Los *tooltips* en todos los paneles se recortan si falta tiempo.

**Pantallas (`app/`).** *Inicio* (qué es VeraScope en una frase, acceso a las dos demos, botones **Investigar** y **Escanear**, y "Usar demo sin conexión"; frase sugerida: "Descubre si un cambio en el clima es una tendencia real o solo El Niño"), *Espacio de trabajo* (mapa centrado en el Pacífico, tarjeta de veredicto, feed de ScanMap y panel Causa · Consecuencia · Realidad con el control de tiempo) y *Glosario*. En el teléfono, el feed es una lista a pantalla completa con pestañas; en web, una columna junto al mapa. Barra de estado que sigue el modo (`expo-status-bar`: `light` en modo oscuro, `dark` en modo claro) y **áreas seguras** (`react-native-safe-area-context`, que viene con la plantilla de Expo Router).

Recorrido de **Investigar** (3 pasos): **1. Variable** → **2. Lugar y ventana** (toque en el mapa) → **3. Veredicto**. Los dos caminos (Investigar y Escanear) terminan en **la misma vista de detalle**.

## 11. Estados de la interfaz

| Situación | Qué muestra |
|---|---|
| Ventana menor a 10 años | Bloquea el envío y explica por qué el ruido entre años impide detectar tendencias |
| Ventana de 10 a 19 años | Envía y muestra el aviso de potencia baja |
| Cargando una celda nueva | Esqueleto en tarjeta y gráficos; el mapa sigue usable |
| POWER tarda más de 8 s (`power_lento`) | Mensaje claro y **botón para usar la celda en caché más cercana** (`celda_cercana`) |
| Celda sobre el océano con humedad del suelo (`sin_datos_tierra`) | Explica que esa variable no aplica sobre el mar y sugiere lluvia o temperatura |
| Celda fuera de la rejilla de ScanMap | Rotula "análisis individual"; las líneas salen de la celda de ScanMap más cercana e indican la distancia |
| Escaneo aún en curso | Feed: "Escaneo en curso" con avance, en lugar de una lista vacía. Líneas y mosaico (error 503 `escaneo_en_curso`): "Las líneas y el mosaico aparecen cuando termine el escaneo"; el análisis de la celda sigue funcionando |
| Sin líneas significativas | Texto de `mensaje_vacio`; también es un resultado |
| Sin tendencia detectable | Se presenta como hallazgo válido, con el texto del estado |
| Error de red / servidor | Qué pasó y qué hacer (reintentar); no mostrar trazas. Si la consulta es de un lugar de las demos, se usa la **demo empaquetada** con su banda "Sin conexión" |
| Sin `assets/demo/` y sin red | Explica que la demo sin conexión aún no está incluida y que hace falta conexión |
| Modo simulado (`salud.simulado`) | Banda visible **"Datos simulados"** en toda la interfaz |

Los mensajes **explican qué pasó y cómo seguir**, sin disculparse y sin jerga. Los textos de error de la API ya vienen en español: muéstralos tal cual.

## 12. Demos guiadas (`features/guided-tours`, F3)

Dos recorridos precargados que se entienden en **menos de tres minutos**. **Cada paso fija el estado por código** (acciones del contrato: `seleccionar_celda`, `quitar_el_nino`, `reproducir`, `detener`, `ir_a_destino`, `fijar_ventana`, `mostrar_periodos`…), de modo que la demo **no depende de que alguien toque el lugar exacto**, y solo usa celdas que ya están en caché o, **sin red, las respuestas empaquetadas** en `assets/demo/`. Los guiones viven en el backend (`demos/{id}`) y también van empaquetados; el frontend los ejecuta con controles Anterior / Siguiente / Salir, también accesibles (lector de pantalla y teclado en web).

**Demo 1 · "El efecto espejo de El Niño"** — lluvia (`PRECTOTCORR`), mensual, costa de Piura. *(Es núcleo: nunca se recorta.)*

| Paso | Lo que dice la pantalla | Lo que hace la plataforma |
|---|---|---|
| 1 | "Esta es Piura. Mira la lluvia: hay meses que parecen catastróficos." | Selecciona la celda de Piura con el interruptor apagado; se marcan los meses inusuales con su fase de El Niño. |
| 2 | "Reproduce el tiempo: la línea se enciende cuando Piura y el otro lado del Pacífico sufren a la vez." | Inicia la reproducción; las líneas ya llegaron con la celda. |
| 3 | "La línea apunta sola a donde falta el agua." | Detiene la reproducción y muestra el panel de consecuencia con las dos regiones en espejo. |
| 4 | "Quita El Niño: ¿queda una tendencia de fondo?" | Activa el interruptor; el veredicto cambia **en el dispositivo, sin red**. |

*Objetivo:* mostrar que un mismo fenómeno produce lluvias extremas en Sudamérica y sequía en Oceanía **al mismo tiempo**, y que esos picos no son una tendencia. Si la respuesta de Piura no es lineal, la tarjeta lo dice.

**Demo 2 · "¿Señal real o ruido climático?"** — temperatura (`T2M`), mensual, una celda elegida por el equipo tras revisar los resultados reales.

| Paso | Lo que dice la pantalla | Lo que hace la plataforma |
|---|---|---|
| 1 | "Con solo 10 años, ¿la temperatura cambió?" | Analiza una ventana de 10 años y muestra el aviso de potencia. |
| 2 | "Ahora con todo el registro desde 1981." | Analiza la ventana completa y compara el veredicto. |
| 3 | "Quita El Niño: lo que queda es el cambio de fondo." | Activa el interruptor y muestra la tendencia sin El Niño. |
| 4 | "Compara dos periodos." | Muestra la diferencia entre 1981–2001 y 2003 en adelante, original y sin El Niño. |

*Objetivo:* enseñar que un resultado no significativo con pocos años es científicamente válido, y que las ciencias de la Tierra necesitan registros largos. Solo escala mensual. *(El paso 1 usa una ventana de 10 años: para que funcione sin red, el backend debe empaquetar **también esa respuesta**; pídeselo a B1.)*

**Antes de la hora 36:** con datos reales, **verifica hacia dónde apuntan las líneas y qué veredicto sale**, y ajusta **el guion a lo que muestran los datos** (con B3 y F3), no al revés; después **vuelve a pedir las respuestas empaquetadas** al backend. El **ensayo de las horas 44–48 se hace con la red desconectada**, con la app en el teléfono y en el navegador de la laptop, usando las respuestas empaquetadas.

## 13. Lenguaje visual, textos y accesibilidad

### Dirección visual elegida (paleta VeraScope, 15 nov 2026; reemplaza al tema solo oscuro anterior)

Interfaz sobria con **modo claro y modo oscuro**, que el usuario cambia con el botón de sol/luna (`shared/components/BotonModo.tsx`, en el encabezado y en el Inicio). Mientras no elija, la app sigue el modo del teléfono o del navegador (`app.json` → `userInterfaceStyle: "automatic"`); lo que elige se guarda en AsyncStorage (`verascope.modo`). **Muy pocos colores, cada uno con un significado fijo, igual en los dos modos.** Logo y hoja de marca: `VeraScope-logo-mision.zip` y `VeraScope-hoja-de-marca-mision.png` (pídelos al humano; no redibujes el logo).

Los colores viven en **`src/shared/tema.ts`** (`paletas.claro` y `paletas.oscuro`, con los mismos tokens; **no hay Tailwind**). Los componentes **nunca** importan un color suelto: leen el modo con `useTema()` y arman sus estilos con `useEstilos(crearEstilos)` (`src/shared/useTema.ts`), donde `const crearEstilos = (colores: Colores) => StyleSheet.create({...})` se declara fuera del componente. El proveedor (`src/shared/ProveedorTema.tsx`) solo se monta en `app/_layout.tsx`; sin proveedor (pruebas) se usa el modo oscuro. El modo **no va al store**.

**Significado de los colores (regla fundamental: el rojo no significa "importante", significa "preocupante")**

| Color | Significa | Se usa en |
|---|---|---|
| Azul (`info`, `lluvia`) | Ciencia, información y datos | Gráficos, indicadores, enlaces, selección (celda elegida, opción elegida, interruptor y barra de tiempo activos), recta de tendencia, lluvia |
| Ámbar (`accion`, `sequia`) | Acción, exploración y descubrimiento | Botones principales ("Investigar", "Escanear"), sequía, borde de la banda "Datos simulados" |
| Rojo (`nino`) | Gravedad, preocupación y riesgo | **Solo** El Niño (franjas, línea de efecto opuesto, *sensible a El Niño*) y alertas críticas. Ningún otro token puede valer rojo (hay prueba) |
| Blanco | Claridad y legibilidad | Fondos, superficies y texto |
| Gris y negro | Estructura y jerarquía | Fondos, bordes, texto secundario, La Niña (gris con trama) |

**Tokens (`Colores`)**

| Token | Modo claro | Modo oscuro | Uso |
|---|---|---|---|
| `fondo` | Space White `#F7F7F5` | Obsidian `#0B0D12` | Fondo principal |
| `superficie` | Pure White `#FFFFFF` | Deep Surface `#111820` | Tarjetas, paneles, ventanas |
| `superficieFuerte` | Atmosphere Gray `#E6E8EB` | Ocean Panel `#17364F` | Fondos secundarios (botón secundario, rieles, esqueletos) |
| `borde` | Atmosphere Gray `#E6E8EB` | Ocean Panel `#17364F` | Bordes y divisores |
| `texto` | Obsidian `#0B0D12` | Star White `#F5F7F8` | Texto principal y títulos |
| `textoSuave` | Orbit Gray `#8B929A` | Atmospheric Gray `#AAB3BC` | Texto secundario y etiquetas |
| `institucional` | Ocean Deep `#102B42` | Star White `#F5F7F8` | Encabezados, navegación e iconos |
| `info` | Signal Blue `#38A9E0` | Signal Blue Light `#4AB7E8` | Datos, enlaces, selección, estados activos |
| `accion` | Discovery Amber `#F5A62D` | Discovery Amber `#FFB23D` | Botones principales |
| `textoSobreAccion` | Obsidian `#0B0D12` | Obsidian `#0B0D12` | Texto sobre `accion` |
| `nino` | ENSO Red `#E3483F` | ENSO Red Light `#F0524A` | El Niño y alertas críticas |
| `lluvia` | Signal Blue `#38A9E0` | Signal Blue Light `#4AB7E8` | Lluvia / más agua (no es La Niña) |
| `sequia` | Discovery Amber `#F5A62D` | Discovery Amber `#FFB23D` | Sequía / menos agua |
| `nina` | Orbit Gray `#8B929A` | Atmospheric Gray `#AAB3BC` | La Niña (siempre con trama y etiqueta) |
| `foco` | Obsidian `#0B0D12` | Star White `#F5F7F8` | Contorno de foco (teclado en web) |
| `aviso` | Pure White `#FFFFFF` | Deep Surface `#111820` | Fondo de la banda "Datos simulados" |
| `mapaOceano` | Pure White `#FFFFFF` | Ocean Panel `#17364F` | Océano del mapa |
| `mapaTierra` | Atmosphere Gray `#E6E8EB` | Deep Surface `#111820` | Tierra del mapa |

- **Contraste en modo claro (pendiente de decidir):** `textoSuave` (Orbit Gray) sobre `fondo` da 2.9:1 y `info` (Signal Blue) sobre `fondo` da 2.5:1, por debajo del mínimo de accesibilidad (4.5:1 para texto, 3:1 para líneas y controles). En modo oscuro todo pasa de 5:1. Si se oscurecen, se cambia el valor en `tema.ts`, no en cada componente.

- **Tipografía:** **Inter**, con **`@expo-google-fonts/inter` y `expo-font`**, incluida en la app (no se descarga). Mantén la pantalla de arranque (`expo-splash-screen`) hasta que cargue la fuente. Números y tablas con **`fontVariant: ['tabular-nums']`**. Texto base ≥ 16; escala tipográfica corta y consistente; etiquetas en minúsculas normales (**sin MAYÚSCULAS SOSTENIDAS**).
- **Una sola cosa memorable:** la línea que se enciende cruzando el Pacífico. El resto de la interfaz es discreta; no agregues adornos, degradados decorativos ni animaciones que no respondan a una acción del usuario.
- **Decisiones de diseño que siguen abiertas** (propónlas en el PR con captura de pantalla; las aprueba otra persona del frontend y se anotan aquí): color de la línea de **mismo efecto** (mientras tanto, **punteada en `texto`**); paleta de la **temperatura** en el mosaico (escala propia en ámbar, dejando el rojo solo para El Niño); colores de la insignia de veredicto (por ahora neutros, con el rojo solo para *sensible a El Niño*). **La Niña** queda en gris (`nina`) **con trama de rayas y etiqueta "La Niña"**, nunca azul saturado ni rojo.
- **Proyector y teléfono al sol:** ensaya la interfaz **en los dos modos, en un proyector o pantalla grande y en un teléfono real a plena luz** antes de la hora 36. Si un modo se ve lavado, sube el contraste en los tokens de `tema.ts`, no en cada componente.
- **Unidades:** en React Native el tamaño es independiente de la densidad de la pantalla (no se escribe `px`); usa los espacios y tamaños del tema en vez de números sueltos.

### Textos (todo en español, sencillo, sin jerga)

- Nombra las cosas **como las entiende el usuario** ("Quitar El Niño", "Tendencia aparente"), no como está construido el sistema ("serie residual", "regresión conjunta"). La jerga va al glosario, no a la pantalla.
- Una acción se llama **igual en todo el flujo** (si el botón dice "Escanear", el estado dice "Escaneo en curso").
- Verbos claros en los botones ("Reproducir", "Quitar El Niño", "Usar la celda cercana"); en infinitivo o imperativo, siempre el mismo.
- Los vacíos **invitan a actuar** ("Toca el mapa para elegir un lugar"); los errores **explican qué pasó y cómo seguir**, sin disculpas ni dramatismo. *(En web puede decir "Haz clic"; usa "Toca" en la app y "Elige" cuando valga para las dos.)*
- **Nada de números inventados** ni textos que suenen más seguros de lo que dicen los datos. Los titulares del feed y los textos de aviso **vienen de la API**; no los reescribas. Formatea números con **un solo formateador** (`shared/format.ts`, `Intl.NumberFormat('es-PE')`) para que todo se vea igual; **siempre con unidad**. *(Si `Intl` en el motor de JavaScript del teléfono no da el formato esperado, resuélvelo dentro de `format.ts` y avisa; no lo resuelvas en cada pantalla.)*
- Formato de una fuente: **"MERRA-2 vía NASA POWER · celda −5.0°, −80.5° · 1981–2025 · descargado 2026-11-14 · Índice: ONI, NOAA CPC"** (todo viene de la respuesta). La insignia "análisis individual", el rótulo "Datos simulados" y la banda "Sin conexión · mostrando la demo guardada en la app" son obligatorios cuando corresponden.
- Redacciones **prohibidas**: "El Niño causó…", "uno provoca el otro", "esto prueba el calentamiento global", "sin resultados" para un vacío legítimo. Redacción **correcta** para una línea: "ocurren a la vez y ambos responden a El Niño".

### Accesibilidad (no se negocia)

- **El color nunca es la única señal:** hay trazo (continua/punteada), forma, trama y texto. Los veredictos llevan **texto**.
- **Lectores de pantalla (VoiceOver y TalkBack) y web:** todo control lleva `accessibilityRole`, `accessibilityLabel` en español y, si corresponde, `accessibilityState` (`checked`, `selected`, `disabled`); también puedes usar sus equivalentes `role` y `aria-*`, que React Native for Web traduce al navegador. El interruptor se anuncia como interruptor con su estado. **El cambio de veredicto y el estado del escaneo se anuncian** (`accessibilityLiveRegion="polite"` en Android y `AccessibilityInfo.announceForAccessibility`).
- **Zonas táctiles de al menos 44 × 44** (usa `hitSlop` si el dibujo es más pequeño). Texto base ≥ 16; etiquetas de gráficos ≥ 12.
- **Teclado en web:** interruptor, control de tiempo, pestañas, tarjetas del feed, pasos de las demos y lista de líneas se usan con teclado, con **foco visible** siempre.
- **Contraste** suficiente (texto normal ≥ 4.5:1; líneas y controles ≥ 3:1) sobre el fondo **de cada modo**.
- **Reducir movimiento:** consulta `AccessibilityInfo.isReduceMotionEnabled()` (en web, `prefers-reduced-motion`): sin transiciones decorativas. La reproducción del tiempo es una acción del usuario y sigue funcionando.
- **Los gráficos y el mapa tienen alternativa en texto** (resumen de cada gráfico, lista de líneas, botones de zoom).
- Unidades **siempre visibles**.

## 14. Pruebas (Jest + Testing Library para React Native, sin red)

Las pruebas usan **respuestas de ejemplo** (`src/shared/api/__fixtures__/`, copiadas de `backend/app/catalogo/simulado/`) y un `fetch` simulado (`global.fetch = jest.fn()`). Los temporizadores se controlan con `jest.useFakeTimers()`. **El CI exige `npx tsc --noEmit`, `npm run test` y `npx expo export -p web` en verde** (más las pruebas del motor del backend).

| Prueba | Qué comprueba |
|---|---|
| Geografía | `lon360(-80) = 280`, `lon360(116) = 116`, `lonNormal(280) = -80`, bordes ±180; cuantización `(-5.12, -80.37) → (-5.0, -80.5)` |
| Costas | Los polígonos de `tierra.json` se proyectan **con su longitud original** y se dibujan con desplazamiento 0 y +360; ningún trazo une un lado del mapa con el otro (sin "rayas" por cruzar Greenwich) |
| Estado | Cambiar `celda`, `variable`, `ventana` o `indice` reinicia `mesVisible`, `reproduciendo` y `destino`; cambiar `variable` conserva la celda; `quitarElNino` se conserva al cambiar de celda |
| **Interruptor sin red** | Alternar `quitarElNino` 10 veces **no** llama a `fetch`; cambia la serie dibujada y el veredicto mostrado |
| **Reproducción sin red** | Con temporizadores falsos: recorre la serie completa en ~30 s, no llama a `fetch`, actualiza `mesVisible` solo al cambiar de mes y al final deja `mesVisible = null` |
| Una llamada por análisis | Elegir una celda produce exactamente `analyze` + `teleconnect` (y, después, `analyze` del destino); volver a esa celda **no** produce llamadas |
| Veredicto | Con la respuesta de ejemplo: interruptor apagado muestra "Tendencia aparente"; encendido muestra el estado de cuatro valores y su texto. Un `sin_tendencia` se presenta como hallazgo |
| Líneas | Con `mesVisible` dentro de `meses_coincidencia` la línea tiene opacidad 1; fuera, ≈ 0.15; sin `mesVisible`, ≈ 0.8. Efecto opuesto = continua; mismo efecto = punteada |
| Mosaico | 4235 celdas generan **pocos** `Path` (uno por clase), no 4235 elementos |
| Ventana corta | Menos de 10 años **no** dispara la llamada y muestra la explicación |
| Errores | `power_lento` muestra el mensaje y el botón de la celda cercana; `sin_datos_tierra` muestra la explicación |
| **Modo sin red** | Si `fetch` falla por red y la celda es de una demo, se responde con `assets/demo/` y aparece la banda "Sin conexión"; para otra celda, aparece el error. No se mezclan datos de las dos fuentes |
| Demos | Ejecutar los pasos de la demo 1 sobre las respuestas de ejemplo deja el estado esperado en cada paso |
| Contrato | Los JSON de ejemplo y los de `assets/demo/` **compilan** contra los tipos generados (si el backend cambia un campo, `tsc` falla) |
| Accesibilidad | El interruptor tiene rol y estado; la lista de líneas es operable; el cambio de veredicto se anuncia (Testing Library para React Native consulta por rol y por etiqueta) |

**Humo manual antes de cada fusión a `main`:** `npx expo start` con la API simulada; correr la **demo 1 completa en el teléfono (Expo Go) y en el navegador** (`w`), con dedos y con teclado/ratón. **Humo de build:** `npx expo export -p web` y, desde la hora 14, un APK de prueba.

## 15. Qué hacer y qué no (resumen)

**Haz:**
- Empieza cada sesión leyendo la rama (`git branch --show-current`), `git status`, `git log -5 --oneline`, y corre `npx tsc --noEmit && npm run test`. La rama te dice qué feature y qué dueño.
- Desarrolla contra la **API simulada** hasta que el motor real esté listo; cuando salga un campo nuevo, regenera los tipos (`npm run tipos`).
- Instala librerías **con `npx expo install`** y comprueba `npx expo install --check`.
- Pregunta al humano **antes** de cambiar el store, un contrato, una regla de la sección 2 o la versión de Expo.
- Muestra los resultados **como llegan**; si algo se ve raro, es un dato que hay que discutir con backend, no algo que corregir en pantalla.
- Revisa cada pantalla en **teléfono, y en laptop o proyector**.
- Prueba en un **teléfono real** y en la **web** antes de cada fusión importante.

**No hagas:**
- **No calcules estadística en el dispositivo** (tendencias, p-valores, z, fases, porcentajes, veredictos). Ni "un pequeño promedio" para una lectura del gráfico.
- No llames a la red en el interruptor, en la reproducción, ni al cambiar de pestaña con datos ya cargados.
- No toques `backend/`. Si falta un campo o una ruta, detente: es un cambio de contrato.
- No uses la API de otra fuente (POWER, NOAA…) desde la app: todo pasa por `/api/v1`.
- **No uses librerías de navegador** (Leaflet, Recharts, Plotly, Tailwind, DOM, `localStorage`) ni agregues librerías (estado, UI, gráficos, mapas, animación) sin avisar. No uses WebGL ni Skia.
- **No cambies de SDK de Expo durante el evento** (ni "solo para probar") sin hablarlo con el humano.
- No dibujes puntos con longitudes −180..180 (la línea cruzaría África), ni conviertas con `lon360` los polígonos de las costas (dibujarían rayas), ni cambies a mapa centrado en Greenwich.
- No dejes una URL `http://` en un build de entrega: las apps nativas la bloquean.
- No pongas texto en inglés en la interfaz, ni tooltips del glosario en todos los paneles (se recortan primero).
- No inventes datos para "que se vea bien", ni dejes datos simulados sin la banda "Datos simulados", ni presentes datos empaquetados como actuales.
- No recortes del núcleo: interruptor, línea Piura → Indonesia/Australia, reproducción en el tiempo, demo 1.

## 16. Definición de "terminado" para un PR del frontend

- [ ] `npx tsc --noEmit`, `npm run test`, `npm run lint` y `npx expo export -p web` en verde.
- [ ] El interruptor y la reproducción **no** hacen peticiones (hay prueba).
- [ ] Textos en español sencillo; unidades, fuente, celda y periodo visibles; sin redacción causal.
- [ ] Funciona **en el teléfono y en la web**; con lector de pantalla (rol, etiqueta, estado) y, en web, con teclado y foco visible; sin depender solo del color.
- [ ] Probado con la API simulada **y**, desde la hora 20, con datos reales; estados de carga, vacío, error y **sin red** revisados (sección 11).
- [ ] Capturas de pantalla en el PR (teléfono y web; y, si cambia el mapa, la línea cruzando el Pacífico).
- [ ] Sin cambios al store o a los tipos sin la revisión de los otros dos del frontend; tipos regenerados si cambió el contrato.
- [ ] Sin dependencias nuevas sin aviso; `npx expo install --check` en verde.
- [ ] Revisado por otra persona del frontend. Este archivo actualizado si cambió una regla o un comando.

**Comprobaciones tempranas (horas 0–6):** que la app abra en **Expo Go en un teléfono real** con el SDK 58 · que el mapa con longitudes 0–360 dibuje la línea de Piura a Indonesia **cruzando el Pacífico** (con datos de ejemplo) y sin rayas en las costas · que los tipos se generen desde `/openapi.json` · que la tipografía y el mapa funcionen **sin internet** · que los dos modos (claro y oscuro) se lean en un proyector y en un teléfono · que `salud.simulado` active la banda "Datos simulados" · que la web exporte (`npx expo export -p web`). **Antes de la hora 14:** rendimiento del mosaico en un teléfono modesto, primer APK con EAS Build y la web desplegada.

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
  "celda": { "lat": -6.0, "lon": -80.0 },
  "pasos": [ { "n": 1, "texto": "Esta es Piura. Mira la lluvia: hay meses que parecen catastróficos.",
               "acciones": [ { "tipo": "seleccionar_celda", "lat": -6.0, "lon": -80.0 },
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
5. **Datos reales en Git solo como paquete.** Los datos van en **`backend/paquete-datos/verascope-datos-AAAAMMDD.tar.gz`** (un solo archivo, verificado con SHA-256) y cada uno los instala en `backend/data/` con `verascope-datos instalar` (ver README, «Datos»). Lo instalado en `backend/data/` (casillero, `tabla/`, resultados) **no se sube**: la API escribe en el casillero mientras corre. Excepciones: la instantánea de las demos en `backend/data/demo/` (incluidas las `respuestas/` para la app) y su copia en `frontend/assets/demo/`. Al publicar datos nuevos se borra el paquete viejo en el mismo PR (decisión del 15-nov-2026).
6. **Commits con prefijo:** `feat:`, `fix:`, `docs:`, `chore:` (y `test:` si solo cambian pruebas). Mensaje en español, en presente, corto. Si el cambio toca una regla estadística, cita su número (por ejemplo `fix: intervalo con varianza corregida (C8)`).
7. **No se hace `push --force` a `main`, ni se salta la revisión, ni se desactivan pruebas para que pase el CI.**
8. Si una tarea te obliga a salir de tu carpeta (`backend/` ↔ `frontend/`), **detente y avisa**: probablemente es un cambio de contrato.
9. **Ramas borradas: no se vuelven a crear.** El 15-nov-2026 se borraron `chore/base-frontend`, `fe/graficos-enso-v2`, `fe/tiempo-comparador-v2` y `fe/distribucion-v2`, porque su contenido ya está en `main` o en las ramas vigentes. Usa estas:

   | Si ibas a usar… | Usa |
   |---|---|
   | `fe/graficos-enso-v2` | `fe/graficos-enso` |
   | `fe/tiempo-comparador-v2` | `fe/tiempo-comparador` |
   | `fe/distribucion-v2` | `fe/distribucion` |
   | `chore/base-frontend` | `main` |

   No las crees ni hagas `push` de una copia local: el push vuelve a crear la rama en GitHub. Si todavía las tienes en tu máquina, ejecuta `git fetch --prune`, cámbiate a la rama vigente y borra la copia con `git branch -D <rama>`. **Agentes de IA:** antes de crear una rama, cambiarte a ella o hacer `push`, comprueba que no sea una de estas; si te la piden, avisa y usa la vigente.

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

- **Diseño del frontend:** la paleta VeraScope (15 nov 2026: modo claro y oscuro a elección del usuario; azul = datos, ámbar = acción, rojo = solo lo preocupante y El Niño; tipografía Inter) **reemplaza** al tema solo oscuro anterior y al azul para La Niña del informe técnico. Detalle en la sección de lenguaje visual del frontend.
- **App móvil y web (informe técnico v2):** el frontend es **una sola base de código con Expo** para iOS, Android y web. Si el humano prefiere **una web aparte con React** (compartiendo tipos, cliente y estado), es una decisión pendiente (tabla de abajo); mientras no se cambie, manda esta.
- **Fin de la ventana:** los informes hablan de 1981–2023 (516 meses, 43 años) porque estaban escritos con ese último año. **No lo fijes en el código**: la ventana termina en el último año completo de MERRA-2 (`VERASCOPE_FIN`, por defecto año actual − 1) y se confirma en las horas 0–6. Los "516 meses" y los "43 años" de los textos son ejemplos que cambian.
- **El prototipo (`verascope-codigo.zip`)** usa nombres viejos en inglés (`/series`, `/feed`, `raw`, `clean`, `p_adj`…). Sirve para ver ideas, **no para copiar nombres**: manda este contrato.

### Pendiente y sin verificar (no lo des por hecho)

| Tema | Qué falta | Quién |
|---|---|---|
| Entregables de la sede | Qué pide el evento y a qué hora cierra la entrega | Todos, antes del evento |
| Una base de código con Expo (adoptada) o web aparte con React | Confirmarlo con el humano | Todos; propone F1, hora 0 |
| Versión de Expo Go de las tiendas y SDK que se fija | **Hecho (15 nov):** la Expo Go de la tienda solo abre el SDK 58 → se fija el 58 | F1, hora 0 |
| Rendimiento del mapa SVG con el mosaico en un teléfono modesto | Medirlo; si no alcanza, se recorta el mosaico | F1, antes de la hora 14 |
| Primer APK con EAS Build y primera exportación web | Que salgan sin sorpresas de cuenta o de cola | F2, antes de la hora 14 |
| Cuenta de Apple Developer (TestFlight) o iOS solo con Expo Go y simulador | Decidirlo | Todos, antes del evento |
| Cuándo corre la descarga de las 4235 celdas | Desde la hora 8, como en el plan, o antes si las reglas de la sede lo permiten | B2 y todos, antes del evento |
| Colores de La Niña y de la línea de mismo efecto | Proponer y aprobar con captura de pantalla | F1 propone, otro del frontend aprueba, hora 14 |
| Último año completo de MERRA-2 en POWER | Confirmarlo con una consulta real; fija el fin de la ventana | B2, horas 0–6 |
| Latencia real de POWER | Medirla desde la sede con 20 celdas distintas **antes de prometer ninguna cifra** | B1, horas 0–6 |
| Alineación de la malla de 0.5° | Verificar con dos consultas vecinas que la cuantización `0.5·round(x/0.5)` cae en la misma celda que POWER | B2 |
| Humedad del suelo sobre el mar | Comprobar que POWER devuelve relleno (−999) y que la regla de descarte lo atrapa | B2 |
| Niño 1+2 para Piura | Decidir si entra como alternativa al ONI | B3, hora 20 |
| CO₂ de Mauna Loa | Solo si sobra tiempo, como franja de contexto | F2, hora 30 |
| Escorrentía de GLDAS (×8) y capa NDVI de AppEEARS | Confirmar convenciones con los servicios reales (solo afectan al preparador de datos y a fichas informativas de la demo 1) | Quien corra el preparador |
| Referencias bibliográficas | Verificarlas (se citaron de memoria) | Todos, antes de la entrega |
| Dirección real de las líneas y veredicto de la demo 1 | Con datos reales, **ajustar el guion a lo que muestran los datos**, no al revés | B3 + F3, antes de la hora 36 |
