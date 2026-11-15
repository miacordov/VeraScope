import { act, cleanup, render, screen } from '@testing-library/react-native';
import { AccessibilityInfo } from 'react-native';

import { useEstado } from '@/estado/store';
import { analyze } from '@/shared/api/__fixtures__';
import type { AnalyzeRespuesta, Tendencia } from '@/shared/api/tipos';
import { TEXTOS_VEREDICTO } from '@/shared/components/textosVeredicto';
import { lineaFuente } from '@/shared/format';

import { TarjetaVeredicto } from '../TarjetaVeredicto';

/**
 * El ejemplo simulado del backend es "sin tendencia". Para probar los otros estados se usan COPIAS
 * modificadas solo dentro de las pruebas; la app nunca inventa datos.
 */
function variante(cambios: {
  original?: Partial<Tendencia>;
  sinElNino?: Partial<Tendencia>;
  veredicto?: Partial<AnalyzeRespuesta['veredicto']>;
  vinculo?: Partial<AnalyzeRespuesta['vinculo_el_nino']>;
}): AnalyzeRespuesta {
  return {
    ...analyze,
    tendencia_original: { ...analyze.tendencia_original, ...cambios.original },
    tendencia_sin_el_nino: { ...analyze.tendencia_sin_el_nino, ...cambios.sinElNino },
    veredicto: { ...analyze.veredicto, ...cambios.veredicto },
    vinculo_el_nino: { ...analyze.vinculo_el_nino, ...cambios.vinculo },
  };
}

const sensible = variante({
  original: { pendiente_decada: 0.31, ic_bajo: 0.1, ic_alto: 0.52, p: 0.004, significativa: true, direccion: 'sube', cambio_pct_decada: 12.5 },
  sinElNino: { pendiente_decada: 0.02, ic_bajo: -0.1, ic_alto: 0.14, p: 0.71, significativa: false, direccion: 'plana' },
  veredicto: { estado: 'sensible_a_el_nino' },
  vinculo: { rezago_meses: 3, r: 0.62, p: 0.001, significativo: true, indicativo: true },
});

const alternar = () => act(() => useEstado.getState().alternarElNino());

beforeEach(() => {
  useEstado.getState().reiniciar();
  global.fetch = jest.fn() as unknown as typeof fetch;
});

// Desmonta las tarjetas de cada prueba para que no reaccionen a los cambios del store de la siguiente.
afterEach(() => cleanup());

describe('TarjetaVeredicto', () => {
  it('con el interruptor apagado muestra la tendencia aparente de la serie original', async () => {
    await render(<TarjetaVeredicto analisis={sensible} />);
    expect(screen.getByText('Tendencia aparente')).toBeOnTheScreen();
    expect(screen.getByText('Parece que sube')).toBeOnTheScreen();
    expect(screen.getByText('0.31 mm/día por década')).toBeOnTheScreen();
    expect(screen.getByText('entre 0.10 y 0.52 mm/día')).toBeOnTheScreen();
    expect(screen.getByText('12.5 % por década')).toBeOnTheScreen();
    expect(screen.getByText('p = 0.004')).toBeOnTheScreen();
    expect(screen.queryByText('Sensible a El Niño')).toBeNull();
  });

  it('con el interruptor encendido muestra el veredicto de 4 estados y la serie sin El Niño', async () => {
    await render(<TarjetaVeredicto analisis={sensible} />);
    await alternar();
    expect(screen.getByText('Sensible a El Niño')).toBeOnTheScreen();
    expect(screen.getByText(TEXTOS_VEREDICTO.sensible_a_el_nino.explicacion)).toBeOnTheScreen();
    expect(screen.getByText('0.02 mm/día por década')).toBeOnTheScreen();
    expect(screen.getByText('p = 0.710')).toBeOnTheScreen();
    // La tendencia sin El Niño no es significativa: no se dice dirección ni se inventa el cambio %.
    expect(screen.queryByText(/Sin El Niño, la tendencia/)).toBeNull();
    expect(screen.queryByText(/% por década/)).toBeNull();
  });

  it('dice la dirección sin El Niño solo cuando es significativa', async () => {
    const robusto = variante({
      sinElNino: { significativa: true, direccion: 'baja', pendiente_decada: -0.2, ic_bajo: -0.3, ic_alto: -0.1, p: 0.01 },
      veredicto: { estado: 'cambio_robusto' },
    });
    useEstado.getState().fijarElNino(true);
    await render(<TarjetaVeredicto analisis={robusto} />);
    expect(screen.getByText('Cambio robusto')).toBeOnTheScreen();
    expect(screen.getByText('Sin El Niño, la tendencia baja.')).toBeOnTheScreen();
    expect(screen.getByText('−0.20 mm/día por década')).toBeOnTheScreen();
  });

  it('"sin tendencia" del ejemplo simulado se muestra como hallazgo, con avisos, fuente y análisis individual', async () => {
    await render(<TarjetaVeredicto analisis={analyze} />);
    expect(screen.getByText('Sin tendencia aparente')).toBeOnTheScreen();
    expect(screen.getByText('análisis individual')).toBeOnTheScreen();
    expect(screen.getByText(analyze.avisos[0].texto)).toBeOnTheScreen();
    expect(screen.getByText(lineaFuente(analyze))).toBeOnTheScreen();
    await alternar();
    expect(screen.getByText('Sin tendencia detectable')).toBeOnTheScreen();
    expect(screen.getByText(TEXTOS_VEREDICTO.sin_tendencia.explicacion)).toBeOnTheScreen();
  });

  it('el vínculo con El Niño se marca como indicativo y sin redacción causal', async () => {
    await render(<TarjetaVeredicto analisis={sensible} />);
    expect(screen.getByText('Sigue al índice de El Niño con 3 meses de retraso (r = 0.62) · indicativo')).toBeOnTheScreen();
  });

  it('sin vínculo significativo no afirma que siga al índice', async () => {
    await render(<TarjetaVeredicto analisis={analyze} />);
    expect(screen.getByText('No se ve un vínculo claro con El Niño (r = 0.00)')).toBeOnTheScreen();
  });

  it('con origen "escaneo" muestra el p ajustado y lo dice', async () => {
    const escaneo = variante({ original: { p: 0.03, p_ajustado: 0.04 }, veredicto: { origen: 'escaneo' } });
    await render(<TarjetaVeredicto analisis={escaneo} />);
    expect(screen.getByText('p = 0.040 (corregido por muchas pruebas)')).toBeOnTheScreen();
    expect(screen.queryByText('análisis individual')).toBeNull();
  });

  it('anuncia el cambio a los lectores de pantalla, pero no al aparecer', async () => {
    const anunciar = jest.spyOn(AccessibilityInfo, 'announceForAccessibility').mockImplementation(() => {});
    anunciar.mockClear(); // el entorno de React Native ya lo simula y guarda llamadas de otras pruebas
    await render(<TarjetaVeredicto analisis={sensible} />);
    expect(anunciar).not.toHaveBeenCalled();
    await alternar();
    expect(anunciar).toHaveBeenCalledWith(
      `Veredicto: Sensible a El Niño. ${TEXTOS_VEREDICTO.sensible_a_el_nino.explicacion}`,
    );
    anunciar.mockRestore();
  });

  it('alternar el interruptor 10 veces no hace ninguna petición', async () => {
    await render(<TarjetaVeredicto analisis={sensible} />);
    for (let i = 0; i < 10; i++) await alternar();
    expect(global.fetch).not.toHaveBeenCalled();
    expect(screen.getByText('Parece que sube')).toBeOnTheScreen();
  });
});
