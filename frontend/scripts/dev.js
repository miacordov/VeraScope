#!/usr/bin/env node
/**
 * `npm run dev`: levanta todo el entorno de desarrollo con un solo comando.
 *
 *  1. Prepara `backend/.venv` la primera vez (convención del README; está en .gitignore) y lo reinstala solo
 *     si cambia `backend/pyproject.toml`. NO modifica archivos versionados de `backend/`: solo lo ejecuta.
 *  2. Arranca la API en modo SIMULADO (`VERASCOPE_SIMULADO=1`) en 0.0.0.0:8000, para que el teléfono la alcance.
 *  3. Detecta la IP de la laptop en la red local y se la pasa a la app como `EXPO_PUBLIC_API_URL`.
 *  4. Arranca Expo (QR para Expo Go, `w` para web). Ctrl+C apaga los dos.
 *
 * Si ya defines `EXPO_PUBLIC_API_URL` en el entorno (p. ej. la URL https desplegada), no levanta la API local.
 * Los argumentos extra pasan a `expo start` (p. ej. `npm run dev -- --web`).
 */
const { spawn, spawnSync } = require('node:child_process');
const crypto = require('node:crypto');
const fs = require('node:fs');
const http = require('node:http');
const net = require('node:net');
const os = require('node:os');
const path = require('node:path');

const FRONTEND = path.resolve(__dirname, '..');
const BACKEND = path.resolve(FRONTEND, '..', 'backend');
const VENV = path.join(BACKEND, '.venv');
const MARCA = path.join(VENV, '.verascope-dev');
const PUERTO_API = 8000;
const PUERTO_EXPO = 8081;
const ES_WINDOWS = process.platform === 'win32';

/** Adaptadores virtuales que no sirven para que el teléfono alcance la laptop. */
const VIRTUALES = /(vethernet|virtualbox|vmware|hyper-v|wsl|docker|loopback|vpn|tailscale|zerotier|utun|bridge|veth)/i;

/** IP privada de la laptop en la red local (la que usa Expo Go en el teléfono), o `null`. */
function elegirIp(interfaces) {
  const candidatas = [];
  for (const [nombre, direcciones] of Object.entries(interfaces)) {
    if (VIRTUALES.test(nombre)) continue;
    for (const d of direcciones ?? []) {
      const ipv4 = d.family === 'IPv4' || d.family === 4;
      if (!ipv4 || d.internal) continue;
      candidatas.push(d.address);
    }
  }
  const prioridad = (ip) =>
    ip.startsWith('192.168.') ? 0 : ip.startsWith('10.') ? 1 : /^172\.(1[6-9]|2\d|3[01])\./.test(ip) ? 2 : 9;
  candidatas.sort((a, b) => prioridad(a) - prioridad(b));
  return candidatas.find((ip) => prioridad(ip) < 9) ?? null;
}

function pythonDelVenv(venv = VENV, windows = ES_WINDOWS) {
  return windows ? path.join(venv, 'Scripts', 'python.exe') : path.join(venv, 'bin', 'python');
}

/** Orígenes de la versión web que la API simulada debe aceptar (CORS). */
function origenesCors(ip, puerto = PUERTO_EXPO) {
  const hosts = ['localhost', '127.0.0.1', ...(ip ? [ip] : [])];
  return hosts.map((h) => `http://${h}:${puerto}`).join(',');
}

function puertoLibre(puerto) {
  return new Promise((resolve) => {
    const servidor = net.createServer();
    servidor.once('error', () => resolve(false));
    servidor.once('listening', () => servidor.close(() => resolve(true)));
    servidor.listen(puerto);
  });
}

/** Primer puerto libre desde `desde` (Expo no puede preguntar en modo no interactivo). */
async function buscarPuerto(desde = PUERTO_EXPO, intentos = 20) {
  for (let p = desde; p < desde + intentos; p++) if (await puertoLibre(p)) return p;
  throw new Error(`No hay puertos libres entre ${desde} y ${desde + intentos - 1} para Expo.`);
}

function huellaPyproject() {
  return crypto.createHash('sha256').update(fs.readFileSync(path.join(BACKEND, 'pyproject.toml'))).digest('hex');
}

