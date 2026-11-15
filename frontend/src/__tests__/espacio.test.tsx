// Simulación oficial de gesture-handler para Jest (se carga aquí para no cambiar la configuración compartida).
import 'react-native-gesture-handler/jestSetup';

import { QueryClientProvider } from '@tanstack/react-query';
import { act, fireEvent, render, screen } from '@testing-library/react-native';
import { Dimensions } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { fireGestureHandler, getByGestureTestId } from 'react-native-gesture-handler/jest-utils';

import Espacio from '../../app/espacio';
import { crearQueryClient } from '../estado/queryClient';
import { useEstado } from '../estado/store';
import { altoDelMapa } from '../features/map/tamano';
import { analyze, variables } from '../shared/api/__fixtures__';
import type { SaludRespuesta } from '../shared/api/tipos';
import { BandaSimulado } from '../shared/components/BandaSimulado';
import { TEXTOS_VEREDICTO } from '../shared/components/textosVeredicto';
import { lineaFuente } from '../shared/format';

const salud: SaludRespuesta = {
  simulado: true,
  ventana_fin: 2025,
  version_metodo: 1,
  escaneo: { estado: 'en_curso', celdas_listas: 0, celdas_total: 4235 },
};

const fetchSimulado = jest.fn((url: string) => {
  const cuerpo = url.includes('/salud')
    ? salud
    : url.includes('/analyze')
      ? analyze
      : url.includes('/variables')
        ? variables
        : null;
  return Promise.resolve({ ok: cuerpo !== null, status: cuerpo ? 200 : 404, json: () => Promise.resolve(cuerpo) });
});

let cliente = crearQueryClient();

async function montar() {
  cliente = crearQueryClient();
  return render(
    // Igual que en app/_layout.tsx: los gestos del mapa necesitan la raíz de gesture-handler.
    <GestureHandlerRootView>
      <QueryClientProvider client={cliente}>
        <BandaSimulado />
        <Espacio />
      </QueryClientProvider>
    </GestureHandlerRootView>,
  );
}

const llamadasA = (ruta: string) => fetchSimulado.mock.calls.filter(([url]: [string]) => url.includes(ruta)).length;

beforeEach(() => {
  fetchSimulado.mockClear();
  global.fetch = fetchSimulado as unknown as typeof fetch;
  useEstado.getState().reiniciar();
});

// El primer montaje de la pantalla carga todo el árbol de módulos y, con la caché
// de Jest vacía (primera corrida o CI), supera los 5 s por defecto.
jest.setTimeout(30_000);

// Sin esto quedan vivos los temporizadores de limpieza de la caché.
afterEach(() => cliente.clear());

describe('espacio de trabajo con la API simulada', () => {
  it('muestra la banda "Datos simulados" y no pide analyze sin celda', async () => {
    await montar();
    expect(await screen.findByText('Datos simulados')).toBeOnTheScreen();
    expect(screen.getByText(/Toca el mapa para elegir un lugar/)).toBeOnTheScreen();
    expect(llamadasA('/analyze')).toBe(0);
  });

  it('el ejemplo simulado pide analyze una vez y muestra veredicto y fuente', async () => {
    await montar();
    await fireEvent.press(await screen.findByRole('button', { name: /Ver el ejemplo simulado/ }));

    expect(await screen.findByText(TEXTOS_VEREDICTO[analyze.veredicto.estado].titulo)).toBeOnTheScreen();
    expect(screen.getByText(lineaFuente(analyze))).toBeOnTheScreen();
    expect(screen.getByText('análisis individual')).toBeOnTheScreen();

    expect(llamadasA('/analyze')).toBe(1);
    const [url] = fetchSimulado.mock.calls.find(([u]: [string]) => u.includes('/analyze'))!;
    expect(url).toContain('variable=PRECTOTCORR&lat=-5&lon=-80.5&inicio=1981&fin=1990&indice=ONI');
  });

  it('el interruptor de El Niño no hace peticiones', async () => {
    await montar();
    await fireEvent.press(await screen.findByRole('button', { name: /Ver el ejemplo simulado/ }));
    await screen.findByText(TEXTOS_VEREDICTO[analyze.veredicto.estado].titulo);
    const antes = fetchSimulado.mock.calls.length;
    for (let i = 0; i < 10; i++) useEstado.getState().alternarElNino();
    expect(fetchSimulado.mock.calls.length).toBe(antes);
  });
});

describe('mapa y selector (fe/mapa-celda, #9)', () => {
  it('los botones del mapa tienen rol y etiqueta', async () => {
    await montar();
    for (const nombre of ['Acercar el mapa', 'Alejar el mapa', 'Restablecer vista', 'Centrar el mapa en Piura']) {
      expect(await screen.findByRole('button', { name: nombre })).toBeOnTheScreen();
    }
  });

  it('los accesos directos centran la vista pero no cambian la celda ni piden datos', async () => {
    await montar();
    await fireEvent.press(await screen.findByRole('button', { name: 'Centrar el mapa en Borneo' }));
    expect(useEstado.getState().celda).toBeNull();
    expect(llamadasA('/analyze')).toBe(0);
  });

  it('muestra las 5 variables de /variables y cambiar de variable conserva la celda', async () => {
    await montar();
    useEstado.getState().seleccionarCelda({ lat: -5, lon: -80.5 });
    for (const v of variables.variables) expect(await screen.findByText(v.nombre)).toBeOnTheScreen();
    await fireEvent.press(screen.getByRole('radio', { name: new RegExp(`^${variables.variables[1].nombre}`) }));
    expect(useEstado.getState().variable).toBe(variables.variables[1].id);
    expect(useEstado.getState().celda).toEqual({ lat: -5, lon: -80.5 });
  });

  it('una ventana de menos de 10 años no pide analyze y explica por qué', async () => {
    await montar();
    useEstado.getState().fijarVentana({ inicio: 2020, fin: null });
    useEstado.getState().seleccionarCelda({ lat: -5, lon: -80.5 });
    expect(await screen.findByText(/Elige al menos 10 años/)).toBeOnTheScreen();
    expect(llamadasA('/analyze')).toBe(0);
  });

  it('dibuja el rectángulo de la celda elegida', async () => {
    await montar();
    // En Jest no hay medidas: se simula el ancho que da onLayout.
    await fireEvent(await screen.findByTestId('mapa-lienzo'), 'layout', {
      nativeEvent: { layout: { x: 0, y: 0, width: 360, height: 270 } },
    });
    expect(await screen.findByTestId('mapa-costas')).toBeOnTheScreen();
    expect(screen.queryByTestId('mapa-celda')).toBeNull();
    useEstado.getState().seleccionarCelda({ lat: -5, lon: -80.5 });
    expect(await screen.findByTestId('mapa-celda')).toBeOnTheScreen();
  });

  it('tocar el centro del mapa elige la celda del centro del Pacífico (lon 210° = −150°)', async () => {
    await montar();
    await fireEvent(await screen.findByTestId('mapa-lienzo'), 'layout', {
      nativeEvent: { layout: { x: 0, y: 0, width: 360, height: 360 } },
    });
    // La vista inicial se centra en lon 210° (0..360) y lat 0°: el centro del lienzo cae ahí.
    // Mismo alto que le da la pantalla en la ventana de Jest (la regla vive en features/map/tamano.ts).
    const centro = { x: 180, y: altoDelMapa(Dimensions.get('window').width) / 2 };
    await act(() => fireGestureHandler(getByGestureTestId('mapa-toque'), [centro, centro]));
    expect(useEstado.getState().celda).toEqual({ lat: 0, lon: -150 });
  });
});

