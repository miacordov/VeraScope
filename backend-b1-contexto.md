# VeraScope — Contexto del rol backend B1

Documento de continuidad para retomar el análisis desde otra terminal o sesión de Gentle Shell. No requiere acceso a la conversación original ni a Engram.

## Origen y estado

- Fuente leída: `VeraScope - Plan de sprints.docx`, ubicado en la sesión de origen en `D:\HACKATON_NASA_SPACE_APP`.
- Repositorio de destino indicado por el usuario: `C:\Users\USUARIO\Documents\GitHub\VeraScope`.
- El usuario ocupa el rol **backend B1** y pidió explicar sus responsabilidades, complejidad, flujo de trabajo y división en tareas.
- Se realizó un análisis del documento; no se inspeccionó la implementación del repositorio ni se desarrolló código.
- Este archivo resume el plan y las recomendaciones del análisis. No sustituye al documento original ni a la guía backend, que contiene contratos y enumeraciones exactos.
- Las horas son horas transcurridas del evento, no horas estimadas de programación.

## Responsabilidad principal

B1 es responsable de los contratos, la API, la integración de datos y estadística, la caché, el despliegue y las respuestas guardadas para las demos.

Flujo general:

```text
Frontend → API de B1 → módulos de datos de B2 → motor estadístico de B3
                    ← respuesta validada y consistente ←
```

B1 no debe duplicar el cliente POWER, la cuantización ni el motor estadístico. B2 desarrolla los módulos de datos y el trabajo de ScanMap; B3 desarrolla el motor y las funciones estadísticas de teleconexión y comparación de periodos. B1 integra y expone esas capacidades.

### Superficies asignadas en el plan

- `backend/app/main.py`
- `backend/app/api/`
- `backend/app/contracts/`
- `backend/app/datos/cache.py`
- `backend/app/catalogo/`
- `backend/jobs/precalentar.py`
- `backend/jobs/instantaneas.py`
- `backend/Dockerfile`
- `.github/workflows/backend.yml`
- `backend/app/estadistica/constantes.py`: lo crea B1 y lo revisa B3.

Las rutas `teleconnect.py` y `compare_periods.py` se trabajan con B3; se debe coordinar la edición para evitar conflictos. Las rutas relativas del plan deben contrastarse con la estructura real antes de implementar.

## Complejidad estimada

**Alta en el contexto de un evento de 48 horas**, principalmente por integración, concurrencia, infraestructura y coordinación. Esta valoración es una estimación del análisis, no una clasificación del documento.

| Área | Complejidad | Motivo |
| --- | --- | --- |
| Contratos | Media–alta | Todo el equipo depende de campos, tipos, enumeraciones y errores estables. |
| API y validación | Media | Debe respetar los contratos y distinguir estados y errores. |
| Caché y concurrencia | Alta | Dos peticiones a una celda nueva deben generar una sola consulta a POWER. |
| Integración B2/B3 | Alta | Los componentes se desarrollan en paralelo y llegan cerca del hito real. |
| Despliegue y persistencia | Media–alta | HTTPS, CORS, configuración, volumen y carga de datos. |
| Feed y catálogos | Media | Lectura, paginación, estados y consistencia de respuestas. |
| Demos sin red | Media–alta | Las instantáneas deben corresponder al contrato, método y guiones vigentes. |

El principal riesgo organizativo es que B1 se convierta en un cuello de botella. El contrato y los JSON simulados tempranos permiten que frontend avance sin esperar al backend real.

## Flujo de trabajo

1. Acordar contratos con F1 y crear modelos Pydantic y JSON simulados.
2. Publicar una API simulada con HTTPS para que frontend integre.
3. Implementar caché y el flujo de análisis con stubs mientras llegan B2 y B3.
4. Sustituir stubs por los módulos reales, sin copiar sus implementaciones.
5. Publicar feed, capa de escaneo, catálogos y rutas compartidas.
6. Generar respuestas guardadas y precalentar datos de las demos.
7. Congelar funciones, corregir, ensayar sin red y preparar la entrega.

Flujo conceptual de `analyze`:

