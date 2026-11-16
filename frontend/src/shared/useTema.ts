/**
 * Hooks del modo claro u oscuro (frontend/CLAUDE.md §13). El proveedor está en `ProveedorTema.tsx`, separado para que
 * los componentes y sus pruebas no carguen AsyncStorage (módulo nativo). Sin proveedor se usa el modo oscuro.
 */

import { createContext, useContext, useMemo } from 'react';

import { paletas, type Colores, type Modo } from './tema';

export type ValorTema = {
  modo: Modo;
  colores: Colores;
  alternarModo: () => void;
};

export const ContextoTema = createContext<ValorTema>({
  modo: 'oscuro',
  colores: paletas.oscuro,
  alternarModo: () => {},
});

/** Modo actual, sus colores y la acción para cambiarlo. */
export function useTema(): ValorTema {
  return useContext(ContextoTema);
}

/**
 * Estilos que dependen del modo. `fabrica` se declara fuera del componente
 * (`const crearEstilos = (colores: Colores) => StyleSheet.create({...})`) y se recalcula solo al cambiar de modo.
 */
export function useEstilos<T>(fabrica: (colores: Colores) => T): T {
  const { colores } = useTema();
  return useMemo(() => fabrica(colores), [fabrica, colores]);
}
