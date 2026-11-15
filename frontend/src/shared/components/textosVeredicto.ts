import type { EstadoVeredicto } from '@/shared/api/tipos';

/**
 * Textos fijos de los cuatro estados (frontend/CLAUDE.md §10, `verdict-card`).
 * El estado lo decide la API; aquí solo se le pone nombre. "Sin tendencia detectable" es un hallazgo válido.
 * Dueña de la tarjeta completa: F3 (`fe/veredicto-feed`).
 */
export const TEXTOS_VEREDICTO: Record<EstadoVeredicto, { titulo: string; explicacion: string; simbolo: string }> = {
  cambio_robusto: {
    titulo: 'Cambio robusto',
    explicacion: 'La tendencia sigue ahí aunque se quite El Niño.',
    simbolo: '●',
  },
  sensible_a_el_nino: {
    titulo: 'Sensible a El Niño',
    explicacion: 'Los eventos de El Niño explican la tendencia que parecía haber.',
    simbolo: '▲',
  },
  cambio_oculto: {
    titulo: 'Cambio oculto',
    explicacion: 'El Niño tapaba una tendencia real.',
    simbolo: '◆',
  },
  sin_tendencia: {
    titulo: 'Sin tendencia detectable',
    explicacion: 'Con estos datos no se ve un cambio. Hace falta un registro más largo.',
    simbolo: '■',
  },
};
