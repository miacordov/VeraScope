/**
 * Estilo de cada línea causa → consecuencia (frontend/CLAUDE.md §9). Función pura: no dibuja ni calcula
 * estadística; solo decide cómo se ve según el tipo que llega de la API y el mes visible del control de tiempo.
 *
 * - `opuesto`: continua y roja (`nino`). `mismo`: punteada en `texto` (su color es una decisión abierta, §13).
 * - `paleta`: los colores del modo actual (`useTema().colores`); por defecto, los del modo oscuro.
 * - Control detenido (`mesVisible = null`): todas se ven (≈ 0.8).
 * - Reproduciendo: se enciende (1 y más gruesa) solo en los meses de `meses_coincidencia`; tenue (≈ 0.15) en los demás.
 */
import type { Linea } from '@/shared/api/tipos';
import { paletas, type Colores } from '@/shared/tema';

export const OPACIDAD_LINEA = {
  reposo: 0.8,
  encendida: 1,
  tenue: 0.15,
} as const;
export const GROSOR_LINEA = { normal: 2, elegida: 3, encendida: 4 } as const;
/** Trazo de la línea de mismo efecto (la forma es la señal; el color solo refuerza). */
export const PUNTEADO = '6 6';

export type EstiloLinea = {
  color: string;
  opacidad: number;
  grosor: number;
  /** `strokeDasharray` del SVG, o `undefined` si es continua. */
  punteado: string | undefined;
};

/** ¿El mes visible es uno de los meses en que ambos lados coinciden? */
export function encendidaEn(linea: Pick<Linea, 'meses_coincidencia'>, mesVisible: string | null): boolean {
  return mesVisible !== null && linea.meses_coincidencia.some((m) => m.fecha === mesVisible);
}

export function estiloLinea(
  linea: Pick<Linea, 'tipo' | 'meses_coincidencia'>,
  mesVisible: string | null,
  elegida = false,
  paleta: Colores = paletas.oscuro,
): EstiloLinea {
  const color = linea.tipo === 'opuesto' ? paleta.nino : paleta.texto;
  const punteado = linea.tipo === 'mismo' ? PUNTEADO : undefined;
  const grosorBase = elegida ? GROSOR_LINEA.elegida : GROSOR_LINEA.normal;

  if (mesVisible === null)
    return {
      color,
      punteado,
      opacidad: OPACIDAD_LINEA.reposo,
      grosor: grosorBase,
    };
  if (encendidaEn(linea, mesVisible)) {
    return {
      color,
      punteado,
      opacidad: OPACIDAD_LINEA.encendida,
      grosor: GROSOR_LINEA.encendida,
    };
  }
  return {
    color,
    punteado,
    opacidad: OPACIDAD_LINEA.tenue,
    grosor: grosorBase,
  };
}
