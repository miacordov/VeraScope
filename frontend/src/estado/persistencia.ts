/**
 * Persistencia de la caché de TanStack Query en AsyncStorage (frontend/CLAUDE.md §8). Dueña: F2.
 * Separado de `queryClient.ts` para que las pruebas que solo usan el cliente no carguen el módulo nativo.
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';
import type { QueryClient } from '@tanstack/react-query';

/** Lo guardado se descarta si cambia esta versión de la app (cambio de forma de la caché). */
export const BUSTER_CACHE = 'verascope-cache-1';
/** Llave donde se recuerda el `version_metodo` del backend con el que se llenó la caché. */
export const LLAVE_VERSION_METODO = 'verascope:version_metodo';

/** AsyncStorage envuelto: si falla (modo privado del navegador, almacenamiento lleno), no rompe la app. */
export const almacenamientoSeguro = {
  getItem: async (llave: string) => {
    try {
      return await AsyncStorage.getItem(llave);
    } catch {
      return null;
    }
  },
  setItem: async (llave: string, valor: string) => {
    try {
      await AsyncStorage.setItem(llave, valor);
    } catch {
      // Sin almacenamiento la app sigue funcionando; solo no recuerda la caché.
    }
  },
  removeItem: async (llave: string) => {
    try {
      await AsyncStorage.removeItem(llave);
    } catch {
      // Igual que arriba.
    }
  },
};

export const persistidor = createAsyncStoragePersister({
  storage: almacenamientoSeguro,
  key: 'verascope:cache',
  throttleTime: 1000,
});

/**
 * Si el backend cambió un cálculo (`version_metodo` distinto al guardado), borra las respuestas guardadas
 * (todo menos `salud`) y recuerda la versión nueva. Devuelve `true` si borró algo.
 */
export async function descartarSiCambioVersion(cliente: QueryClient, versionMetodo: number): Promise<boolean> {
  const guardada = await almacenamientoSeguro.getItem(LLAVE_VERSION_METODO);
  const actual = String(versionMetodo);
  if (guardada === actual) return false;
  await almacenamientoSeguro.setItem(LLAVE_VERSION_METODO, actual);
  if (guardada === null) return false;
  cliente.removeQueries({ predicate: (q) => q.queryKey[0] !== 'salud' });
  return true;
}

