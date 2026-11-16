import type { EstadoVeredicto, LayerRespuesta } from '@/shared/api/tipos';
import { colores } from '@/shared/tema';

import { CLASES_MOSAICO, claseCelda, estiloMosaico, gruposMosaico, nombreClase } from '../mosaico';
import { escalaMinima, vistaInicial, type Tamano } from '../proyeccion';

const VEREDICTOS: (EstadoVeredicto | null)[] = [
  'cambio_robusto',
  'sensible_a_el_nino',
  'cambio_oculto',
  'sin_tendencia',
  null,
];

/** 4235 celdas sintéticas con todas las clases (la rejilla real de ScanMap tiene 4235). */
function layerSintetico(): LayerRespuesta {
  const lat: number[] = [];
  const lon: number[] = [];
  const veredicto: (EstadoVeredicto | null)[] = [];
  const pendiente: (number | null)[] = [];
  for (let i = 0; i < 4235; i += 1) {
    lat.push(-60 + 2 * (i % 61));
    lon.push(-180 + 2 * Math.floor(i / 61));
    const v = VEREDICTOS[i % VEREDICTOS.length]!;
    veredicto.push(v);
    pendiente.push(v === null ? null : i % 2 === 0 ? 0.3 : -0.2);
  }
  return {
    variable: 'PRECTOTCORR',
    paso_grados: 2,
    lat,
    lon,
    veredicto,
    pendiente_decada: pendiente,
    efecto: pendiente,
  };
}

describe('mosaico de ScanMap', () => {
  const t: Tamano = { ancho: 1200, alto: 480 };

  it('4235 celdas se dibujan en pocos trazados (uno por clase), no en 4235 elementos', () => {
    const v = { ...vistaInicial(t), escala: escalaMinima(t) };
    const grupos = gruposMosaico(layerSintetico(), v, t);
    expect(grupos.length).toBeGreaterThan(1);
    expect(grupos.length).toBeLessThanOrEqual(CLASES_MOSAICO.length);
    const total = grupos.reduce((s, g) => s + g.celdas, 0);
    // Las celdas sin serie válida (null) no se dibujan.
    expect(total).toBeLessThanOrEqual(4235 - Math.floor(4235 / VEREDICTOS.length));
    expect(total).toBeGreaterThan(1000);
    for (const g of grupos) expect(g.d.match(/M/g)).toHaveLength(g.celdas);
  });

  it('cada celda es un cuadrado M x y h w v h h −w z del tamaño del paso', () => {
    const v = vistaInicial(t);
    const capa: LayerRespuesta = {
      variable: 'T2M',
      paso_grados: 2,
      lat: [0],
      lon: [-150],
      veredicto: ['cambio_robusto'],
      pendiente_decada: [0.2],
      efecto: [1],
    };
    const [g] = gruposMosaico(capa, v, t);
    const lado = Math.round(2 * v.escala * 10) / 10;
    expect(g!.clase).toBe('cambio_robusto_sube');
    expect(g!.d).toMatch(new RegExp(`h${lado}v${lado}h-${lado}z$`));
  });

  it('las celdas fuera de la pantalla no se escriben', () => {
    const v = { ...vistaInicial(t), escala: 40 };
    const grupos = gruposMosaico(layerSintetico(), v, t);
    const total = grupos.reduce((s, g) => s + g.celdas, 0);
    expect(total).toBeLessThan(200);
  });

  it('clase por veredicto y signo; sin tendencia = apagado; sin serie = no se dibuja', () => {
    expect(claseCelda('cambio_oculto', -0.1)).toBe('cambio_oculto_baja');
    expect(claseCelda('sin_tendencia', 0.5)).toBe('sin_hallazgo');
    expect(claseCelda(null, null)).toBeNull();
    expect(nombreClase('cambio_robusto_sube')).toBe('Cambio robusto, sube');
  });

  it('el rojo queda solo para El Niño; la temperatura usa ámbar', () => {
    for (const clase of CLASES_MOSAICO) {
      expect(estiloMosaico(clase, 'PRECTOTCORR').color).not.toBe(colores.nino);
      expect(estiloMosaico(clase, 'T2M').color).not.toBe(colores.nino);
    }
    expect(estiloMosaico('cambio_robusto_sube', 'T2M').color).toBe(colores.sequia);
    expect(estiloMosaico('cambio_robusto_sube', 'PRECTOTCORR').color).toBe(colores.lluvia);
  });
});
