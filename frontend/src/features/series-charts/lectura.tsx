/**
 * Lectura con el dedo o el cursor, compartida entre los tres gráficos del panel (frontend/CLAUDE.md §10).
 * Vive en un contexto de React, no en el store: es un detalle de la vista y cambia en cada movimiento.
 * Dueña: F2 (`fe/graficos-enso`).
 */
import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

type Lectura = {
  /** Posición (índice de mes) que se está leyendo, o `null` si nadie toca un gráfico. */
  indice: number | null;
  fijarIndice: (indice: number | null) => void;
};

const ContextoLectura = createContext<Lectura>({ indice: null, fijarIndice: () => {} });

export function ProveedorLectura({ children }: { children: ReactNode }) {
  const [indice, fijarIndice] = useState<number | null>(null);
  const valor = useMemo(() => ({ indice, fijarIndice }), [indice]);
  return <ContextoLectura.Provider value={valor}>{children}</ContextoLectura.Provider>;
}

export function useLectura(): Lectura {
  return useContext(ContextoLectura);
}
