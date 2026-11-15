/**
 * Zoom con la rueda del ratón en web (frontend/CLAUDE.md §9: "En web, la rueda del ratón hace zoom").
 *
 * Archivo solo web: el `onWheel` de React es pasivo y no puede impedir que la página se desplace mientras se
 * hace zoom, así que se escucha `wheel` directamente en el nodo del lienzo con `passive: false`. En React Native
 * for Web la referencia de un `View` es ese nodo. La versión para el teléfono (`rueda.ts`) no hace nada.
 */
import { useEffect, useRef } from 'react';

import { factorRueda } from './proyeccion';
import type { AlGirarRueda, RefLienzo } from './rueda';

/** Lo mínimo que se usa del nodo y del evento del navegador. */
type EventoRueda = {
  deltaY: number;
  deltaMode: number;
  clientX: number;
  clientY: number;
  preventDefault: () => void;
};
type NodoWeb = {
  addEventListener: (tipo: 'wheel', fn: (e: EventoRueda) => void, opciones: { passive: false }) => void;
  removeEventListener: (tipo: 'wheel', fn: (e: EventoRueda) => void) => void;
  getBoundingClientRect: () => { left: number; top: number };
};

export function useZoomConRueda(lienzo: RefLienzo, alGirar: AlGirarRueda): void {
  // La función más reciente, sin volver a registrar el evento en cada render.
  const ultimo = useRef(alGirar);
  useEffect(() => {
    ultimo.current = alGirar;
  });

  useEffect(() => {
    const nodo = lienzo.current as unknown as NodoWeb | null;
    if (!nodo?.addEventListener) return;
    const alRodar = (e: EventoRueda) => {
      e.preventDefault();
      const caja = nodo.getBoundingClientRect();
      ultimo.current(factorRueda(e.deltaY, e.deltaMode), { x: e.clientX - caja.left, y: e.clientY - caja.top });
    };
    nodo.addEventListener('wheel', alRodar, { passive: false });
    return () => nodo.removeEventListener('wheel', alRodar);
  }, [lienzo]);
}
