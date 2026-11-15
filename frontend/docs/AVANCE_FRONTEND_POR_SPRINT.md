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

## 1. Dónde estamos (15 de noviembre, hacia la hora 36)

| | Estado |
|---|---|
| **Sprint en el que deberíamos estar** | **S4 → S5** (congelamiento en la hora 36) |
| **Sprint en el que está el frontend** | **S1–S3**: la base está en `main`. F2 terminó el gráfico, el interruptor y la reproducción, y F3 la tarjeta y los textos de estados, pero **nada de eso está fusionado todavía**. F1 no ha empezado el mapa ni las líneas |
| **Backend** | ✅ `analyze` real con caché de dos niveles y precalentamiento (#30), avisos de Niño costero (#29, #31), demo de Piura en la celda de ScanMap (−6, −80) (#32), precalentamiento de Borneo y norte de Australia (#39). **Por avanzar:** URL pública con HTTPS, rutas reales de feed y mosaico (#7) y respuestas de demo para la app sin red (#8) |
| **Correcciones de la dueña del repo** | Pasó `main` a las ramas del frontend, subió el tiempo límite de `espacio.test.tsx` (#36) y dejó escrito en `CLAUDE.md` qué ramas se borraron y no se vuelven a crear (#37, #38) |

### Ramas vigentes (las `-v2` y `chore/base-frontend` se borraron: no se vuelven a crear)

| Rama | Rol | Estado |
|---|---|---|
| `fe/graficos-enso` | F2 | 🟡 código del #10 listo y actualizado con `main` · **por avanzar:** abrir PR y fusionar |
| `fe/tiempo-comparador` | F2 | 🟡 código del #14 (reproducción) listo, incluye el #10 · **por avanzar:** PR después del #10 |
| `fe/distribucion` | F2 | ✅ `eas.json` ya en `main` · **por avanzar:** primer APK, web y versiones finales |
| `feat/f3-logo-textos-estados` | F3 | 🟡 PR #33 abierto · **por avanzar:** revisión y fusión |
| `fe/veredicto-feed` | F3 | 🟡 PR #34 abierto · **por avanzar:** revisión y fusión |
| `fix/f3-atribucion-fuente` | F3 | 🟡 PR #35 abierto (incluye el #34) · **por avanzar:** revisión y fusión |
| `fe/mapa-celda` | F1 | **por avanzar:** sin commits |
| `fe/lineas-mosaico` | F1 | **por avanzar:** sin commits |
| `fe/demos-glosario` | F3 | **por avanzar:** sin commits |

### Pendientes en GitHub

- [x] Cerrar el PR #28 sin fusionarlo ✅
- [x] Borrar las ramas `-v2` y `chore/base-frontend` ✅ (#37, #38)
- [ ] Cerrar el issue #1 (parte frontend fusionada en el #25) — **por avanzar**
- [ ] Asignar en GitHub los issues #10, #12 y #14 a F2, y los #11 y #15 a F3 — **por avanzar**
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
- [ ] Cerrar el issue #1 — **por avanzar**

**F2**
- [x] Revisar que el esqueleto compile en web (`expo export -p web` en verde) ✅
- [x] `queryClient.ts` mínimo ✅ (#25)
- [ ] Cuenta de Expo y `eas login` — **por avanzar**

**F3**
- [x] Logo oficial en `assets/` (sin redibujar) 🟡 (`feat/f3-logo-textos-estados`, PR #33) — **por avanzar:** fusionar
- [x] Textos de los estados de error y de la interfaz (`textosEstados.ts`, con pruebas) 🟡 (PR #33) — **por avanzar:**
      fusionar
- [x] `_layout.tsx` con Inter, pantalla de arranque, barra de estado y áreas seguras ✅ (venía en la base, #25)

**Criterio del hito 6:**
- [ ] URL pública con HTTPS (backend) — **por avanzar**
- [x] La app muestra el analyze simulado en la web, en local con `npm run dev` ✅
- [ ] Probado en un teléfono real por el equipo — **por avanzar**

---

### S1 · Piezas base (horas 6–13)

**F1 · `fe/mapa-celda` (#9)**
- [ ] Costas Natural Earth 110m en `assets/geo/tierra.json`; mapa centrado en el Pacífico (vista 90–330) — **por avanzar**
- [ ] Polígonos con desplazamiento 0 y +360 (sin rayas); puntos con `lon360` — **por avanzar**
- [ ] Toque → celda cuantizada → rectángulo visible (≥ ~12 px), con la celda que devuelve la API — **por avanzar**
- [ ] Gestos, botones ＋/− y Restablecer vista — **por avanzar**
- [ ] Accesos directos a Piura, Borneo y norte de Australia — **por avanzar**
- [ ] Selector de variable (desde `/variables`) y ventana (< 10 años no se envía) — **por avanzar**
- [ ] Selector de índice con Niño 1+2 — **por avanzar** (B3 ya lo decidió: entra como complementario, #29)

**F2 · `fe/distribucion` (#12) y `fe/graficos-enso` (#10)**
- [x] `eas.json` con perfil `preview` (APK) y `expo.android.package` ✅ (#25)
- [x] GraficoSerie con react-native-svg y d3 (los `null` son huecos) 🟡 (`fe/graficos-enso`) — **por avanzar:** fusionar
- [ ] `EXPO_PUBLIC_API_URL` con la URL HTTPS — **por avanzar** (falta la URL del backend)
- [ ] Primer APK con `eas build -p android --profile preview` — **por avanzar**
- [ ] Primera web publicada y su origen enviado al backend para `VERASCOPE_CORS` — **por avanzar**

**F3 · `fe/veredicto-feed` (#11), parte veredicto**
- [x] Tarjeta: "Tendencia aparente" con el interruptor apagado e insignia de 4 estados con el interruptor encendido 🟡
      (PR #34) — **por avanzar:** fusionar
- [x] Pendiente por década con intervalo y unidad, cambio % solo si viene, p-valor (corregido si viene del escaneo),
      vínculo con El Niño, avisos tal cual, fuente y "análisis individual" 🟡 (PR #34 y #35) — **por avanzar:** fusionar
- [x] Cambio de veredicto anunciado a lectores de pantalla 🟡 (PR #34) — **por avanzar:** fusionar
- [x] Atribución de la fuente y pruebas de los avisos de la costa 🟡 (PR #35) — **por avanzar:** fusionar
- [x] `format.ts` es-PE con unidad ✅ (#25; ajuste en PR #35)

**Criterio de cierre (hora 13):**
- [ ] Mapa con toque → celda, en el teléfono y en la web — **por avanzar** (F1)
- [ ] Primer APK instalado o en cola — **por avanzar** (F2)

---

### S2 · Flujo real (horas 13–20) → Hito 20

**F1 · cierre de `fe/mapa-celda` (#9)**
- [ ] `espacio.tsx` adaptable (teléfono con hoja inferior, tableta, web) — **por avanzar**
- [ ] Rendimiento en un Android de gama baja — **por avanzar**
- [ ] Colores de La Niña y de la línea de mismo efecto, con captura — **por avanzar**
- [ ] Probar contra el `analyze` real (el backend ya lo tiene, #30) — **por avanzar**

**F2 · `fe/graficos-enso` (#10)** 🟡 todo hecho en la rama
- [x] Panel **Causa** (índice con franjas de El Niño y trama de La Niña, referencias ±0.5) 🟡
- [x] Panel **Consecuencia** (`serie_z` de la celda y del destino superpuestas) 🟡
- [x] Panel **Realidad** (serie original o sin El Niño, recta completa, meses inusuales marcados) 🟡
- [x] Lectura con el dedo o el cursor, compartida por contexto de React 🟡
- [x] Interruptor "Quitar El Niño" accesible, sin red, con la frase del rezago 🟡
- [x] `queryClient.ts` completo: persistencia en AsyncStorage, descarte por `version_metodo`, sin reintentar
      `power_lento` 🟡
- [x] Pruebas: interruptor 10 veces = 0 llamadas, huecos en los `null`, caché 🟡
- [ ] **Abrir PR de `fe/graficos-enso` y fusionar en `main`** (lo aprueba F3) — **por avanzar**

**F3 · `fe/veredicto-feed` (#11), inicio y errores**
- [ ] Inicio: frase de VeraScope, Investigar, Escanear, demos y "Usar demo sin conexión" — **por avanzar**
- [x] Textos de los estados de error (`power_lento`, `sin_datos_tierra`, red) 🟡 (PR #33) — **por avanzar:** mostrarlos
      en pantalla y fusionar
- [x] Tarjeta conectada a `quitarElNino` del store 🟡 (PR #34) — **por avanzar:** fusionar
- [ ] ~~Feed de ScanMap con pestañas~~ ✂️ como mucho, lista simple si sobra tiempo

**Criterio del hito 20:**
- [ ] Tocar el mapa (teléfono y web) lleva al veredicto — **por avanzar** (falta el mapa de F1)
- [ ] El interruptor cambia gráfico y veredicto sin red — **por avanzar:** fusionar #10 (F2) y #34 (F3)

---

### S3 · Diferenciadores I (horas 20–28)

**F1 · `fe/lineas-mosaico` (#13)**
- [ ] Arco de Piura hacia el otro lado del Pacífico, **solo efecto opuesto** (continua y roja) — **por avanzar**
- [ ] Se enciende en los meses de coincidencia según `mesVisible` — **por avanzar** (la animación de F2 ya existe en
      `fe/tiempo-comparador`)
- [ ] Zona táctil ancha, `elegirDestino`, lista accesible y `mensaje_vacio` — **por avanzar**
- [ ] ~~Líneas de mismo efecto~~ ✂️

**F2 · `fe/tiempo-comparador` (#14), parte tiempo** 🟡 hecho en la rama
- [x] Reproducir/Pausa y barra de tiempo accesible (adjustable, aumentar/disminuir, arrastre) 🟡
- [x] ~30 s por tiempo transcurrido; cambia `mesVisible` solo al cambiar de mes y termina en `null` 🟡
- [x] Prueba con temporizadores falsos, sin red 🟡
- [ ] **Abrir PR de `fe/tiempo-comparador` y fusionar** (después del #10) — **por avanzar**
- [ ] Avisar a F1 que `mesVisible` ya está animado — **por avanzar**

**F3**
- [ ] ~~Feed paginado con "Escaneo en curso"~~ ✂️
- [ ] Ejecutor de guiones con Anterior / Siguiente / Salir (`fe/demos-glosario`, #15) — **por avanzar**

**Criterio de cierre (hora 28):**
- [ ] Desde Piura salen líneas hacia el otro lado del Pacífico — **por avanzar**
- [ ] La reproducción enciende las líneas — **por avanzar**

---

### S4 · Diferenciadores II y demos (horas 28–36) → Hito 36 ← **estamos aquí**

**F1**
- [ ] ~~Mosaico de ScanMap~~ ✂️
- [ ] Captura de la línea de Piura cruzando el Pacífico — **por avanzar**
- [ ] Revisar los PR de F3 (#33, #34, #35) — **por avanzar**

**F2**
- [ ] ~~"Antes y después" con `compare-periods`~~ ✂️ (queda la reproducción)
- [ ] ~~Franja de CO₂ de Mauna Loa~~ ✂️

**F3 · `fe/demos-glosario` (#15)**
- [ ] Acciones del contrato en el ejecutor de guiones — **por avanzar**
- [ ] **Demo 1 "El efecto espejo de El Niño"** con la celda de Piura (−6, −80) — **por avanzar** (núcleo)
- [ ] ~~Demo 2~~ solo si sobra tiempo
- [ ] Modo sin red con `assets/demo/` y banda "Sin conexión" — **por avanzar** (necesita las respuestas del backend, #8)
- [ ] Página de glosario simple y créditos (Natural Earth, NASA POWER, NOAA CPC) — **por avanzar**
- [ ] Ensayo en proyector y en teléfono a plena luz — **por avanzar**

**Criterio del hito 36:**
- [ ] La demo 1 corre completa en el teléfono y en la web, con y sin red — **por avanzar**
- [ ] El núcleo está en `main` — **por avanzar**

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
| 1 | Fusionar `fe/graficos-enso` (#10) | F2 (aprueba F3) | — |
| 2 | Fusionar los PR de F3: #33, #34 y #35 | F3 (aprueba F1; si no está, F2) | — |
| 3 | Mapa con toque → celda y acceso a Piura (#9) | F1 | Base (ya está) |
| 4 | Fusionar `fe/tiempo-comparador` (#14) | F2 (aprueba F3) | #10 en `main` |
| 5 | Línea de Piura que se enciende al reproducir (#13) | F1 | #9; #14 para encenderse |
| 6 | Inicio con acceso a la demo y "Usar demo sin conexión" | F3 | — |
| 7 | Demo 1 con modo sin red (#15) | F3 | #9, #10, #11, #13, #14 y las respuestas del backend (#8) |
| 8 | Cuenta de Expo, `eas login` y primer APK (#12) | F2 | — |
| 9 | APK y web finales en modo avión (#12) | F2 | Demo 1 y `assets/demo/` |
| 10 | URL HTTPS de la API | Backend | — (sin ella, todo funciona con la demo guardada) |

**Nunca se recorta:** análisis mensual con y sin El Niño, el interruptor, la línea de Piura hacia Indonesia y Australia,
la reproducción en el tiempo y la demo 1.
