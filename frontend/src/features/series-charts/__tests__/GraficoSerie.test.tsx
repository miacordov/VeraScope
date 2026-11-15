import { indiceVisible, trazoSerie } from '../GraficoSerie';

const x = (i: number) => i * 10;
const y = (v: number) => v;

describe('GraficoSerie', () => {
  it('los null son huecos: cortan la línea en dos tramos, no la bajan a cero', () => {
    const d = trazoSerie([1, 2, null, 4, 5], x, y);
    const tramos = d.match(/M/g) ?? [];
    expect(tramos).toHaveLength(2);
    expect(d).not.toMatch(/,0[LZ]?$/);
  });

  it('una serie sin datos no dibuja nada', () => {
    expect(trazoSerie([null, null], x, y)).toBe('');
  });

  it('mesVisible recorta hasta ese mes; null dibuja la serie completa', () => {
    const fechas = ['1981-01', '1981-02', '1981-03'];
    expect(indiceVisible(fechas, null)).toBe(2);
    expect(indiceVisible(fechas, '1981-02')).toBe(1);
    expect(indiceVisible(fechas, '2030-01')).toBe(2);
  });
});
