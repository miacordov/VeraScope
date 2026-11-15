import { analyze } from '../api/__fixtures__';
import { celda, conUnidad, lineaFuente, numero, periodo, pValor } from '../format';

describe('format (es-PE)', () => {
  it('usa punto decimal, separador de miles y signo menos tipográfico', () => {
    expect(numero(0.31)).toBe('0.31');
    expect(numero(-1234.5, 1)).toBe('−1,234.5');
  });

  it('siempre muestra la unidad y nunca inventa un valor', () => {
    expect(conUnidad(0.31, 'mm/día')).toBe('0.31 mm/día');
    expect(conUnidad(null, 'mm/día')).toBe('sin dato');
    expect(numero(Number.NaN)).toBe('sin dato');
  });

  it('formatea celda y periodo', () => {
    expect(celda({ lat: -5, lon: -80.5 })).toBe('−5.0°, −80.5°');
    expect(periodo('1981-01', '1990-12')).toBe('1981–1990');
  });

  it('formatea el p-valor sin inventarlo', () => {
    expect(pValor(0.004)).toBe('p = 0.004');
    expect(pValor(1)).toBe('p = 1.000');
    expect(pValor(1e-9)).toBe('p < 0.001');
    expect(pValor(null)).toBe('p: sin dato');
  });

  it('arma la línea de fuente solo con datos de la respuesta', () => {
    expect(lineaFuente(analyze)).toBe(
      `${analyze.fuente} · celda −5.0°, −80.5° · 1981–1990 · descargado ${analyze.descarga} · Índice: ONI, NOAA CPC`,
    );
  });
});
