import { QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react-native';

import { crearQueryClient } from '../../../estado/queryClient';
import { useEstado } from '../../../estado/store';
import { PanelSeries } from '../../series-charts/PanelSeries';
import { analyze } from '../../../shared/api/__fixtures__';
import type { SaludRespuesta } from '../../../shared/api/tipos';
import { InterruptorElNino, textoRezago } from '../InterruptorElNino';

const salud: SaludRespuesta = {
  simulado: true,
  ventana_fin: 2025,
  version_metodo: 1,
  escaneo: { estado: 'completo', celdas_listas: 4235, celdas_total: 4235 },
};

const fetchSimulado = jest.fn((url: string) => {
  const cuerpo = url.includes('/salud') ? salud : null;
  return Promise.resolve({ ok: cuerpo !== null, status: cuerpo ? 200 : 404, json: () => Promise.resolve(cuerpo) });
});

let cliente = crearQueryClient();

beforeEach(() => {
  fetchSimulado.mockClear();
  global.fetch = fetchSimulado as unknown as typeof fetch;
  useEstado.getState().reiniciar();
  cliente = crearQueryClient();
});

afterEach(() => cliente.clear());

describe('interruptor "Quitar El Niño"', () => {
  it('se anuncia como interruptor con su estado', async () => {
    await render(<InterruptorElNino rezagoMeses={3} />);
    const interruptor = screen.getByRole('switch', { name: 'Quitar El Niño' });
    expect(interruptor.props.accessibilityState).toEqual({ checked: false });
    await fireEvent.press(interruptor);
    expect(screen.getByRole('switch', { name: 'Quitar El Niño' }).props.accessibilityState).toEqual({ checked: true });
    expect(useEstado.getState().quitarElNino).toBe(true);
  });

  it('explica el rezago que manda la API', () => {
    expect(textoRezago(3)).toBe('Quita la parte de la serie que explica El Niño, con 3 meses de retraso.');
    expect(textoRezago(1)).toContain('1 mes de retraso');
    expect(textoRezago(0)).toContain('en el mismo mes');
  });

  it('alternarlo 10 veces cambia la serie dibujada y no hace ninguna petición', async () => {
    await render(
      <QueryClientProvider client={cliente}>
        <InterruptorElNino rezagoMeses={analyze.vinculo_el_nino.rezago_meses} />
        <PanelSeries analisis={analyze} />
      </QueryClientProvider>,
    );
    await screen.findByText('Realidad (original)');
    const llamadasAntes = fetchSimulado.mock.calls.length;

    for (let i = 0; i < 10; i++) {
      await fireEvent.press(screen.getByRole('switch', { name: 'Quitar El Niño' }));
      expect(screen.getByText(i % 2 === 0 ? 'Realidad (sin El Niño)' : 'Realidad (original)')).toBeTruthy();
    }

    expect(fetchSimulado.mock.calls.length).toBe(llamadasAntes);
    expect(fetchSimulado.mock.calls.some(([url]: [string]) => url.includes('/analyze'))).toBe(false);
  });
});
