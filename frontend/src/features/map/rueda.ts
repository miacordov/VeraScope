/**
 * Zoom con la rueda del ratón: solo existe en web (`rueda.web.ts`). En el teléfono no hay rueda: se usan el
 * pellizco y los botones ＋ / −, así que esta versión no hace nada.
 */
import type { ComponentRef, RefObject } from 'react';
import type { View } from 'react-native';

import type { Punto } from './proyeccion';

export type RefLienzo = RefObject<ComponentRef<typeof View> | null>;
export type AlGirarRueda = (factor: number, foco: Punto) => void;

export function useZoomConRueda(_lienzo: RefLienzo, _alGirar: AlGirarRueda): void {}
