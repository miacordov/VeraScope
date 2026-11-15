/**
 * Traduce la selección del store a los parámetros de `analyze`. No calcula estadística:
 * solo resuelve la ventana y bloquea el envío si es menor a 10 años (C5).
 */
import type { ParametrosAnalyze } from '@/shared/api/cliente';

import type { DatosEstado } from './store';

/** Ventana mínima para enviar un análisis (C5: 120 meses). */
export const MIN_ANIOS_VENTANA = 10;

export function aniosDeVentana(inicio: number, fin: number): number {
  return fin - inicio + 1;
}

export type Seleccion = Pick<DatosEstado, 'variable' | 'celda' | 'ventana' | 'indice'>;

/**
 * `null` si falta la celda, si aún no se conoce el último año (`ventanaFin`) o si la ventana es corta.
 * `ventana.fin = null` significa "todo el registro" = `salud.ventana_fin`.
 */
export function parametrosAnalyze(seleccion: Seleccion, ventanaFin: number | undefined): ParametrosAnalyze | null {
  const { celda, ventana, variable, indice } = seleccion;
  if (celda === null) return null;
  const fin = ventana.fin ?? ventanaFin;
  if (fin === undefined) return null;
  if (aniosDeVentana(ventana.inicio, fin) < MIN_ANIOS_VENTANA) return null;
  return { variable, lat: celda.lat, lon: celda.lon, inicio: ventana.inicio, fin, indice };
}
