## La forma fácil: el panel visual

No hace falta escribir comandos. El panel es una página web que corre **solo en tu computadora**
y tiene un botón para cada paso, un mapa donde se ve cómo se llena la descarga y un registro de lo
que hace el programa.

1. **Windows:** doble clic en `Abrir-panel.bat`. **Mac:** doble clic en `Abrir-panel.command`
   (si lo bloquea: clic derecho, Abrir). **Linux:** `./abrir-panel.sh`.
2. La primera vez prepara todo solo (necesita Python 3.10 o más nuevo, e internet; tarda unos minutos).
3. Se abre el navegador. Pulsa **Prueba rápida** y, si sale bien, **Hacer todo**.

Qué encuentras en el panel:

| Parte | Para qué sirve |
|---|---|
| **Prueba rápida** y **Hacer todo** | La prueba baja solo Piura, Borneo y el norte de Australia en menos de un minuto. «Hacer todo» corre los seis pasos |
| **Mapa del Pacífico** | Cada punto es una celda; se enciende al descargarse. El botón «Resultados» lo pinta según el veredicto de cada variable |
| **Paso a paso** | Los seis pasos con su estado. Cada uno se puede correr por separado |
| **Tu cuenta de NASA** | Ingresas usuario y contraseña de Earthdata (solo viven mientras el panel está abierto) y puedes probarla |
| **¿Los datos cuentan la historia correcta?** | Comprueba que la lluvia de Piura sube con El Niño y la de Borneo baja. Si sale al revés, algo se descargó mal |
| **Registro** | Lo que hace el programa por dentro. Si algo falla, «Copiar registro» y se lo pasas a quien te ayuda |
| **Detener** | Corta el trabajo sin perder nada: al volver a ejecutar, sigue donde se quedó |

Para instalar el paquete que te manda otro integrante, arrastra el `.tar.gz` al cuadro punteado del paso 6.
Para apagar el panel, usa el botón **Apagar panel** de abajo o cierra la ventana negra.

Si ya tienes el programa instalado, también se abre con `verascope-datos panel`
(opciones: `--puerto 8765`, `--no-abrir`).

El resto de este documento explica los mismos pasos con comandos, por si prefieres la terminal.

## 1. Instalar (una vez)

Requiere Python 3.10 o más reciente.

```bash
cd backend/verascope_datos
pip install -e .
```

## 2. Cuenta de NASA Earthdata (solo para V8–V12)

POWER y NOAA no piden cuenta. GPM, GLDAS y MODIS sí: crea una cuenta gratuita en
https://urs.earthdata.nasa.gov y define, antes de correr el programa:

```bash
export EARTHDATA_USERNAME=tu_usuario
export EARTHDATA_PASSWORD=tu_contraseña
```

(En Windows: `set EARTHDATA_USERNAME=...`.) Si no las defines, el programa baja todo lo demás y
avisa que faltan V8–V12.

## 3. Correr todo

```bash
verascope-datos todo
```

Hace los seis pasos en orden y muestra una barra de progreso en cada uno:

| Paso | Qué hace | Variables | Tiempo aproximado |
|---|---|---|---|
| 1 | Baja los índices de NOAA | V6 ONI, V7 Niño 1+2, V13 CO₂ | segundos |
| 2 | Baja NASA POWER: primero Piura, Borneo y el norte de Australia; luego la rejilla de 4235 celdas | V1–V5 | ~71 min |
| 3 | Baja GPM, GLDAS y MODIS para los 3 lugares de las demos | V8–V12 | de minutos a horas (AppEEARS hace fila) |
| 4 | Arma la tabla gigante y calcula tendencias con y sin El Niño | — | ~8 min |
| 5 | Exporta el respaldo de las demos (funciona sin internet) | las 13 | segundos |
| 6 | Junta todo en un paquete para el equipo | — | segundos |

**Se puede cortar en cualquier momento** (Ctrl+C, se cae internet, se apaga la laptop).
Lo descargado queda guardado: al volver a correr el comando, sigue donde quedó y reintenta lo que falló.

## 4. Compartir con el equipo

El paso 6 deja un archivo `backend/data/paquetes/verascope-datos-AAAAMMDD.tar.gz` (~50 MB).
Súbelo a un *release* de GitHub o a una carpeta compartida. Cada integrante corre:

```bash
verascope-datos instalar verascope-datos-AAAAMMDD.tar.gz
```

El programa verifica que ningún archivo llegó dañado.

### Subir a un release de GitHub

1. Ve a https://github.com/miacordov/VeraScope/releases
2. Haz clic en **Draft a new release**
3. Tag: `datos-AAAAMMDD` (ejemplo: `datos-20261115`)
4. Título: `Datos AAAAMMDD`
5. Arrastra el `.tar.gz` de `backend/data/paquetes/` al cuadro de archivos adjuntos
6. Publica el release

Para instalar desde el release:

```bash
# Descargar el paquete
curl -L -o verascope-datos-latest.tar.gz "https://github.com/miacordov/VeraScope/releases/latest/download/verascope-datos-AAAAMMDD.tar.gz"

# Instalar en la carpeta de datos
verascope-datos instalar verascope-datos-latest.tar.gz --datos /ruta/a/los/datos
```

### Verificar la instalación

```bash
verascope-datos estado --datos /ruta/a/los/datos
```

Deberías ver ✔ en "Tabla gigante", "Lista de resultados", "Respaldo de demos" y "Paquete".

### Escaneo parcial para pruebas

Si necesitas probar las rutas de la API sin esperar el escaneo completo (4235 celdas), usa `--minimo-celdas`:

