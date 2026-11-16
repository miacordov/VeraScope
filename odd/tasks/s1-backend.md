# S1 · Backend (B1, B2, B3)

Sprint S1 del backend de VeraScope, un responsable por bloque, avanzando uno por uno.
Guía obligatoria: `backend/CLAUDE.md` (secciones 2, 6, 8, 12, 13, 17). Leer hasta `## Log`.

## Specs

S1. B1 · be/api-cache-despliegue (#3)
- "datos/cache.py: nivel 1 = casillero SQLite del preparador (backend/data/casillero.sqlite, llave lugar_celda); nivel 2 = resultados con llave celda + variable + ventana + índice + VERSION_METODO."
- "Cerrojo por celda (dos peticiones a una celda nueva → una sola llamada a POWER)."
- "Esqueleto de la ruta analyze real (validar → cuantizar → caché → POWER 8 s → motor → guardar → origen) usando stubs de B2/B3 hasta que lleguen."
- "Errores en español sencillo; power_lento con celda_cercana."
- "Log de una línea por petición (t_total_ms, acierto/fallo de caché)."
- "Despliegue continuo desde main; volumen VERASCOPE_DATOS=/data."

S2. B2 · be/datos-power (#2) → cierra hora 12
- "celdas.py terminado, con regla de empates x.25/x.75."
- "power_client.py: 5 variables en una petición; timeout parámetro (8 s vivo / 60 s lote); -999 → NaN; ignora mes \"13\"; espera creciente ante 429."
- "validacion.py: huecos ≤ 2 meses se interpolan; > 10 % faltante o hueco > 2 se descarta; mínimo 120 meses; aviso bajo 240; suelo sobre mar → sin_datos_tierra."
- "indices.py: ONI y Niño 1+2 locales; fases nino/nina/neutro; Niño 1+2 desde 1982; recorte al último mes con índice."
- "Una sola implementación compartida con el preparador."
- "Pruebas sin red (cuantización, geografía, calidad, ventana, cliente con servidor falso)."
- "Hora 8: lanzar descarga completa en segundo plano (verascope-datos power, ~71 min, demos primero). Vigilarla."
- "Hora 12: PR de be/datos-power a main; empezar be/scanmap-job (#5)."

S3. B3 · be/motor-enso (#4)
- "anomalias.py (climatología dentro de la ventana)."
- "enso.py: rezago 0–6, regresión conjunta con tendencia, serie sin El Niño, n_efectivo, colinealidad."
- "tendencia.py: Theil-Sen a mano, Mann-Kendall Hamed-Rao 12 rezagos, IC con la misma varianza que el p-valor, cambio total, cambio % (nunca en temperatura), recta."
- "veredicto.py (cuatro estados y avisos) y fdr.py (Benjamini-Hochberg)."
- "Pruebas: recuperación, sin tendencia, coherencia IC ↔ p (0 % contradicciones), falsos positivos, potencia, correlación con tamaño efectivo, mismos meses, rendimiento."

S4. Pendientes adicionales pedidos por el humano (L6)
- "B1: datos/cache.py. Carga de ScanMap en main.py. jobs/precalentar.py y jobs/instantaneas.py. URL pública con HTTPS."
- "B2: power_client.py, validacion.py, indices.py y jobs/scanmap.py."
- "B3: todo estadistica/ menos constantes.py." (incluye teleconexion.py y periodos.py)
- jobs/ entra en la imagen de la API (L7).

## Tasks

Orden B2 → B3 → B1 (L7). Un bloque por vez en su rama be/*; el agente NO hace commits ni push: deja el diff y el humano commitea (L7).

- [x] T2 · S2, S4 · B2 datos: power_client.py, validacion.py, indices.py · rama be/datos-power · verificado (PASS), sin commitear: lo commitea el humano · commit: (humano)
- [ ] T3 · S3, S4 · B3 motor: anomalias, enso, tendencia, veredicto, fdr · rama be/motor-enso · commit: (humano)
- [ ] T4 · S4 · B3 teleconexion.py y periodos.py · rama be/teleconexion-periodos · commit: (humano)
- [ ] T5 · S4 · B2 jobs/scanmap.py · rama be/scanmap-job · commit: (humano)
- [ ] T1 · S1, S4 · B1 cache.py, analyze real, jobs/precalentar.py, jobs/ en la imagen · rama be/api-cache-despliegue · commit: (humano)
- [ ] T6 · S4 · B1 carga de ScanMap en main.py y rutas scan · rama be/scan-feed-api · commit: (humano)
- [ ] T7 · S4 · B1 jobs/instantaneas.py · rama be/instantaneas-demo · commit: (humano)
- [ ] T8 · S1, S4 · B1 URL pública con HTTPS · bloqueada: falta proveedor y autorización de cuenta (L7) · commit: (humano)

## Log

L1 (pedido original, literal): "Backend B1 · be/api-cache-despliegue (#3) ... B3 · be/motor-enso (#4) ... avancemos uno por uno" (texto completo en S1–S3).
L2: Previo: chore/verifica-b1 verifica B1 de S0 (184 pruebas, ruff, Docker, latencia en backend/docs/latencia-power.md). Despliegue HTTPS de S0 bloqueado: falta hosting y autorización de cuenta.
L3: Hallazgo B2 S0: POWER usa 0.625° en longitud (MERRA-2 nativo); decisión de equipo pendiente, celdas.py sigue la regla 0.5° de la guía.
L4: Decisión del humano sobre la malla: "Mantener 0.5° y declararlo". celdas.py sigue igual; queda documentado en backend/docs/comprobaciones-b2.md.
L5: Comprobaciones B2 verificadas con POWER real (14-nov-2026): PRECTOTCORR en mm/day, mes 13 presente, GWETROOT -999 en el mar y GWETTOP 1.0. Pendiente: Prueba rápida del panel y latencia desde la sede.
L6 (humano, literal): "se eliminaria jobs solo si es una carpeta que no sirve para el proyecto y quiero que resolvamos esto nunca subas ni comitees eso lo voy a hacer yo    B1: - datos/cache.py. - Carga de ScanMap en main.py. - jobs/precalentar.py y jobs/instantaneas.py. - URL pública con HTTPS. - B2: power_client.py, validacion.py, indices.py y jobs/scanmap.py. - B3: todo estadistica/ menos constantes.py."
L7: Decisiones del humano: orden B2 → B3 → B1; un bloque por vez en su rama be/*, sin commits del agente; HTTPS: el humano dirá el proveedor; jobs/ entra en la imagen. jobs/ NO se borra (aloja scanmap, precalentar, instantaneas).
L8: Diseño B2 (mapa del explorador): app.datos es la implementación única; el preparador importa de app.datos (no al revés, porque el preparador no entra en la imagen). Se mueven parsear/ClientePower (fuentes/power.py), parsear_oni/parsear_nino12 (fuentes/noaa.py), ventana_valida (calcular.py) y rellenar_huecos (motor.py) a app/datos/.
L9: T2 hecho en be/datos-power (sin commitear): app/datos/{power_client,validacion,indices}.py + 63 pruebas; preparador importa de app.datos (fuentes/power.py como subclase adaptadora por --fin). Backend 250 pasan, ruff verde, preparador 13 pasan. Cambio intencional: timeout de POWER no se reintenta (PowerLento inmediato). Abierto: datos/ importa estadistica/constantes (choca con CLAUDE.md §5).
L10: Verificación independiente de T2: PASS (251 pruebas backend, 13 preparador, ruff verde, comparación antes/después del preparador sin diferencias no buscadas). Mensaje de PowerLento neutro; prueba de no-reintento del preparador agregada. Pendiente de decisión humana: excepción de CLAUDE.md §5 para estadistica/constantes.py.
L11 (humano, literal): "todo lo quiero en spañol no respondas en ingles"
L12: Diseño T3 (mapa del explorador): app/estadistica/ es la implementación única; módulos anomalias.py + enso.py (worker A), tendencia.py (worker B), veredicto.py + fdr.py (worker C), con entradas escalares/arreglos para no acoplarse; después el integrador escribe estadistica/celda.py (analizar_celda + fila_escaneo) y redirige el preparador (calcular.py, panel/servidor.py, motor.py como reexportación).
L13: Decisiones de B3 (CLAUDE.md las deja a B3): diferencia 1 → las dos tendencias sobre los mismos meses a[rezago:]; diferencia 2 → orden anomalías y después relleno de huecos, documentado; diferencia 3 → se aplica BH también a p_enso por variable (recomendado en la guía); diferencia 4 → quitar_enso devuelve n_efectivo; umbrales fijos (120, 6, 12, 3, 0.05) solo desde constantes.py; VERSION_METODO pasa a 2 porque cambian los números del escaneo. Avisos sin regla numérica en la guía (respuesta_no_lineal, nino_costero) no se inventan: quedan fuera hasta que el informe los defina.
L14: Hallazgo T3: con Hamed-Rao de pymannkendall la cobertura del IC de Theil-Sen da ~92-93 % (§13 pide ≥ 95 %), porque solo suma autocorrelaciones significativas y a veces reduce la varianza. Decisión del humano: opción B, usar max(var_s corregida, var_s sin corregir) para que Hamed-Rao nunca achique el intervalo; se mantiene el 95 %; VERSION_METODO = 2.
L15: Con max(var_s, var0) la cobertura llega a 95,1 % con ruido blanco pero queda en 92-93 % con AR(1) (Hamed-Rao corrige de menos: ~1,63× frente a ~1,86× real). Decisión del humano: opción A, la prueba de recuperación exige ≥ 90 % con AR(1) y se documenta en la prueba y en backend/CLAUDE.md §13; el método no cambia más.
L16: Verificación independiente de T3: FALLA en la coherencia IC ↔ p con empates (meses secos en 0.00, valores redondeados): las cotas por rango cuentan las pendientes cero y S no; ya existía en el motor original. Corrección: rangos (N + Z0 − C)/2 y (N − Z0 + C)/2 + 1 con Z0 = número de pendientes iguales a cero; más pruebas de recuperación con ruido blanco ≥ 95 %, potencia sin El Niño frente a la original y falsos positivos con el motor completo.
