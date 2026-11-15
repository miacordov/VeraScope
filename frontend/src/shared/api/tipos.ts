/**
 * Nombres cortos para los tipos del contrato. NO se escriben tipos a mano aquí:
 * todo sale de `esquema.ts`, que se regenera con `npm run tipos` desde `/openapi.json`.
 */
import type { components } from './esquema';

type S = components['schemas'];

export type Variable = S['Variable'];
export type IndiceId = S['IndiceId'];
export type EstadoVeredicto = S['EstadoVeredicto'];
export type Direccion = S['Direccion'];
export type Fase = S['Fase'];
export type OrigenVeredicto = S['OrigenVeredicto'];
export type TipoLinea = S['TipoLinea'];
export type TipoFeed = S['TipoFeed'];
export type CodigoAviso = S['CodigoAviso'];
export type CodigoError = S['CodigoError'];

export type Coordenadas = S['Coordenadas'];
export type Escaneo = S['Escaneo'];
export type SaludRespuesta = S['SaludRespuesta'];
export type DefinicionVariable = S['DefinicionVariable'];
export type DefinicionIndice = S['DefinicionIndice'];
export type VariablesRespuesta = S['VariablesRespuesta'];
export type GlosarioRespuesta = S['GlosarioRespuesta'];
export type Termino = S['Termino'];
export type Tendencia = S['Tendencia'];
export type AnalyzeRespuesta = S['AnalyzeRespuesta'];
export type Linea = S['Linea'];
export type TeleconnectRespuesta = S['TeleconnectRespuesta'];
export type ComparePeriodsRespuesta = S['ComparePeriodsRespuesta'];
export type Tarjeta = S['Tarjeta'];
export type FeedRespuesta = S['FeedRespuesta'];
export type LayerRespuesta = S['LayerRespuesta'];
export type DemoRespuesta = S['DemoRespuesta'];
export type PasoDemo = S['PasoDemo'];
export type ErrorDetalle = S['ErrorDetalle'];
export type ErrorRespuesta = S['ErrorRespuesta'];

export type DemoId = DemoRespuesta['id'];
