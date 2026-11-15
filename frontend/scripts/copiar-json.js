#!/usr/bin/env node
/**
 * Copia respuestas del backend al frontend. Solo LEE `../backend/`; nunca escribe allí.
 *
 *   node scripts/copiar-json.js demo       → ../backend/data/demo/respuestas/*.json  a  assets/demo/   (tal cual)
 *   node scripts/copiar-json.js fixtures   → ../backend/app/catalogo/simulado/*.json a  src/shared/api/__fixtures__/*.ts
 *
 * Los fixtures se escriben como módulos TypeScript anotados con el tipo del contrato: así `tsc` falla si el
 * backend cambia un campo (un JSON importado perdería los tipos literales de las enumeraciones).
 */
const fs = require('node:fs');
const path = require('node:path');

const raiz = path.resolve(__dirname, '..');
const backend = path.resolve(raiz, '..', 'backend');

/** Mismo emparejamiento archivo → modelo que `backend/app/api/simulados.py`. */
const TIPO_POR_ARCHIVO = {
  analyze: 'AnalyzeRespuesta',
  'compare-periods': 'ComparePeriodsRespuesta',
  'efecto-espejo': 'DemoRespuesta',
  'senal-o-ruido': 'DemoRespuesta',
  feed: 'FeedRespuesta',
  glosario: 'GlosarioRespuesta',
  layer: 'LayerRespuesta',
  teleconnect: 'TeleconnectRespuesta',
  'teleconnect-t2m': 'TeleconnectRespuesta',
  variables: 'VariablesRespuesta',
};

function jsonDe(carpeta) {
  if (!fs.existsSync(carpeta)) return [];
  return fs
    .readdirSync(carpeta)
    .filter((f) => f.endsWith('.json'))
    .sort();
}

function copiarDemo() {
  const origen = path.join(backend, 'data', 'demo', 'respuestas');
  const destino = path.join(raiz, 'assets', 'demo');
  const archivos = jsonDe(origen);
  if (archivos.length === 0) {
    console.log(`No hay respuestas de demo en ${origen}. El backend aún no las generó (jobs/instantaneas.py).`);
    return;
  }
  fs.mkdirSync(destino, { recursive: true });
  for (const f of archivos) {
    JSON.parse(fs.readFileSync(path.join(origen, f), 'utf8')); // falla si el archivo no es JSON válido
    fs.copyFileSync(path.join(origen, f), path.join(destino, f));
  }
  console.log(`Copiadas ${archivos.length} respuestas a assets/demo/.`);
}

function identificador(nombre) {
  return nombre.replace(/-([a-z0-9])/g, (_, c) => c.toUpperCase());
}

function copiarFixtures() {
  const origenSimulado = path.join(backend, 'app', 'catalogo', 'simulado');
  const origenCanonico = path.join(backend, 'app', 'catalogo');
  const destino = path.join(raiz, 'src', 'shared', 'api', '__fixtures__');
  // Fixtures simulados + canónicos (variables.json y glosario.json viven en catalogo/)
  const archivosSimulados = jsonDe(origenSimulado);
  const archivosCanonicosExtra = ['variables.json', 'glosario.json'].filter((f) =>
    fs.existsSync(path.join(origenCanonico, f)),
  );
  const archivos = [...archivosSimulados, ...archivosCanonicosExtra];
  if (archivos.length === 0) throw new Error(`No se encontraron JSON simulados en ${origenSimulado}.`);
  fs.rmSync(destino, { recursive: true, force: true });
  fs.mkdirSync(destino, { recursive: true });

  const exportaciones = [];
  for (const f of archivos) {
    const nombre = f.replace(/\.json$/, '');
    const tipo = TIPO_POR_ARCHIVO[nombre];
    if (!tipo) throw new Error(`No sé qué tipo del contrato corresponde a ${f}. Agrégalo a TIPO_POR_ARCHIVO.`);
    const rutaArchivo = archivosCanonicosExtra.includes(f)
      ? path.join(origenCanonico, f)
      : path.join(origenSimulado, f);
    const datos = JSON.parse(fs.readFileSync(rutaArchivo, 'utf8'));
    const contenido = [
      `// Generado por \`npm run fixtures:copiar\` desde backend/app/catalogo/${archivosCanonicosExtra.includes(f) ? '' : 'simulado/'}${f}. No editar a mano.`,
      `import type { ${tipo} } from '../tipos';`,
      '',
      `const fixture: ${tipo} = ${JSON.stringify(datos, null, 2)};`,
      '',
      'export default fixture;',
      '',
    ].join('\n');
    fs.writeFileSync(path.join(destino, `${nombre}.ts`), contenido, 'utf8');
    exportaciones.push(`export { default as ${identificador(nombre)} } from './${nombre}';`);
  }
  fs.writeFileSync(
    path.join(destino, 'index.ts'),
    ['// Generado por `npm run fixtures:copiar`. No editar a mano.', ...exportaciones, ''].join('\n'),
    'utf8',
  );
  console.log(`Escritos ${archivos.length} fixtures en src/shared/api/__fixtures__/.`);
}

const modo = process.argv[2];
if (modo === 'demo') copiarDemo();
else if (modo === 'fixtures') copiarFixtures();
else {
  console.error('Uso: node scripts/copiar-json.js <demo|fixtures>');
  process.exit(1);
}
