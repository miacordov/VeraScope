import { esVentanaCorta, moverAnio } from '../ventana';

const FIN = 2025;

describe('selector de ventana', () => {
  it('por defecto es todo el registro y no es corta', () => {
    expect(esVentanaCorta({ inicio: 1981, fin: null }, FIN)).toBe(false);
  });

  it('menos de 10 años es corta; 10 ya no', () => {
    expect(esVentanaCorta({ inicio: 2017, fin: null }, FIN)).toBe(true);
    expect(esVentanaCorta({ inicio: 2016, fin: null }, FIN)).toBe(false);
    expect(esVentanaCorta({ inicio: 1981, fin: 1990 }, FIN)).toBe(false);
  });

  it('no baja de 1981 ni pasa del último año completo', () => {
    expect(moverAnio({ inicio: 1981, fin: null }, FIN, 'inicio', -1)).toEqual({ inicio: 1981, fin: null });
    expect(moverAnio({ inicio: 1981, fin: null }, FIN, 'fin', 1)).toEqual({ inicio: 1981, fin: null });
  });

  it('el inicio no cruza el final y viceversa', () => {
    expect(moverAnio({ inicio: 2000, fin: 2000 }, FIN, 'inicio', 1)).toEqual({ inicio: 2000, fin: 2000 });
    expect(moverAnio({ inicio: 2000, fin: 2000 }, FIN, 'fin', -1)).toEqual({ inicio: 2000, fin: 2000 });
  });

  it('volver al último año guarda null (todo el registro)', () => {
    expect(moverAnio({ inicio: 1981, fin: 2024 }, FIN, 'fin', 1)).toEqual({ inicio: 1981, fin: null });
    expect(moverAnio({ inicio: 1981, fin: null }, FIN, 'fin', -1)).toEqual({ inicio: 1981, fin: 2024 });
  });
});
