/**
 * Consultas de TanStack Query con las llaves de frontend/CLAUDE.md §8.
 * Los datos del servidor viven aquí, nunca en el store.
 */
import { useQuery } from '@tanstack/react-query';

import { api, type ParametrosAnalyze } from './cliente';
import type { Variable } from './tipos';

/** Parámetros de `teleconnect`: la misma variable y celda que `analyze` (sin ventana ni índice). */
export type ParametrosTeleconnect = { variable: Variable; lat: number; lon: number };

export const llaves = {
  salud: ['salud'] as const,
  variables: ['variables'] as const,
  glosario: ['glosario'] as const,
  analyze: (p: ParametrosAnalyze) => ['analyze', p.variable, p.lat, p.lon, p.inicio, p.fin, p.indice] as const,
  teleconnect: (p: ParametrosTeleconnect) => ['teleconnect', p.variable, p.lat, p.lon] as const,
  layer: (variable: Variable) => ['layer', variable] as const,
};

export function useSalud() {
  return useQuery({ queryKey: llaves.salud, queryFn: ({ signal }) => api.salud(signal) });
}

export function useVariables() {
  return useQuery({ queryKey: llaves.variables, queryFn: ({ signal }) => api.variables(signal) });
}

export function useGlosario() {
  return useQuery({ queryKey: llaves.glosario, queryFn: ({ signal }) => api.glosario(signal) });
}

/** `parametros = null` no dispara la llamada (sin celda o sin ventana válida). */
export function useAnalyze(parametros: ParametrosAnalyze | null) {
  return useQuery({
    queryKey: parametros ? llaves.analyze(parametros) : ['analyze', 'sin-seleccion'],
    queryFn: ({ signal }) => api.analyze(parametros as ParametrosAnalyze, signal),
    enabled: parametros !== null,
  });
}

/** Líneas causa → consecuencia de la celda; va en paralelo con `analyze` (§6, regla 1). `null` = sin celda. */
export function useTeleconnect(parametros: ParametrosTeleconnect | null) {
  return useQuery({
    queryKey: parametros ? llaves.teleconnect(parametros) : ['teleconnect', 'sin-seleccion'],
    queryFn: ({ signal }) => api.teleconnect(parametros as ParametrosTeleconnect, signal),
    enabled: parametros !== null,
  });
}

/** Mosaico de ScanMap: solo se pide cuando `activo` (`mosaicoVisible`). */
export function useLayer(variable: Variable, activo: boolean) {
  return useQuery({
    queryKey: llaves.layer(variable),
    queryFn: ({ signal }) => api.layer(variable, signal),
    enabled: activo,
  });
}
