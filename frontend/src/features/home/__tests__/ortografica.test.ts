import { circuloMaximo, proyectar, trazadoArco, trazadoTierra } from '../ortografica';

const CENTRO = { lon: -155, lat: 0 };
const R = 100;

describe('proyección ortográfica del globo del Inicio', () => {
  test('el centro de la vista es el centro del globo y el norte queda arriba', () => {
    const centro = proyectar(-155, 0, CENTRO, R);
    expect(centro.visible).toBe(true);
    expect(centro.x).toBeCloseTo(0, 9);
    expect(centro.y).toBeCloseTo(0, 9);
    const norte = proyectar(-155, 45, CENTRO, R);
    expect(norte.visible).toBe(true);
    expect(norte.y).toBeLessThan(0);
    expect(proyectar(-145, 0, CENTRO, R).x).toBeGreaterThan(0); // el este queda a la derecha
  });

  test('un punto de la cara oculta no se ve y se lleva al borde', () => {
    const p = proyectar(25, 10, CENTRO, R); // África, del otro lado del Pacífico
    expect(p.visible).toBe(false);
    expect(Math.hypot(p.x, p.y)).toBeCloseTo(R, 5);
  });

  test('Piura y el norte de Australia (la línea de la demo) quedan en la cara visible', () => {
    expect(proyectar(-80, -6, CENTRO, R).visible).toBe(true);
    expect(proyectar(132, -14, CENTRO, R).visible).toBe(true);
  });

  test('el círculo máximo empieza y termina en sus extremos y cruza el Pacífico', () => {
    const arco = circuloMaximo({ lon: -80, lat: -6 }, { lon: 132, lat: -14 }, 10);
    expect(arco).toHaveLength(11);
    expect(arco[0].lon).toBeCloseTo(-80, 6);
    expect(arco[10].lat).toBeCloseTo(-14, 6);
    expect(Math.abs(arco[5].lon)).toBeGreaterThan(150); // el punto medio cae cerca del antimeridiano, no sobre África
  });

  test('el arco es un solo trazo continuo cuando se ve entero', () => {
    const d = trazadoArco({ lon: -80, lat: -6 }, { lon: 132, lat: -14 }, CENTRO, R);
    expect(d.startsWith('M')).toBe(true);
    expect(d.match(/M/g)).toHaveLength(1);
  });

  test('una tierra que sigue por la cara oculta no tapa el centro del globo', () => {
    // Una franja que asoma por el borde oeste (lon −240 ≈ 120 E) y da la vuelta por detrás del planeta.
    const franja = [120, -10, 120, 10, 60, 10, 0, 10, 0, -10, 60, -10, 120, -10];
    const d = trazadoTierra([franja], CENTRO, R);
    const puntos = [...d.matchAll(/[ML](-?[\d.]+) (-?[\d.]+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
    expect(puntos.length).toBeGreaterThan(0);
    // Todo lo dibujado queda cerca del borde izquierdo: nada cruza el centro del Pacífico.
    expect(Math.max(...puntos.map(([x]) => x))).toBeLessThan(-R / 2);
  });

  test('una tierra que entra y sale por el mismo lado se cierra siguiendo el borde, no con una recta', () => {
    // Como Norteamérica: la costa visible toca el borde derecho arriba y abajo y el resto queda detrás.
    const continente = [-80, 40, -80, -30, -40, -30, -40, 40, -80, 40];
    const d = trazadoTierra([continente], CENTRO, R);
    const puntos = [...d.matchAll(/[ML](-?[\d.]+) (-?[\d.]+)/g)].map((m) => [Number(m[1]), Number(m[2])]);
    // El cierre pasa por el borde derecho a la altura del ecuador (una recta entre los extremos no lo haría).
    expect(puntos.some(([x, y]) => x > 0.99 * R && Math.abs(y) < 0.2 * R)).toBe(true);
    expect(Math.min(...puntos.map(([x]) => x))).toBeGreaterThan(0);
  });

  test('las costas que quedan enteras en la cara oculta no se dibujan', () => {
    const lejos = [20, 0, 30, 0, 30, 10, 20, 0];
    const cerca = [-160, 0, -150, 0, -150, 10, -160, 0];
    expect(trazadoTierra([lejos], CENTRO, R)).toBe('');
    expect(trazadoTierra([cerca], CENTRO, R)).toMatch(/^M.*Z$/);
  });
});
