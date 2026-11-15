import type { AnalyzeRespuesta, Tendencia } from '@/shared/api/tipos';
import { TEXTOS_VEREDICTO } from '@/shared/components/textosVeredicto';
import { conUnidad, numero, pValor } from '@/shared/format';

/**
 * Textos de la tarjeta de veredicto (frontend/CLAUDE.md §10, `verdict-card`).
 * Solo eligen QUÉ mostrar de la respuesta y le dan formato: no calculan nada.
 */

type Vinculo = AnalyzeRespuesta['vinculo_el_nino'];
type Origen = AnalyzeRespuesta['veredicto']['origen'];

/**
 * Atribución que va sobre el veredicto en TODAS las tarjetas: el resultado es lo que muestra la fuente,
 * no un hecho absoluto (revisión de anomalías, hallazgo 6: tendencias de lluvia de MERRA-2 en los
 * trópicos). La fuente sale de la respuesta; no se hace un caso especial por lugar.
 */
export function atribucion(analisis: Pick<AnalyzeRespuesta, 'fuente'>): string {
  return `Según los datos de ${analisis.fuente}`;
}

/** Interruptor apagado: "Tendencia aparente", leída de `tendencia_original`. Flecha + texto (no solo color). */
export function tendenciaAparente(t: Tendencia): { simbolo: string; texto: string } {
  if (t.significativa && t.direccion === 'sube') return { simbolo: '↗', texto: 'Parece que sube' };
  if (t.significativa && t.direccion === 'baja') return { simbolo: '↘', texto: 'Parece que baja' };
  return { simbolo: '→', texto: 'Sin tendencia aparente' };
}

/** Interruptor encendido: la dirección solo se dice si la tendencia sin El Niño es significativa. */
export function direccionSinElNino(t: Tendencia): string | null {
  if (!t.significativa) return null;
  if (t.direccion === 'sube') return 'Sin El Niño, la tendencia sube.';
  if (t.direccion === 'baja') return 'Sin El Niño, la tendencia baja.';
  return null;
}

export function pendiente(t: Tendencia, unidad: string): string {
  return `${conUnidad(t.pendiente_decada, unidad)} por década`;
}

export function intervalo(t: Tendencia, unidad: string): string {
  return `entre ${numero(t.ic_bajo)} y ${conUnidad(t.ic_alto, unidad)}`;
}

/** Solo si la API lo manda (no existe para temperatura). */
export function cambioPorcentual(t: Tendencia): string | null {
  return t.cambio_pct_decada === null ? null : `${numero(t.cambio_pct_decada, 1)} % por década`;
}

/** Con `origen = "escaneo"` se muestra el p ajustado y se dice que está corregido. */
export function pValorTendencia(t: Tendencia, origen: Origen): string {
  if (origen === 'escaneo' && t.p_ajustado !== null) return `${pValor(t.p_ajustado)} (corregido por muchas pruebas)`;
  return pValor(t.p);
}

function retraso(meses: number): string {
  if (meses === 0) return 'en el mismo mes';
  return meses === 1 ? 'con 1 mes de retraso' : `con ${meses} meses de retraso`;
}

/** "Sigue al índice con 3 meses de retraso (r = 0.62)". Nunca redacción causal. */
export function vinculo(v: Vinculo): { texto: string; indicativo: boolean } {
  const r = `r = ${numero(v.r)}`;
  if (!v.significativo) return { texto: `No se ve un vínculo claro con El Niño (${r})`, indicativo: false };
  return { texto: `Sigue al índice de El Niño ${retraso(v.rezago_meses)} (${r})`, indicativo: v.indicativo };
}

/** Lo que se anuncia a los lectores de pantalla cuando cambia lo que dice la tarjeta. */
export function anuncio(analisis: AnalyzeRespuesta, quitarElNino: boolean): string {
  if (!quitarElNino) return `Tendencia aparente: ${tendenciaAparente(analisis.tendencia_original).texto}.`;
  const t = TEXTOS_VEREDICTO[analisis.veredicto.estado];
  return `Veredicto: ${t.titulo}. ${t.explicacion}`;
}
