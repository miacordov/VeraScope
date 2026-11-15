/**
 * Reglas del selector de ventana (C5, frontend/CLAUDE.md §10). No calcula estadística: solo acota años.
 */
import { aniosDeVentana, MIN_ANIOS_VENTANA } from '@/estado/seleccion';
import { ANIO_INICIO_REGISTRO, type VentanaAnios } from '@/estado/store';

export const TEXTO_VENTANA_CORTA =
  'Elige al menos 10 años. Con menos, el ruido de un año a otro impide ver tendencias.';

/** Años concretos de la ventana; `fin = null` es "todo el registro" (`ventanaFin`). */
export function aniosElegidos(ventana: VentanaAnios, ventanaFin: number): { inicio: number; fin: number } {
  return { inicio: ventana.inicio, fin: ventana.fin ?? ventanaFin };
}

export function esVentanaCorta(ventana: VentanaAnios, ventanaFin: number): boolean {
  const { inicio, fin } = aniosElegidos(ventana, ventanaFin);
  return aniosDeVentana(inicio, fin) < MIN_ANIOS_VENTANA;
}

/**
 * Mueve el año inicial o el final `paso` años, sin salir de 1981 → `ventanaFin` ni cruzar el otro extremo.
 * Si el final vuelve al último año, se guarda `null` (todo el registro, el valor por defecto).
 */
export function moverAnio(
  ventana: VentanaAnios,
  ventanaFin: number,
  extremo: 'inicio' | 'fin',
  paso: number,
): VentanaAnios {
  const { inicio, fin } = aniosElegidos(ventana, ventanaFin);
  if (extremo === 'inicio') {
    return { inicio: Math.min(fin, Math.max(ANIO_INICIO_REGISTRO, inicio + paso)), fin: ventana.fin };
  }
  const nuevoFin = Math.max(inicio, Math.min(ventanaFin, fin + paso));
  return { inicio, fin: nuevoFin === ventanaFin ? null : nuevoFin };
}
