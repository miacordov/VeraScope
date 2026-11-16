import { act, fireEvent, render, screen } from '@testing-library/react-native';
import { AccessibilityInfo } from 'react-native';

import { PlanetaGirando } from '@/shared/components/PlanetaGirando';
import { Desplegable, Texto } from '@/shared/ui';

const oculto = { includeHiddenElements: true } as const;

/** `d` de las costas del planeta dibujado. */
function trazadoCostas(): string {
  return screen.getByTestId('planeta-costas', oculto).props.d as string;
}

beforeEach(() => {
  jest.useFakeTimers();
  global.fetch = jest.fn() as unknown as typeof fetch;
});

afterEach(() => {
  jest.useRealTimers();
  jest.restoreAllMocks();
});

describe('PlanetaGirando', () => {
  it('dibuja las costas, gira con el tiempo y no pide datos a la red', async () => {
    await render(<PlanetaGirando tamano={300} />);
    await act(async () => {}); // resuelve isReduceMotionEnabled
    const antes = trazadoCostas();
    expect(antes.length).toBeGreaterThan(100);
    await act(async () => jest.advanceTimersByTime(1000));
    expect(trazadoCostas()).not.toBe(antes);
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('es decoración: no se anuncia a lectores de pantalla', async () => {
    await render(<PlanetaGirando tamano={300} />);
    expect(screen.queryByTestId('planeta-girando')).toBeNull();
    expect(screen.getByTestId('planeta-girando', oculto)).toBeTruthy();
  });

  it('con "reducir movimiento" se queda quieto', async () => {
    jest.spyOn(AccessibilityInfo, 'isReduceMotionEnabled').mockResolvedValue(true);
    await render(<PlanetaGirando tamano={300} />);
    await act(async () => {});
    const antes = trazadoCostas();
    await act(async () => jest.advanceTimersByTime(2000));
    expect(trazadoCostas()).toBe(antes);
  });

  it('sin foco (girando = false) se queda quieto', async () => {
    await render(<PlanetaGirando tamano={300} girando={false} />);
    await act(async () => {});
    const antes = trazadoCostas();
    await act(async () => jest.advanceTimersByTime(2000));
    expect(trazadoCostas()).toBe(antes);
  });
});

describe('Desplegable', () => {
  it('muestra el resumen cerrado, abre el contenido y anuncia su estado', async () => {
    await render(
      <Desplegable titulo="Ver detalles" tituloAbierto="Ocultar detalles" resumen="p-valor">
        <Texto>contenido</Texto>
      </Desplegable>,
    );
    expect(screen.getByText('p-valor')).toBeOnTheScreen();
    expect(screen.queryByText('contenido')).toBeNull();
    expect(screen.getByRole('button', { name: 'Ver detalles' })).toBeCollapsed();

    await fireEvent.press(screen.getByRole('button', { name: 'Ver detalles' }));
    expect(screen.getByText('contenido')).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: 'Ocultar detalles' })).toBeExpanded();

    await fireEvent.press(screen.getByRole('button', { name: 'Ocultar detalles' }));
    expect(screen.queryByText('contenido')).toBeNull();
  });
});
