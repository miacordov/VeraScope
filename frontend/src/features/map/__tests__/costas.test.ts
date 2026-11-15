import { rectanguloCelda, LADO_VISUAL_MINIMO } from '../celda';
import { anilloCerrado, tierra, trazadoCostas } from '../costas';
import { escalaMinima, vistaInicial, type Tamano, type Vista } from '../proyeccion';

const t: Tamano = { ancho: 1200, alto: 480 };

/** Separa un `d` en subtrazados y devuelve las coordenadas x de cada uno. */
function subtrazados(d: string): number[][] {
  return d
    .split('M')
    .filter(Boolean)
    .map((s) => [...s.matchAll(/(-?[\d.]+) (-?[\d.]+)/g)].map((m) => Number(m[1])));
}

describe('tierra.json (Natural Earth 110m)', () => {
  it('trae longitudes originales en −180..180, sin convertir con lon360', () => {
    const lons = tierra.anillos.flatMap((a) => a.filter((_, i) => i % 2 === 0));
    expect(Math.min(...lons)).toBeGreaterThanOrEqual(-180);
    expect(Math.max(...lons)).toBeLessThanOrEqual(180);
    // Europa y África cruzan Greenwich: hay longitudes negativas y positivas pequeñas.
    expect(lons.some((l) => l < 0 && l > -20)).toBe(true);
  });

  it('ningún anillo salta más de 180° entre dos vértices', () => {
    for (const a of tierra.anillos) {
      for (let i = 2; i < a.length; i += 2) expect(Math.abs(a[i] - a[i - 2])).toBeLessThan(180);
    }
  });

  it('solo la Antártida (partida en ±180) queda abierta', () => {
    const abiertos = tierra.anillos.filter((a) => !anilloCerrado(a));
    expect(abiertos).toHaveLength(1);
    expect(Math.min(...abiertos[0].filter((_, i) => i % 2 === 1))).toBeLessThan(-60);
  });
});

describe('trazado de las costas', () => {
  it.each<[string, Vista]>([
    ['vista inicial', vistaInicial(t)],
    ['vista más alejada', { ...vistaInicial(t), escala: escalaMinima(t) }],
  ])('en la %s ningún trazo une un lado del mapa con el otro', (_, v) => {
    const d = trazadoCostas(v, t);
    for (const xs of subtrazados(d)) {
      for (let i = 1; i < xs.length; i++) expect(Math.abs(xs[i] - xs[i - 1])).toBeLessThan(t.ancho / 4);
    }
  });

  it('dibuja cada anillo dos veces (desplazamiento 0 y +360) cuando las dos copias se ven', () => {
    const d = trazadoCostas(vistaInicial(t), t);
    expect(subtrazados(d)).toHaveLength(tierra.anillos.length * 2);
  });

  it('el anillo abierto de la Antártida no se cierra con Z', () => {
    const abierto = tierra.anillos.filter((a) => !anilloCerrado(a));
    expect(trazadoCostas(vistaInicial(t), t, abierto)).not.toContain('Z');
  });
});

describe('rectángulo de la celda', () => {
  const piura = { lat: -5.0, lon: -80.5 };

  it('tiene un tamaño visual mínimo de 12 px a la escala inicial', () => {
    const r = rectanguloCelda(vistaInicial(t), t, piura);
    expect(r.ancho).toBe(LADO_VISUAL_MINIMO);
    expect(r.alto).toBe(LADO_VISUAL_MINIMO);
  });

  it('con mucho zoom mide lo que mide la celda de 0.5°', () => {
    const v = { ...vistaInicial(t), escala: 60 };
    expect(rectanguloCelda(v, t, piura).ancho).toBe(30);
  });
});
