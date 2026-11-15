/**
 * Un solo formateador de números (es-PE) para toda la app (frontend/CLAUDE.md §13).
 * Solo da formato a lo que llega de la API: no calcula nada.
 */

const MENOS = '−';
const SIN_DATO = 'sin dato';

const cache = new Map<number, Intl.NumberFormat>();

function formateador(decimales: number): Intl.NumberFormat {
  let f = cache.get(decimales);
  if (!f) {
    f = new Intl.NumberFormat('es-PE', {
      minimumFractionDigits: decimales,
      maximumFractionDigits: decimales,
    });
    cache.set(decimales, f);
  }
  return f;
}

/** Número con `decimales` fijos y signo menos tipográfico. `null` → "sin dato". */
export function numero(valor: number | null | undefined, decimales = 2): string {
  if (valor === null || valor === undefined || !Number.isFinite(valor)) return SIN_DATO;
  return formateador(decimales).format(valor).replace('-', MENOS);
}

/** Número siempre con su unidad: "0.31 mm/día". */
export function conUnidad(valor: number | null | undefined, unidad: string, decimales = 2): string {
  const texto = numero(valor, decimales);
  return texto === SIN_DATO ? texto : `${texto} ${unidad}`;
}

/** Coordenadas de una celda: "−5.0°, −80.5°" (lon en −180..180, como llega del servidor). */
export function celda({ lat, lon }: { lat: number; lon: number }): string {
  return `${numero(lat, 1)}°, ${numero(lon, 1)}°`;
}

/** Periodo "1981–1990" a partir de fechas "AAAA-MM". */
export function periodo(inicio: string, fin: string): string {
  return `${inicio.slice(0, 4)}–${fin.slice(0, 4)}`;
}

type FuenteAnalisis = {
  fuente: string;
  descarga: string;
  celda: { lat: number; lon: number };
  ventana: { inicio: string; fin: string };
  indice: { fuente: string };
};

/**
 * Línea de fuente obligatoria (§13):
 * "MERRA-2 vía NASA POWER · celda −5.0°, −80.5° · 1981–2025 · descargado 2026-11-14 · Índice: ONI, NOAA CPC".
 * Todo sale de la respuesta.
 */
export function lineaFuente(r: FuenteAnalisis): string {
  return [
    r.fuente,
    `celda ${celda(r.celda)}`,
    periodo(r.ventana.inicio, r.ventana.fin),
    `descargado ${r.descarga}`,
    `Índice: ${r.indice.fuente}`,
  ].join(' · ');
}
