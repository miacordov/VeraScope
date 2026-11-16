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

## 1. Dónde estamos (15 de noviembre, tarde · `main` en `5f85edc`)

| | Estado |
|---|---|
| **Sprint en el que deberíamos estar** | **S4 → S5** (congelamiento en la hora 36; `release/demo` todavía no existe) |
| **Sprint en el que está el frontend** | **S2–S3**: en `main` están la base, el panel de gráficos con el interruptor (F2, #40) y la tarjeta de veredicto, el logo y los textos de estados (F3, #33, #34, #35). En `fe/mapa-celda` (F1, sin fusionar): mapa, selector y la tarjeta montada en `espacio.tsx` (#9). **Por avanzar:** fusionar el #9 (F1), la reproducción (F2, `fe/tiempo-comparador`), las líneas (F1) y las demos (F3) |
| **Backend** | ✅ `analyze` real con caché y precalentamiento (#30), avisos de Niño costero (#29, #31), demo de Piura en la celda (−6, −80) (#32), `teleconnect` y `compare-periods` con datos reales (#41, #42) y **paquete de datos reales en el repo** (#43, `backend/paquete-datos/verascope-datos-20261115.tar.gz`). **Por avanzar:** URL pública con HTTPS, rutas del feed y del mosaico (#7) y respuestas de demo para la app sin red (#8). `/salud` dice escaneo `en_curso` aunque el escaneo esté listo (error conocido) |
| **Verificación de `main`** | `npx tsc --noEmit`, `npm run lint` y `npm run test` en verde (14 archivos, 92 pruebas). Con los datos reales, `analyze` de Piura (−6, −80) devuelve 540 meses y veredicto `sin_tendencia` (origen `escaneo`) |

### ⚠️ Lo que hay que resolver ya

- ~~**La tarjeta de veredicto está en `main` pero no se ve.**~~ 🟡 Resuelto en `fe/mapa-celda` (F1): `espacio.tsx`
  monta `TarjetaVeredicto` y el interruptor cambia el veredicto sin red (probado con datos reales de Piura) —
  **por avanzar:** fusionar el #9.
- ~~**Los textos de estados no los usa ninguna pantalla.**~~ 🟡 En `fe/mapa-celda`, los errores de `espacio.tsx` y del
  selector de variable usan `estadoDeError()` (con "Usar la celda cercana" y "Ver la lluvia en este lugar") —
  **por avanzar:** fusionar el #9. El logo (`LogoVeraScope`) sigue sin usarse en ninguna pantalla (F3).
- **`/variables` con datos reales responde 503 (`escaneo_en_curso`):** el selector de variable no puede cargar el
  catálogo; la app muestra el aviso y se puede analizar la lluvia (variable por defecto). Es del backend (B1).
- **Guion de la demo 1:** con los datos reales (comentario en el issue #6), la lluvia de Piura **no tiene líneas** hacia
  Indonesia ni hacia el norte de Australia; solo `RH2M` da líneas de efecto opuesto, hacia el Pacífico norte tropical.
  El guion se ajusta a los datos: hay que decidirlo con B3 antes de construir la demo 1 (cambios ya pedidos en el
  issue #15: celda (−6, −80), 1998 en vez de 1983, Niño costero 2017, `cambio_oculto` en el norte de Australia y
  cautela con Borneo).

### Ramas vigentes (las `-v2` y `chore/base-frontend` se borraron: no se vuelven a crear)

| Rama | Rol | Estado |
|---|---|---|
| `fe/graficos-enso` | F2 | ✅ fusionada en `main` (#40) |
| `fe/tiempo-comparador` | F2 | 🟡 reproducción lista (7 commits fuera de `main`) · **por avanzar:** abrir PR y fusionar |
| `fe/distribucion` | F2 | ✅ `eas.json` ya en `main` · **por avanzar:** primer APK, web y versiones finales |
| `fe/veredicto-feed` | F3 | ✅ tarjeta en `main` (#34, #35) · **por avanzar:** que se vea en `espacio.tsx`; el feed está recortado |
| `fe/mapa-celda` | F1 | ✅ fusionada en `main` (#47) · **por avanzar:** rendimiento y capturas en un teléfono real |
| `fe/lineas-mosaico` | F1 | 🟡 #13 hecho en la rama (sobre `main` `d4ad255`, con la reproducción de #51): líneas, lista accesible y mosaico · **por avanzar:** capturas en el teléfono, abrir PR y fusionar |
| `fe/demos-glosario` | F3 | **por avanzar:** sin commits propios |

### Pendientes en GitHub

- [x] Cerrar el PR #28 sin fusionarlo ✅
- [x] Borrar las ramas `-v2` y `chore/base-frontend` ✅ (#37, #38)
- [x] Cerrar el issue #1 ✅
- [x] Asignar los issues #11 y #15 a F3 ✅
- [ ] Asignar en GitHub los issues #10, #12 y #14 a F2 — **por avanzar**
- [ ] Cerrar el issue #10 (código fusionado en #40) — **por avanzar** (F2)
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
- [ ] Cuenta de Expo y `eas login` — **por avanzar**

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
- [x] Costas Natural Earth 110m en `assets/geo/tierra.json`; mapa centrado en el Pacífico (vista 90–330) 🟡 (`fe/mapa-celda`) — **por avanzar:** fusionar
- [x] Polígonos con desplazamiento 0 y +360 (sin rayas); puntos con `lon360` 🟡 — **por avanzar:** fusionar
- [x] Toque → celda cuantizada → rectángulo visible (≥ ~12 px), con la celda que devuelve la API 🟡 — **por avanzar:** fusionar
- [x] Gestos, botones ＋/− y Restablecer vista; rueda del ratón en web 🟡 — **por avanzar:** fusionar
- [x] Accesos directos a Piura, Borneo y norte de Australia 🟡 — **por avanzar:** fusionar
- [x] Selector de variable (desde `/variables`) y ventana (< 10 años no se envía) 🟡 — **por avanzar:** fusionar
- [x] Selector de índice con Niño 1+2 (aparece solo si `/variables` lo ofrece) 🟡 — **por avanzar:** fusionar

**F2 · `fe/distribucion` (#12) y `fe/graficos-enso` (#10)**
- [x] `eas.json` con perfil `preview` (APK) y `expo.android.package` ✅ (#25)
- [x] GraficoSerie con react-native-svg y d3 (los `null` son huecos) ✅ (#40)
- [ ] `EXPO_PUBLIC_API_URL` con la URL HTTPS — **por avanzar** (falta la URL del backend)
- [ ] Primer APK con `eas build -p android --profile preview` — **por avanzar**
- [ ] Primera web publicada y su origen enviado al backend para `VERASCOPE_CORS` — **por avanzar**

**F3 · `fe/veredicto-feed` (#11), parte veredicto**
- [x] Tarjeta: "Tendencia aparente" con el interruptor apagado e insignia de 4 estados con el interruptor encendido ✅
      (#34)
- [x] Pendiente por década con intervalo y unidad, cambio % solo si viene, p-valor (corregido si viene del escaneo),
      vínculo con El Niño, avisos tal cual, fuente y "análisis individual" ✅ (#34, #35)
- [x] Cambio de veredicto anunciado a lectores de pantalla ✅ (#34)
- [x] Atribución de la fuente y pruebas de los avisos de la costa ✅ (#35)
- [x] `format.ts` es-PE con unidad ✅ (#25; ajuste en #35)

**Criterio de cierre (hora 13):**
- [x] Mapa con toque → celda, en la web 🟡 (`fe/mapa-celda`) — **por avanzar:** probarlo en el teléfono y fusionar
- [ ] Primer APK instalado o en cola — **por avanzar** (F2)

---

### S2 · Flujo real (horas 13–20) → Hito 20

**F1 · cierre de `fe/mapa-celda` (#9)**
- [ ] `espacio.tsx` adaptable (teléfono con hoja inferior, tableta, web) — **por avanzar** (ya hay dos columnas en web
      ≥ 1024 y una columna en el teléfono; falta la hoja inferior)
- [x] Montar `TarjetaVeredicto` en `espacio.tsx` en lugar de `InsigniaVeredicto` 🟡 (`fe/mapa-celda`) — **por avanzar:**
      fusionar
- [x] Usar `estadoDeError()` de `textosEstados.ts` en los errores de `espacio.tsx` y del selector (botón "Usar la celda
      cercana") 🟡 — **por avanzar:** fusionar
- [ ] Rendimiento en un Android de gama baja — **por avanzar**
- [ ] Colores de La Niña y de la línea de mismo efecto, con captura — **por avanzar**
- [x] Probar contra el `analyze` real (el backend ya lo tiene, #30; datos en #43) 🟡 (en la web con Piura) — **por avanzar:** fusionar

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
- [ ] Inicio: frase de VeraScope, Investigar, Escanear, demos y "Usar demo sin conexión" — **por avanzar** (hoy: frase,
      Investigar y Glosario, de la base)
- [x] Textos de los estados de error (`power_lento`, `sin_datos_tierra`, red) ✅ (#33) — **por avanzar:** que
      `espacio.tsx` los muestre (F1)
- [x] Tarjeta conectada a `quitarElNino` del store ✅ (#34) — **por avanzar:** montarla en `espacio.tsx` (F1)
- [ ] ~~Feed de ScanMap con pestañas~~ ✂️ como mucho, lista simple si sobra tiempo (el backend #7 sigue abierto)

**Criterio del hito 20:**
- [x] Tocar el mapa lleva al veredicto 🟡 (`fe/mapa-celda`, probado en la web con datos reales) — **por avanzar:**
      fusionar el #9 y probarlo en un teléfono real
- [x] El interruptor cambia gráfico y veredicto sin red 🟡 (gráfico #40; tarjeta montada en `fe/mapa-celda`) —
      **por avanzar:** fusionar el #9

---

### S3 · Diferenciadores I (horas 20–28)

**F1 · `fe/lineas-mosaico` (#13)**
- [x] Arco en `lon360` de la celda de ScanMap hacia el otro lado del Pacífico, continua y roja 🟡 (`fe/lineas-mosaico`).
      Con datos reales: la celda de Piura (−6, −80) responde sin líneas (se muestra `mensaje_vacio`); la vecina
      (−4, −82) tiene líneas opuestas hacia (4, 150), (4, 160) y Borneo (0, 118)
- [x] Se enciende (opacidad 1, trazo grueso) en los meses de `meses_coincidencia`; 0.15 fuera y 0.8 sin `mesVisible` 🟡
      (probado con la reproducción de #51, sin peticiones)
- [x] Zona táctil de 24 px (por geometría, sin chocar con el toque de celda), `elegirDestino`, destino por defecto,
      lista accesible con franja de detalle, `mensaje_vacio` y 503 `escaneo_en_curso` 🟡
- [x] Líneas de mismo efecto (punteadas) 🟡 — estaban recortadas ✂️; salen en la misma respuesta. **Se quedan**
      (decisión de F1, 15-nov)

**F2 · `fe/tiempo-comparador` (#14), parte tiempo** 🟡 hecho en la rama
- [x] Reproducir/Pausa y barra de tiempo accesible (adjustable, aumentar/disminuir, arrastre) 🟡
- [x] ~30 s por tiempo transcurrido; cambia `mesVisible` solo al cambiar de mes y termina en `null` 🟡
- [x] Prueba con temporizadores falsos, sin red 🟡
- [ ] **Abrir PR de `fe/tiempo-comparador` y fusionar** — **por avanzar** (el #10 ya está en `main`, #40)
- [ ] Avisar a F1 que `mesVisible` ya está animado — **por avanzar**

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
| 1 | Montar `TarjetaVeredicto` y los textos de error en `espacio.tsx` | F1 | — (la tarjeta ya está en `main`) |
| 2 | Acordar el guion de la demo 1 con los datos reales | F3 + B3 | — |
| 3 | Mapa con toque → celda y acceso a Piura (#9) | F1 | Base (ya está) |
| 4 | Fusionar `fe/tiempo-comparador` (#14) | F2 (aprueba F3) | — (#10 ya en `main`) |
| 5 | Línea de Piura que se enciende al reproducir (#13) | F1 | 🟡 hecho en `fe/lineas-mosaico` (#9 y #14 ya en `main`) · por avanzar: PR |
| 6 | Ejecutor de guiones e inicio con acceso a la demo y "Usar demo sin conexión" | F3 | — |
| 7 | Demo 1 con modo sin red (#15) | F3 | #9, #13, #14, guion acordado y las respuestas del backend (#8) |
| 8 | Cuenta de Expo, `eas login` y primer APK (#12) | F2 | — |
| 9 | APK y web finales en modo avión (#12) | F2 | Demo 1 y `assets/demo/` |
| 10 | URL HTTPS de la API | Backend | — (sin ella, todo funciona con la demo guardada) |

**Nunca se recorta:** análisis mensual con y sin El Niño, el interruptor, la línea de Piura hacia Indonesia y Australia,
la reproducción en el tiempo y la demo 1.
