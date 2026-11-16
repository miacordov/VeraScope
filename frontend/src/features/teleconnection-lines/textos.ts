/**
 * Textos de las líneas (frontend/CLAUDE.md §9 y §13). Todo número viene de la respuesta de `teleconnect`;
 * aquí solo se le da formato. Redacción fija y no causal: "ocurren a la vez y ambos responden a El Niño".
 */
import type { Linea, TipoLinea } from '@/shared/api/tipos';
import { celda, numero } from '@/shared/format';

export const FRASE_LINEAS = 'Ocurren a la vez y ambos responden a El Niño.';

export const NOMBRE_TIPO: Record<TipoLinea, string> = {
  opuesto: 'Efecto opuesto',
  mismo: 'Mismo efecto',
};

export const LEYENDA_LINEAS = 'Línea continua roja: efecto opuesto. Línea punteada: mismo efecto.';

type DatosLinea = Pick<Linea, 'tipo' | 'r' | 'distancia_km' | 'meses_coincidencia'>;

/** "r = −0.80 · 14,800 km · 23 meses a la vez" (sin el tipo). */
export function detalleLinea(linea: Omit<DatosLinea, 'tipo'>): string {
  const meses = linea.meses_coincidencia.length;
  return [
    `r = ${numero(linea.r, 2)}`,
    `${numero(linea.distancia_km, 0)} km`,
    `${meses} ${meses === 1 ? 'mes' : 'meses'} a la vez`,
  ].join(' · ');
}

/** "Efecto opuesto · r = −0.80 · 14,800 km · 23 meses a la vez". */
export function textoLinea(linea: DatosLinea): string {
  return `${NOMBRE_TIPO[linea.tipo]} · ${detalleLinea(linea)}`;
}

/** Etiqueta para lectores de pantalla: tipo, destino, r, distancia y la frase fija. */
export function etiquetaLinea(linea: DatosLinea & Pick<Linea, 'lat' | 'lon'>): string {
  return `${textoLinea(linea)}. Destino: celda ${celda(linea)}. ${FRASE_LINEAS}`;
}
