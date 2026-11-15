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

## Pendiente de verificar con los servicios reales

El formato de cada fuente se tomó de su documentación y se probó con archivos simulados, pero
desde el entorno donde se escribió el programa no había acceso a los servidores de la NASA.
En la primera corrida real conviene revisar:

- **GLDAS, escorrentía (V10):** la conversión × 8 supone que `Qs_acc` y `Qsb_acc` son acumulados de 3 horas promediados en el mes. Confírmalo en la guía de GLDAS.
- **AppEEARS (V12):** el nombre exacto de la capa (`CMG_0.05_Deg_Monthly_NDVI`). Si AppEEARS lo rechaza, búscalo en su lista de capas de MOD13C2.061.
