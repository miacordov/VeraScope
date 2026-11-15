/**
 * Caché de respuestas (TanStack Query), frontend/CLAUDE.md §8. Dueña: F2 (`fe/graficos-enso`).
 *
 * - `staleTime: Infinity`: los años cerrados no cambian; volver a una celda no repite la llamada.
 * - Solo los errores de red se reintentan, y una vez. `power_lento` y los del contrato no.
 * - La caché se guarda en AsyncStorage (ver `persistencia.ts` y `ProveedorConsultas.tsx`). Si el almacenamiento falla o viene vacío,
 *   la app funciona igual.
 * - Cuando el backend sube `version_metodo`, lo guardado se descarta.
 */
import { QueryClient, type Query } from '@tanstack/react-query';

import { esErrorApi } from '@/shared/api/cliente';

/** Solo los errores de red se reintentan, y una sola vez. `power_lento` y los del contrato no. */
export function debeReintentar(intentos: number, error: unknown): boolean {
  return intentos < 1 && esErrorApi(error) && error.tipo === 'red';
}

/** Rutas cuyas respuestas se guardan en el teléfono. `salud` no: se pide siempre al abrir. */
const RUTAS_PERSISTIDAS = new Set(['analyze', 'teleconnect', 'compare-periods', 'variables', 'glosario', 'demo']);

export function debePersistir(query: Pick<Query, 'queryKey' | 'state'>): boolean {
  const ruta = query.queryKey[0];
  return query.state.status === 'success' && typeof ruta === 'string' && RUTAS_PERSISTIDAS.has(ruta);
}

/** Lo guardado vale como máximo una semana. */
export const EDAD_MAXIMA_CACHE = 7 * 24 * 60 * 60 * 1000;

export function crearQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: Infinity,
        // Debe ser ≥ la edad máxima de lo persistido para que no se borre antes de guardarse.
        gcTime: EDAD_MAXIMA_CACHE,
        retry: debeReintentar,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
      },
    },
  });
}

export const queryClient = crearQueryClient();
