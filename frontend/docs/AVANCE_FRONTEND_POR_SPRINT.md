# Avance del frontend por sprint · VeraScope (F1 · F2 · F3)

Seguimiento de las tareas del frontend según el *Plan de sprints (48 horas)*, los issues #1 y #9–#15,
`frontend/CLAUDE.md` y [`REGLAS_COLABORACION_IA.md`](REGLAS_COLABORACION_IA.md). Solo frontend: no cambia nada del
backend.

> ### ✅ Cómo se mantiene este archivo (obligatorio)
> **Cada vez que un miembro sube un cambio (push) o fusiona un PR, actualiza este archivo en ese mismo cambio:**
> 1. Marca la casilla: `- [ ]` → `- [x]`.
> 2. Cambia la marca de estado (🟡 → ✅) y borra el "**por avanzar**" de esa línea.
> 3. Al final de la línea anota **el PR y la hora del evento**, por ejemplo: `(#31, h 36)`.
> 4. Si algo se recorta, márcalo con `~~tachado~~` y ✂️.

**Roles:**
- **F1**: base, mapa, líneas, `store.ts`, `espacio.tsx`.
- **F2**: gráficos, interruptor de El Niño, reproducción, caché y distribución (APK y web).
- **F3**: veredicto, inicio, textos de estados, feed, demos y glosario.

**Revisión cruzada:** a F1 lo revisa F2, a F2 la revisa F3 y a F3 la revisa F1.

**Leyenda:**
- `- [x]` ✅ en `main`.
- `- [x]` 🟡 hecho en su rama: **por avanzar** que se fusione.
- `- [ ]` **por avanzar**: sin hacer.
- ✂️ recortado.

---

## 1. Dónde estamos (15 de noviembre, noche · `main` en `d4ad255`)

