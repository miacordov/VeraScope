import { esErrorApi, type CodigoErrorCliente } from '@/shared/api/cliente';
import { numero } from '@/shared/format';

/**
 * Textos de los estados de la interfaz (frontend/CLAUDE.md §11).
 *
 * Reglas que siguen todos los textos:
 * - Explican qué pasó y cómo seguir, sin disculpas, sin jerga y sin redacción causal.
 * - Los mensajes de error de la API ya vienen en español: se muestran TAL CUAL. Los textos de
 *   `mensajeRespaldo` solo se usan si el error llega sin mensaje.
 * - "Sin tendencia detectable" no está aquí: es un hallazgo válido y su texto vive en `textosVeredicto.ts`.
 * - "Datos simulados" no está aquí: lo muestra `BandaSimulado.tsx`.
 * - No se calcula nada: solo se da formato a lo que llega de la API (ni porcentajes).
 */

/** Qué botón ofrece cada error. `null` = no hay botón (el usuario corrige su elección). */
export type AccionError = 'reintentar' | 'celda_cercana' | 'usar_lluvia' | null;

type TextoError = { titulo: string; mensajeRespaldo: string; accion: AccionError };

export const TEXTOS_ERROR: Record<CodigoErrorCliente, TextoError> = {
  ventana_corta: {
    titulo: 'Elige al menos 10 años',
    mensajeRespaldo: 'Elige al menos 10 años. Con menos, el ruido de un año a otro impide ver tendencias.',
    accion: null,
  },
  fuera_de_rango: {
    titulo: 'Fuera de los datos disponibles',
    mensajeRespaldo: 'Ese lugar o esos años están fuera de los datos disponibles. Elige otro lugar o cambia los años.',
    accion: null,
  },
  sin_datos_tierra: {
    titulo: 'Esta variable no aplica sobre el mar',
    mensajeRespaldo:
      'La humedad del suelo solo existe en tierra firme. Sobre el mar puedes ver la lluvia o la temperatura.',
    accion: 'usar_lluvia',
  },
  power_lento: {
    titulo: 'Los datos de este lugar están tardando',
    mensajeRespaldo:
      'NASA POWER tarda en enviar los datos de este lugar. Puedes ver ahora la celda más cercana que ya está guardada.',
    accion: 'celda_cercana',
  },
  power_error: {
    titulo: 'No llegaron los datos de este lugar',
    mensajeRespaldo: 'NASA POWER no respondió bien. Vuelve a intentarlo en un momento.',
    accion: 'reintentar',
  },
  escaneo_en_curso: {
    titulo: 'El escaneo aún no termina',
    mensajeRespaldo:
      'Las líneas y el mosaico aparecen cuando termine el escaneo. El análisis de este lugar ya está disponible.',
    accion: null,
  },
  sin_conexion: {
    titulo: 'Sin conexión',
    mensajeRespaldo: 'No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.',
    accion: 'reintentar',
  },
  tiempo_agotado: {
    titulo: 'El servidor tardó demasiado',
    mensajeRespaldo: 'El servidor tardó demasiado en responder. Vuelve a intentarlo en un momento.',
    accion: 'reintentar',
  },
  respuesta_invalida: {
    titulo: 'No se pudo leer la respuesta',
    mensajeRespaldo: 'El servidor envió una respuesta que no se pudo leer. Inténtalo de nuevo.',
    accion: 'reintentar',
  },
};

/** Texto del botón de cada acción. Una acción se llama igual en todo el flujo. */
export const TEXTOS_ACCION: Record<Exclude<AccionError, null>, string> = {
  reintentar: 'Reintentar',
  celda_cercana: 'Usar la celda cercana',
  usar_lluvia: 'Ver la lluvia en este lugar',
};

/** Error de algo que no es un `ErrorApi` (no debería pasar, pero nunca se muestra una traza). */
const ERROR_DESCONOCIDO = {
  titulo: 'No se pudo cargar',
  mensaje: 'Algo salió mal al pedir los datos. Inténtalo de nuevo.',
  accion: 'reintentar',
} as const;

export type EstadoError = { titulo: string; mensaje: string; accion: AccionError };

/**
 * Convierte cualquier error en lo que se muestra: título, mensaje y botón.
 * - El mensaje del servidor se respeta tal cual.
 * - `power_lento` sin `celda_cercana` ofrece reintentar, nunca un botón que no lleva a ningún lado.
 */
export function estadoDeError(error: unknown): EstadoError {
  if (!esErrorApi(error)) return { ...ERROR_DESCONOCIDO };
  const textos = TEXTOS_ERROR[error.codigo] ?? null;
  if (textos === null) return { ...ERROR_DESCONOCIDO, mensaje: error.message || ERROR_DESCONOCIDO.mensaje };
  const accion = textos.accion === 'celda_cercana' && error.celdaCercana === null ? 'reintentar' : textos.accion;
  return { titulo: textos.titulo, mensaje: error.message || textos.mensajeRespaldo, accion };
}

/** Estados que no son errores (§11). */
export const TEXTOS_ESTADO = {
  /** Esqueleto mientras llega una celda nueva (etiqueta para lectores de pantalla). */
  cargando: 'Cargando el análisis de este lugar',
  /** Vacío que invita a actuar. "Elige" vale para teléfono y web. */
  sinCelda: 'Elige un lugar en el mapa para ver su análisis.',
  /** Insignia obligatoria cuando `veredicto.origen = "individual"`. */
  analisisIndividual: 'análisis individual',
  /** Feed y estado del escaneo (`escaneo.estado = "en_curso"`): nunca una lista vacía. */
  escaneoEnCurso: 'Escaneo en curso',
  /** Respaldo si `mensaje_vacio` llegara en `null` con la lista de líneas vacía. También es un resultado. */
  sinLineasRespaldo: 'No se encontró un vínculo que cumpla los criterios.',
  /** Banda obligatoria cuando se usa la demo guardada (§8). */
  bandaSinConexion: 'Sin conexión · mostrando la demo guardada en la app',
  /** Sin `assets/demo/` y sin red. */
  sinDemoGuardada: {
    titulo: 'La demo sin conexión aún no está incluida',
    mensaje: 'Esta versión de la app todavía no trae la demo guardada. Conéctate a internet para verla.',
  },
} as const;

/** "1,200 de 4,235 lugares listos" (solo formato: el frontend no calcula porcentajes). */
export function avanceEscaneo(celdasListas: number, celdasTotal: number): string {
  return `${numero(celdasListas, 0)} de ${numero(celdasTotal, 0)} lugares listos`;
}

/** Celda fuera de la rejilla de ScanMap: de dónde salen las líneas (la distancia viene de la API). */
export function lineasDesdeCeldaCercana(distanciaKm: number): string {
  return `Las líneas salen del punto de ScanMap más cercano, a ${numero(distanciaKm, 0)} km.`;
}
