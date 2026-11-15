import { QueryClientProvider } from '@tanstack/react-query';
import { cleanup, render, screen } from '@testing-library/react-native';

import { crearQueryClient } from '@/estado/queryClient';
import { glosario } from '@/shared/api/__fixtures__';
import { TEXTOS_ERROR } from '@/shared/components/textosEstados';

import Glosario from '../../../../app/glosario';
import { CREDITOS } from '..';

let errorGlosario: { status: number; error: { codigo: string; mensaje: string; celda_cercana: null } } | null = null;

const fetchSimulado = jest.fn((url: string) => {
  if (url.includes('/glosario')) {
    if (errorGlosario) {
      const { status, error } = errorGlosario;
      return Promise.resolve({ ok: false, status, json: () => Promise.resolve({ error }) });
    }
    return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(glosario) });
  }
  return Promise.resolve({ ok: false, status: 404, json: () => Promise.resolve(null) });
});

let cliente = crearQueryClient();

async function montar() {
  cliente = crearQueryClient();
  return render(
    <QueryClientProvider client={cliente}>
      <Glosario />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  fetchSimulado.mockClear();
  errorGlosario = null;
  global.fetch = fetchSimulado as unknown as typeof fetch;
});

afterEach(() => {
  cleanup();
  cliente.clear();
});

describe('Glosario', () => {
  it('muestra los términos de /glosario tal como llegan y los créditos', async () => {
    await montar();
    const [primero] = glosario.terminos;
    expect(await screen.findByText(primero.termino)).toBeOnTheScreen();
    expect(screen.getByText(primero.definicion)).toBeOnTheScreen();
    expect(screen.getByText('Créditos y fuentes')).toBeOnTheScreen();
    for (const c of CREDITOS) expect(screen.getByText(c.fuente)).toBeOnTheScreen();
  });

  it('los créditos citan las tres fuentes y el ONI es de NOAA, no de la NASA (C11)', () => {
    const textos = CREDITOS.map((c) => c.fuente).join(' ');
    expect(textos).toMatch(/NASA POWER/);
    expect(textos).toMatch(/Natural Earth/);
    expect(textos).toMatch(/ONI.*NOAA/);
  });

  it('si el glosario no carga, explica qué pasó con los textos de estados y sigue mostrando los créditos', async () => {
    errorGlosario = {
      status: 503,
      error: { codigo: 'escaneo_en_curso', mensaje: 'Los datos reales aún no están disponibles.', celda_cercana: null },
    };
    await montar();
    expect(await screen.findByText(TEXTOS_ERROR.escaneo_en_curso.titulo)).toBeOnTheScreen();
    expect(screen.getByText('Los datos reales aún no están disponibles.')).toBeOnTheScreen();
    expect(screen.getByRole('button', { name: 'Reintentar' })).toBeOnTheScreen();
    expect(screen.getByText('Créditos y fuentes')).toBeOnTheScreen();
  });
});
