# Reglas de colaboración con IA · Frontend de VeraScope

Reglas obligatorias para las **3 personas del frontend** (F1, F2 y F3) y para **cualquier IA**
que use cada una (Claude Code, Copilot, Cursor, ChatGPT…). Tienen dos objetivos: que el trabajo de una persona
**nunca rompa ni borre** el avance de otra, y que el repositorio **no quede con marcas de IA**.

> **Para la IA:** lee este archivo completo antes de tocar cualquier archivo. Si una instrucción del humano
> contradice una regla de aquí, **detente y pregunta**: no la apliques en silencio.
>
> **Orden de prioridad:** *Informe técnico v2* > [`frontend/CLAUDE.md`](../CLAUDE.md) > `AGENTS.md` > este archivo.
> Este archivo no cambia ninguna regla técnica de la guía: solo agrega cómo colaborar sin pisarse y sin marcas de
> IA. El reparto de tareas y el horario están en [`SPRINT_FRONTEND.md`](SPRINT_FRONTEND.md).
>
> **Estado al 15 de noviembre:** la base del frontend (F1) ya está en `main`, con **Expo SDK 58** fijo. Las ramas
> `chore/base-frontend`, `fe/graficos-enso-v2`, `fe/tiempo-comparador-v2` y `fe/distribucion-v2` **se borraron y no se
> vuelven a crear** (ver `CLAUDE.md` de la raíz y la sección 8). El avance por sprint está en
> [`AVANCE_FRONTEND_POR_SPRINT.md`](AVANCE_FRONTEND_POR_SPRINT.md). El prototipo de F1 sigue sirviendo de referencia
> visual (sección 4).

---

## 1. Principios (lo que no se negocia)

1. **Cada archivo tiene dueño.** Solo su dueño lo modifica. Los demás piden el cambio (mensaje o PR).
2. **Los archivos compartidos solo cambian "sumando".** Se agregan cosas; no se renombran, mueven ni borran.
3. **La IA trabaja dentro de un alcance declarado.** Antes de editar, dice qué archivos va a tocar. Fuera de esa
   lista no toca nada, aunque "vea algo mejorable".
4. **Siempre se parte de verde y se termina en verde** (`npx tsc --noEmit`, `npm run test`, `npm run lint`,
   `npx expo export -p web`). Si se encuentra rojo al empezar, se avisa al dueño antes de seguir.
5. **Ni rastro de IA en el repositorio** (sección 6): ni en commits, ni en PR, ni en el código.
6. **Ante la duda, se pregunta.** Un minuto de mensaje evita una hora de conflicto.

---

## 2. Mapa de dueños

**La IA debe preguntar "¿quién eres: F1, F2 o F3?"** si no lo sabe, y confirmar la rama con
`git branch --show-current`.

