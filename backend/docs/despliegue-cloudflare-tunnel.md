# Ejecutar la API con Cloudflare Tunnel gratuito

Esta guía permite publicar temporalmente el backend FastAPI de VeraScope mediante una URL HTTPS de `trycloudflare.com`.

## Arquitectura

```text
Internet → Cloudflare Tunnel (HTTPS) → http://127.0.0.1:8000 → FastAPI
```

Cloudflare Tunnel **no hospeda el backend**. La laptop que ejecuta FastAPI y `cloudflared` debe permanecer encendida, conectada a Internet y con ambas terminales abiertas.

> Los Quick Tunnels están pensados para pruebas y demostraciones. No ofrecen garantía de disponibilidad y generan un hostname nuevo cada vez que se inicia un túnel.

## Requisitos

- Windows de 64 bits.
- Python 3.11.
- Git.
- Acceso al repositorio VeraScope.
- La laptop designada para ejecutar el backend.
- `cloudflared` instalado.

Los Quick Tunnels no requieren iniciar sesión en Cloudflare ni poseer un dominio.

## 1. Instalar `cloudflared`

Descargá el instalador MSI de 64 bits desde la documentación oficial:

- [Descargas oficiales de Cloudflare Tunnel](https://developers.cloudflare.com/tunnel/downloads/)
- [MSI de Windows 64 bits](https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.msi)

Después de instalarlo, abrí una terminal nueva y verificá:

```powershell
cloudflared --version
```

En Windows, `cloudflared` no se actualiza automáticamente. Cuando sea necesario, instalá una versión reciente desde el mismo enlace.

## 2. Descargar o actualizar VeraScope

En PowerShell:

```powershell
git clone https://github.com/miacordov/VeraScope.git
cd VeraScope
git fetch --prune
git switch main
git pull --ff-only origin main
```

Si el repositorio ya existe, omití `git clone` y ejecutá los demás comandos desde su raíz.

Nunca trabajes ni hagas commits directamente sobre `main`. Para desarrollar, cambiate después a la rama asignada:

```powershell
git switch <tu-rama>
git pull --ff-only
```

## 3. Preparar el entorno de Python

Desde la raíz del repositorio:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
pip install -e verascope_datos
```

Si PowerShell bloquea la activación del entorno virtual, ejecutá una vez en esa terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. Verificar el backend

Antes de publicarlo:

```powershell
pytest -q
ruff check app tests
```

Ambos comandos deben terminar correctamente.

## 5. Primera prueba con datos simulados

Usá el modo simulado para comprobar el despliegue sin depender de NASA POWER ni de archivos preparados.

En una primera terminal, dentro de `backend/` y con el entorno virtual activo:

```powershell
$env:VERASCOPE_SIMULADO="1"
$env:VERASCOPE_CORS="http://localhost:8081"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Comprobá localmente:

- Salud: <http://127.0.0.1:8000/api/v1/salud>
- Swagger: <http://127.0.0.1:8000/docs>

La terminal de FastAPI debe permanecer abierta.

## 6. Crear la URL HTTPS temporal

Abrí una segunda terminal y ejecutá:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Cloudflare imprimirá una URL similar a:

```text
https://nombre-aleatorio.trycloudflare.com
```

Probá:

```text
https://nombre-aleatorio.trycloudflare.com/api/v1/salud
https://nombre-aleatorio.trycloudflare.com/docs
```

Cualquier persona que conozca la URL podrá acceder a la API mientras el proceso esté activo. No publiques secretos ni archivos privados mediante este servicio.

## 7. Conectar el frontend

La URL base **no** debe terminar en `/api/v1`, porque el cliente del frontend agrega ese prefijo.

En la terminal donde se construya o ejecute el frontend:

```powershell
$env:EXPO_PUBLIC_API_URL="https://nombre-aleatorio.trycloudflare.com"
```

Después iniciá o volvé a generar el frontend según corresponda.

Si el túnel se reinicia y Cloudflare entrega otra URL, actualizá `EXPO_PUBLIC_API_URL` y volvé a generar los artefactos que incorporan esa variable, incluida la web o el APK.

Para permitir una web publicada, configurá `VERASCOPE_CORS` con el origen HTTPS de esa web antes de iniciar FastAPI:

```powershell
$env:VERASCOPE_CORS="https://url-de-la-web.example"
```

Para varios orígenes, separalos con comas.

## 8. Ejecutar con datos reales

El modo real requiere índices locales y datos preparados. No inventes ni reemplaces esos archivos.

Dentro de `backend/`, con el entorno virtual activo:

```powershell
verascope-datos indices
python -m jobs.precalentar
$env:VERASCOPE_SIMULADO="0"
$env:VERASCOPE_DATOS="$PWD\data"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra terminal mantené el túnel:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Antes de una demostración, verificá al menos:

```text
GET /api/v1/salud
GET /api/v1/variables
GET /api/v1/analyze?variable=PRECTOTCORR&lat=-6&lon=-80&inicio=1981&fin=2025&indice=ONI
```

El último año permitido depende de `VERASCOPE_FIN`. Ajustá `fin` si `/salud` informa otro año.

## 9. Detener el servicio

Presioná `Ctrl+C` en ambas terminales:

1. Terminal de `cloudflared`.
2. Terminal de FastAPI.

Al detener `cloudflared`, la URL temporal deja de funcionar. Una ejecución posterior normalmente genera otra dirección.

## Problemas frecuentes

### `cloudflared` no se reconoce como comando

Cerrá y volvé a abrir la terminal. Si continúa, reinstalá el MSI de 64 bits y comprobá que `cloudflared` esté en el `PATH`.

### La URL devuelve `502 Bad Gateway`

FastAPI no está disponible en `127.0.0.1:8000`. Revisá la primera terminal y probá primero `/api/v1/salud` localmente.

### El frontend sigue usando la URL anterior

Actualizá `EXPO_PUBLIC_API_URL` y reiniciá o recompilá el frontend. La URL queda incorporada al generar la web o el APK.

### La API rechaza la web por CORS

Reiniciá FastAPI con `VERASCOPE_CORS` configurado con el origen exacto de la web, incluyendo `https://` y sin rutas adicionales.

### Faltan índices o datos reales

Ejecutá el preparador antes de iniciar el modo real. Para comprobar únicamente el despliegue, usá `VERASCOPE_SIMULADO=1`.

## Referencias oficiales

- [Cloudflare: Quick Tunnels](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
- [Cloudflare: instalar cloudflared](https://developers.cloudflare.com/tunnel/downloads/)