```text
Validar → cuantizar con B2 → buscar resultado en caché
  ├─ acierto: responder
  └─ fallo: obtener datos disponibles o consultar POWER
            → motor de B3 → guardar resultado → responder con origen y avisos
```

Debe incluir cerrojo por celda, timeout de POWER y errores comprensibles.

## Desglose propuesto de tareas

Las siguientes tareas descomponen las responsabilidades del plan; no son issues nuevos ni evidencia de trabajo terminado.

### Preparación — Antes del evento

- Elegir hosting HTTPS de la API, coordinando con F2 el hosting web.
- Averiguar entregables y hora de cierre de la sede.
- Leer la guía backend y los issues propios.
- Confirmar interfaces, responsables y entregas con B2, B3 y F1.

### Issue #1 — `chore/contratos` — Horas 0–6

1. Preparar Python 3.11, `pyproject.toml`, dependencias y árbol del backend.
2. Definir modelos Pydantic v2 de todas las rutas y del error estándar con las enumeraciones exactas de la guía.
3. Crear JSON simulados por ruta y pruebas que los validen contra los modelos.
4. Entregar modelos y JSON a F1 alrededor de la hora 2.
5. Crear `constantes.py` con `VERSION_METODO = 1`; revisión de B3 alrededor de la hora 3.
6. Configurar `/api/v1`, GZip, salud, `VERASCOPE_SIMULADO=1` y CORS mediante `VERASCOPE_CORS`.
7. Preparar Dockerfile y `.dockerignore`, excluyendo datos pesados y tests según el plan.
8. Crear CI: `ruff check`, `ruff format --check`, `pytest -q`.
9. Desplegar con HTTPS y registrar URL en README.
10. Medir latencia de POWER con 20 celdas, una por segundo, y documentarla en el PR.

**Cierre del hito 6:** API pública simulada; teléfono y web muestran la respuesta; CI backend y frontend en verde en main. El contrato se aprueba con F1 alrededor de la hora 5.

### Issue #3 — `be/api-cache-despliegue` — Horas 6–20

1. Implementar caché de datos con SQLite del preparador: `backend/data/casillero.sqlite`, clave `lugar_celda`.
2. Implementar caché de resultados con clave celda + variable + ventana + índice + `VERSION_METODO`.
3. Implementar cerrojo por celda y comprobar que dos solicitudes a una celda nueva hacen una sola llamada a POWER.
4. Armar `analyze` con stubs: validar → cuantizar → caché → POWER → motor → guardar → origen.
5. Aplicar timeout vivo de 8 segundos, errores en español sencillo y `power_lento` con `celda_cercana`.
6. Registrar una línea por petición con `t_total_ms` y acierto/fallo de caché.
7. Configurar despliegue continuo desde main y volumen `VERASCOPE_DATOS=/data`.
8. Integrar módulos de B2 previstos a la hora 12 y motor de B3 previsto a la hora 18.
9. Cargar catálogo, índices, tabla y resultados al arrancar; recargar parquet cuando cambie.
10. Instalar el paquete de datos de B2 en el servidor.
11. Crear `jobs/precalentar.py` para demos y unas 50 ciudades, secuencialmente y con pausas.
12. Probar el recorrido completo con F1 antes de la hora 20.

**Cierre del hito 20:** toque en mapa → veredicto con datos reales en teléfono y web; el interruptor cambia gráfico y veredicto sin red; estado de ScanMap visible.

### Issue #7 — `be/scan-feed-api` — Horas 20–36

1. Publicar `scan/feed`: pestañas fuertes, opuestas y ocultas; 20 por página; ID estable; `en_curso` con HTTP 200.
2. Publicar `scan/layer`: columnas paralelas, `null` sin serie, GZip y HTTP 503 `escaneo_en_curso`.
3. Publicar variables, glosario y `demos/{id}` desde catálogos.
4. Generar `variables.json` desde el paquete de B2 y añadir definiciones sencillas de las cinco variables.
5. Preparar glosario y titulares mediante plantillas, nunca mediante un modelo de lenguaje.
6. Coordinar con B3 las rutas `teleconnect` y `compare-periods` sin duplicar sus cálculos.
7. Preparar guiones `efecto-espejo.json` y `senal-o-ruido.json` con F3 y B3.
8. Configurar CORS con el origen final de la web que entrega F2.
9. Preparar etiqueta `v1.0-freeze` y rama `release/demo` a la hora 36.

