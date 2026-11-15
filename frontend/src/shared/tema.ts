/**
 * Tokens de la interfaz (frontend/CLAUDE.md §13). Los componentes importan el token, nunca el valor suelto.
 * El azul es de la marca (el planeta): no se usa como color de interfaz.
 */

export const colores = {
  /** Fondo grafito. */
  fondo: '#0E0F11',
  /** Superficies (tarjetas, hoja inferior) un poco más claras que el fondo. */
  superficie: '#17191D',
  superficieFuerte: '#20232A',
  borde: '#2C3038',
  /** Texto principal. */
  texto: '#F2F2F0',
  /** Texto secundario (contraste ≥ 4.5:1 sobre `fondo`). */
  textoSuave: '#A7ABB3',
  /** El Niño: franjas, línea de efecto opuesto, interruptor activo. */
  nino: '#E04A3A',
  /** Lluvia / más agua (valores de variables; no es La Niña). */
  lluvia: '#4FC3F7',
  /** Sequía / menos agua (valores de variables). */
  sequia: '#F2A93B',
  /** La Niña: gris azulado apagado, siempre con trama y etiqueta (decisión abierta, §13). */
  nina: '#7D8A99',
  /** Contorno de foco visible (teclado en web). */
  foco: '#F2F2F0',
  /** Fondo de la banda "Datos simulados". */
  aviso: '#3A2F12',
} as const;

export const espacios = { xs: 4, s: 8, m: 12, l: 16, xl: 24, xxl: 32 } as const;

export const radios = { s: 6, m: 12, l: 18 } as const;

/** Familias de Inter cargadas en `app/_layout.tsx` con @expo-google-fonts/inter. */
export const fuentes = {
  normal: 'Inter_400Regular',
  media: 'Inter_500Medium',
  seminegrita: 'Inter_600SemiBold',
  negrita: 'Inter_700Bold',
} as const;

/** Escala tipográfica corta. Texto base ≥ 16; etiquetas de gráficos ≥ 12. */
export const tipografia = {
  titulo: { fontFamily: fuentes.negrita, fontSize: 28, lineHeight: 34 },
  subtitulo: { fontFamily: fuentes.seminegrita, fontSize: 20, lineHeight: 26 },
  cuerpo: { fontFamily: fuentes.normal, fontSize: 16, lineHeight: 24 },
  cuerpoFuerte: { fontFamily: fuentes.seminegrita, fontSize: 16, lineHeight: 24 },
  pequeno: { fontFamily: fuentes.normal, fontSize: 14, lineHeight: 20 },
  etiqueta: { fontFamily: fuentes.media, fontSize: 12, lineHeight: 16 },
} as const;

/** Zona táctil mínima (§13, accesibilidad). */
export const TOQUE_MIN = 44;

/** Cortes de diseño adaptable (§10): teléfono < 768 ≤ tableta < 1024 ≤ web/laptop. */
export const cortes = { tableta: 768, laptop: 1024 } as const;

export const tema = { colores, espacios, radios, fuentes, tipografia } as const;
export type Tema = typeof tema;
