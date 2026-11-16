/**
 * Costas de Natural Earth 110m (dominio público) convertidas en trazados SVG (frontend/CLAUDE.md §9).
 *
 * Los anillos se proyectan con su longitud ORIGINAL (−180..180) y se dibujan dos veces, con desplazamiento
 * 0 y +360: así Asia y Oceanía (0) y las Américas (+360) quedan continuas en la vista del Pacífico.
 * Nunca se convierten con `lon360` (dibujarían rayas de lado a lado).
 * El trazado se calcula una vez por vista confirmada, no en cada cuadro del gesto.
 */
import tierraJson from '../../../assets/geo/tierra.json';

import { aPantalla, type Tamano, type Vista } from './proyeccion';

/** Cada anillo es una lista plana `[lon0, lat0, lon1, lat1, …]` en −180..180. */
export type Tierra = { fuente: string; licencia: string; anillos: number[][] };

export const tierra: Tierra = tierraJson;

export const DESPLAZAMIENTOS = [0, 360] as const;

const r = (x: number) => Math.round(x * 10) / 10;

/** Un anillo partido (la Antártida en ±180) queda abierto: cerrarlo con `Z` dibujaría una raya. */
export function anilloCerrado(a: readonly number[]): boolean {
  const n = a.length;
  return n >= 4 && a[0] === a[n - 2] && a[1] === a[n - 1];
}

/** `d` de un solo `<Path>` con todas las tierras visibles en la vista. */
export function trazadoCostas(v: Vista, t: Tamano, anillos: readonly (readonly number[])[] = tierra.anillos): string {
  const lonVisibleMin = v.lonCentro - t.ancho / 2 / v.escala;
  const lonVisibleMax = v.lonCentro + t.ancho / 2 / v.escala;
  const partes: string[] = [];
  for (const desplazamiento of DESPLAZAMIENTOS) {
    // Si la copia entera queda fuera de la vista, no se dibuja.
    if (desplazamiento - 180 > lonVisibleMax || desplazamiento + 180 < lonVisibleMin) continue;
    for (const anillo of anillos) {
      let d = '';
      for (let i = 0; i < anillo.length; i += 2) {
        const p = aPantalla(v, t, anillo[i] + desplazamiento, anillo[i + 1]);
        d += `${i === 0 ? 'M' : 'L'}${r(p.x)} ${r(p.y)}`;
      }
      partes.push(anilloCerrado(anillo) ? `${d}Z` : d);
    }
  }
  return partes.join('');
}
