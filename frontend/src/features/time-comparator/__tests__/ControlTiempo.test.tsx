import { act, fireEvent, render, screen } from '@testing-library/react-native';

import { useEstado } from '../../../estado/store';
import { ControlTiempo } from '../ControlTiempo';
import { DURACION_REPRODUCCION_MS, mesParaAvance } from '../useReproduccion';

const fechas = Array.from({ length: 120 }, (_, i) => {
  const anio = 1981 + Math.floor(i / 12);
  const mes = String((i % 12) + 1).padStart(2, '0');
  return `${anio}-${mes}`;
});

const fetchEspia = jest.fn();

const rafOriginal = global.requestAnimationFrame;
const cafOriginal = global.cancelAnimationFrame;

beforeEach(() => {
  jest.useFakeTimers();
  // El entorno de React Native en Jest agenda los cuadros con un temporizador de 0 ms, que con temporizadores
  // falsos no avanza el reloj. Aquí cada cuadro dura 16 ms, como en un teléfono a 60 cuadros por segundo.
  global.requestAnimationFrame = ((cb: FrameRequestCallback) =>
    setTimeout(() => cb(Date.now()), 16) as unknown as number) as typeof requestAnimationFrame;
  global.cancelAnimationFrame = ((id: number) => clearTimeout(id)) as typeof cancelAnimationFrame;
  fetchEspia.mockClear();
  global.fetch = fetchEspia as unknown as typeof fetch;
  useEstado.getState().reiniciar();
});

afterEach(() => {
  useEstado.getState().detener();
  jest.useRealTimers();
  global.requestAnimationFrame = rafOriginal;
  global.cancelAnimationFrame = cafOriginal;
});

describe('reproducción en el tiempo', () => {
  it('el avance elige el mes; al terminar devuelve null', () => {
    expect(mesParaAvance(fechas, 0)).toBe('1981-01');
    expect(mesParaAvance(fechas, 0.5)).toBe('1986-01');
    expect(mesParaAvance(fechas, 1)).toBeNull();
  });

  it('recorre la serie en ~30 s, cambia mesVisible solo al cambiar de mes, termina en null y no usa la red', async () => {
    await render(<ControlTiempo fechas={fechas} />);
    const cambios: (string | null)[] = [];
    const desuscribir = useEstado.subscribe((e, previo) => {
      if (e.mesVisible !== previo.mesVisible) cambios.push(e.mesVisible);
    });

    await fireEvent.press(screen.getByRole('button', { name: 'Reproducir la serie en el tiempo' }));
    expect(useEstado.getState().reproduciendo).toBe(true);

    await act(async () => {
      jest.advanceTimersByTime(DURACION_REPRODUCCION_MS / 2);
    });
    expect(useEstado.getState().mesVisible).toMatch(/^198[56]-/);

    await act(async () => {
      jest.advanceTimersByTime(DURACION_REPRODUCCION_MS / 2 + 500);
    });
    desuscribir();

    expect(useEstado.getState().reproduciendo).toBe(false);
    expect(useEstado.getState().mesVisible).toBeNull();
    // Un cambio por mes (sin repetir) y el null final: nunca uno por cuadro.
    const meses = cambios.filter((c) => c !== null);
    expect(new Set(meses).size).toBe(meses.length);
    expect(meses.length).toBeLessThanOrEqual(fechas.length);
    expect(cambios.at(-1)).toBeNull();
    expect(fetchEspia).not.toHaveBeenCalled();
  });

  it('Pausa detiene sin borrar el mes; la barra se mueve un mes con aumentar y disminuir', async () => {
    await render(<ControlTiempo fechas={fechas} />);
    await fireEvent.press(screen.getByRole('button', { name: 'Reproducir la serie en el tiempo' }));
    await act(async () => {
      jest.advanceTimersByTime(3000);
    });
    await fireEvent.press(screen.getByRole('button', { name: 'Pausar la reproducción' }));
    const mes = useEstado.getState().mesVisible;
    expect(useEstado.getState().reproduciendo).toBe(false);
    expect(mes).not.toBeNull();

    const barra = screen.getByRole('adjustable', { name: 'Barra de tiempo' });
    await fireEvent(barra, 'accessibilityAction', { nativeEvent: { actionName: 'increment' } });
    expect(useEstado.getState().mesVisible).toBe(fechas[fechas.indexOf(mes as string) + 1]);
    await fireEvent(barra, 'accessibilityAction', { nativeEvent: { actionName: 'decrement' } });
    expect(useEstado.getState().mesVisible).toBe(mes);
    expect(fetchEspia).not.toHaveBeenCalled();
  });
});
