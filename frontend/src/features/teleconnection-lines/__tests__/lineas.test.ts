import { teleconnect } from '@/shared/api/__fixtures__';
import type { Linea } from '@/shared/api/tipos';
import { colores } from '@/shared/tema';

import { aPantalla, vistaInicial, type Tamano } from '../../map/proyeccion';
import { arcoLinea, distanciaAlArco, lineaTocada, lonsDeDibujo } from '../arco';
import { encendidaEn, estiloLinea, GROSOR_LINEA, OPACIDAD_LINEA, PUNTEADO } from '../estilo';
import { etiquetaLinea, FRASE_LINEAS, textoLinea } from '../textos';

const opuesta: Linea = {
  tipo: 'opuesto',
  lat: 0,
  lon: 118,
  r: -0.8,
  p_ajustado: 1e-6,
  distancia_km: 14800,
  r_el_nino_origen: 0.62,
  r_el_nino_destino: -0.55,
  meses_coincidencia: [
    { fecha: '1998-01', fase: 'nino' },
    { fecha: '1998-02', fase: 'nino' },
  ],
};
const misma: Linea = { ...opuesta, tipo: 'mismo', lat: -2, lon: -120, r: 0.77 };

describe('estilo de las líneas según mesVisible', () => {
  it('sin mesVisible todas se ven (≈ 0.8)', () => {
    expect(estiloLinea(opuesta, null).opacidad).toBe(OPACIDAD_LINEA.reposo);
    expect(estiloLinea(misma, null).opacidad).toBe(OPACIDAD_LINEA.reposo);
  });

  it('dentro de meses_coincidencia se enciende: opacidad 1 y trazo grueso', () => {
    const e = estiloLinea(opuesta, '1998-02');
    expect(encendidaEn(opuesta, '1998-02')).toBe(true);
    expect(e.opacidad).toBe(1);
    expect(e.grosor).toBe(GROSOR_LINEA.encendida);
  });

  it('fuera de meses_coincidencia queda tenue (≈ 0.15)', () => {
    expect(estiloLinea(opuesta, '1999-06').opacidad).toBeCloseTo(0.15);
    expect(encendidaEn(opuesta, '1999-06')).toBe(false);
  });

  it('efecto opuesto = continua roja; mismo efecto = punteada', () => {
    expect(estiloLinea(opuesta, null)).toMatchObject({
      color: colores.nino,
      punteado: undefined,
    });
    expect(estiloLinea(misma, null)).toMatchObject({
      color: colores.texto,
      punteado: PUNTEADO,
    });
  });

  it('la línea elegida es más gruesa en reposo', () => {
    expect(estiloLinea(opuesta, null, true).grosor).toBeGreaterThan(estiloLinea(opuesta, null).grosor);
  });
});

describe('arco en el espacio lon360', () => {
  const t: Tamano = { ancho: 1200, alto: 480 };
  const v = vistaInicial(t);
  const piura = { lat: -6, lon: -80 };

  it('Piura (280°) → Borneo (118°) cruza el Pacífico, no África', () => {
    const [a, b] = lonsDeDibujo(piura, { lat: 0, lon: 118 }, v.lonCentro);
    expect(a).toBe(280);
    expect(b).toBe(118);
    const arco = arcoLinea(v, t, piura, { lat: 0, lon: 118 });
    // Todo el arco queda entre los dos extremos a lo ancho (sobre el Pacífico), dentro de la pantalla.
    const xBorneo = aPantalla(v, t, 118, 0).x;
    const xPiura = aPantalla(v, t, 280, -6).x;
    for (const p of arco.puntos) {
      expect(p.x).toBeGreaterThanOrEqual(xBorneo - 0.5);
      expect(p.x).toBeLessThanOrEqual(xPiura + 0.5);
    }
    expect(arco.d.startsWith('M')).toBe(true);
    expect(arco.d).toContain('Q');
  });

  it('los dos extremos se mueven juntos a la copia más cercana al centro de la vista', () => {
    const [a, b] = lonsDeDibujo(piura, { lat: 0, lon: 118 }, 560);
    expect(b - a).toBe(118 - 280);
    expect(a).toBe(640);
  });

  it('el arco se comba hacia arriba de la pantalla', () => {
    const arco = arcoLinea(v, t, piura, { lat: -6, lon: 118 });
    const medio = arco.puntos[Math.floor(arco.puntos.length / 2)]!;
    expect(medio.y).toBeLessThan(arco.inicio.y);
  });

  it('un toque sobre la línea la detecta (zona ≥ 24 px) y uno lejano no', () => {
    const arcos = [arcoLinea(v, t, piura, { lat: 0, lon: 118 }), arcoLinea(v, t, piura, { lat: -30, lon: 200 })];
    const sobre = arcos[1]!.puntos[10]!;
    expect(lineaTocada({ x: sobre.x, y: sobre.y + 10 }, arcos)).toBe(1);
    expect(lineaTocada({ x: 5, y: 470 }, arcos)).toBe(-1);
    expect(distanciaAlArco(arcos[0]!.fin, arcos[0]!)).toBeLessThan(1);
  });
});

describe('textos de las líneas', () => {
  it('todo sale de la respuesta y la redacción no es causal', () => {
    expect(textoLinea(opuesta)).toBe('Efecto opuesto · r = −0.80 · 14,800 km · 2 meses a la vez');
    expect(etiquetaLinea(misma)).toContain(FRASE_LINEAS);
    expect(FRASE_LINEAS).toBe('Ocurren a la vez y ambos responden a El Niño.');
    expect(`${textoLinea(opuesta)} ${FRASE_LINEAS}`).not.toMatch(/caus|provoca/i);
  });

  it('funciona con el fixture de teleconnect', () => {
    expect(textoLinea(teleconnect.lineas[0]!)).toMatch(/^Efecto opuesto · r = /);
  });
});
