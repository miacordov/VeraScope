import { fireEvent, render, screen } from '@testing-library/react-native';

import { useEstado } from '@/estado/store';

import Inicio from '../../../../app/index';
import { PASO_PENDIENTE } from '../acciones';

// Jest solo deja usar dentro de `jest.mock` variables cuyo nombre empieza con `mock`.
const mockNavegar = jest.fn();
jest.mock('expo-router', () => ({ useRouter: () => ({ navigate: mockNavegar, push: mockNavegar }) }));

beforeEach(() => {
  mockNavegar.mockClear();
  useEstado.getState().reiniciar();
  global.fetch = jest.fn() as unknown as typeof fetch;
});

describe('Inicio', () => {
  it('muestra el logo, el globo, el titular y los accesos, sin Escanear (feed recortado)', async () => {
    await render(<Inicio />);
    expect(screen.getByLabelText('Logo de VeraScope')).toBeOnTheScreen();
    expect(screen.getByLabelText(/La Tierra vista desde el Pacífico/)).toBeOnTheScreen();
    expect(screen.getByRole('header', { name: '¿Cambió de verdad, o es El Niño?' })).toBeOnTheScreen();
    expect(screen.getByText('Tendencias en datos de la NASA, sin el ruido de El Niño.')).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: /Investigar/ })).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: /Ver la demo guiada/ })).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: 'Glosario' })).toBeOnTheScreen();
    expect(screen.queryByText('Escanear')).toBeNull();
  });

  it('Investigar va al espacio de trabajo sin pedir datos aquí', async () => {
    await render(<Inicio />);
    await fireEvent.press(screen.getByRole('button', { name: /Investigar/ }));
    expect(mockNavegar).toHaveBeenCalledWith('/espacio');
    expect(useEstado.getState().demo).toBeNull();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('la demo empieza (pendiente del guion) y lleva al espacio de trabajo, sin pedir datos aquí', async () => {
    await render(<Inicio />);
    await fireEvent.press(screen.getByRole('button', { name: /Ver la demo guiada/ }));
    expect(useEstado.getState().demo).toEqual({ id: 'efecto-espejo', paso: PASO_PENDIENTE });
    expect(mockNavegar).toHaveBeenCalledWith('/espacio');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('Explorar va al espacio de trabajo sin empezar la demo ni pedir datos', async () => {
    await render(<Inicio />);
    await fireEvent.press(screen.getByRole('button', { name: /Explorar/ }));
    expect(mockNavegar).toHaveBeenCalledWith('/espacio');
    expect(useEstado.getState().demo).toBeNull();
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('Glosario lleva a su página', async () => {
    await render(<Inicio />);
    await fireEvent.press(screen.getByRole('button', { name: 'Glosario' }));
    expect(mockNavegar).toHaveBeenCalledWith('/glosario');
  });
});
