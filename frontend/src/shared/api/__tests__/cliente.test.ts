import { analyze as analyzeFixture } from '../__fixtures__';
import { api, ErrorApi, TIEMPO_MAX_MS } from '../cliente';

const fetchSimulado = jest.fn();

function respuesta(estado: number, cuerpo: unknown) {
  return Promise.resolve({ ok: estado >= 200 && estado < 300, status: estado, json: () => Promise.resolve(cuerpo) });
}

beforeEach(() => {
  fetchSimulado.mockReset();
  global.fetch = fetchSimulado as unknown as typeof fetch;
});

afterEach(() => jest.useRealTimers());

describe('cliente de la API', () => {
  it('antepone la URL base y /api/v1, y envía los parámetros', async () => {
    fetchSimulado.mockReturnValue(respuesta(200, analyzeFixture));
    const datos = await api.analyze({ variable: 'PRECTOTCORR', lat: -5, lon: -80.5, inicio: 1981, fin: 1990, indice: 'ONI' });
    expect(datos.veredicto.estado).toBe(analyzeFixture.veredicto.estado);
    const [url] = fetchSimulado.mock.calls[0];
    expect(url).toBe(
      'http://localhost:8000/api/v1/analyze?variable=PRECTOTCORR&lat=-5&lon=-80.5&inicio=1981&fin=1990&indice=ONI',
    );
  });

  it('convierte el error estándar en ErrorApi con su mensaje y celda cercana', async () => {
    fetchSimulado.mockReturnValue(
      respuesta(504, {
        error: { codigo: 'power_lento', mensaje: 'POWER tarda en responder.', celda_cercana: { lat: -5, lon: -80 } },
      }),
    );
    const error = await api.salud().catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ErrorApi);
    expect(error).toMatchObject({
      estado: 504,
      codigo: 'power_lento',
      message: 'POWER tarda en responder.',
      celdaCercana: { lat: -5, lon: -80 },
      tipo: 'servidor',
    });
  });

  it('un estado de error sin cuerpo estándar da un mensaje en español', async () => {
    fetchSimulado.mockReturnValue(respuesta(500, null));
    await expect(api.salud()).rejects.toMatchObject({ codigo: 'respuesta_invalida', tipo: 'servidor' });
  });

  it('un fallo de red se marca como de red', async () => {
    fetchSimulado.mockReturnValue(Promise.reject(new TypeError('Network request failed')));
    await expect(api.variables()).rejects.toMatchObject({ codigo: 'sin_conexion', tipo: 'red', estado: 0 });
  });

  it('corta la petición al pasar el tiempo máximo', async () => {
    jest.useFakeTimers();
    fetchSimulado.mockImplementation(
      (_url: string, init: { signal: AbortSignal }) =>
        new Promise((_resolve, reject) => {
          init.signal.addEventListener('abort', () => reject(new Error('abortada')));
        }),
    );
    const promesa = api.glosario();
    jest.advanceTimersByTime(TIEMPO_MAX_MS);
    await expect(promesa).rejects.toMatchObject({ codigo: 'tiempo_agotado', tipo: 'red' });
  });
});
