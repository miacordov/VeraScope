# CLAUDE.md · VeraScope

Las guías completas están en `backend/CLAUDE.md` y `frontend/CLAUDE.md`; las reglas de revisión, en `AGENTS.md`. Lee la guía de tu carpeta antes de trabajar.

## Ramas borradas: no se vuelven a crear

El 15-nov-2026 se borraron estas ramas, porque su contenido ya está en `main` o en las ramas vigentes:

| Rama borrada | Usa en su lugar |
|---|---|
| `fe/graficos-enso-v2` | `fe/graficos-enso` |
| `fe/tiempo-comparador-v2` | `fe/tiempo-comparador` |
| `fe/distribucion-v2` | `fe/distribucion` |
| `chore/base-frontend` | `main` |

- Antes de crear una rama, cambiarte a ella o hacer `push`, comprueba que no sea una de las borradas. Si te piden una, avisa y usa la vigente.
- No hagas `push` de una copia local de esas ramas: el push vuelve a crearlas en GitHub.
- Si todavía están en la máquina: `git fetch --prune`, cámbiate a la rama vigente y bórrala con `git branch -D <rama>`.
- La versión estable del equipo es `main`. Antes de empezar, actualízate: `git pull --rebase origin main`.

## Probar todo el repositorio

`scripts/testea-repo.sh` (`--rapido` omite `expo export -p web` y el esquema OpenAPI) corre backend, preparador, frontend y la conexión entre la API simulada y la app. Sale con 1 si algo falla. Córrelo antes de abrir un PR que toque las dos carpetas o el contrato.
