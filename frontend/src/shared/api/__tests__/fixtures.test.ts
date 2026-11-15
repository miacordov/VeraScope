/**
 * Los fixtures son módulos TS anotados con los tipos del contrato: si el backend cambia un campo,
 * `tsc --noEmit` falla. Esta prueba comprueba además que siguen siendo copia fiel de los JSON simulados.
 */
import fs from 'node:fs';
import path from 'node:path';

import * as todos from '../__fixtures__';

const fixtures: Record<string, unknown> = { ...todos };

const carpetaBackend = path.resolve(__dirname, '../../../../../backend/app/catalogo/simulado');

const nombreDeFixture = (archivo: string) =>
  archivo.replace(/\.json$/, '').replace(/-([a-z0-9])/g, (_, c: string) => c.toUpperCase());

describe('fixtures del contrato', () => {
  const archivos = fs.readdirSync(carpetaBackend).filter((f) => f.endsWith('.json'));

  it('hay un fixture por cada JSON simulado del backend', () => {
    expect(archivos.map(nombreDeFixture).sort()).toEqual(Object.keys(fixtures).sort());
  });

  it.each(archivos)('%s es igual al JSON del backend (corre `npm run fixtures:copiar` si falla)', (archivo) => {
    const original = JSON.parse(fs.readFileSync(path.join(carpetaBackend, archivo), 'utf8'));
    expect(fixtures[nombreDeFixture(archivo)]).toEqual(original);
  });
});
