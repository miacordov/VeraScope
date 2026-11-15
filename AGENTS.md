# AGENTS.md · VeraScope

Reglas para agentes de IA y para la revisión automática de código (GGA). Las guías completas están en `backend/CLAUDE.md` y `frontend/CLAUDE.md`; si algo aquí contradice esas guías, mandan ellas. El informe técnico v2 manda sobre todo.

## Proyecto

VeraScope (NASA Space Apps 2026, *Earth System Trend Detective*) calcula la tendencia de una variable de la Tierra dos veces, con y sin El Niño, y da un veredicto de cuatro estados: `cambio_robusto`, `sensible_a_el_nino`, `cambio_oculto`, `sin_tendencia`.

- `backend/`: un servicio FastAPI (Python 3.11) con los paquetes datos, estadística y catálogo, más el preparador `backend/verascope_datos/`.
- `frontend/`: app React Native con Expo SDK 58 (iOS, Android y web desde el mismo código).

## Reglas de revisión (rechaza el cambio si no se cumplen)

### Generales
- Las reglas C1–C19 y V1–V8 de las guías ya están decididas. Un cambio que las revierta o las "mejore" se rechaza.
- Nada de redacción causal: se escribe "ocurren a la vez y ambos responden a El Niño", nunca "X causa Y" ni "El Niño causó esto".
- No se inventan números. Los datos simulados siempre se rotulan como simulados.
- Cada dato mostrado indica fuente, unidad, celda y periodo ("MERRA-2 vía NASA POWER", "ONI, NOAA CPC").
- "Sin tendencia detectable" es un hallazgo válido, no un error.
- Ni secretos ni credenciales en el diff. Nada de `backend/data/` en Git, salvo `backend/data/demo/`.
- Un PR de backend no toca `frontend/` y un PR de frontend no toca `backend/`. Si hace falta, es un cambio de contrato y necesita aprobación de ambos lados.
- Textos para el usuario y mensajes de error en español sencillo.
- Commits en español con prefijo `feat:`, `fix:`, `docs:`, `chore:` o `test:`.
- Ramas borradas, no se recrean: `chore/base-frontend`, `fe/graficos-enso-v2`, `fe/tiempo-comparador-v2` y `fe/distribucion-v2`. Se usan `main`, `fe/graficos-enso`, `fe/tiempo-comparador` y `fe/distribucion`. Rechaza un PR que salga de una de las borradas.

### Backend
- NASA POWER es la única fuente en vivo. Las pruebas no llaman a servicios externos.
- Solo cinco variables: `PRECTOTCORR`, `T2M`, `GWETROOT`, `GWETTOP`, `RH2M`. Análisis mensual sobre celdas de 0.5°.
- Prohibido el Mann-Kendall original: se usa Hamed-Rao con 12 rezagos.
- El intervalo de Theil-Sen se calcula a mano con la varianza corregida. No se usa `scipy.stats.theilslopes` para el intervalo, ni `scipy.stats.pearsonr` para p-valores con El Niño (se usa el tamaño efectivo de muestra), ni `pymannkendall.seasonal_test`.
- Benjamini-Hochberg en ScanMap, con dos familias.
- Los umbrales viven solo en `constantes.py`. Si cambia un cálculo, se sube `VERSION_METODO`.
- Sin Redis, colas, microservicios ni un segundo proceso. El panel del preparador escucha solo en 127.0.0.1.
- Cada cambio lleva su prueba; `pytest -q` y `ruff` deben quedar en verde.

### Frontend
- El frontend nunca calcula estadística: ni tendencias, ni p-valores, ni z, ni fases, ni porcentajes, ni veredictos.
- El interruptor "Quitar El Niño", la reproducción y el cambio de pestaña no hacen peticiones de red.
- Todo pasa por `/api/v1`; la app no llama a POWER ni a NOAA directamente.
- Nada de librerías de navegador (Leaflet, Recharts, Plotly, Tailwind, DOM, `localStorage`), WebGL ni Skia. Estilos con `StyleSheet` y tokens de tema.
- No se agregan dependencias sin aviso; se instalan con `npx expo install`. No se cambia el SDK de Expo.
- El mapa usa longitudes 0–360 centradas en el Pacífico.
- Ninguna URL `http://` en un build de entrega.
- Accesibilidad: rol, etiqueta y estado en los controles; nunca depender solo del color.
- `npx tsc --noEmit`, `npm run test` y `npm run lint` deben quedar en verde.
