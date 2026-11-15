/**
 * Estado global (Zustand), frontend/CLAUDE.md §7. Dueño: F1; cualquier campo nuevo lo aprueban F1, F2 y F3.
 *
 * Aquí va SOLO lo que decide el usuario (o una demo). Los datos del servidor viven en TanStack Query.
 * El store no se persiste: al abrir la app se empieza de cero.
 * Los componentes no mutan el estado: usan las acciones.
 */
import { create } from 'zustand';

import type { IndiceId, Linea, TipoFeed, Variable } from '@/shared/api/tipos';
import { cuantizarCelda, type Coordenadas } from '@/shared/geo';

/** Años de la ventana. `fin = null` = hasta el último año completo (`salud.ventana_fin`). */
export type VentanaAnios = { inicio: number; fin: number | null };

export type DemoEnCurso = { id: string; paso: number };

/** Primer año del registro de MERRA-2 en POWER (C5). */
export const ANIO_INICIO_REGISTRO = 1981;

export type DatosEstado = {
  variable: Variable;
  /** Celda de 0.5° cuantizada, con `lon` en −180..180. */
  celda: Coordenadas | null;
  ventana: VentanaAnios;
  quitarElNino: boolean;
  /** Mes "AAAA-MM" hasta el que se dibuja; `null` = serie completa. */
  mesVisible: string | null;
  reproduciendo: boolean;
  destino: Coordenadas | null;
  filtroFeed: TipoFeed;
  demo: DemoEnCurso | null;
  indice: IndiceId;
  mosaicoVisible: boolean;
};

export type AccionesEstado = {
  seleccionarCelda: (celda: Coordenadas | null) => void;
  cambiarVariable: (variable: Variable) => void;
  fijarVentana: (ventana: VentanaAnios) => void;
  fijarIndice: (indice: IndiceId) => void;
  alternarElNino: () => void;
  fijarElNino: (valor: boolean) => void;
  irAlMes: (mes: string | null) => void;
  reproducir: () => void;
  detener: () => void;
  elegirDestino: (destino: Coordenadas | null) => void;
  /** Al llegar `teleconnect`: si no hay destino, toma la primera línea de efecto opuesto (o queda `null`). */
  destinoPorDefecto: (lineas: readonly Pick<Linea, 'tipo' | 'lat' | 'lon'>[]) => void;
  fijarFiltroFeed: (filtro: TipoFeed) => void;
  fijarDemo: (demo: DemoEnCurso | null) => void;
  alternarMosaico: () => void;
  /** Vuelve al estado inicial (pruebas y "Salir" de una demo). */
  reiniciar: () => void;
};

export type EstadoVeraScope = DatosEstado & AccionesEstado;

export const estadoInicial: DatosEstado = {
  variable: 'PRECTOTCORR',
  celda: null,
  ventana: { inicio: ANIO_INICIO_REGISTRO, fin: null },
  quitarElNino: false,
  mesVisible: null,
  reproduciendo: false,
  destino: null,
  filtroFeed: 'fuertes',
  demo: null,
  indice: 'ONI',
  mosaicoVisible: false,
};

/** Lo que se reinicia al cambiar celda, variable, ventana o índice. `quitarElNino` se conserva. */
const reinicioDeAnalisis = { mesVisible: null, reproduciendo: false, destino: null } as const;

export const useEstado = create<EstadoVeraScope>()((set, get) => ({
  ...estadoInicial,

  seleccionarCelda: (celda) => set({ celda: celda ? cuantizarCelda(celda) : null, ...reinicioDeAnalisis }),
  cambiarVariable: (variable) => set({ variable, ...reinicioDeAnalisis }),
  fijarVentana: (ventana) => set({ ventana: { ...ventana }, ...reinicioDeAnalisis }),
  fijarIndice: (indice) => set({ indice, ...reinicioDeAnalisis }),

  alternarElNino: () => set({ quitarElNino: !get().quitarElNino }),
  fijarElNino: (valor) => set({ quitarElNino: valor }),

  irAlMes: (mes) => set({ mesVisible: mes }),
  reproducir: () => set({ reproduciendo: true }),
  detener: () => set({ reproduciendo: false }),

  elegirDestino: (destino) => set({ destino }),
  destinoPorDefecto: (lineas) => {
    if (get().destino !== null) return;
    const opuesta = lineas.find((l) => l.tipo === 'opuesto');
    if (opuesta) set({ destino: { lat: opuesta.lat, lon: opuesta.lon } });
  },

  fijarFiltroFeed: (filtroFeed) => set({ filtroFeed }),
  fijarDemo: (demo) => set({ demo }),
  alternarMosaico: () => set({ mosaicoVisible: !get().mosaicoVisible }),

  reiniciar: () => set({ ...estadoInicial }),
}));
