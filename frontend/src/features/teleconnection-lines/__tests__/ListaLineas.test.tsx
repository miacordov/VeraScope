import { fireEvent, render, screen } from '@testing-library/react-native';

import { useEstado } from '@/estado/store';
import { teleconnect } from '@/shared/api/__fixtures__';
import { ErrorApi } from '@/shared/api/cliente';
import type { TeleconnectRespuesta } from '@/shared/api/tipos';
import { TEXTOS_ERROR } from '@/shared/components/textosEstados';

import { ListaLineas } from '../ListaLineas';
import { FRASE_LINEAS } from '../textos';

const respuesta: TeleconnectRespuesta = {
  ...teleconnect,
  lineas: [
    teleconnect.lineas[0]!,
    {
      ...teleconnect.lineas[0]!,
      tipo: 'mismo',
      lat: -2,
      lon: -120,
      r: 0.77,
      distancia_km: 4500,
    },
  ],
};

beforeEach(() => useEstado.getState().reiniciar());

describe('lista accesible de líneas', () => {
  it('cada línea es un botón con tipo, destino, r y distancia; activarlo elige el destino', async () => {
    await render(
      <ListaLineas respuesta={respuesta} cargando={false} error={null} destino={null} reintentar={jest.fn()} />,
    );
    const botones = screen.getAllByRole('button');
    expect(botones).toHaveLength(2);

    const mismo = screen.getByRole('button', {
      name: /^Mismo efecto · r = 0\.77 · 4,500 km/,
    });
    expect(mismo.props.accessibilityLabel).toContain('Destino: celda −2.0°, −120.0°');
    expect(mismo.props.accessibilityLabel).toContain(FRASE_LINEAS);

    await fireEvent.press(mismo);
    expect(useEstado.getState().destino).toEqual({ lat: -2, lon: -120 });
  });

  it('la línea elegida se marca y su detalle aparece en la franja fija', async () => {
    const elegida = respuesta.lineas[0]!;
    await render(
      <ListaLineas
        respuesta={respuesta}
        cargando={false}
        error={null}
        destino={{ lat: elegida.lat, lon: elegida.lon }}
        reintentar={jest.fn()}
      />,
    );
    expect(screen.getByRole('button', { selected: true })).toBeOnTheScreen();
    expect(screen.getByTestId('franja-linea')).toBeOnTheScreen();
    expect(screen.getByText('Efecto opuesto · elegida')).toBeOnTheScreen();
  });

  it('origen fuera del lugar elegido: dice de qué celda de ScanMap salen las líneas', async () => {
    await render(
      <ListaLineas respuesta={respuesta} cargando={false} error={null} destino={null} reintentar={jest.fn()} />,
    );
    expect(screen.getByText(/Las líneas salen del punto de ScanMap más cercano, a 120 km/)).toBeOnTheScreen();
  });

  it('sin líneas muestra mensaje_vacio como resultado (no es un error)', async () => {
    const vacia = {
      ...respuesta,
      lineas: [],
      mensaje_vacio: 'No se encontró un vínculo que cumpla los criterios.',
    };
    await render(<ListaLineas respuesta={vacia} cargando={false} error={null} destino={null} reintentar={jest.fn()} />);
    expect(screen.getByText(vacia.mensaje_vacio)).toBeOnTheScreen();
    expect(screen.queryByRole('alert')).toBeNull();
  });

  it('503 escaneo_en_curso muestra el aviso sin botón', async () => {
    const error = new ErrorApi({
      codigo: 'escaneo_en_curso',
      mensaje: '',
      estado: 503,
      tipo: 'servidor',
    });
    await render(
      <ListaLineas respuesta={undefined} cargando={false} error={error} destino={null} reintentar={jest.fn()} />,
    );
    expect(screen.getByText(TEXTOS_ERROR.escaneo_en_curso.titulo)).toBeOnTheScreen();
    expect(screen.getByText(TEXTOS_ERROR.escaneo_en_curso.mensajeRespaldo)).toBeOnTheScreen();
    expect(screen.queryByRole('button')).toBeNull();
  });
});