/**
 * Detiene un proceso y sus hijos. En Windows, el python.exe de un venv es un lanzador que abre otro Python:
 * `kill()` solo cerraría el lanzador y la API seguiría ocupando el puerto, por eso se usa `taskkill /T`.
 */
function detenerArbol(proceso) {
  if (!proceso || proceso.exitCode !== null || proceso.pid === undefined) return;
  if (ES_WINDOWS) spawnSync('taskkill', ['/pid', String(proceso.pid), '/T', '/F'], { stdio: 'ignore' });
  else proceso.kill('SIGTERM');
}

function aviso(texto) {
  console.log(`\n[dev] ${texto}`);
}

function correr(cmd, args, opciones = {}) {
  const r = spawnSync(cmd, args, { stdio: 'inherit', ...opciones });
  return r.status === 0;
}

function existe(cmd, args) {
  const r = spawnSync(cmd, args, { stdio: 'ignore' });
  return r.status === 0;
}

/** Crea `backend/.venv` con Python ≥ 3.11 (uv si está, si no `py`/`python3`/`python`). */
function crearVenv() {
  if (existe('uv', ['--version'])) {
    aviso('Creando backend/.venv con uv (Python 3.11)…');
    return correr('uv', ['venv', '--python', '3.11', VENV]) ? 'uv' : null;
  }
  const comprobar = 'import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)';
  const candidatos = ES_WINDOWS
    ? [['py', ['-3.11']], ['py', ['-3']], ['python', []]]
    : [['python3.11', []], ['python3', []], ['python', []]];
  for (const [cmd, extra] of candidatos) {
    if (!existe(cmd, [...extra, '-c', comprobar])) continue;
    aviso(`Creando backend/.venv con ${[cmd, ...extra].join(' ')}…`);
    return correr(cmd, [...extra, '-m', 'venv', VENV]) ? 'pip' : null;
  }
  return null;
}

function prepararBackend() {
  const python = pythonDelVenv();
  const huella = huellaPyproject();
  const listo = fs.existsSync(python) && fs.existsSync(MARCA) && fs.readFileSync(MARCA, 'utf8') === huella;
  if (listo) return python;

  let instalador = fs.existsSync(python) ? (existe('uv', ['--version']) ? 'uv' : 'pip') : crearVenv();
  if (!instalador || !fs.existsSync(python)) {
    throw new Error(
      'No encontré Python 3.11 o superior. Instálalo (https://www.python.org/downloads/) y vuelve a correr `npm run dev`.',
    );
  }
  aviso('Instalando la API en backend/.venv (solo la primera vez o si cambia pyproject.toml)…');
  const env = { ...process.env, PYTHONDONTWRITEBYTECODE: '1' };
  const ok =
    instalador === 'uv'
      ? correr('uv', ['pip', 'install', '--python', python, '-e', BACKEND], { env })
      : correr(python, ['-m', 'pip', 'install', '--disable-pip-version-check', '-e', BACKEND], { env });
  if (!ok) throw new Error('No se pudo instalar la API. Revisa el mensaje de arriba y vuelve a intentarlo.');
  fs.writeFileSync(MARCA, huella, 'utf8');
  return python;
}

function pedirSalud(timeoutMs = 1500) {
  return new Promise((resolve) => {
    const req = http.get({ host: '127.0.0.1', port: PUERTO_API, path: '/api/v1/salud', timeout: timeoutMs }, (res) => {
      let cuerpo = '';
      res.on('data', (c) => (cuerpo += c));
      res.on('end', () => {
        try {
          resolve(res.statusCode === 200 ? JSON.parse(cuerpo) : null);
        } catch {
          resolve(null);
        }
      });
    });
    req.on('timeout', () => req.destroy());
    req.on('error', () => resolve(null));
  });
}

async function esperarApi(proceso, limiteMs = 60_000) {
  const inicio = Date.now();
  while (Date.now() - inicio < limiteMs) {
    if (proceso.exitCode !== null) return false;
    if (await pedirSalud()) return true;
    await new Promise((r) => setTimeout(r, 500));
  }
  return false;
}

