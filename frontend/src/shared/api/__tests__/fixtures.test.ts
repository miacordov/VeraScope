/**
 * Los fixtures son módulos TS anotados con los tipos del contrato: si el backend cambia un campo,
 * `tsc --noEmit` falla. Esta prueba comprueba además que siguen siendo copia fiel de los JSON simulados.
 */
import fs from 'node:fs';
import path from 'node:path';

import * as todos from '../__fixtures__';

const fixtures: Record<string, unknown> = { ...todos };

const carpetaSimulado = path.resolve(__dirname, '../../../../../backend/app/catalogo/simulado');
const carpetaCanonico = path.resolve(__dirname, '../../../../../backend/app/catalogo');

// variables.json y glosario.json viven en catalogo/, el resto en catalogo/simulado/
const archivosCanonicosExtra = ['variables.json', 'glosario.json'].filter((f) =>
  fs.existsSync(path.join(carpetaCanonico, f)),
);

const nombreDeFixture = (archivo: string) =>
  archivo.replace(/\.json$/, '').replace(/-([a-z0-9])/g, (_, c: string) => c.toUpperCase());

const rutaDeArchivo = (archivo: string) =>
  archivosCanonicosExtra.includes(archivo)
    ? path.join(carpetaCanonico, archivo)
    : path.join(carpetaSimulado, archivo);

describe('fixtures del contrato', () => {
  const archivosSimulados = fs.readdirSync(carpetaSimulado).filter((f) => f.endsWith('.json'));
  const archivos = [...archivosSimulados, ...archivosCanonicosExtra];

  it('hay un fixture por cada JSON simulado del backend', () => {
    expect(archivos.map(nombreDeFixture).sort()).toEqual(Object.keys(fixtures).sort());
  });

  it.each(archivos)('%s es igual al JSON del backend (corre `npm run fixtures:copiar` si falla)', (archivo) => {
    const original = JSON.parse(fs.readFileSync(rutaDeArchivo(archivo), 'utf8'));
    expect(fixtures[nombreDeFixture(archivo)]).toEqual(original);
  });
});
