/**
 * Conversión de longitudes y cuantización a la celda de 0.5° (frontend/CLAUDE.md §9).
 * ÚNICO lugar donde viven estas conversiones: no las repitas en otro archivo.
 *
 * - La API habla en −180..180.
 * - Todo lo que se dibuja como PUNTO (celdas, líneas, marcadores) usa 0..360 (`lon360`), así la línea
 *   Piura → Indonesia cruza el Pacífico y no África.
 * - Los polígonos de las costas NO se convierten con `lon360` (dibujarían rayas): se proyectan con su
 *   longitud original y se dibujan dos veces (desplazamiento 0 y +360).
 */

export type Coordenadas = { lat: number; lon: number };

/** Lado de la celda de análisis, en grados (C3). */
export const LADO_CELDA = 0.5;

/** Longitud en 0..360 para dibujar puntos. */
export function lon360(lon: number): number {
  return (((lon % 360) + 360) % 360) + 0;
}

/** Longitud en −180..180 para enviar al servidor. 180 se escribe como −180. */
export function lonNormal(lon: number): number {
  return ((((lon + 180) % 360) + 360) % 360) - 180 + 0;
}

/** Redondea al centro de la malla de 0.5° (`0.5·round(x/0.5)`). El `+ 0` evita el −0. */
export function cuantizar(x: number): number {
  return LADO_CELDA * Math.round(x / LADO_CELDA) + 0;
}

/**
 * Celda de 0.5° de un toque: latitud acotada a ±90 y longitud en −180..180.
 * El servidor es la autoridad: si la `celda` de la respuesta difiere, manda la de la respuesta.
 */
export function cuantizarCelda({ lat, lon }: Coordenadas): Coordenadas {
  return {
    lat: Math.max(-90, Math.min(90, cuantizar(lat))),
    lon: lonNormal(cuantizar(lonNormal(lon))),
  };
}

export function mismaCelda(a: Coordenadas | null, b: Coordenadas | null): boolean {
  if (a === null || b === null) return a === b;
  return a.lat === b.lat && a.lon === b.lon;
}
