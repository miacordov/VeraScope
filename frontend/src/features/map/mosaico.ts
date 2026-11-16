/**
 * Mosaico de ScanMap (frontend/CLAUDE.md §9). Funciones puras: agrupan las 4235 celdas de `scan/layer` en POCOS
 * trazados, uno por clase (veredicto × signo de la pendiente) más uno apagado para "sin hallazgo". Nunca un
 * elemento por celda. No se calcula estadística: el veredicto y la pendiente llegan de la API; aquí solo se
 * mira su signo para elegir el grupo.
 */
import type { EstadoVeredicto, LayerRespuesta, Variable } from '@/shared/api/tipos';
import { colores } from '@/shared/tema';

import { aPantalla, lonParaDibujo, type Tamano, type Vista } from './proyeccion';

type ConHallazgo = Exclude<EstadoVeredicto, 'sin_tendencia'>;
export type ClaseMosaico = `${ConHallazgo}_${'sube' | 'baja'}` | 'sin_hallazgo';

/** Orden de dibujo y de la leyenda (lo apagado primero, así lo demás queda encima). */
export const CLASES_MOSAICO: readonly ClaseMosaico[] = [
  'sin_hallazgo',
  'sensible_a_el_nino_sube',
  'sensible_a_el_nino_baja',
  'cambio_oculto_sube',
  'cambio_oculto_baja',
  'cambio_robusto_sube',
  'cambio_robusto_baja',
];

/** Clase de una celda; `null` si la celda no tiene serie válida (no se dibuja). */
export function claseCelda(veredicto: EstadoVeredicto | null, pendiente: number | null): ClaseMosaico | null {
  if (veredicto === null) return null;
  if (veredicto === 'sin_tendencia' || pendiente === null || pendiente === 0) return 'sin_hallazgo';
  return `${veredicto}_${pendiente > 0 ? 'sube' : 'baja'}`;
}

export type GrupoMosaico = { clase: ClaseMosaico; d: string; celdas: number };

/**
 * Un `d` por clase: cada celda es un cuadrado `M x y h w v h h −w z` del tamaño de `paso_grados`, centrado en la
 * celda (en `lon360`, como todo punto). Las celdas fuera de la pantalla no se escriben.
 */
export function gruposMosaico(layer: LayerRespuesta, v: Vista, t: Tamano): GrupoMosaico[] {
  const lado = layer.paso_grados * v.escala;
  const medio = lado / 2;
  const partes = new Map<ClaseMosaico, string[]>();
  const conteo = new Map<ClaseMosaico, number>();

  for (let i = 0; i < layer.lat.length; i += 1) {
    const clase = claseCelda(layer.veredicto[i] ?? null, layer.pendiente_decada[i] ?? null);
    if (clase === null) continue;
    const lat = layer.lat[i]!;
    const centro = aPantalla(v, t, lonParaDibujo(layer.lon[i]!, v.lonCentro), lat);
    const x = centro.x - medio;
    const y = centro.y - medio;
    if (x > t.ancho || y > t.alto || x + lado < 0 || y + lado < 0) continue;
    const lista = partes.get(clase) ?? [];
    lista.push(`M${r(x)} ${r(y)}h${r(lado)}v${r(lado)}h${r(-lado)}z`);
    partes.set(clase, lista);
    conteo.set(clase, (conteo.get(clase) ?? 0) + 1);
  }

  return CLASES_MOSAICO.filter((c) => partes.has(c)).map((clase) => ({
    clase,
    d: partes.get(clase)!.join(''),
    celdas: conteo.get(clase)!,
  }));
}

const r = (x: number) => Math.round(x * 10) / 10;

/** Variables de agua (sube = más agua → cian; baja = menos agua → ámbar). La temperatura va en escala ámbar. */
const VARIABLES_DE_AGUA: ReadonlySet<Variable> = new Set(['PRECTOTCORR', 'GWETROOT', 'GWETTOP', 'RH2M']);

/**
 * Color y opacidad de un grupo. Propuesta pendiente de aprobación (§13): el rojo queda solo para El Niño; la
 * opacidad (por grupo, no por celda) separa la fuerza del veredicto, y la leyenda lo dice en texto.
 */
export function estiloMosaico(clase: ClaseMosaico, variable: Variable): { color: string; opacidad: number } {
  if (clase === 'sin_hallazgo') return { color: colores.textoSuave, opacidad: 0.12 };
  const sube = clase.endsWith('_sube');
  const color = VARIABLES_DE_AGUA.has(variable)
    ? sube
      ? colores.lluvia
      : colores.sequia
    : sube
      ? colores.sequia
      : colores.textoSuave;
  const opacidad = clase.startsWith('cambio_robusto') ? 0.7 : clase.startsWith('cambio_oculto') ? 0.5 : 0.35;
  return { color, opacidad };
}

const NOMBRE_VEREDICTO: Record<ConHallazgo, string> = {
  cambio_robusto: 'Cambio robusto',
  cambio_oculto: 'Cambio oculto',
  sensible_a_el_nino: 'Sensible a El Niño',
};

/** Texto de la leyenda: "Cambio robusto, sube". */
export function nombreClase(clase: ClaseMosaico): string {
  if (clase === 'sin_hallazgo') return 'Sin tendencia detectable';
  const sube = clase.endsWith('_sube');
  const veredicto = clase.replace(/_(sube|baja)$/, '') as ConHallazgo;
  return `${NOMBRE_VEREDICTO[veredicto]}, ${sube ? 'sube' : 'baja'}`;
}
