import { QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react-native';

import Espacio from '../../app/espacio';
import { crearQueryClient } from '../estado/queryClient';
import { useEstado } from '../estado/store';
import { analyze } from '../shared/api/__fixtures__';
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
  const cuerpo = url.includes('/salud') ? salud : url.includes('/analyze') ? analyze : null;
  return Promise.resolve({ ok: cuerpo !== null, status: cuerpo ? 200 : 404, json: () => Promise.resolve(cuerpo) });
});

let cliente = crearQueryClient();

async function montar() {
  cliente = crearQueryClient();
  return render(
    <QueryClientProvider client={cliente}>
      <BandaSimulado />
      <Espacio />
    </QueryClientProvider>,
  );
}

const llamadasA = (ruta: string) => fetchSimulado.mock.calls.filter(([url]: [string]) => url.includes(ruta)).length;

beforeEach(() => {
  fetchSimulado.mockClear();
  global.fetch = fetchSimulado as unknown as typeof fetch;
  useEstado.getState().reiniciar();
});

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
