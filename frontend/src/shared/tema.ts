/**
 * Tokens de la interfaz (frontend/CLAUDE.md §13). Los componentes leen los colores con `useTema()` o
 * `useEstilos()` (`shared/ProveedorTema.tsx`), nunca el valor suelto: así cambian al pasar de modo claro a oscuro.
 *
 * Significado fijo de cada color (igual en los dos modos):
 * - Azul: ciencia, información y datos (gráficos, indicadores, enlaces, selección).
 * - Ámbar: acción, exploración y descubrimiento (botones principales).
 * - Rojo: gravedad, preocupación y riesgo. El rojo no significa "importante", significa "preocupante":
 *   solo El Niño (ENSO Red) y alertas críticas.
 * - Blanco: claridad y legibilidad (fondos, superficies, texto).
 * - Gris y negro: estructura y jerarquía (fondos, bordes, texto secundario).
 */

export type Colores = {
  /** Fondo principal de la aplicación. */
  fondo: string;
  /** Tarjetas, ventanas, paneles y superficies elevadas. */
  superficie: string;
  /** Fondos secundarios (botón secundario, rieles, esqueletos de carga). */
  superficieFuerte: string;
  /** Bordes, divisores y separaciones. */
  borde: string;
  /** Texto principal y títulos. */
  texto: string;
  /** Texto secundario, descripciones y etiquetas. */
  textoSuave: string;
  /** Color institucional: encabezados, navegación e iconos. */
  institucional: string;
  /** Información, datos, enlaces, selección y estados activos. */
  info: string;
  /** Acciones principales y exploración (botón "Investigar", "Escanear"). */
  accion: string;
  /** Texto sobre un fondo `accion`. */
  textoSobreAccion: string;
  /** El Niño y alertas críticas (ENSO Red). Reservado para lo preocupante. */
  nino: string;
  /** Lluvia / más agua (valores de variables; no es La Niña). */
  lluvia: string;
  /** Sequía / menos agua (valores de variables). */
  sequia: string;
  /** La Niña: gris apagado, siempre con trama y etiqueta (§13). */
  nina: string;
  /** Contorno de foco visible (teclado en web). */
  foco: string;
  /** Fondo de la banda "Datos simulados" (lleva borde inferior `sequia`). */
  aviso: string;
  /** Océano del mapa: fondo de mapas y visualizaciones. */
  mapaOceano: string;
  /** Tierra del mapa. */
  mapaTierra: string;
};

/** Modo claro (paleta VeraScope, 15 nov 2026). */
const claro: Colores = {
  fondo: '#F7F7F5', // Space White
  superficie: '#FFFFFF', // Pure White
  superficieFuerte: '#E6E8EB', // Atmosphere Gray
  borde: '#E6E8EB', // Atmosphere Gray
  texto: '#0B0D12', // Obsidian
  textoSuave: '#8B929A', // Orbit Gray
  institucional: '#102B42', // Ocean Deep
  info: '#38A9E0', // Signal Blue
  accion: '#F5A62D', // Discovery Amber
  textoSobreAccion: '#0B0D12', // Obsidian
  nino: '#E3483F', // ENSO Red
  lluvia: '#38A9E0', // Signal Blue
  sequia: '#F5A62D', // Discovery Amber
  nina: '#8B929A', // Orbit Gray
  foco: '#0B0D12', // Obsidian
  aviso: '#FFFFFF', // Pure White
  mapaOceano: '#FFFFFF', // Pure White
  mapaTierra: '#E6E8EB', // Atmosphere Gray
};

/** Modo oscuro (paleta VeraScope, 15 nov 2026). */
const oscuro: Colores = {
  fondo: '#0B0D12', // Obsidian
  superficie: '#111820', // Deep Surface
  superficieFuerte: '#17364F', // Ocean Panel
  borde: '#17364F', // Ocean Panel
  texto: '#F5F7F8', // Star White
  textoSuave: '#AAB3BC', // Atmospheric Gray
  institucional: '#F5F7F8', // Star White
  info: '#4AB7E8', // Signal Blue Light
  accion: '#FFB23D', // Discovery Amber
  textoSobreAccion: '#0B0D12', // Obsidian
  nino: '#F0524A', // ENSO Red Light
  lluvia: '#4AB7E8', // Signal Blue Light
  sequia: '#FFB23D', // Discovery Amber
  nina: '#AAB3BC', // Atmospheric Gray
  foco: '#F5F7F8', // Star White
  aviso: '#111820', // Deep Surface
  mapaOceano: '#17364F', // Ocean Panel
  mapaTierra: '#111820', // Deep Surface
};

export type Modo = 'claro' | 'oscuro';

export const paletas: Record<Modo, Colores> = { claro, oscuro };

/**
 * @deprecated usar `useTema().colores` o `useEstilos(crearEstilos)` (`shared/useTema.ts`), que siguen el modo claro
 * u oscuro. Queda solo para el código de ramas abiertas (PR #60), siempre en modo oscuro; se borra cuando nadie
 * lo use (REGLAS_COLABORACION_IA.md §3).
 */
export const colores: Colores = paletas.oscuro;

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

export const tema = { paletas, espacios, radios, fuentes, tipografia } as const;
export type Tema = typeof tema;