| Zona | Dueño | Ramas (issue) | Archivos |
|---|---|---|---|
| **F1 · Base, mapa y líneas** | F1 | `fe/mapa-celda` (#9), `fe/lineas-mosaico` (#13) · base ✅ ya en `main` (#1) | Esqueleto de `frontend/` (`package.json`, `tsconfig.json`, `eslint.config.js`, `scripts/`), `src/estado/store.ts`, `src/estado/seleccion.ts`, `src/shared/api/`, `src/shared/geo.ts`, `src/shared/tema.ts`, `src/shared/ui/`, `src/shared/ejemploSimulado.ts`, `app/espacio.tsx`, `src/features/map/`, `variable-picker/`, `teleconnection-lines/`, `assets/geo/`, `.github/workflows/frontend.yml` |
| **F2 · Gráficos, El Niño, tiempo y distribución** | F2 | `fe/graficos-enso` (#10), `fe/tiempo-comparador` (#14), `fe/distribucion` (#12) | `src/features/series-charts/`, `enso-toggle/`, `time-comparator/`, `src/estado/queryClient.ts`, `src/estado/persistencia.ts`, `src/estado/ProveedorConsultas.tsx`, `eas.json`, `app.json` |
| **F3 · Veredicto, feed, inicio, demos y glosario** | F3 | `fe/veredicto-feed` (#11), `fe/demos-glosario` (#15), `feat/f3-logo-textos-estados`, `fix/f3-atribucion-fuente` | `src/features/verdict-card/`, `scan-feed/`, `guided-tours/`, `glossary/`, `src/shared/components/`, `src/shared/format.ts`, `app/_layout.tsx`, `app/index.tsx`, `app/glosario.tsx`, `assets/demo/` |

**Cómo quedó la base (ya en `main`):** F1 creó todos los archivos de la base, incluidos algunos que son de otros. Desde
que se fusionó, cada archivo es de su dueño según esta tabla:
- `queryClient.ts`, `app.json` y `eas.json` son de F2.
- `format.ts`, `src/shared/components/`, `app/_layout.tsx`, `app/index.tsx` y `app/glosario.tsx` son de F3.

Cada persona crea su carpeta en `src/features/` en su rama. Para que su feature aparezca en `espacio.tsx` (de F1), deja
un hueco marcado con un comentario y lo avisa en el PR; F1 lo revisa.

**Zona compartida (riesgo alto):** cualquier cambio se **anuncia antes** y lo **revisan las otras dos personas**.

| Archivo | Por qué es delicado |
|---|---|
| `src/estado/store.ts` | Estado global que leen las tres zonas. Dueño F1; un cambio lo aprueban F1, F2 y F3 |
| `src/shared/api/` | Tipos **generados** del contrato con el backend (`npm run tipos` produce `esquema.ts`; `npm run fixtures:copiar` produce `__fixtures__/`). No se editan a mano; un cambio de contrato lo aprueban B1 y F1 |
| `src/shared/ui/` | Componentes básicos que usan todas las pantallas |
| `src/shared/tema.ts` | Tokens de color y espacios de toda la app |
| `app/espacio.tsx` | Vista de detalle donde se juntan las features de los tres (cada feature entra por su hueco, sin editar las ajenas) |
| `app/_layout.tsx` | Proveedores, tipografía y navegación raíz |
| `package.json`, `package-lock.json`, `app.json`, `eas.json`, `tsconfig.json`, `eslint.config.js`, `.github/workflows/frontend.yml` | Configuración: un cambio aquí afecta a todos a la vez |
| `frontend/CLAUDE.md`, `frontend/docs/` | Guía y acuerdos del equipo |

**Fuera del frontend (no se tocan):** `backend/` y los archivos de la raíz (`README.md`, `AGENTS.md`, `.gitignore`,
`Docs/`, `.github/workflows/backend.yml` y `preparador-datos.yml`). Si una tarea lo exige, se para y se avisa: casi
seguro es un cambio de contrato.

Un archivo nuevo pertenece a quien lo crea y se anota en esta tabla en el mismo cambio.

---

## 3. Contratos de lo compartido (cómo cambiarlo sin romper a otros)

Lo exportado por los archivos compartidos es un **contrato**. Las reglas:

- ✅ **Permitido:** agregar un componente, función o token nuevo; agregar una **prop opcional** con valor por
  defecto que mantenga el comportamiento actual.
- ❌ **Prohibido sin acuerdo de los tres:** renombrar o borrar un export; volver obligatoria una prop; cambiar el
  significado o el tipo de una prop; cambiar el valor de un color o de un token existente; cambiar los puntos de
  corte del diseño adaptable (`< 768` teléfono, `768–1023` tableta, `≥ 1024` web).
- ❌ **Prohibido sin aprobación de backend y frontend:** inventar, renombrar o "proponer" campos del contrato de la
  API. Si falta un campo, se le pide a B1.
- Si algo compartido "ya no sirve", se marca con un comentario `/** @deprecated usar X */` y se elimina **solo
  cuando nadie lo use** (verificado con búsqueda en todo `src/` y `app/`).
- Antes de cambiar cualquier export, la IA **busca todos sus usos** y los enumera al humano.

**Estado global (`src/estado/store.ts`, Zustand):** campos de la sección 7 de la guía: `variable`, `celda`,
`ventana`, `quitarElNino`, `mesVisible`, `reproduciendo`, `destino`, `filtroFeed`, `demo`, `indice`,
`mosaicoVisible`. Se cambian **solo con sus acciones** (`seleccionarCelda`, `alternarElNino`, `irAlMes`…). Los
datos del servidor viven en TanStack Query, nunca en el store. No se crean estados globales paralelos (otro Context
u otro store) para lo mismo.

---

## 4. Reglas técnicas del proyecto (resumen de la guía, para que todo encaje)

**Rutas (Expo Router)**
- Las pantallas viven en `frontend/app/` y son delgadas; la lógica va en `src/`.
- No crear `index.tsx` dentro de una subcarpeta de rutas (por ejemplo `app/demos/index.tsx`): rompe los tipos de
  rutas.
- Navegar con `router.navigate('/ruta')` o con `{ pathname, params }`. Nunca concatenar texto para armar rutas.
- No renombrar ni mover rutas existentes: otras pantallas navegan a ellas.

**Interfaz**
- Solo componentes de React Native (`View`, `Text`, `Pressable`, `ScrollView`, `FlatList`). Nada de `div`, CSS,
  `document`, `window` ni `localStorage` en código compartido.
- Colores **siempre** desde `src/shared/tema.ts`. Prohibido escribir colores hex sueltos en pantallas o
  componentes.
- Usar los componentes de `src/shared/ui/`; no crear duplicados locales.
- Diseño adaptable con `useWindowDimensions()`; probar siempre en ancho de teléfono y de escritorio.
- Mapa y gráficos con `react-native-svg` y d3. Prohibidos Leaflet, `react-native-maps`, Recharts, Plotly, Skia,
  WebGL y Tailwind.
- Mapa con longitudes 0–360 centradas en el Pacífico; las conversiones viven solo en `src/shared/geo.ts`.
- Accesibilidad: rol, etiqueta y estado en cada control; zonas táctiles de al menos 44 × 44; nunca depender solo
  del color.

**Datos y honestidad**
- **El frontend nunca calcula estadística:** ni tendencias, ni p-valores, ni z, ni fases, ni porcentajes, ni
  veredictos. Tampoco con un "simulador" dentro de la app: los datos simulados los da el backend
  (`VERASCOPE_SIMULADO=1`).
- El interruptor "Quitar El Niño", la reproducción y el cambio de pestaña no hacen peticiones de red.
- Todo pasa por `/api/v1`; la app no llama a POWER ni a NOAA.
- Los datos simulados siempre se rotulan con la banda **"Datos simulados"**. No se borra ese rótulo.
- Textos de la interfaz en **español sencillo**. Nunca redacción causal ("El Niño causó…"): se dice "ocurren a la
  vez y ambos responden a El Niño".
- Cada dato muestra fuente, unidad, celda y periodo.

**Qué se copia del prototipo de F1 (repositorio de pruebas de F1)**
- ✅ **Sí:** piezas visuales de `src/components/vs/`. Se copia la lógica de toque y dibujo de `maps.tsx` a
  `features/map/` (F1), `charts.tsx` a `features/series-charts/` (F2), `verdict.tsx` a `features/verdict-card/`
  (F3) y, si falta alguno, los componentes básicos de `ui.tsx` a `src/shared/ui/` (F1). Cada uno copia a **su**
  carpeta.
- ❌ **No:** `src/lib/stats.ts`, `analysis.ts` ni `simulate.ts`, ni nada que calcule tendencias, p-valores o
  veredictos. Tampoco `simulation.tsx` (el estado es `store.ts`), `colors.ts` (el tema es grafito `#0E0F11`) ni datos
  inventados de `src/data/`.
- Al copiar hay que adaptar dos cosas: el mapa pasa a longitudes 0–360 centradas en el Pacífico (no `centerLon` 0) y
  los datos salen de la respuesta de la API, no de un simulador.

---

## 5. Lo que la IA nunca hace (lista negra)

1. Editar archivos fuera del alcance declarado, ni "de paso".
2. Reformatear archivos completos, reordenar imports o cambiar comillas, sangría o fines de línea en código ajeno.
3. Borrar código "que parece no usarse", comentarios o TODO de otra persona.
4. Renombrar o mover archivos, carpetas, exports o rutas.
5. Instalar, actualizar o quitar dependencias sin acuerdo; correr `npx expo install --fix`, `npm update` o
   `npm audit fix`; **cambiar la versión de Expo (SDK 58 fijo)**, de React o de React Native; borrar o regenerar
   `package-lock.json`.
6. Tocar `tsconfig.json` o `eslint.config.js` para silenciar errores. Usar `@ts-ignore`, `@ts-expect-error`, `any`
   para salir del paso, o `eslint-disable`.
7. Editar archivos generados: `.expo/`, `expo-env.d.ts`, `dist/`, `node_modules/`, `ios/`, `android/` y los tipos
   de `src/shared/api/` (se regeneran con `npm run tipos`).
8. Crear archivos de configuración nuevos (`babel.config.js`, `metro.config.js`, `.prettierrc`…) sin acuerdo.
9. Usar `git add -A` / `git add .`, `git push --force`, `git reset --hard`, `git checkout -- .`, `git clean`,
   `git stash drop`, o reescribir commits ya subidos.
10. Resolver un conflicto **eligiendo "mi versión" en un archivo de otra persona**.
11. Subir secretos, `.env`, credenciales de Earthdata o datos personales.
12. Tocar `backend/` o los archivos de la raíz del repositorio.
13. Dejar cualquier marca de IA (sección 6).

---

## 6. Sin marcas de IA

El repositorio es del equipo: cada commit, PR y línea de código la firma **la persona** que lo sube, aunque la haya
ayudado una IA.

**Prohibido en mensajes de commit, títulos y descripciones de PR, comentarios de issues y nombres de ramas:**
- Líneas `Co-Authored-By:` de cualquier IA (Claude, Copilot, Cursor, ChatGPT, Gemini, Codex…).
- Frases como "Generated with Claude Code", "Generado con IA", "Made with Cursor" o el emoji 🤖.
- Nombres de herramientas de IA usados como firma o autor.

**Prohibido en el código y los documentos:**
- Comentarios del tipo "generado por IA", "Claude:", "Copilot sugiere…", "as an AI…" o restos de conversación con
  la IA (explicaciones dirigidas al humano, "aquí tienes…", "espero que te sirva").
- Nombres de herramientas de IA en identificadores, archivos o carpetas.
- Archivos de configuración de herramientas de IA subidos al repo: `.cursor/`, `.cursorrules`,
  `.github/copilot-instructions.md`, `.claude/settings.local.json`, `.windsurf*`, `.aider*`. Si los usas, ponlos en
  `.git/info/exclude` de tu copia (no hace falta tocar el `.gitignore` compartido).

**Excepción:** `frontend/CLAUDE.md`, `backend/CLAUDE.md` y `AGENTS.md` son guías oficiales del proyecto y se quedan.

**Cómo dejarlo configurado (cada persona, en su computadora):**
- Autor de los commits: tu nombre y tu correo (`git config user.name` y `git config user.email`), nunca los de una
  herramienta.
- **Claude Code:** en tu archivo de usuario `~/.claude/settings.json`, agrega
  `"attribution": { "commit": "", "pr": "" }` para que no agregue firmas.
- **Copilot, Cursor u otra:** revisa siempre el mensaje que proponen antes de confirmar el commit y borra cualquier
  firma.
- **Antes de cada `git push`**, este comando no debe mostrar nada:

  ```bash
  git log origin/main..HEAD --format=%B | grep -i -E "co-authored-by|generated with|claude|copilot|cursor|chatgpt|openai|anthropic|🤖"
  ```

  Si muestra algo y el commit **todavía no está subido**, corrígelo con `git commit --amend` (solo el último) o
  pide ayuda. Si ya está subido, avisa al grupo: no se reescribe historia compartida.

**Si una firma ya quedó en una rama subida:** GitHub muestra el avatar de la herramienta junto al autor por la línea
`Co-Authored-By` del mensaje. El código no cambia al quitarla.
1. **Al fusionar (recomendada):** "Squash and merge" y, en la caja del mensaje, se borran las líneas `Co-authored-by`
   antes de confirmar.
2. **Si ya entró a `main`, se deja así.** Quitarla exigiría reescribir `main` con push forzado, que está prohibido
   (sección 8). Pasó una vez con los 8 commits de la base (PR #25): no se repite.

> Esto es sobre la autoría en el repositorio. Si las reglas de NASA Space Apps piden **declarar** el uso de IA en la
> entrega, se declara en la descripción del proyecto; lo decide el equipo completo.

---

## 7. Protocolo de cada sesión con IA

**Al empezar**
1. Decir a la IA quién eres (F1, F2 o F3) y la tarea concreta (rama e issue).
2. Ponerte al día: `git switch main`, `git pull --rebase origin main`, luego `git switch <tu-rama>` y
   `git rebase main`.
3. Comprobar que partes de verde: `npx tsc --noEmit`, `npm run test` y `npm run lint`. Si hay rojo que no es tuyo:
   avisar y no tocarlo.
4. La IA propone un plan de 3–5 líneas con la **lista exacta de archivos** que tocará. El humano la aprueba.

**Durante**
- Cambios pequeños y frecuentes. Un commit = una idea.
- Si la tarea exige tocar un archivo compartido o de otra persona: **parar**, avisar al grupo y esperar el visto
  bueno (sección 3).

**Al terminar**
1. `npx tsc --noEmit`, `npm run test`, `npm run lint` y `npx expo export -p web` en verde.
2. Revisar el diff completo: `git diff --stat` → **solo** aparecen los archivos aprobados. Si aparece otro, se
   revierte ese archivo antes de seguir.
3. Probar en el navegador y en el teléfono (Expo Go) las pantallas tocadas **y** las que usan algo compartido que
   hayas cambiado.
4. Commit con `git add <rutas concretas>` y mensaje en español con prefijo (`feat:`, `fix:`, `docs:`, `chore:`,
   `test:`), **sin firmas de IA** (sección 6).
5. Dejar una **nota de traspaso** en el PR: qué hiciste, qué archivos tocaste, qué quedó pendiente, si cambiaste
   algo compartido, capturas (teléfono y web) y `Cierra #N`.

---

## 8. Flujo de ramas (mínimo)

- `main` siempre funciona. Nadie trabaja directo en `main`; todo entra por PR con **1 aprobación** de otra persona
  del frontend (F1 → revisa F2 · F2 → revisa F3 · F3 → revisa F1) y el CI en verde.
- Se usan **las ramas de los issues** (tabla de la sección 2). Para una corrección pequeña aparte:
  `fix/f2-huecos-grafico`, `docs/f3-glosario` (la letra indica de quién es).
- Ramas cortas: se integra a `main` **al menos cada 4 a 6 horas**. Para ponerte al día con `main`: si tu rama **aún no
  está subida**, `git pull --rebase origin main`; si **ya está subida**, `git merge origin/main` (GitHub **no permite
  forzar el push** en las ramas `fe/…`, así que no se reescribe una rama subida).
- **Ramas borradas que no se vuelven a crear:** `chore/base-frontend`, `fe/graficos-enso-v2`, `fe/tiempo-comparador-v2`
  y `fe/distribucion-v2`. Se usan `main`, `fe/graficos-enso`, `fe/tiempo-comparador` y `fe/distribucion`. Si tienes
  copias locales: `git fetch --prune` y `git branch -D <rama>`. Nunca hagas push de una copia local de esas ramas.
- Desde la hora 36 (`v1.0-freeze`) solo entran ramas `fix/…` hacia `release/demo`.
- **Dependencias y configuración** (`package.json`, `app.json`, `eas.json`…) van en un **PR aparte** que solo hace
  eso, anunciado al grupo, y se fusiona antes que el resto.
- **Conflictos:**
  - En tu archivo, lo resuelves tú.
  - En el archivo de otra persona, lo resuelves **junto con ella**.
  - En `package-lock.json`, se toma la versión de `main` y se vuelve a ejecutar `npx expo install <tu paquete>`.

---

## 9. Definición de "terminado"

- [ ] Solo cambiaron archivos de mi zona, o compartidos con aprobación previa.
- [ ] Ningún export compartido se renombró, borró ni cambió de significado; el store y el contrato, intactos o
      aprobados.
- [ ] `npx tsc --noEmit`, `npm run test`, `npm run lint` y `npx expo export -p web` en verde.
- [ ] Probado en teléfono (o ancho ≤ 500 px) y en web, con teclado y lector de pantalla en lo que toqué.
- [ ] Textos en español, datos rotulados como simulados, sin redacción causal, sin estadística en la app.
- [ ] Sin marcas de IA en commits, PR ni código.
- [ ] Nota de traspaso escrita en el PR.

---

## 10. Mensaje para pegar al inicio de cada sesión con la IA

```
Soy F<1|2|3> del frontend de VeraScope. Antes de nada lee frontend/docs/REGLAS_COLABORACION_IA.md,
frontend/docs/SPRINT_FRONTEND.md y frontend/CLAUDE.md, y respétalos (SDK 58 fijo).
Rama e issue: <rama> (#N). Tarea: <describe la tarea>.
1) Confirma mi zona y lista los archivos exactos que vas a tocar.
2) Si necesitas tocar un archivo compartido, de otra zona o de backend, detente y dímelo.
3) No instales dependencias, no cambies configuración ni el SDK, no reformatees ni borres código ajeno.
4) No calcules estadística en la app y no inventes campos del contrato.
5) No dejes marcas de IA: nada de Co-Authored-By, "Generated with…" ni comentarios de IA.
6) Al terminar ejecuta: npx tsc --noEmit, npm run test, npm run lint, npx expo export -p web,
   y muéstrame git diff --stat para comprobar que solo cambió lo acordado.
```
