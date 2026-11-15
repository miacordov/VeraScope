/**
 * Cliente ÚNICO de la API (frontend/CLAUDE.md §8). Toda llamada pasa por aquí:
 * antepone `EXPO_PUBLIC_API_URL` y `/api/v1`, corta a los ~12 s y convierte el error estándar
 * (`{ error: { codigo, mensaje, celda_cercana } }`) en un `ErrorApi`.
 * La app nunca llama a POWER ni a NOAA directamente.
 */
import type {
  AnalyzeRespuesta,
  CodigoError,
  ComparePeriodsRespuesta,
  Coordenadas,
  DemoId,
  DemoRespuesta,
  FeedRespuesta,
  GlosarioRespuesta,
  IndiceId,
  LayerRespuesta,
  SaludRespuesta,
  TeleconnectRespuesta,
  TipoFeed,
  Variable,
  VariablesRespuesta,
} from './tipos';

/** URL base (se incrusta al compilar). En un build de entrega debe ser `https://`. */
export const API_URL = (process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000').replace(/\/+$/, '');

/** POWER en vivo espera 8 s; el cliente corta un poco después. */
export const TIEMPO_MAX_MS = 12_000;

/** Errores propios del cliente, además de los códigos del contrato. */
export type CodigoErrorCliente = CodigoError | 'sin_conexion' | 'tiempo_agotado' | 'respuesta_invalida';

/** `red`: no hubo respuesta del servidor. `servidor`: respondió con el error estándar u otro estado. */
export type TipoFallo = 'red' | 'servidor';

export class ErrorApi extends Error {
  readonly estado: number;
  readonly codigo: CodigoErrorCliente;
  readonly celdaCercana: Coordenadas | null;
  readonly tipo: TipoFallo;

  constructor(datos: {
    estado: number;
    codigo: CodigoErrorCliente;
    mensaje: string;
    celdaCercana?: Coordenadas | null;
    tipo: TipoFallo;
  }) {
    super(datos.mensaje);
    this.name = 'ErrorApi';
    this.estado = datos.estado;
    this.codigo = datos.codigo;
    this.celdaCercana = datos.celdaCercana ?? null;
    this.tipo = datos.tipo;
  }
}

export function esErrorApi(e: unknown): e is ErrorApi {
  return e instanceof ErrorApi;
}

type Parametros = Record<string, string | number | undefined>;

function construirUrl(ruta: string, parametros?: Parametros): string {
  const pares = Object.entries(parametros ?? {}).filter(
    (par): par is [string, string | number] => par[1] !== undefined,
  );
  const consulta = pares.map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`).join('&');
  return `${API_URL}/api/v1${ruta}${consulta ? `?${consulta}` : ''}`;
}

function errorEstandar(cuerpo: unknown): { codigo: CodigoError; mensaje: string; celda_cercana: Coordenadas | null } | null {
  if (typeof cuerpo !== 'object' || cuerpo === null || !('error' in cuerpo)) return null;
  const error = (cuerpo as { error: unknown }).error;
  if (typeof error !== 'object' || error === null) return null;
  const { codigo, mensaje, celda_cercana } = error as Record<string, unknown>;
  if (typeof codigo !== 'string' || typeof mensaje !== 'string') return null;
  return {
    codigo: codigo as CodigoError,
    mensaje,
    celda_cercana: (celda_cercana as Coordenadas | null | undefined) ?? null,
  };
}

/** GET con tiempo máximo. `senal` permite que TanStack Query cancele la petición. */
export async function obtener<T>(ruta: string, parametros?: Parametros, senal?: AbortSignal): Promise<T> {
  const control = new AbortController();
  let agotado = false;
  const reloj = setTimeout(() => {
    agotado = true;
    control.abort();
  }, TIEMPO_MAX_MS);
  const cancelar = () => control.abort();
  senal?.addEventListener('abort', cancelar);

  let respuesta: Response;
  try {
    respuesta = await fetch(construirUrl(ruta, parametros), {
      signal: control.signal,
      headers: { Accept: 'application/json' },
    });
  } catch (e) {
    if (senal?.aborted && !agotado) throw e;
    throw new ErrorApi(
      agotado
        ? {
            estado: 0,
            codigo: 'tiempo_agotado',
            mensaje: 'El servidor tardó demasiado en responder. Vuelve a intentarlo en un momento.',
            tipo: 'red',
          }
        : {
            estado: 0,
            codigo: 'sin_conexion',
            mensaje: 'No se pudo conectar con el servidor. Revisa tu conexión e inténtalo de nuevo.',
            tipo: 'red',
          },
    );
  } finally {
    clearTimeout(reloj);
    senal?.removeEventListener('abort', cancelar);
  }

  const cuerpo: unknown = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const detalle = errorEstandar(cuerpo);
    throw new ErrorApi({
      estado: respuesta.status,
      codigo: detalle?.codigo ?? 'respuesta_invalida',
      // Los mensajes del servidor ya vienen en español sencillo: se muestran tal cual.
      mensaje: detalle?.mensaje ?? `El servidor respondió con un error (${respuesta.status}). Inténtalo de nuevo.`,
      celdaCercana: detalle?.celda_cercana ?? null,
      tipo: 'servidor',
    });
  }
  if (cuerpo === null) {
    throw new ErrorApi({
      estado: respuesta.status,
      codigo: 'respuesta_invalida',
      mensaje: 'El servidor envió una respuesta que no se pudo leer. Inténtalo de nuevo.',
      tipo: 'servidor',
    });
  }
  return cuerpo as T;
}

export type ParametrosAnalyze = {
  variable: Variable;
  lat: number;
  lon: number;
  inicio: number;
  fin: number;
  indice: IndiceId;
};

export type ParametrosPeriodos = {
  variable: Variable;
  lat: number;
  lon: number;
  p1_inicio: number;
  p1_fin: number;
  p2_inicio: number;
  p2_fin: number;
};

/** Una función por ruta del contrato (§17). */
export const api = {
  salud: (senal?: AbortSignal) => obtener<SaludRespuesta>('/salud', undefined, senal),
  variables: (senal?: AbortSignal) => obtener<VariablesRespuesta>('/variables', undefined, senal),
  glosario: (senal?: AbortSignal) => obtener<GlosarioRespuesta>('/glosario', undefined, senal),
  analyze: (p: ParametrosAnalyze, senal?: AbortSignal) => obtener<AnalyzeRespuesta>('/analyze', p, senal),
  teleconnect: (p: { variable: Variable; lat: number; lon: number }, senal?: AbortSignal) =>
    obtener<TeleconnectRespuesta>('/teleconnect', p, senal),
  comparePeriods: (p: ParametrosPeriodos, senal?: AbortSignal) =>
    obtener<ComparePeriodsRespuesta>('/compare-periods', p, senal),
  feed: (tipo: TipoFeed, pagina = 0, senal?: AbortSignal) =>
    obtener<FeedRespuesta>('/scan/feed', { tipo, pagina }, senal),
  layer: (variable: Variable, senal?: AbortSignal) => obtener<LayerRespuesta>('/scan/layer', { variable }, senal),
  demo: (id: DemoId, senal?: AbortSignal) => obtener<DemoRespuesta>(`/demos/${encodeURIComponent(id)}`, undefined, senal),
};
