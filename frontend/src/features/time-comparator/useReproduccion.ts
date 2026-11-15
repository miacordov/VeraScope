/**
 * Reproducción en el tiempo (frontend/CLAUDE.md §10, `time-comparator`). Dueña: F2 (`fe/tiempo-comparador`).
 *
 * - Recorre toda la serie en ~30 s con `requestAnimationFrame`; el avance depende del tiempo transcurrido,
 *   no de cuántos cuadros se dibujan.
 * - Actualiza `mesVisible` solo cuando cambia el mes (no en cada cuadro).
 * - Al llegar al final se detiene y deja `mesVisible = null` (serie completa).
 * - No recalcula nada ni pide nada a la red: solo recorta lo visible.
 */
import { useEffect } from 'react';

import { useEstado } from '@/estado/store';

/** Duración de una reproducción completa, de punta a punta de la serie. */
export const DURACION_REPRODUCCION_MS = 30_000;

/** Mes que corresponde a un avance entre 0 y 1. `null` cuando ya terminó. */
export function mesParaAvance(fechas: readonly string[], avance: number): string | null {
  if (fechas.length === 0 || avance >= 1) return null;
  const i = Math.min(Math.floor(Math.max(avance, 0) * fechas.length), fechas.length - 1);
  return fechas[i] ?? null;
}

/** Avance (0 a 1) desde el que arranca la reproducción: sigue desde `mesVisible` si ya había uno. */
export function avanceInicial(fechas: readonly string[], mesVisible: string | null): number {
  if (mesVisible === null || fechas.length === 0) return 0;
  const i = fechas.indexOf(mesVisible);
  return i <= 0 || i >= fechas.length - 1 ? 0 : i / fechas.length;
}

export function useReproduccion(fechas: readonly string[]) {
  const reproduciendo = useEstado((e) => e.reproduciendo);

  useEffect(() => {
    if (!reproduciendo || fechas.length === 0) return;
    const { irAlMes, detener } = useEstado.getState();
    const inicio = Date.now() - avanceInicial(fechas, useEstado.getState().mesVisible) * DURACION_REPRODUCCION_MS;
    let ultimoMes = useEstado.getState().mesVisible;
    let cuadro = 0;

    const avanzar = () => {
      const mes = mesParaAvance(fechas, (Date.now() - inicio) / DURACION_REPRODUCCION_MS);
      if (mes === null) {
        detener();
        irAlMes(null);
        return;
      }
      if (mes !== ultimoMes) {
        ultimoMes = mes;
        irAlMes(mes);
      }
      cuadro = requestAnimationFrame(avanzar);
    };

    cuadro = requestAnimationFrame(avanzar);
    return () => cancelAnimationFrame(cuadro);
  }, [reproduciendo, fechas]);
}
