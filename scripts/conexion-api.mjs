#!/usr/bin/env node
/**
 * Conexión backend ↔ frontend: pide a la API simulada (ya levantada) cada ruta que usa la app
 * (`frontend/src/shared/api/cliente.ts`) y comprueba que responde 200 con exactamente el JSON
 * simulado del backend. La prueba `fixtures.test.ts` del frontend ya exige que los fixtures de la
 * app sean copia de esos JSON; con esta, lo que la app espera es lo que la API sirve por HTTP.
 *
 * Uso: node scripts/conexion-api.mjs http://127.0.0.1:8000
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const simulado = path.join(raiz, 'backend', 'app', 'catalogo', 'simulado');
const base = `${(process.argv[2] ?? 'http://localhost:8000').replace(/\/+$/, '')}/api/v1`;
const ORIGEN_WEB = 'http://localhost:8081';

const json = (archivo) => JSON.parse(fs.readFileSync(path.join(simulado, archivo), 'utf8'));
const analyze = json('analyze.json');
const periodos = json('compare-periods.json');
const celda = { lat: analyze.celda.lat, lon: analyze.celda.lon };

// Ruta y parámetros tal como los arma `api` en cliente.ts; el valor esperado es el JSON simulado.
const casos = [
  ['salud', '/salud', {}, null],
  ['variables', '/variables', {}, 'variables.json'],
  ['glosario', '/glosario', {}, 'glosario.json'],
  [
    'analyze',
    '/analyze',
    {
      variable: analyze.variable,
      ...celda,
      inicio: Number(analyze.ventana.inicio.slice(0, 4)),
      fin: Number(analyze.ventana.fin.slice(0, 4)),
      indice: analyze.indice.id,
    },
    'analyze.json',
  ],
  ['teleconnect', '/teleconnect', { variable: analyze.variable, ...celda }, 'teleconnect.json'],
  ['teleconnect T2M', '/teleconnect', { variable: 'T2M', ...celda }, 'teleconnect-t2m.json'],
  [
    'compare-periods',
    '/compare-periods',
    {
      variable: analyze.variable,
      ...celda,
      p1_inicio: periodos.p1.anios[0],
      p1_fin: periodos.p1.anios[1],
      p2_inicio: periodos.p2.anios[0],
      p2_fin: periodos.p2.anios[1],
    },
    'compare-periods.json',
  ],
  ['scan/feed', '/scan/feed', { tipo: json('feed.json').tipo, pagina: 0 }, 'feed.json'],
  ['scan/layer', '/scan/layer', { variable: json('layer.json').variable }, 'layer.json'],
  ['demo efecto-espejo', '/demos/efecto-espejo', {}, 'efecto-espejo.json'],
  ['demo senal-o-ruido', '/demos/senal-o-ruido', {}, 'senal-o-ruido.json'],
];

let fallos = 0;
const informar = (ok, nombre, detalle = '') => {
  if (!ok) fallos += 1;
  console.log(`  ${ok ? 'ok   ' : 'FALLA'} ${nombre}${detalle ? ` — ${detalle}` : ''}`);
};

for (const [nombre, ruta, params, esperado] of casos) {
  const url = `${base}${ruta}?${new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]))}`;
  try {
    const respuesta = await fetch(url, { headers: { Origin: ORIGEN_WEB } });
    const cuerpo = await respuesta.json();
    if (respuesta.status !== 200) {
      informar(false, nombre, `HTTP ${respuesta.status}: ${JSON.stringify(cuerpo).slice(0, 200)}`);
      continue;
    }
    if (nombre === 'salud') {
      assert.equal(cuerpo.simulado, true, 'salud.simulado debería ser true');
      const cors = respuesta.headers.get('access-control-allow-origin');
      assert.equal(cors, ORIGEN_WEB, `CORS no permite ${ORIGEN_WEB} (llegó ${cors})`);
    } else {
      assert.deepStrictEqual(cuerpo, json(esperado));
    }
    informar(true, nombre);
  } catch (error) {
    informar(false, nombre, String(error.message ?? error).split('\n')[0]);
  }
}

// Un error del contrato llega con el cuerpo estándar que el cliente convierte en ErrorApi.
try {
  const respuesta = await fetch(`${base}/analyze?variable=PRECTOTCORR&lat=-5&lon=-80.5&inicio=1981&fin=1985`);
  const cuerpo = await respuesta.json();
  assert.equal(respuesta.status, 422);
  assert.equal(cuerpo.error?.codigo, 'ventana_corta');
  assert.equal(typeof cuerpo.error?.mensaje, 'string');
  informar(true, 'error estándar (ventana_corta)');
} catch (error) {
  informar(false, 'error estándar (ventana_corta)', String(error.message ?? error).split('\n')[0]);
}

process.exit(fallos ? 1 : 0);