function conPrefijo(flujo, prefijo, destino) {
  let resto = '';
  flujo.on('data', (trozo) => {
    const lineas = (resto + trozo.toString()).split(/\r?\n/);
    resto = lineas.pop() ?? '';
    for (const l of lineas) if (l.trim()) destino.write(`${prefijo} ${l}\n`);
  });
}

async function levantarApi(ip, puertoExpo) {
  const yaCorre = await pedirSalud();
  if (yaCorre) {
    aviso(`Ya hay una API en el puerto ${PUERTO_API} (simulado: ${yaCorre.simulado}). La uso tal cual.`);
    return null;
  }
  const python = prepararBackend();
  aviso(`Arrancando la API simulada en el puerto ${PUERTO_API}…`);
  const api = spawn(
    python,
    ['-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', String(PUERTO_API), '--workers', '1'],
    {
      cwd: BACKEND,
      env: {
        ...process.env,
        VERASCOPE_SIMULADO: '1',
        VERASCOPE_CORS: origenesCors(ip, puertoExpo),
        PYTHONDONTWRITEBYTECODE: '1',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    },
  );
  conPrefijo(api.stdout, '[api]', process.stdout);
  conPrefijo(api.stderr, '[api]', process.stderr);
  if (!(await esperarApi(api))) {
    detenerArbol(api);
    throw new Error(`La API no respondió en el puerto ${PUERTO_API}. Revisa los mensajes [api] de arriba.`);
  }
  return api;
}

async function principal() {
  const ip = elegirIp(os.networkInterfaces());
  const puertoExpo = await buscarPuerto();
  if (puertoExpo !== PUERTO_EXPO) aviso(`El puerto ${PUERTO_EXPO} está ocupado (¿otro expo start abierto?). Uso el ${puertoExpo}.`);
  let api = null;
  let urlApi = process.env.EXPO_PUBLIC_API_URL;

  if (urlApi) {
    aviso(`Uso la API de EXPO_PUBLIC_API_URL: ${urlApi} (no levanto la API local).`);
  } else {
    api = await levantarApi(ip, puertoExpo);
    urlApi = `http://${ip ?? 'localhost'}:${PUERTO_API}`;
    if (!ip) aviso('No encontré la IP de la red local: la app funcionará en la web, pero no en el teléfono.');
  }

  aviso(`La app usará la API en ${urlApi}`);
  aviso('Teléfono: misma red Wi-Fi que la laptop y escanea el QR con Expo Go. Web: pulsa w. Salir: Ctrl+C.');
  if (api && ES_WINDOWS) aviso('Si Windows pregunta por el firewall para Python, acepta "redes privadas".');

  // Se llama a la CLI de Expo con el mismo Node (sin npx ni shell): funciona igual en Windows, macOS y Linux.
  const cliExpo = require.resolve('expo/bin/cli', { paths: [FRONTEND] });
  const expo = spawn(process.execPath, [cliExpo, 'start', '--port', String(puertoExpo), ...process.argv.slice(2)], {
    cwd: FRONTEND,
    env: { ...process.env, EXPO_PUBLIC_API_URL: urlApi },
    stdio: 'inherit',
  });

  let apagando = false;
  const apagar = (codigo) => {
    if (apagando) return;
    apagando = true;
    detenerArbol(expo);
    detenerArbol(api);
    process.exit(codigo ?? 0);
  };
  // Último recurso: si el proceso termina por otra vía, no deja la API ocupando el puerto 8000.
  process.on('exit', () => detenerArbol(api));
  process.on('SIGINT', () => apagar(0));
  process.on('SIGTERM', () => apagar(0));
  expo.on('exit', (codigo) => apagar(codigo));
  api?.on('exit', (codigo) => {
    if (expo.exitCode === null) aviso(`La API se detuvo (código ${codigo}). La app seguirá abierta sin datos.`);
  });
}

if (require.main === module) {
  principal().catch((e) => {
    console.error(`\n[dev] ${e.message}`);
    process.exit(1);
  });
}

module.exports = { elegirIp, pythonDelVenv, origenesCors };
