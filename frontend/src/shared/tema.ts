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

/**
 * Modo claro: neutros cálidos (escala "zinc"), bordes finos y el color reservado para los datos.
 * El botón principal es tinta sobre papel, como en la referencia "Dark Minimalist"; contraste AA comprobado en
 * `shared/__tests__/tema.test.tsx`.
 */
const claro: Colores = {
  fondo: '#FAFAF9', // Stone 50
  superficie: '#FFFFFF', // White
  superficieFuerte: '#F4F4F5', // Zinc 100
  borde: '#E4E4E7', // Zinc 200
  texto: '#18181B', // Zinc 900
  textoSuave: '#5F5F68', // Zinc 600 (AA sobre Zinc 100)
  institucional: '#18181B', // Zinc 900
  info: '#0369A1', // Sky 700
  accion: '#18181B', // Zinc 900
  textoSobreAccion: '#FAFAFA', // Zinc 50
  nino: '#DC2626', // ENSO Red
  lluvia: '#0284C7', // Sky 600
  sequia: '#D97706', // Amber 600
  nina: '#71717A', // Zinc 500
  foco: '#18181B', // Zinc 900
  aviso: '#FFFBEB', // Amber 50
  mapaOceano: '#EEF2F6', // Mist
  mapaTierra: '#D4D4D8', // Zinc 300
};

/** Modo oscuro: grafito neutro en lugar de azul; el azul queda solo para el océano del mapa y los datos. */
const oscuro: Colores = {
  fondo: '#09090B', // Zinc 950
  superficie: '#111113', // Graphite
  superficieFuerte: '#1C1C1F', // Zinc 900+
  borde: '#27272A', // Zinc 800
  texto: '#FAFAFA', // Zinc 50
  textoSuave: '#A1A1AA', // Zinc 400
  institucional: '#FAFAFA', // Zinc 50
  info: '#7DD3FC', // Sky 300
  accion: '#FAFAFA', // Zinc 50
  textoSobreAccion: '#09090B', // Zinc 950
  nino: '#F87171', // ENSO Red Light
  lluvia: '#38BDF8', // Sky 400
  sequia: '#FBBF24', // Amber 400
  nina: '#A1A1AA', // Zinc 400
  foco: '#FAFAFA', // Zinc 50
  aviso: '#1C1917', // Stone 900
  mapaOceano: '#0F1722', // Night Ocean
  mapaTierra: '#2A2D33', // Basalt
};

export type Modo = 'claro' | 'oscuro';

export const paletas: Record<Modo, Colores> = { claro, oscuro };

/**
 * @deprecated usar `useTema().colores` o `useEstilos(crearEstilos)` (`shared/useTema.ts`), que siguen el modo claro
 * u oscuro. Queda solo para el código de ramas abiertas (PR #59 y #60), siempre en modo oscuro; se borra cuando nadie
 * lo use (REGLAS_COLABORACION_IA.md §3).
 */
export const colores: Colores = paletas.oscuro;

export const espacios = { xs: 4, s: 8, m: 12, l: 16, xl: 24, xxl: 32 } as const;

export const radios = { s: 6, m: 10, l: 14 } as const;

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
