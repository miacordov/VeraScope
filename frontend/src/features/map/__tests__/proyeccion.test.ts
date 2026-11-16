import { cuantizarCelda } from '@/shared/geo';

import { LUGARES } from '../lugares';
import {
  acercar,
  aMapa,
  aPantalla,
  centrarEn,
  desplazar,
  ESCALA_MAXIMA,
  escalaMinima,
  factorRueda,
  lonParaDibujo,
  vistaInicial,
  type Tamano,
} from '../proyeccion';

const telefono: Tamano = { ancho: 360, alto: 270 };
const laptop: Tamano = { ancho: 1200, alto: 480 };

const piura = { lat: -5.0, lon: -80.5 };
const indonesia = { lat: -2.0, lon: 116.0 };

describe.each([
  ['teléfono', telefono],
  ['laptop', laptop],
])('vista inicial en %s', (_, t) => {
  const v = vistaInicial(t);
  const enPantalla = (c: { lat: number; lon: number }) => aPantalla(v, t, lonParaDibujo(c.lon, v.lonCentro), c.lat);

  it('se ven Piura (~280°) e Indonesia (~116°)', () => {
    for (const lugar of [piura, indonesia]) {
      const p = enPantalla(lugar);
      expect(p.x).toBeGreaterThanOrEqual(0);
      expect(p.x).toBeLessThanOrEqual(t.ancho);
      expect(p.y).toBeGreaterThanOrEqual(0);
      expect(p.y).toBeLessThanOrEqual(t.alto);
    }
  });

  it('la recta Piura → Indonesia cruza el Pacífico, no África', () => {
    const a = enPantalla(piura);
    const b = enPantalla(indonesia);
    // Indonesia queda a la IZQUIERDA de Piura: entre ambas solo hay océano Pacífico (116° → 280°).
    expect(b.x).toBeLessThan(a.x);
    const lonMedia = aMapa(v, t, { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 }).lon;
    expect(lonMedia).toBeGreaterThan(160);
    expect(lonMedia).toBeLessThan(240);
  });
});

describe('proyección', () => {
  const v = vistaInicial(laptop);

  it('aMapa deshace aPantalla', () => {
    const p = aPantalla(v, laptop, 250, 12.5);
    const c = aMapa(v, laptop, p);
    expect(c.lon).toBeCloseTo(250);
    expect(c.lat).toBeCloseTo(12.5);
  });

  it('dibuja los puntos en 0..360 y toma la copia más cercana al centro', () => {
    expect(lonParaDibujo(-80, 210)).toBe(280);
    expect(lonParaDibujo(116, 210)).toBe(116);
    expect(lonParaDibujo(10, 380)).toBe(370);
  });
});

describe('gestos y botones', () => {
  const t = laptop;
  const v = vistaInicial(t);

  it('acercar deja quieto el punto bajo el foco', () => {
    const foco = { x: 300, y: 100 };
    const antes = aMapa(v, t, foco);
    const despues = aMapa(acercar(v, t, 2, foco), t, foco);
    expect(despues.lon).toBeCloseTo(antes.lon);
    expect(despues.lat).toBeCloseTo(antes.lat);
  });

  it('el zoom tiene tope por arriba y por abajo', () => {
    expect(acercar(v, t, 1000).escala).toBe(ESCALA_MAXIMA);
    expect(acercar(v, t, 0.0001).escala).toBe(escalaMinima(t));
  });

  it('no se puede arrastrar fuera del mundo dibujado', () => {
    const lejos = desplazar(v, t, -1e6, 1e6);
    const borde = aMapa(lejos, t, { x: t.ancho, y: t.alto });
    expect(borde.lon).toBeLessThanOrEqual(540 + 1e-9);
    expect(borde.lat).toBeGreaterThanOrEqual(-90 - 1e-9);
  });

  it('los accesos directos centran la vista sin cambiar el zoom', () => {
    for (const { centro } of LUGARES) {
      const c = centrarEn(acercar(v, t, 4), t, centro);
      const p = aPantalla(c, t, lonParaDibujo(centro.lon, c.lonCentro), centro.lat);
      expect(p.x).toBeCloseTo(t.ancho / 2);
      expect(p.y).toBeCloseTo(t.alto / 2);
      expect(c.escala).toBeCloseTo(acercar(v, t, 4).escala);
    }
  });

  it('tocar un punto de la pantalla da la celda de 0.5° de ese lugar', () => {
    const p = aPantalla(v, t, lonParaDibujo(-80.37, v.lonCentro), -5.12);
    expect(cuantizarCelda(aMapa(v, t, p))).toEqual({ lat: -5.0, lon: -80.5 });
  });
});

describe('rueda del ratón (web)', () => {
  it('hacia arriba acerca, hacia abajo aleja y sin giro no cambia', () => {
    expect(factorRueda(-100)).toBeGreaterThan(1);
    expect(factorRueda(100)).toBeLessThan(1);
    expect(factorRueda(0)).toBe(1);
  });

  it('dos giros pequeños suman lo mismo que uno grande', () => {
    expect(factorRueda(-50) * factorRueda(-50)).toBeCloseTo(factorRueda(-100));
  });

  it('las líneas de Firefox cuentan como píxeles y un giro brusco tiene tope', () => {
    expect(factorRueda(-3, 1)).toBeCloseTo(factorRueda(-48, 0));
    expect(factorRueda(-100_000)).toBe(2);
    expect(factorRueda(100_000)).toBe(0.5);
  });
});
