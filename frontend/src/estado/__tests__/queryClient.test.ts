import { QueryClient } from '@tanstack/react-query';

import { ErrorApi } from '../../shared/api/cliente';
import { descartarSiCambioVersion, LLAVE_VERSION_METODO } from '../persistencia';
import { debePersistir, debeReintentar } from '../queryClient';

jest.mock('@react-native-async-storage/async-storage', () =>
  jest.requireActual('@react-native-async-storage/async-storage/jest/async-storage-mock'),
);

const AsyncStorage = jest.requireMock('@react-native-async-storage/async-storage');

const consulta = (llave: unknown[], status: 'success' | 'error' | 'pending' = 'success') =>
  ({ queryKey: llave, state: { status } }) as unknown as Parameters<typeof debePersistir>[0];

describe('caché de respuestas', () => {
  it('guarda analyze y teleconnect, pero no salud ni lo que falló', () => {
    expect(debePersistir(consulta(['analyze', 'PRECTOTCORR', -5, -80.5, 1981, 1990, 'ONI']))).toBe(true);
    expect(debePersistir(consulta(['teleconnect', 'PRECTOTCORR', -5, -80.5]))).toBe(true);
    expect(debePersistir(consulta(['salud']))).toBe(false);
    expect(debePersistir(consulta(['analyze'], 'error'))).toBe(false);
  });

  it('no reintenta power_lento; un error de red sí, una vez', () => {
    const lento = new ErrorApi({ estado: 503, codigo: 'power_lento', mensaje: 'POWER tarda', tipo: 'servidor' });
    const red = new ErrorApi({ estado: 0, codigo: 'sin_conexion', mensaje: 'Sin conexión', tipo: 'red' });
    expect(debeReintentar(0, lento)).toBe(false);
    expect(debeReintentar(0, red)).toBe(true);
    expect(debeReintentar(1, red)).toBe(false);
  });

  it('borra lo guardado cuando el backend cambia version_metodo', async () => {
    await AsyncStorage.clear();
    const cliente = new QueryClient();
    cliente.setQueryData(['analyze', 'x'], { a: 1 });
    cliente.setQueryData(['salud'], { version_metodo: 1 });

    expect(await descartarSiCambioVersion(cliente, 1)).toBe(false);
    expect(cliente.getQueryData(['analyze', 'x'])).toEqual({ a: 1 });

    expect(await descartarSiCambioVersion(cliente, 2)).toBe(true);
    expect(cliente.getQueryData(['analyze', 'x'])).toBeUndefined();
    expect(cliente.getQueryData(['salud'])).toEqual({ version_metodo: 1 });
    expect(await AsyncStorage.getItem(LLAVE_VERSION_METODO)).toBe('2');
    cliente.clear();
  });
});
