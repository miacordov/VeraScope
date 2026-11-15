# Sprint final del frontend · VeraScope (horas 31–48)

Plan de emergencia para las horas que quedan. Reemplaza al reparto anterior del frontend. Se basa en el *Plan de
sprints (48 horas)*, en los issues #1 y #9–#15 y en las reglas de
[`REGLAS_COLABORACION_IA.md`](REGLAS_COLABORACION_IA.md). Solo cubre el frontend: no cambia nada del backend.

> Las horas son **horas del evento**. Este plan se actualizó el 15 de noviembre, hacia la hora 31.

---

## 1. Dónde estamos

### Frontend

**Kevin terminó la base en `chore/contratos`:** 8 commits, 63 archivos y **Expo SDK 58** (RN 0.88, React 19.3). Lo que
trae la base:

| Pieza | Archivos |
|---|---|
| Contrato tipado y cliente único de `/api/v1` | `src/shared/api/` (`esquema.ts` generado, `cliente.ts` con corte a 12 s y errores en español, `consultas.ts` con las llaves de la sección 8, fixtures tipados con prueba de sincronía) |
| Estado | `src/estado/store.ts` con los 11 campos y las acciones de la sección 7 · `queryClient.ts` mínimo para F2 |
| Utilidades | `geo.ts` (lon360, cuantización a 0.5°) · `format.ts` (es-PE con unidad) · `tema.ts` (grafito) |
| Componentes | `src/shared/ui/` (Boton, Tarjeta, Texto) · `src/shared/components/` (BandaSimulado, EtiquetaFuente, InsigniaVeredicto) |
| Pantallas | `_layout`, `index`, `espacio` (pide el analyze simulado de Piura y muestra veredicto y fuente), `glosario` |
| Herramientas | `npm run dev` (API simulada más Expo Go con un solo comando) · scripts `tipos`, `fixtures:copiar`, `demo:copiar` · CI `frontend.yml` |
| Guías | `frontend/CLAUDE.md` y `AGENTS.md` ya dicen SDK 58 |

Lo que le falta a la base:
- [ ] **No hay PR abierto** y el **issue #1 sigue abierto**: la base todavía no está en `main`.
- [ ] Los 8 commits tienen la línea `Co-Authored-By: Claude…`, y por eso GitHub muestra "Kevin and Claude". Se quita
      al fusionar (sección 5).
- [ ] Falta actualizar `backend/CLAUDE.md` al SDK 58, como el mismo Kevin anotó en su commit. Eso es de B1.
- [ ] No hay carpetas en `src/features/`: cada persona crea la suya.

### Backend (solo para saber qué esperar)