**Entregas previstas:** feed, glosario y demos a F3 alrededor de la hora 24; capa a F1 alrededor de la hora 26. B3 entrega teleconnect alrededor de la hora 25 y compare-periods a la hora 30.

**Cierre del hito 36:** las dos demos completas funcionan en teléfono y web con y sin red. Desde ese momento solo correcciones `fix/…` hacia `release/demo`.

### Issue #8 — `be/instantaneas-demo` — Horas 36–44

1. Crear `jobs/instantaneas.py` y guardar respuestas en `backend/data/demo/respuestas/`.
2. Incluir analyze de Piura y destinos, analyze de demo 2 completa y de 10 años, teleconnect, compare-periods y demos.
3. Regenerar respuestas si cambia el contrato, `VERSION_METODO` o un guion.
4. Completar precalentamiento para no pedir datos nuevos a NASA durante la demo.
5. Entregar respuestas regeneradas a F3 alrededor de la hora 40.
6. Coordinar que F3 entregue assets a F2 alrededor de la hora 41 para APK y web finales alrededor de la hora 43.

**Cierre hora 44:** APK y web finales funcionan sin red y README contiene enlaces.

### Entrega — Horas 44–48

- Ensayar sin red el servidor con API y web en la misma laptop.
- Completar README y URLs finales.
- Preparar etiqueta `v1.0-entrega`.
- Enviar entregables antes del cierre de la sede con el equipo.

## Coordinación y reglas del documento

- Contratos: dueño B1; aprobación B1 + F1.
- PR de B1: revisa B2; suplente B3.
- No editar carpetas ajenas sin avisar.
- Si una dependencia no llega, continuar contra JSON simulado y avisar.
- Una sola implementación de cuantización, cliente POWER y motor estadístico.
- Ramas cortas, integración cada 4–6 horas, revisión y CI obligatorios.
- El plan pide commits pequeños en español con prefijos `feat:`, `fix:`, `docs:`, `chore:` o `test:`.
- Datos pesados fuera de Git, salvo respaldos de demo autorizados por el plan.
- Nunca guardar credenciales NASA en archivos.
- Frontend muestra resultados; no calcula estadística.
- Evitar afirmaciones causales entre regiones: ambos lugares pueden responder a El Niño.

## Incertidumbres detectadas y recomendaciones

1. **Instantáneas y hito 36:** el plan ubica el trabajo principal de instantáneas en S5, pero exige demos sin red en la hora 36 y una primera tanda de respuestas alrededor de la hora 34. Recomendación: generar una primera versión antes del congelamiento y usar S5 para regenerar y verificar. No es una modificación del plan aprobada por el equipo.
2. **Descanso y capa de escaneo:** B1 descansa de la hora 25 a la 29 y debe entregar `scan/layer` alrededor de la 26. Recomendación: fusionar antes o coordinar un relevo.
3. **Falta de guía técnica en este análisis:** se leyó solo el plan de sprints. Debe leerse la guía backend, especialmente contratos y enumeraciones, antes de implementar.
4. **Estado real desconocido:** no se comprobó qué archivos, issues, servicios o pruebas ya existen en el repositorio de destino.

## Cómo retomar en otra sesión

Mensaje sugerido:

> Leé `backend-b1-contexto.md`. Soy backend B1 de VeraScope. Retomá el análisis de responsabilidades, complejidad y tareas. Contrastá este resumen con el plan de sprints y la guía backend disponibles. No implementes todavía: primero revisemos el estado real del repositorio y qué tarea me corresponde iniciar.

La creación de este archivo no autoriza implementación, commits, despliegues ni entrega. El siguiente paso es ubicar los documentos fuente y contrastar el plan con el estado actual.
