/**
 * Geometría de las líneas causa → consecuencia (frontend/CLAUDE.md §9). Funciones puras.
 *
 * Los dos extremos se dibujan en el espacio `lon360` (así Piura, a 280°, y Borneo, a 118°, se unen cruzando el
 * Pacífico y no África). Si la vista se desplazó más allá de 360°, los dos extremos se mueven juntos a la copia
 * más cercana al centro: nunca se separan en copias distintas.
 */
import { lon360, type Coordenadas } from '@/shared/geo';

import { aPantalla, type Punto, type Tamano, type Vista } from '../map/proyeccion';

/** Cuánto se curva el arco: el punto de control se aleja de la recta esta fracción de su largo. */
const CURVATURA = 0.18;
/** Puntos de muestra del arco para saber si un toque cayó sobre él. */
const MUESTRAS = 32;
/** Mitad de la zona táctil de una línea (la zona total mide ≥ 24 px, §9). */
export const TOLERANCIA_TOQUE = 12;

export type Arco = { d: string; inicio: Punto; fin: Punto; puntos: Punto[] };

/** Longitudes de dibujo de los dos extremos: `lon360`, desplazadas juntas hacia el centro de la vista. */
export function lonsDeDibujo(origen: Coordenadas, destino: Coordenadas, lonCentro: number): [number, number] {
  const a = lon360(origen.lon);
  const b = lon360(destino.lon);
  const desplazamiento = 360 * Math.round((lonCentro - (a + b) / 2) / 360);
  return [a + desplazamiento, b + desplazamiento];
}

/** Arco suave (curva cuadrática) de `origen` a `destino`, combado hacia arriba de la pantalla. */
export function arcoLinea(v: Vista, t: Tamano, origen: Coordenadas, destino: Coordenadas): Arco {
  const [lonA, lonB] = lonsDeDibujo(origen, destino, v.lonCentro);
  const inicio = aPantalla(v, t, lonA, origen.lat);
  const fin = aPantalla(v, t, lonB, destino.lat);

  const dx = fin.x - inicio.x;
  const dy = fin.y - inicio.y;
  const largo = Math.hypot(dx, dy);
  // Perpendicular a la recta; se elige el lado que sube en la pantalla (y menor).
  let nx = largo === 0 ? 0 : -dy / largo;
  let ny = largo === 0 ? 0 : dx / largo;
  if (ny > 0) {
    nx = -nx;
    ny = -ny;
  }
  const control = {
    x: (inicio.x + fin.x) / 2 + nx * largo * CURVATURA,
    y: (inicio.y + fin.y) / 2 + ny * largo * CURVATURA,
  };

  const puntos: Punto[] = [];
  for (let i = 0; i <= MUESTRAS; i += 1) {
    const s = i / MUESTRAS;
    const r = 1 - s;
    puntos.push({
      x: r * r * inicio.x + 2 * r * s * control.x + s * s * fin.x,
      y: r * r * inicio.y + 2 * r * s * control.y + s * s * fin.y,
    });
  }

  const d = `M${redondear(inicio.x)} ${redondear(inicio.y)} Q${redondear(control.x)} ${redondear(control.y)} ${redondear(fin.x)} ${redondear(fin.y)}`;
  return { d, inicio, fin, puntos };
}

const redondear = (x: number) => Math.round(x * 10) / 10;

function distanciaASegmento(p: Punto, a: Punto, b: Punto): number {
  const dx = b.x - a.x;
  const dy = b.y - a.y;
  const largo2 = dx * dx + dy * dy;
  const s = largo2 === 0 ? 0 : Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / largo2));
  return Math.hypot(p.x - (a.x + s * dx), p.y - (a.y + s * dy));
}

/** Distancia en píxeles de un punto al arco (a su trazo o al círculo del destino). */
export function distanciaAlArco(p: Punto, arco: Pick<Arco, 'puntos'>): number {
  let minima = Infinity;
  for (let i = 1; i < arco.puntos.length; i += 1) {
    minima = Math.min(minima, distanciaASegmento(p, arco.puntos[i - 1]!, arco.puntos[i]!));
  }
  return minima;
}

/** Índice del arco más cercano al toque dentro de la zona táctil, o −1 si el toque no cayó en ninguno. */
export function lineaTocada(p: Punto, arcos: readonly Pick<Arco, 'puntos'>[], tolerancia = TOLERANCIA_TOQUE): number {
  let elegido = -1;
  let mejor = tolerancia;
  arcos.forEach((arco, i) => {
    const d = distanciaAlArco(p, arco);
    if (d <= mejor) {
      mejor = d;
      elegido = i;
    }
  });
  return elegido;
}