| Hecho en `main` | Falta |
|---|---|
| Datos (`power_client`, `celdas`, `validacion`, `indices`), motor (`tendencia`, `enso`, `veredicto`, `fdr`), teleconexión y periodos (#19), `jobs/scanmap.py` (#21), pares opuestos (#22) | **Las rutas siguen respondiendo JSON simulados**: `analyze.py` dice "sin cálculo ni descarga". Falta la caché y el analyze real (#3), las rutas reales de scan/feed (#7), las respuestas de demo (#8) y **la URL pública con HTTPS** (según el README, "se documentará cuando el equipo active el alojamiento temporal") |

Consecuencia para el frontend: todo se construye contra el **modo simulado**, que solo responde para Piura
(−5.0, −80.5), `PRECTOTCORR`, 1981–1990 y ONI. Cuando B1 conecte el motor, la app sigue igual porque el contrato no
cambia.

---

## 1b. Avance de Isabel (F2), 15 de noviembre

Las tres ramas parten de la base de Kevin (`chore/contratos`) y tienen `tsc`, las 72 pruebas, el lint y `expo export -p web`
en verde, también corriendo sin caché, como en el CI.

| Rama | Issue | Qué trae | Cambios en archivos de otros (avisados en el PR) |
|---|---|---|---|
| `fe/graficos-enso` | #10 | `features/series-charts/` (GraficoSerie, panel, lectura compartida), `features/enso-toggle/`, `estado/queryClient.ts`, `persistencia.ts`, `ProveedorConsultas.tsx` y pruebas | `app/_layout.tsx`: usa `ProveedorConsultas` (Franco) · `app/espacio.tsx`: hueco de F2 (Kevin) · `package.json`: Jest con d3 en CommonJS y `testTimeout` de 20 s (Kevin) |
| `fe/tiempo-comparador` | #14 (parte reproducción) | `features/time-comparator/` (Reproducir/Pausa, barra accesible, `useReproduccion`) y pruebas. Parte de `fe/graficos-enso` | `app/espacio.tsx`: agrega el control de tiempo |
| `fe/distribucion` | #12 (primera parte) | `eas.json` y `expo.android.package` | — |

Falta de Isabel: crear la cuenta de Expo, `eas login`, el primer APK y, más adelante, la web y el APK finales.

## 2. Quién es quién

| Rol | Persona | Issues | Ramas |
|---|---|---|---|
| F1 | Kevin (KevinDC65) | #1 base (hecha, falta fusionar) · #9 mapa y celda · #13 línea de Piura | `chore/contratos`, `fe/mapa-celda`, `fe/lineas-mosaico` |
| F2 | Isabel | #10 gráficos e interruptor · #14 reproducción · #12 APK y web | `fe/graficos-enso`, `fe/tiempo-comparador`, `fe/distribucion` |
| F3 | Franco | #11 veredicto, inicio y errores · #15 demo 1, sin red y glosario | `fe/veredicto-feed`, `fe/demos-glosario` |

En GitHub los issues #10, #12 y #14 están **sin asignar**: hay que asignárselos a Isabel. Los #11 y #15 también, a
Franco.

**Revisión cruzada:** a Kevin lo revisa **Isabel**, a Isabel la revisa Franco y a Franco lo revisa Kevin.

## 3. Recortes que se aplican desde ya

1. Vistas diaria y anual del gráfico.
2. Tooltips del glosario (queda una página simple).
3. Líneas de "mismo efecto" (quedan solo las de efecto opuesto).
4. Mosaico de ScanMap en el mapa.
5. Pestañas del feed (si sobra tiempo, queda una lista simple).
6. Comparación por periodos, la parte "Antes y después" del #14.

**Nunca se recorta:**
- el análisis mensual con y sin El Niño;
- el interruptor;
- la línea de Piura hacia Indonesia y Australia;
- la reproducción en el tiempo;
- la demo 1.

---

## 4. Horario

### Bloque A · Fusionar la base (horas 31–33)

- [ ] **Kevin:** abrir el PR de `chore/contratos` hacia `main` con `Cierra #1` (parte frontend).
- [ ] **Isabel (revisora):** bajar la rama, correr `npm ci`, `npx tsc --noEmit`, `npm run test`, `npm run lint` y
      `npm run dev`, y abrir la app en el teléfono con Expo Go y en la web. Si todo está en verde, aprobar.
- [ ] **B1:** aprobar la parte del contrato (la regla pide B1 + F1).
- [ ] **Fusionar con "Squash and merge"**, borrando las líneas `Co-authored-by` del mensaje (sección 5).
- [ ] Todos: `git switch main`, `git pull` y crear su rama desde `main`.
- [ ] **Isabel:** crear la cuenta en https://expo.dev/signup y correr `eas login`.

### Bloque B · Flujo completo (horas 33–38) → hito "toque → veredicto"

| Persona | Rama | Tareas |
|---|---|---|
| Kevin | `fe/mapa-celda` (#9) | - [ ] mapa SVG con costas (`assets/geo/tierra.json`) en 0–360 centrado en el Pacífico · - [ ] toque → rectángulo de la celda que devuelve la API · - [ ] acceso directo a Piura · - [ ] selector de variable mínimo · - [ ] huecos en `espacio.tsx` para gráfico, interruptor, tarjeta y reproducción |
| Isabel | `fe/graficos-enso` (#10) | - [x] GraficoSerie con react-native-svg y d3 (los `null` son huecos) · - [x] panel Causa · Consecuencia · Realidad (franjas de El Niño y trama de La Niña, serie original o sin El Niño con su recta, meses inusuales, lectura con el dedo) · - [x] interruptor "Quitar El Niño" accesible y **sin red** · - [x] `queryClient.ts` completo con persistencia en AsyncStorage y descarte por `version_metodo` · - [x] prueba: 10 cambios del interruptor = 0 llamadas · - [ ] **lanzar el primer `eas build -p android --profile preview`** (falta `eas login`) |
| Franco | `fe/veredicto-feed` (#11) | - [ ] tarjeta: "Tendencia aparente" o la insignia de 4 estados según el interruptor (usar `InsigniaVeredicto`), pendiente con intervalo y unidad, p-valor, fuente y avisos tal como llegan · - [ ] Inicio (frase, Investigar, demo 1, "Usar demo sin conexión") · - [ ] estados de error |

**Hora 38 · prueba conjunta:**
- Tocar Piura en el teléfono y en la web lleva a la tarjeta y al gráfico.
- El interruptor cambia los dos sin red.
- La prueba se hace con la API simulada (`npm run dev`).

### Bloque C · Lo que hace única a VeraScope (horas 38–43) → congelamiento

| Persona | Rama | Tareas |
|---|---|---|
| Kevin | `fe/lineas-mosaico` (#13) | - [ ] arco de Piura → destino cruzando el Pacífico, solo de **efecto opuesto** (con el fixture de `teleconnect`) · - [ ] se enciende en los meses de coincidencia según `mesVisible` · - [ ] lista accesible en texto y `mensaje_vacio` |
| Isabel | `fe/tiempo-comparador` (#14) | - [x] solo **Reproducir/Pausa** y barra de tiempo accesible · - [x] actualiza `mesVisible` solo cuando cambia el mes (`irAlMes`) y nunca recalcula · - [x] prueba con temporizadores falsos, sin red · - [ ] **avisar a Kevin que `mesVisible` ya está animado** (ya se puede: está en `fe/tiempo-comparador`) |
| Franco | `fe/demos-glosario` (#15) | - [ ] ejecutor de guiones con Anterior / Siguiente / Salir (fixture `efecto-espejo`) · - [ ] **demo 1 "El efecto espejo de El Niño"** · - [ ] modo sin red con `assets/demo/` (`npm run demo:copiar`) y la banda "Sin conexión" · - [ ] página de glosario simple y créditos (Natural Earth, NASA POWER, NOAA CPC) |

**Hora 43 · congelamiento:** desde aquí solo entran ramas `fix/…`. La demo 1 tiene que correr completa en el teléfono
y en la web.

### Bloque D · Sin red y pulido (horas 43–46)

| Persona | Tareas |
|---|---|
| Isabel · `fe/distribucion` (#12) | - [x] `eas.json` (perfil `preview` → APK) y `expo.android.package = org.verascope.app` · - [ ] APK y web finales con `npm run demo:copiar` · - [ ] probarlos en modo avión · - [ ] `EXPO_PUBLIC_API_URL` con la URL HTTPS de B1 (si no hay, la app funciona con la demo guardada) · - [ ] pasarle a B1 el origen de la web para `VERASCOPE_CORS` y los enlaces para el README |
| Franco | - [ ] copiar a `assets/demo/` las respuestas que regenera B1 · - [ ] revisión de textos (español sencillo, sin redacción causal, unidades y fuentes) · - [ ] accesibilidad |
| Kevin | - [ ] arreglos `fix/…` del mapa y la línea · - [ ] probar el rendimiento en un teléfono modesto |

### Bloque E · Entrega (horas 46–48)

- [ ] Ensayo sin red de la app en el teléfono y en el navegador (Franco).
- [ ] Video de la demo (Franco graba, Isabel edita).
- [ ] Apoyo libre a quien vaya atrasado (Kevin).

---

## 5. Cómo quitar la marca de Claude de la base sin perder nada

GitHub muestra "Kevin and Claude" porque cada uno de los 8 commits termina con
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Es solo texto en el mensaje: **el código no cambia** al
quitarlo.

**Forma recomendada:** al fusionar el PR se elige **"Squash and merge"** y, en la caja del mensaje que abre GitHub,
se borran todas las líneas `Co-authored-by: Claude…` antes de confirmar. A `main` entra **un solo commit** limpio a
nombre de Kevin, con todo su avance. Después se borra la rama `chore/contratos`.

**Lo que no se hace:** que otra persona reescriba la rama de Kevin, o forzar un push mientras él tenga cambios sin
subir. Si el equipo quiere limpiar también la rama, lo hace **Kevin**, avisando antes (sección 6 de las reglas).

## 6. Entregas entre personas

| Hora | De → A | Qué |
|---|---|---|
| 31 | Kevin → Isabel | PR de `chore/contratos` abierto para revisar |
| 33 | Isabel + B1 → Kevin | Aprobación y fusión limpia (squash) |
| 33 | Isabel → B1 | Pedir la URL HTTPS y la fecha del analyze real |
| 38 | Los tres | Prueba conjunta "toque → veredicto" |
| 40 | Isabel → Kevin | `mesVisible` animado para encender la línea |
| ~42 | B1 → Franco | Respuestas de demo regeneradas |
| 44 | Franco → Isabel | `assets/demo/` final para el APK |
| 46 | Isabel → todos | APK y web finales |

## 7. Descansos (90 minutos, nunca dos personas a la vez)

| Horas | Descansa | Quedan despiertos |
|---|---|---|
| 38:30–40 | Isabel (después del hito) | Kevin, Franco |
| 43–44:30 | Kevin (después del congelamiento) | Isabel, Franco |
| 44:30–46 | Franco | Isabel, Kevin |

## 8. Si algo se atrasa

- Si Kevin no abre el PR a tiempo, Isabel y Franco crean sus ramas **desde `chore/contratos`** y hacen rebase sobre
  `main` cuando se fusione.
- Si a la hora 43 no hay URL HTTPS, el APK y la web salen con la demo guardada y se avisa en la entrega.
- Si el mapa va lento en un teléfono modesto, se quitan detalles de las costas, nunca la línea de Piura.
- Si alguien se atrasa más de 1 hora en el bloque C, quien vaya adelantado le ayuda. Primero se recortan el glosario y
  el feed. El núcleo de la sección 3 no se recorta nunca.
