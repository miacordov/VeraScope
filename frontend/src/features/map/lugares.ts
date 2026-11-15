import type { Coordenadas } from '@/shared/geo';

/**
 * Accesos directos "Lugares" (frontend/CLAUDE.md §9): los de las demos. Centran la vista; NO cambian la celda.
 * Son puntos para mirar el mapa, no datos: no se envían al servidor.
 */
export const LUGARES: readonly { nombre: string; centro: Coordenadas }[] = [
  { nombre: 'Piura', centro: { lat: -5.0, lon: -80.5 } },
  { nombre: 'Borneo', centro: { lat: 0.5, lon: 114.0 } },
  { nombre: 'Norte de Australia', centro: { lat: -18.0, lon: 142.0 } },
];
