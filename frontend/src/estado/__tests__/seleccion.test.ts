import { parametrosAnalyze } from '../seleccion';
import { estadoInicial } from '../store';

const piura = { lat: -5, lon: -80.5 };

describe('parametrosAnalyze', () => {
  it('sin celda no hay llamada', () => {
    expect(parametrosAnalyze(estadoInicial, 2025)).toBeNull();
  });

  it('"todo el registro" usa salud.ventana_fin; sin ese dato no hay llamada', () => {
    const seleccion = { ...estadoInicial, celda: piura };
    expect(parametrosAnalyze(seleccion, undefined)).toBeNull();
    expect(parametrosAnalyze(seleccion, 2025)).toEqual({
      variable: 'PRECTOTCORR',
      lat: -5,
      lon: -80.5,
      inicio: 1981,
      fin: 2025,
      indice: 'ONI',
    });
  });

  it('una ventana de menos de 10 años no se envía', () => {
    const seleccion = { ...estadoInicial, celda: piura, ventana: { inicio: 1981, fin: 1989 } };
    expect(parametrosAnalyze(seleccion, 2025)).toBeNull();
  });

  it('10 años exactos sí se envían', () => {
    const seleccion = { ...estadoInicial, celda: piura, ventana: { inicio: 1981, fin: 1990 } };
    expect(parametrosAnalyze(seleccion, 2025)).toMatchObject({ inicio: 1981, fin: 1990 });
  });
});
