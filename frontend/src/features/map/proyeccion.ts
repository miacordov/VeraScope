/**
 * Proyección equirrectangular del mapa del Pacífico (frontend/CLAUDE.md §9). Funciones puras: no dibujan.
 *
 * La vista se guarda como centro + escala (píxeles por grado). Es lo mismo que `lonMin/lonMax/latMin/latMax`
 * de la guía, pero no deforma el mapa cuando cambia el tamaño de la pantalla.
 * `lonCentro` vive en el espacio continuo de dibujo (0..360, que puede pasar de 360 al desplazarse): las
 * costas se dibujan en −180..180 y en +360, así que el mundo dibujado va de −180 a 540.
 */
import { lon360, type Coordenadas } from '@/shared/geo';

export type Vista = { lonCentro: number; latCentro: number; escala: number };
export type Tamano = { ancho: number; alto: number };
export type Punto = { x: number; y: number };

/** Lo que debe verse al abrir: de Indonesia (~116°) a Piura (~280°), entre 40° S y 40° N. */
export const ENCUADRE_INICIAL = { lonMin: 90, lonMax: 330, latMin: -40, latMax: 40 } as const;

/** Zoom máximo: una celda de 0.5° mide 40 px. */
export const ESCALA_MAXIMA = 80;

/** Extremos del mundo dibujado (costas con desplazamiento 0 y +360). */
const LON_DIBUJADA_MIN = -180;
const LON_DIBUJADA_MAX = 540;

const acotar = (x: number, min: number, max: number) => Math.min(max, Math.max(min, x));

function escalaQueEncuadra(t: Tamano): number {
  const { lonMin, lonMax, latMin, latMax } = ENCUADRE_INICIAL;
  return Math.min(t.ancho / (lonMax - lonMin), t.alto / (latMax - latMin));
}

/** Lo más lejos que se puede alejar: la vuelta entera al mundo a lo ancho, o el encuadre inicial si es menor. */
export function escalaMinima(t: Tamano): number {
  return Math.min(t.ancho / 360, escalaQueEncuadra(t));
}

/** Mantiene la vista dentro del mundo dibujado y entre los zooms permitidos. */
export function limitarVista(v: Vista, t: Tamano): Vista {
  const escala = acotar(v.escala, escalaMinima(t), ESCALA_MAXIMA);
  const medioAncho = t.ancho / 2 / escala;
  const medioAlto = t.alto / 2 / escala;
  const lonCentro =
    medioAncho * 2 >= LON_DIBUJADA_MAX - LON_DIBUJADA_MIN
      ? (LON_DIBUJADA_MIN + LON_DIBUJADA_MAX) / 2
      : acotar(v.lonCentro, LON_DIBUJADA_MIN + medioAncho, LON_DIBUJADA_MAX - medioAncho);
  const latCentro = medioAlto >= 90 ? 0 : acotar(v.latCentro, -90 + medioAlto, 90 - medioAlto);
  return { lonCentro, latCentro, escala };
}

export function vistaInicial(t: Tamano): Vista {
  const { lonMin, lonMax, latMin, latMax } = ENCUADRE_INICIAL;
  return limitarVista(
    { lonCentro: (lonMin + lonMax) / 2, latCentro: (latMin + latMax) / 2, escala: escalaQueEncuadra(t) },
    t,
  );
}

/** Grados → píxeles. `lon` en el espacio continuo de dibujo (usa `lonParaDibujo` para los puntos). */
export function aPantalla(v: Vista, t: Tamano, lon: number, lat: number): Punto {
  return { x: t.ancho / 2 + (lon - v.lonCentro) * v.escala, y: t.alto / 2 - (lat - v.latCentro) * v.escala };
}

/** Píxeles → grados (la longitud sale en el espacio continuo; `cuantizarCelda` la pasa a −180..180). */
export function aMapa(v: Vista, t: Tamano, p: Punto): Coordenadas {
  return { lon: v.lonCentro + (p.x - t.ancho / 2) / v.escala, lat: v.latCentro - (p.y - t.alto / 2) / v.escala };
}

/**
 * Longitud de un PUNTO para dibujarlo: `lon360` (así Piura → Indonesia cruza el Pacífico) y, si la vista se
 * desplazó más allá de 360, la copia más cercana al centro.
 */
export function lonParaDibujo(lon: number, lonCentro: number): number {
  const base = lon360(lon);
  return base + 360 * Math.round((lonCentro - base) / 360);
}

/** Acerca (factor > 1) o aleja (factor < 1) dejando quieto el punto del mapa que está bajo `foco`. */
export function acercar(v: Vista, t: Tamano, factor: number, foco: Punto = { x: t.ancho / 2, y: t.alto / 2 }): Vista {
  const fijo = aMapa(v, t, foco);
  const escala = acotar(v.escala * factor, escalaMinima(t), ESCALA_MAXIMA);
  return limitarVista(
    {
      escala,
      lonCentro: fijo.lon - (foco.x - t.ancho / 2) / escala,
      latCentro: fijo.lat + (foco.y - t.alto / 2) / escala,
    },
    t,
  );
}

/** Arrastra el mapa `dx`, `dy` píxeles (el mapa sigue al dedo). */
export function desplazar(v: Vista, t: Tamano, dx: number, dy: number): Vista {
  return limitarVista({ ...v, lonCentro: v.lonCentro - dx / v.escala, latCentro: v.latCentro + dy / v.escala }, t);
}

/** Centra la vista en un lugar sin cambiar el zoom (accesos directos "Lugares"). */
export function centrarEn(v: Vista, t: Tamano, lugar: Coordenadas): Vista {
  return limitarVista({ ...v, lonCentro: lonParaDibujo(lugar.lon, v.lonCentro), latCentro: lugar.lat }, t);
}
