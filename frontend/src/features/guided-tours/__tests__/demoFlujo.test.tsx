// Simulación oficial de gesture-handler para Jest (el espacio de trabajo tiene el mapa con gestos).
import 'react-native-gesture-handler/jestSetup';

import { QueryClientProvider } from '@tanstack/react-query';
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';

import { crearQueryClient } from '@/estado/queryClient';
import { useEstado } from '@/estado/store';
import { analyze, efectoEspejo, variables } from '@/shared/api/__fixtures__';
import type { SaludRespuesta } from '@/shared/api/tipos';
import { TEXTOS_VEREDICTO } from '@/shared/components/textosVeredicto';

import Espacio from '../../../../app/espacio';
import Inicio from '../../../../app/index';
import { BandaDemo } from '..';

/**
 * Flujo completo de F3 con las pantallas reales: Inicio → "Ver la demo" → espacio de trabajo con la banda de la
 * demo, sobre las respuestas de ejemplo (sin red). Comprueba que el ejecutor mueve el espacio de F1 y la tarjeta
 * de F3 como pide la demo 1, y que cambiar de paso o quitar El Niño no pide datos.
 */

const mockNavegar = jest.fn();
jest.mock('expo-router', () => ({ useRouter: () => ({ navigate: mockNavegar, push: mockNavegar }) }));

const salud: SaludRespuesta = {
  simulado: true,
  ventana_fin: 2025,
  version_metodo: 2,
  escaneo: { estado: 'completo', celdas_listas: 2, celdas_total: 2 },
};

const fetchSimulado = jest.fn((url: string) => {
  const cuerpo = url.includes('/salud')
    ? salud
    : url.includes('/demos/efecto-espejo')
      ? efectoEspejo
      : url.includes('/analyze')
        ? analyze
        : url.includes('/variables')
          ? variables
          : null;
  return Promise.resolve({ ok: cuerpo !== null, status: cuerpo ? 200 : 404, json: () => Promise.resolve(cuerpo) });
});

const llamadasA = (ruta: string) => fetchSimulado.mock.calls.filter(([url]: [string]) => url.includes(ruta)).length;
/** Llamadas a una ruta (`/analyze`, `/teleconnect`) para una celda concreta. */
const llamadasDe = (ruta: string, celda: string) =>
  fetchSimulado.mock.calls.filter(([url]: [string]) => url.includes(ruta) && url.includes(celda)).length;
const estado = () => useEstado.getState();

let cliente = crearQueryClient();

/** Lo que monta `_layout.tsx` alrededor de las pantallas: la banda de la demo arriba. */
async function montar(pantalla: 'inicio' | 'espacio') {
  cliente = crearQueryClient();
  return render(
    <GestureHandlerRootView>
      <QueryClientProvider client={cliente}>
        <BandaDemo />
        {pantalla === 'inicio' ? <Inicio /> : <Espacio />}
      </QueryClientProvider>
    </GestureHandlerRootView>,
  );
}

beforeEach(() => {
  fetchSimulado.mockClear();
  mockNavegar.mockClear();
  global.fetch = fetchSimulado as unknown as typeof fetch;
  estado().reiniciar();
});

afterEach(() => {
  cleanup();
  cliente.clear();
});

jest.setTimeout(30_000);

describe('demo 1 de punta a punta (respuestas de ejemplo)', () => {
  it('desde el Inicio, "Ver la demo" empieza la demo y lleva al espacio de trabajo', async () => {
    await montar('inicio');
    await fireEvent.press(screen.getByRole('button', { name: /Ver la demo guiada/ }));
    expect(mockNavegar).toHaveBeenCalledWith('/espacio');
    // La banda ya pide el guion y aplica el primer paso, aunque la pantalla siga siendo el Inicio.
    expect(await screen.findByText(efectoEspejo.pasos[0].texto)).toBeOnTheScreen();
    expect(estado().celda).toEqual(efectoEspejo.celda);
  });

  it('en el espacio, el paso 1 elige Piura y muestra la tarjeta; los pasos y el interruptor no piden datos', async () => {
    await montar('espacio');
    await act(() => {
      estado().fijarDemo({ id: 'efecto-espejo', paso: -1 });
    });

    // Paso 1: celda de la demo, interruptor apagado → la tarjeta de F3 dice "Tendencia aparente".
    expect(await screen.findByText(efectoEspejo.pasos[0].texto)).toBeOnTheScreen();
    expect(await screen.findByText('Tendencia aparente')).toBeOnTheScreen();
    expect(llamadasA('/demos/')).toBe(1);
    expect(llamadasA('/analyze')).toBe(1);
    const analyzeAntes = llamadasA('/analyze');

    // Paso 2 y 3: reproducir, detener y destino; no cambian la celda → no hay otro analyze.
    await fireEvent.press(screen.getByRole('button', { name: 'Paso siguiente' }));
    expect(screen.getByText(efectoEspejo.pasos[1].texto)).toBeOnTheScreen();
    expect(estado().reproduciendo).toBe(true);
    await fireEvent.press(screen.getByRole('button', { name: 'Paso siguiente' }));
    expect(screen.getByText(efectoEspejo.pasos[2].texto)).toBeOnTheScreen();
    expect(estado().destino).toEqual({ lat: -18, lon: 142 });

    // Quitar El Niño durante la demo: la tarjeta pasa al veredicto de 4 estados sin red.
    await act(() => estado().alternarElNino());
    expect(screen.getByText(TEXTOS_VEREDICTO[analyze.veredicto.estado].titulo)).toBeOnTheScreen();

    // Volver al paso 1 repite el estado del paso 1 (interruptor apagado) y la celda sigue en caché.
    await fireEvent.press(screen.getByRole('button', { name: 'Paso anterior' }));
    await fireEvent.press(screen.getByRole('button', { name: 'Paso anterior' }));
    expect(screen.getByText(efectoEspejo.pasos[0].texto)).toBeOnTheScreen();
    expect(estado().quitarElNino).toBe(false);
    expect(await screen.findByText('Tendencia aparente')).toBeOnTheScreen();

    expect(llamadasA('/demos/')).toBe(1);
    // Ir y volver entre pasos no repite el analyze de Piura (staleTime infinito). El único analyze extra es el del
    // destino del paso 3, que el panel de Consecuencia pide a propósito (guía del frontend §6, regla 1).
    expect(llamadasDe('/analyze', 'lat=-5&lon=-80.5')).toBe(analyzeAntes);
    expect(llamadasDe('/analyze', 'lat=-18&lon=142')).toBe(1);
    expect(llamadasA('/analyze')).toBe(analyzeAntes + 1);
    // Si el espacio pide las líneas de la celda (teleconnect, en paralelo con analyze, §6), tampoco se repiten.
    expect(llamadasDe('/teleconnect', 'lat=-5&lon=-80.5')).toBeLessThanOrEqual(1);
  });

  it('Salir cierra la banda y deja el espacio vacío, listo para investigar', async () => {
    await montar('espacio');
    await act(() => {
      estado().fijarDemo({ id: 'efecto-espejo', paso: -1 });
    });
    await screen.findByText(efectoEspejo.pasos[0].texto);

    await fireEvent.press(screen.getByRole('button', { name: 'Salir de la demo' }));
    expect(screen.queryByText(efectoEspejo.pasos[0].texto)).toBeNull();
    expect(screen.getByText(/Toca el mapa para elegir un lugar/)).toBeOnTheScreen();
    expect(estado().demo).toBeNull();
  });
});