| | Estado |
|---|---|
| **Sprint en el que deberíamos estar** | **S4 → S5** (congelamiento en la hora 36; `release/demo` todavía no existe) |
| **Sprint en el que está el frontend** | **S3–S4**: en `main` están la base, el mapa con el selector y la tarjeta montada (F1, #47), el panel de gráficos con el interruptor (F2, #40), la **reproducción en el tiempo** (F2, #51) y la tarjeta de veredicto, el logo, los textos de estados y el inicio (F3, #33, #34, #35, #52). **Por avanzar:** las líneas (F1), las demos y el glosario (F3, PR #53 y #54 abiertos) y el APK y la web (F2, esperan la URL fija) |
| **Backend** | ✅ `analyze` real con caché y precalentamiento (#30), avisos de Niño costero (#29, #31), demo de Piura en la celda (−6, −80) (#32), `teleconnect` y `compare-periods` con datos reales (#41, #42) y **paquete de datos reales en el repo** (#43, `backend/paquete-datos/verascope-datos-20261115.tar.gz`). Rutas del feed y del mosaico con datos reales (#45) y `/variables` y `/glosario` desde `catalogo/` (#48). **URL HTTPS:** hoy solo hay un túnel temporal de Cloudflare (cambia al reiniciarse; `backend/docs/despliegue-cloudflare-tunnel.md`); el equipo pasa a **Render con URL fija** (configuración en #50, URL todavía no publicada). **Por avanzar:** la URL fija de Render y las respuestas de demo para la app sin red (#8). `/salud` dice escaneo `en_curso` aunque el escaneo esté listo (error conocido) |
| **Verificación de `main`** | `npx tsc --noEmit`, `npm run lint` y `npm run test` en verde (14 archivos, 92 pruebas). Con los datos reales, `analyze` de Piura (−6, −80) devuelve 540 meses y veredicto `sin_tendencia` (origen `escaneo`) |

### ⚠️ Lo que hay que resolver ya

- ~~**La tarjeta de veredicto está en `main` pero no se ve.**~~ ✅ `espacio.tsx` monta `TarjetaVeredicto` y el
  interruptor cambia el veredicto sin red (#47).
- ~~**Los textos de estados no los usa ninguna pantalla.**~~ ✅ Los errores de `espacio.tsx` y del selector usan
  `estadoDeError()` (#47) y el inicio muestra el logo (#52).
- **`/variables` con datos reales respondía 503 (`escaneo_en_curso`):** ✅ arreglado en `main` (#48). Si un servidor
  todavía muestra "El escaneo aún no termina", corre una versión anterior al #48 y hay que actualizarlo y reiniciarlo
  (B1). `analyze` y `teleconnect` funcionan igual.
- **Guion de la demo 1:** con los datos reales (comentario en el issue #6), la lluvia de Piura **no tiene líneas** hacia
  Indonesia ni hacia el norte de Australia; solo `RH2M` da líneas de efecto opuesto, hacia el Pacífico norte tropical.
  El guion se ajusta a los datos: hay que decidirlo con B3 antes de construir la demo 1 (cambios ya pedidos en el
  issue #15: celda (−6, −80), 1998 en vez de 1983, Niño costero 2017, `cambio_oculto` en el norte de Australia y
  cautela con Borneo).

### Ramas vigentes (las `-v2` y `chore/base-frontend` se borraron: no se vuelven a crear)

| Rama | Rol | Estado |
|---|---|---|
| `fe/graficos-enso` | F2 | ✅ fusionada en `main` (#40) |


### Pendientes en GitHub

- [x] Cerrar el PR #28 sin fusionarlo ✅
- [x] Borrar las ramas `-v2` y `chore/base-frontend` ✅ (#37, #38)
- [x] Cerrar el issue #1 ✅
- [x] Asignar los issues #11 y #15 a F3 ✅
- [ ] Asignar en GitHub los issues #12 y #14 a F2 — **por avanzar**
- [x] Cerrar el issue #10 (código fusionado en #40) ✅
- [ ] ~~Quitar la firma de IA de los 8 commits de la base que ya están en `main`~~ ✂️ no se hace: exigiría reescribir
      `main`. Desde aquí ningún commit nuevo lleva firma de IA

---

## 2. Avance por sprint

### S0 · Cimientos (horas 0–6) → Hito 6

**F1 · `chore/contratos` (#1)**
- [x] App Expo con Expo Router y TypeScript estricto, abierta en un teléfono real con Expo Go (SDK 58) ✅ (#25)
- [x] Stack instalado con `npx expo install` y verificado con `expo install --check` ✅ (#25)
- [x] Scripts `test`, `lint`, `tipos`, `fixtures:copiar`, `demo:copiar` y `dev` ✅ (#25)
- [x] `store.ts`, `tema.ts`, `geo.ts`, cliente único en `shared/api/` y fixtures ✅ (#25)
- [x] Pantallas `_layout`, `index`, `espacio` y `glosario` con la banda "Datos simulados" ✅ (#25)
- [x] CI `frontend.yml` ✅ (#25)
- [x] Cerrar el issue #1 ✅

**F2**
- [x] Revisar que el esqueleto compile en web (`expo export -p web` en verde) ✅
- [x] `queryClient.ts` mínimo ✅ (#25)
- [x] Cuenta de Expo y `eas login` ✅

**F3**
- [x] Logo oficial en `assets/marca/` (sin redibujar) y `LogoVeraScope` ✅ (#33) — **por avanzar:** mostrarlo en una
      pantalla
- [x] Textos de los estados de error y de la interfaz (`textosEstados.ts`, con pruebas) ✅ (#33)
- [x] `_layout.tsx` con Inter, pantalla de arranque, barra de estado y áreas seguras ✅ (venía en la base, #25)

**Criterio del hito 6:**
- [ ] URL pública con HTTPS (backend) — **por avanzar**
- [x] La app muestra el analyze simulado en la web, en local con `npm run dev` ✅
- [ ] Probado en un teléfono real por el equipo — **por avanzar**

---

### S1 · Piezas base (horas 6–13)

**F1 · `fe/mapa-celda` (#9)**
- [x] Costas Natural Earth 110m en `assets/geo/tierra.json`; mapa centrado en el Pacífico (vista 90–330) ✅ (#47)
- [x] Polígonos con desplazamiento 0 y +360 (sin rayas); puntos con `lon360` ✅ (#47)
- [x] Toque → celda cuantizada → rectángulo visible (≥ ~12 px), con la celda que devuelve la API ✅ (#47)
- [x] Gestos, botones ＋/− y Restablecer vista; rueda del ratón en web ✅ (#47)
- [x] Accesos directos a Piura, Borneo y norte de Australia ✅ (#47)
- [x] Selector de variable (desde `/variables`) y ventana (< 10 años no se envía) ✅ (#47)
- [x] Selector de índice con Niño 1+2 (aparece solo si `/variables` lo ofrece) ✅ (#47)

**F2 · `fe/distribucion` (#12) y `fe/graficos-enso` (#10)**
- [x] `eas.json` con perfil `preview` (APK) y `expo.android.package` ✅ (#25)
- [x] GraficoSerie con react-native-svg y d3 (los `null` son huecos) ✅ (#40)
- [ ] `EXPO_PUBLIC_API_URL` con la URL HTTPS — **por avanzar** (se espera la URL fija de Render, #50; no se genera con el túnel temporal porque la URL queda grabada al compilar)
- [ ] Primer APK con `eas build -p android --profile preview` — **por avanzar** (con la URL de Render)
- [ ] Primera web publicada y su origen enviado al backend para `VERASCOPE_CORS` — **por avanzar** (con la URL de Render)

**F3 · `fe/veredicto-feed` (#11), parte veredicto**
- [x] Tarjeta: "Tendencia aparente" con el interruptor apagado e insignia de 4 estados con el interruptor encendido ✅
      (#34)
- [x] Pendiente por década con intervalo y unidad, cambio % solo si viene, p-valor (corregido si viene del escaneo),
      vínculo con El Niño, avisos tal cual, fuente y "análisis individual" ✅ (#34, #35)
- [x] Cambio de veredicto anunciado a lectores de pantalla ✅ (#34)
- [x] Atribución de la fuente y pruebas de los avisos de la costa ✅ (#35)
- [x] `format.ts` es-PE con unidad ✅ (#25; ajuste en #35)

**Criterio de cierre (hora 13):**
- [x] Mapa con toque → celda, en la web ✅ (#47) — **por avanzar:** probarlo en el teléfono
- [ ] Primer APK instalado o en cola — **por avanzar** (F2)

---

### S2 · Flujo real (horas 13–20) → Hito 20

**F1 · cierre de `fe/mapa-celda` (#9)**
- [ ] `espacio.tsx` adaptable (teléfono con hoja inferior, tableta, web) — **por avanzar** (ya hay dos columnas en web
      ≥ 1024 y una columna en el teléfono; falta la hoja inferior)
- [x] Montar `TarjetaVeredicto` en `espacio.tsx` en lugar de `InsigniaVeredicto` ✅ (#47)
- [x] Usar `estadoDeError()` de `textosEstados.ts` en los errores de `espacio.tsx` y del selector (botón "Usar la celda
      cercana") ✅ (#47)
- [ ] Rendimiento en un Android de gama baja — **por avanzar**
- [ ] Colores de La Niña y de la línea de mismo efecto, con captura — **por avanzar**
- [x] Probar contra el `analyze` real (el backend ya lo tiene, #30; datos en #43) ✅ (#47, en la web con Piura)

**F2 · `fe/graficos-enso` (#10)** ✅ fusionado en `main` (#40)
- [x] Panel **Causa** (índice con franjas de El Niño y trama de La Niña, referencias ±0.5) ✅ (#40)
- [x] Panel **Consecuencia** (`serie_z` de la celda y del destino superpuestas) ✅ (#40)
- [x] Panel **Realidad** (serie original o sin El Niño, recta completa, meses inusuales marcados) ✅ (#40)
- [x] Lectura con el dedo o el cursor, compartida por contexto de React ✅ (#40)
- [x] Interruptor "Quitar El Niño" accesible, sin red, con la frase del rezago ✅ (#40)
- [x] `queryClient.ts` completo: persistencia en AsyncStorage, descarte por `version_metodo`, sin reintentar
      `power_lento` ✅ (#40)
- [x] Pruebas: interruptor 10 veces = 0 llamadas, huecos en los `null`, caché ✅ (#40)
- [x] Abrir PR de `fe/graficos-enso` y fusionar en `main` ✅ (#40)

**F3 · `fe/veredicto-feed` (#11), inicio y errores**
- [ ] Inicio: frase de VeraScope, Investigar, Escanear, demos y "Usar demo sin conexión" — **por avanzar** (ya están el
      logo, Investigar y Glosario, #52)
- [x] Textos de los estados de error (`power_lento`, `sin_datos_tierra`, red) ✅ (#33; se muestran en `espacio.tsx`, #47)
- [x] Tarjeta conectada a `quitarElNino` del store ✅ (#34; montada en `espacio.tsx`, #47)
- [ ] ~~Feed de ScanMap con pestañas~~ ✂️ como mucho, lista simple si sobra tiempo (el backend #7 sigue abierto)

**Criterio del hito 20:**
- [x] Tocar el mapa lleva al veredicto ✅ (#47, probado en la web con datos reales) — **por avanzar:** probarlo en un
      teléfono real
- [x] El interruptor cambia gráfico y veredicto sin red ✅ (gráfico #40; tarjeta montada #47)

---

### S3 · Diferenciadores I (horas 20–28)

**F1 · `fe/lineas-mosaico` (#13)**


**F2 · `fe/tiempo-comparador` (#14), parte tiempo** ✅ fusionado en `main` (#51)
- [x] Reproducir/Pausa y barra de tiempo accesible (adjustable, aumentar/disminuir, arrastre) ✅ (#51)
- [x] ~30 s por tiempo transcurrido; cambia `mesVisible` solo al cambiar de mes y termina en `null` ✅ (#51)
- [x] Prueba con temporizadores falsos, sin red ✅ (#51)
- [x] `ControlTiempo` montado en `espacio.tsx`, debajo del interruptor ✅ (#51)
- [x] Abrir PR de `fe/tiempo-comparador` y fusionar ✅ (#51)
- [x] Avisar a F1 que `mesVisible` ya está animado ✅

**F3**
- [ ] ~~Feed paginado con "Escaneo en curso"~~ ✂️
- [ ] Ejecutor de guiones con Anterior / Siguiente / Salir (`fe/demos-glosario`, #15) — **por avanzar**

**Criterio de cierre (hora 28):**
- [x] Desde la costa de Piura salen líneas hacia el otro lado del Pacífico 🟡 (desde (−4, −82); la celda (−6, −80) no
      tiene líneas con datos reales) — **por avanzar:** fusionar el #13
- [x] La reproducción enciende las líneas 🟡 — **por avanzar:** fusionar el #13

---

### S4 · Diferenciadores II y demos (horas 28–36) → Hito 36 ← **estamos aquí**

**F1**
- [x] Mosaico de ScanMap 🟡 — estaba recortado ✂️; el backend ya lo sirve con datos reales (4235 celdas en 7 trazados,
      tras el botón "Mostrar el mosaico de ScanMap"). **Se queda** (decisión de F1, 15-nov); su paleta (§13) se aprueba con captura en el PR
- [ ] Captura de la línea de Piura cruzando el Pacífico — **por avanzar** (web hecha; falta el teléfono)
- [ ] Revisar los PR de F3 — **por avanzar** (#33, #34 y #35 ya se fusionaron con la aprobación de miacordov)

**F2**
- [ ] ~~"Antes y después" con `compare-periods`~~ ✂️ (queda la reproducción)
- [ ] ~~Franja de CO₂ de Mauna Loa~~ ✂️

**F3 · `fe/demos-glosario` (#15)**
- [ ] Acordar con B3 el guion de la demo 1 según los datos reales (sección 1) — **por avanzar**
- [ ] Acciones del contrato en el ejecutor de guiones — **por avanzar**
- [ ] **Demo 1 "El efecto espejo de El Niño"** con la celda de Piura (−6, −80) — **por avanzar** (núcleo)
- [ ] ~~Demo 2~~ solo si sobra tiempo
- [ ] Modo sin red con `assets/demo/` y banda "Sin conexión" — **por avanzar** (`assets/demo/` y
      `backend/data/demo/respuestas/` siguen vacías; necesita el backend #8)
- [ ] Página de glosario con créditos (Natural Earth, NASA POWER, NOAA CPC) y enlaces desde la tarjeta — **por
      avanzar** (hoy `glosario.tsx` lista los términos de `/glosario`, de la base)
- [ ] Ensayo en proyector y en teléfono a plena luz — **por avanzar**

**Criterio del hito 36:**
- [ ] La demo 1 corre completa en el teléfono y en la web, con y sin red — **por avanzar**
- [ ] El núcleo está en `main` — **por avanzar** (están el análisis con y sin El Niño y el interruptor; faltan la línea
      de Piura, la reproducción y la demo 1)

---

### S5 · Sin red y pulido (horas 36–44)

**F1**
- [ ] Correcciones `fix/…` del mapa y las líneas — **por avanzar**
- [ ] Rendimiento final en un teléfono modesto — **por avanzar**

**F2 · `fe/distribucion` (#12)**
- [ ] APK y web finales con las demos empaquetadas (`npm run demo:copiar`) — **por avanzar**
- [ ] Probados en modo avión — **por avanzar**
- [ ] Enlaces del APK y de la web para el README — **por avanzar**

**F3**
- [ ] Copiar a `assets/demo/` las respuestas del backend — **por avanzar**
- [ ] Revisión final de textos (español sencillo, sin redacción causal, unidades y fuentes) — **por avanzar**
- [ ] Revisión de accesibilidad en todas las pantallas — **por avanzar**

**Criterio de cierre (hora 44):**
- [ ] APK y web finales funcionan en modo avión — **por avanzar**

---

### S6 · Entrega (horas 44–48)

- [ ] Ensayo sin red de la app en el teléfono y en el navegador (F3) — **por avanzar**
- [ ] Video de la demo (F3 graba, F2 edita) — **por avanzar**
- [ ] Apoyo libre a quien vaya atrasado (F1) — **por avanzar**

---

## 3. Qué falta, en orden de prioridad

| # | Qué | Rol | Depende de |
|---|---|---|---|
| 1 | ~~Montar `TarjetaVeredicto` y los textos de error en `espacio.tsx`~~ ✅ (#47) | F1 | — |
| 2 | Acordar el guion de la demo 1 con los datos reales | F3 + B3 | — |

| 6 | Ejecutor de guiones e inicio con acceso a la demo y "Usar demo sin conexión" | F3 | — |
| 7 | Demo 1 con modo sin red (#15) | F3 | #9, #13, #14, guion acordado y las respuestas del backend (#8) |
| 8 | Primer APK y primera web (#12); la cuenta de Expo y `eas login` ya están ✅ | F2 | URL fija de Render (#50) |
| 9 | APK y web finales en modo avión (#12) | F2 | Demo 1 y `assets/demo/` |
| 10 | URL HTTPS fija de la API (Render) | Backend | — (mientras tanto, túnel temporal de Cloudflare) |

**Nunca se recorta:** análisis mensual con y sin El Niño, el interruptor, la línea de Piura hacia Indonesia y Australia,
la reproducción en el tiempo y la demo 1.
