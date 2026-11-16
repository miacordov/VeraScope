import { QueryClientProvider } from '@tanstack/react-query';
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react-native';
import { AccessibilityInfo } from 'react-native';

import { crearQueryClient } from '@/estado/queryClient';
import { useEstado } from '@/estado/store';
import { efectoEspejo } from '@/shared/api/__fixtures__';
import { TEXTOS_ERROR } from '@/shared/components/textosEstados';

import { iniciarDemo } from '../acciones';
import { BandaDemo } from '../BandaDemo';

// Celda y destino de la demo 1, leídos del guion: si el guion cambia de celda, las pruebas lo siguen.
const lugarDelGuion = (tipo: 'seleccionar_celda' | 'ir_a_destino') => {
  const accion = efectoEspejo.pasos.flatMap((paso) => paso.acciones).find((a) => a.tipo === tipo) as
    | { lat: number; lon: number }
    | undefined;
  if (!accion) throw new Error(`El guion de la demo 1 no tiene la acción ${tipo}`);
  return { lat: accion.lat, lon: accion.lon };
};
const PIURA = lugarDelGuion('seleccionar_celda');
const DESTINO = lugarDelGuion('ir_a_destino');

/** Error que debe devolver `/demos` en una prueba, o `null`. */
let errorDemo: { status: number; error: { codigo: string; mensaje: string; celda_cercana: null } } | null = null;

const fetchSimulado = jest.fn((url: string) => {
  if (url.includes('/demos/efecto-espejo')) {
    if (errorDemo) {
      const { status, error } = errorDemo;
      return Promise.resolve({ ok: false, status, json: () => Promise.resolve({ error }) });
    }
    return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(efectoEspejo) });
  }
  return Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve(null) });
});

let cliente = crearQueryClient();

async function montar() {
  cliente = crearQueryClient();
  return render(
    <QueryClientProvider client={cliente}>
      <BandaDemo />
    </QueryClientProvider>,
  );
}

const llamadasA = (ruta: string) => fetchSimulado.mock.calls.filter(([url]: [string]) => url.includes(ruta)).length;
const estado = () => useEstado.getState();

beforeEach(() => {
  fetchSimulado.mockClear();
  errorDemo = null;
  global.fetch = fetchSimulado as unknown as typeof fetch;
  estado().reiniciar();
});

afterEach(() => {
  cleanup();
  cliente.clear();
});

describe('BandaDemo', () => {
  it('sin demo en curso no muestra nada ni pide el guion', async () => {
    await montar();
    expect(screen.queryByText(/Demo ·/)).toBeNull();
    expect(llamadasA('/demos/')).toBe(0);
  });

  it('al iniciar pide el guion una vez, aplica el primer paso y muestra su texto tal cual', async () => {
    await montar();
    await act(() => iniciarDemo('efecto-espejo'));

    expect(await screen.findByText(efectoEspejo.pasos[0].texto)).toBeOnTheScreen();
    expect(screen.getByText(`Demo · ${efectoEspejo.titulo} · paso 1 de 3`)).toBeOnTheScreen();
    expect(estado().celda).toEqual(PIURA);
    expect(estado().demo).toEqual({ id: 'efecto-espejo', paso: 0 });
    expect(screen.getByRole('button', { name: 'Paso anterior' })).toBeDisabled();
    expect(llamadasA('/demos/')).toBe(1);
  });

  it('Siguiente y Anterior cambian de paso sin pedir datos y fijan el estado de ese paso', async () => {
    const anunciar = jest.spyOn(AccessibilityInfo, 'announceForAccessibility');
    await montar();
    await act(() => iniciarDemo('efecto-espejo'));
    await screen.findByText(efectoEspejo.pasos[0].texto);

    await fireEvent.press(screen.getByRole('button', { name: 'Paso siguiente' }));
    expect(screen.getByText(efectoEspejo.pasos[1].texto)).toBeOnTheScreen();
    expect(estado().reproduciendo).toBe(true);
    expect(anunciar).toHaveBeenCalledWith(efectoEspejo.pasos[1].texto);

    await fireEvent.press(screen.getByRole('button', { name: 'Paso siguiente' }));
    expect(screen.getByText(efectoEspejo.pasos[2].texto)).toBeOnTheScreen();
    expect(estado().destino).toEqual(DESTINO);
    expect(screen.getByRole('button', { name: 'Paso siguiente' })).toBeDisabled();

    await fireEvent.press(screen.getByRole('button', { name: 'Paso anterior' }));
    expect(screen.getByText(efectoEspejo.pasos[1].texto)).toBeOnTheScreen();
    expect(estado().destino).toBeNull();

    expect(llamadasA('/demos/')).toBe(1);
    anunciar.mockRestore();
  });

  it('Salir cierra la banda y vuelve al estado inicial', async () => {
    await montar();
    await act(() => iniciarDemo('efecto-espejo'));
    await screen.findByText(efectoEspejo.pasos[0].texto);

    await fireEvent.press(screen.getByRole('button', { name: 'Salir de la demo' }));
    expect(screen.queryByText(efectoEspejo.pasos[0].texto)).toBeNull();
    expect(estado().demo).toBeNull();
    expect(estado().celda).toBeNull();
  });

  it('si el guion no llega, muestra el error con los textos de estados y permite salir', async () => {
    errorDemo = {
      status: 503,
      error: { codigo: 'escaneo_en_curso', mensaje: 'Los datos reales aún no están disponibles.', celda_cercana: null },
    };
    await montar();
    await act(() => iniciarDemo('efecto-espejo'));

    expect(await screen.findByText(TEXTOS_ERROR.escaneo_en_curso.titulo)).toBeOnTheScreen();
    expect(screen.getByText('Los datos reales aún no están disponibles.')).toBeOnTheScreen();
    // No se aplicó nada a medias: la demo sigue pendiente y no hay celda.
    expect(estado().celda).toBeNull();

    await fireEvent.press(screen.getByRole('button', { name: 'Salir de la demo' }));
    expect(estado().demo).toBeNull();
  });

  it('una demo que no existe en el contrato se explica y no pide nada', async () => {
    await montar();
    await act(() => estado().fijarDemo({ id: 'otra', paso: 0 }));
    expect(screen.getByText('Demo no disponible')).toBeOnTheScreen();
    expect(llamadasA('/demos/')).toBe(0);
  });
});
