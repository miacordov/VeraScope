/**
 * Caché de respuestas (TanStack Query), frontend/CLAUDE.md §8. Versión MÍNIMA para el hito de la hora 6.
 * Dueño: F2 (`fe/graficos-enso`), que agrega la persistencia en AsyncStorage con `buster = salud.version_metodo`,
 * la reconsulta de `feed`/`salud` con el escaneo en curso y los esqueletos.
 */
import { QueryClient } from '@tanstack/react-query';

import { esErrorApi } from '@/shared/api/cliente';

/** Solo los errores de red se reintentan, y una sola vez. `power_lento` y los del contrato no. */
export function debeReintentar(intentos: number, error: unknown): boolean {
  return intentos < 1 && esErrorApi(error) && error.tipo === 'red';
}

export function crearQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        // Los años cerrados no cambian: volver a una celda no repite la llamada.
        staleTime: Infinity,
        gcTime: 24 * 60 * 60 * 1000,
        retry: debeReintentar,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
      },
    },
  });
}

export const queryClient = crearQueryClient();