```bash
# Escanear solo las primeras 10 celdas
verascope-datos calcular --minimo-celdas 10

# O desde el job directamente
python -m jobs.scanmap --minimo-celdas 10
```

El estado del escaneo reflejará `celdas_total: 10` y la API mostrará solo esas celdas en `/scan/feed` y `/scan/layer`.

## 5. Comandos sueltos

```bash
verascope-datos panel         # el panel visual
verascope-datos estado        # qué hay y qué falta, variable por variable
verascope-datos variables     # el catálogo de las 13 variables
verascope-datos indices       # solo el paso 1
verascope-datos power         # solo el paso 2 (opciones: --solo-demos, --limite N, --pausa S)
verascope-datos satelites     # solo el paso 3 (opción: --solo imerg,gldas,ndvi)
verascope-datos calcular      # solo el paso 4
verascope-datos demos         # solo el paso 5
verascope-datos empaquetar    # solo el paso 6
```

### Exportar el catálogo

`variables.py` es la única fuente de los metadatos. Sin opciones, `variables` mantiene
la tabla de las 13 variables. `verascope-datos variables --ayuda` describe ambos formatos:

- `--json ARCHIVO`: objeto público con `variables` (las 5 en vivo) e `indices`
  (ONI y Niño 1+2), con id, nombre, definición, unidad y fuente; no incluye V8–V13.
- `--json-completo ARCHIVO`: lista técnica completa V1–V13, con código, capa,
  año inicial, nota y definición. Esta opción conserva la exportación que antes hacía `--json`.

Para regenerar el catálogo de la API, desde `backend/`:

```bash
verascope-datos variables --json app/catalogo/variables.json
verascope-datos variables --json-completo catalogo-completo.json
```

No edites a mano el JSON público: cambia los metadatos en `variables.py` y regénéralo.
Ambas opciones aceptan `-` para escribir solo JSON en la salida estándar y son excluyentes:

```bash
verascope-datos variables --json -
verascope-datos variables --json-completo -
```

Opciones generales: `--datos CARPETA` (por defecto `$VERASCOPE_DATOS`; si no, `backend/data` del repo VeraScope; fuera del repo, `./datos`) y `--fin AÑO` (por defecto, el año
pasado: el último año completo de MERRA-2).

**Primera prueba recomendada:** `verascope-datos power --solo-demos` baja solo los 3 lugares de las
demos en unos segundos y confirma que todo funciona antes de lanzar la rejilla completa.

## 6. Si algo falla

| Situación | Qué hacer |
|---|---|
| NOAA no responde | Descarga a mano `oni.ascii.txt`, `sstoi.indices` y `co2_mm_mlo.txt` y usa `verascope-datos indices --carpeta DONDE_ESTÁN` |
| POWER devuelve errores seguidos | Sube la pausa: `--pausa 2`. Los lugares fallidos se reintentan en la siguiente corrida |
| AppEEARS sigue procesando | Vuelve a correr `satelites --solo ndvi` más tarde: retoma la misma tarea, no crea otra |
| Ya tienes los archivos de GPM, GLDAS o MODIS | `satelites --archivos-locales CARPETA` con subcarpetas `imerg/`, `gldas/` y `ndvi/` |

## 7. Dónde queda cada cosa

```
backend/data/
├── casillero.sqlite      # todas las series, una fila por variable y lugar (binario float32)
├── tabla/                # la tabla gigante: una matriz celdas × meses por variable (.npy)
├── resultados.parquet    # veredicto, pendiente, intervalo y p-valores de cada celda
├── demo/                 # respaldo JSON de Piura, Borneo y el norte de Australia (13 variables)
├── crudo/                # textos de NOAA y estado de las tareas de AppEEARS
└── paquetes/             # el archivo para compartir con el equipo
```

## 8. Probar sin internet

```bash
pip install -e ".[pruebas]"
pytest tests
```

Las pruebas del programa y del panel (13 en total) fabrican archivos con el mismo formato que entregan NASA y NOAA (con un El Niño simulado,
no con datos reales) y corre el flujo completo, incluidos cortes de red y la instalación en otra
carpeta.

## Decisiones sobre fuentes de datos

### GLDAS escorrentía (V10)

La variable `Qs_acc` + `Qsb_acc` de GLDAS NOAH viene en m/s (acumulado por paso de 3 h).
Para obtener mm/día se multiplica por 8 (pasos de 3 h por día) × 1000 (m → mm) × 3600 (s → h)
÷ 3 (horas por paso) = × 8 simplificado. **Decisión:** mantener la conversión × 8 hasta que
alguien verifique con la guía de GLDAS NOAH025_M v2.1 que el factor es correcto.

### NDVI de AppEEARS (V12)

El NDVI usa MOD13C2 v061 (0.05° mensual) vía AppEEARS. AppEEARS tiene cola de procesamiento
(puede tardar horas). **Decisión:** mantener NDVI como variable opcional. Si AppEEARS no
responde, las demos funcionan con los 12 restantes.

### Despliegue en Render

El backend se despliega en Render (plan gratuito) con `render.yaml` y `scripts/start-render.sh`.
Los datos se instalan desde un paquete `.tar.gz` incluido en el repo (`paquete-datos/`).
El servicio se duerme después de 15 min sin tráfico; la primera petición tarda ~30 s.

**Nota:** Render no tiene disco persistente en el plan gratuito. Cada reinicio reinstala los
datos desde el paquete. Para datos actualizados, sube un nuevo paquete al repo y haz un deploy.
