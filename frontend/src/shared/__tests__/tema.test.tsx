import { act, fireEvent, render, screen, waitFor } from '@testing-library/react-native';

import { BotonModo } from '@/shared/components/BotonModo';
import { ProveedorTema } from '@/shared/ProveedorTema';
import { paletas } from '@/shared/tema';
import { Texto } from '@/shared/ui';
import { useTema } from '@/shared/useTema';

jest.mock('@react-native-async-storage/async-storage', () =>
  jest.requireActual('@react-native-async-storage/async-storage/jest/async-storage-mock'),
);

const AsyncStorage = jest.requireMock('@react-native-async-storage/async-storage');

function ModoActual() {
  const { modo, colores } = useTema();
  return <Texto testID="modo">{`${modo} ${colores.fondo}`}</Texto>;
}

beforeEach(async () => {
  await AsyncStorage.clear();
});

describe('paletas', () => {
  it('los dos modos tienen exactamente los mismos tokens', () => {
    expect(Object.keys(paletas.claro).sort()).toEqual(Object.keys(paletas.oscuro).sort());
  });

  it('el rojo de El Niño no se usa en ningún otro token', () => {
    for (const colores of Object.values(paletas)) {
      const otros = Object.entries(colores).filter(([token]) => token !== 'nino');
      expect(otros.map(([, valor]) => valor)).not.toContain(colores.nino);
    }
  });
});

describe('modo claro y oscuro', () => {
  it('sin proveedor se usa el modo oscuro', async () => {
    await render(<ModoActual />);
    expect(screen.getByTestId('modo')).toHaveTextContent(`oscuro ${paletas.oscuro.fondo}`);
  });

  it('el botón cambia de modo y la elección se guarda', async () => {
    await render(
      <ProveedorTema>
        <ModoActual />
        <BotonModo />
      </ProveedorTema>,
    );
    const inicial = screen.getByTestId('modo').props.children as string;
    const haciaClaro = inicial.startsWith('oscuro');
    const boton = screen.getByRole('button', { name: haciaClaro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro' });

    await act(async () => fireEvent.press(boton));

    const esperado = haciaClaro ? 'claro' : 'oscuro';
    expect(screen.getByTestId('modo')).toHaveTextContent(`${esperado} ${paletas[esperado].fondo}`);
    await waitFor(() => expect(AsyncStorage.setItem).toHaveBeenCalledWith('verascope.modo', esperado));
    expect(
      screen.getByRole('button', { name: haciaClaro ? 'Cambiar a modo oscuro' : 'Cambiar a modo claro' }),
    ).toBeOnTheScreen();
  });

  it('al abrir la app recupera el modo guardado', async () => {
    await AsyncStorage.setItem('verascope.modo', 'claro');
    await render(
      <ProveedorTema>
        <ModoActual />
      </ProveedorTema>,
    );
    await waitFor(() => expect(screen.getByTestId('modo')).toHaveTextContent(`claro ${paletas.claro.fondo}`));
  });
});
