/**
 * Rectángulo de la celda elegida (frontend/CLAUDE.md §9, C3). Una celda de 0.5° cabe en menos de un píxel a la
 * escala inicial: se dibuja con un tamaño visual mínimo, centrado en la celda. Los datos siguen siendo de 0.5°.
 */
import { LADO_CELDA, type Coordenadas } from '@/shared/geo';

import { aPantalla, lonParaDibujo, type Tamano, type Vista } from './proyeccion';

export const LADO_VISUAL_MINIMO = 12;
export const BORDE_CELDA = 2;

export type Rectangulo = { x: number; y: number; ancho: number; alto: number };

export function rectanguloCelda(v: Vista, t: Tamano, celda: Coordenadas): Rectangulo {
  const centro = aPantalla(v, t, lonParaDibujo(celda.lon, v.lonCentro), celda.lat);
  const lado = Math.max(LADO_CELDA * v.escala, LADO_VISUAL_MINIMO);
  return { x: centro.x - lado / 2, y: centro.y - lado / 2, ancho: lado, alto: lado };
}
