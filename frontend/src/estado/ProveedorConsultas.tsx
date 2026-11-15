/**
 * Proveedor de TanStack Query con la caché guardada en AsyncStorage (frontend/CLAUDE.md §8).
 * Reemplaza a `QueryClientProvider` en `app/_layout.tsx`. Dueña: F2 (`fe/graficos-enso`).
 */
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { useEffect, type ReactNode } from 'react';

import { useSalud } from '@/shared/api/consultas';

import { BUSTER_CACHE, descartarSiCambioVersion, persistidor } from './persistencia';
import { debePersistir, EDAD_MAXIMA_CACHE, queryClient } from './queryClient';

function VigilaVersionMetodo() {
  const version = useSalud().data?.version_metodo;
  useEffect(() => {
    if (version !== undefined) void descartarSiCambioVersion(queryClient, version);
  }, [version]);
  return null;
}

export function ProveedorConsultas({ children }: { children: ReactNode }) {
  return (
    <PersistQueryClientProvider
      client={queryClient}
      persistOptions={{
        persister: persistidor,
        buster: BUSTER_CACHE,
        maxAge: EDAD_MAXIMA_CACHE,
        dehydrateOptions: { shouldDehydrateQuery: debePersistir },
      }}>
      <VigilaVersionMetodo />
      {children}
    </PersistQueryClientProvider>
  );
}
