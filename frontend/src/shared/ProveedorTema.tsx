/**
 * Proveedor del modo claro u oscuro (frontend/CLAUDE.md §13). No va al store: es una preferencia de la interfaz,
 * no del análisis. Los componentes usan los hooks de `useTema.ts`.
 *
 * - Mientras el usuario no elija, se sigue el modo del teléfono o del navegador.
 * - Lo que el usuario elige con el botón se guarda en AsyncStorage. Si el almacenamiento falla (modo privado del
 *   navegador), la app funciona igual y solo olvida la elección al cerrarse.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useColorScheme } from 'react-native';

import { paletas, type Modo } from './tema';
import { ContextoTema } from './useTema';

export const LLAVE_MODO = 'verascope.modo';

export function ProveedorTema({ children }: { children: ReactNode }) {
  const delSistema: Modo = useColorScheme() === 'light' ? 'claro' : 'oscuro';
  const [elegido, setElegido] = useState<Modo | null>(null);

  useEffect(() => {
    let vigente = true;
    AsyncStorage.getItem(LLAVE_MODO)
      .then((guardado) => {
        if (vigente && (guardado === 'claro' || guardado === 'oscuro')) setElegido(guardado);
      })
      .catch(() => {});
    return () => {
      vigente = false;
    };
  }, []);

  const modo = elegido ?? delSistema;

  const alternarModo = useCallback(() => {
    const siguiente: Modo = modo === 'oscuro' ? 'claro' : 'oscuro';
    setElegido(siguiente);
    AsyncStorage.setItem(LLAVE_MODO, siguiente).catch(() => {});
  }, [modo]);

  const valor = useMemo(() => ({ modo, colores: paletas[modo], alternarModo }), [modo, alternarModo]);

  return <ContextoTema.Provider value={valor}>{children}</ContextoTema.Provider>;
}
