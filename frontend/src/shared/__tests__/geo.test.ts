import { cuantizar, cuantizarCelda, lon360, lonNormal, mismaCelda } from '../geo';

describe('lon360 (para dibujar puntos)', () => {
  it('lleva Piura e Indonesia a 0..360', () => {
    expect(lon360(-80)).toBe(280);
    expect(lon360(116)).toBe(116);
  });

  it('respeta los bordes ±180 y 360', () => {
    expect(lon360(180)).toBe(180);
    expect(lon360(-180)).toBe(180);
    expect(lon360(0)).toBe(0);
    expect(lon360(360)).toBe(0);
    expect(lon360(-360)).toBe(0);
    expect(Object.is(lon360(-0), 0)).toBe(true);
  });
});

describe('lonNormal (para enviar al servidor)', () => {
  it('vuelve a −180..180', () => {
    expect(lonNormal(280)).toBe(-80);
    expect(lonNormal(116)).toBe(116);
    expect(lonNormal(-80)).toBe(-80);
  });

  it('respeta los bordes ±180', () => {
    expect(lonNormal(180)).toBe(-180);
    expect(lonNormal(-180)).toBe(-180);
    expect(lonNormal(540)).toBe(-180);
    expect(lonNormal(359.5)).toBe(-0.5);
    expect(Object.is(lonNormal(360), 0)).toBe(true);
  });

  it('es la inversa de lon360 en todo el rango', () => {
    for (let lon = -179.5; lon < 180; lon += 0.5) {
      expect(lonNormal(lon360(lon))).toBeCloseTo(lon, 10);
    }
  });
});

describe('cuantización a la celda de 0.5°', () => {
  it('(-5.12, -80.37) → (-5.0, -80.5)', () => {
    expect(cuantizarCelda({ lat: -5.12, lon: -80.37 })).toEqual({ lat: -5.0, lon: -80.5 });
  });

  it('acepta un toque en 0..360 y devuelve lon en −180..180', () => {
    expect(cuantizarCelda({ lat: -5.12, lon: 279.63 })).toEqual({ lat: -5.0, lon: -80.5 });
  });

  it('no produce −0', () => {
    expect(Object.is(cuantizar(-0.1), 0)).toBe(true);
    expect(Object.is(cuantizarCelda({ lat: -0.2, lon: -0.2 }).lat, 0)).toBe(true);
  });

  it('cerca de ±180 queda dentro del rango del contrato', () => {
    expect(cuantizarCelda({ lat: 0, lon: 179.9 }).lon).toBe(-180);
    expect(cuantizarCelda({ lat: 0, lon: -179.9 }).lon).toBe(-180);
  });

  it('acota la latitud a ±90', () => {
    expect(cuantizarCelda({ lat: 95, lon: 0 }).lat).toBe(90);
    expect(cuantizarCelda({ lat: -95, lon: 0 }).lat).toBe(-90);
  });

  it('es idempotente', () => {
    const c = cuantizarCelda({ lat: 12.34, lon: 116.26 });
    expect(cuantizarCelda(c)).toEqual(c);
  });
});

describe('mismaCelda', () => {
  it('compara celdas y nulos', () => {
    expect(mismaCelda({ lat: 1, lon: 2 }, { lat: 1, lon: 2 })).toBe(true);
    expect(mismaCelda({ lat: 1, lon: 2 }, { lat: 1, lon: 2.5 })).toBe(false);
    expect(mismaCelda(null, null)).toBe(true);
    expect(mismaCelda(null, { lat: 1, lon: 2 })).toBe(false);
  });
});
