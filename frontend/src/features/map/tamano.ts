/**
 * Alto del mapa según el ancho de la ventana (frontend/CLAUDE.md §10). Un solo lugar para la regla, que usan la
 * pantalla (`app/espacio.tsx`) y sus pruebas.
 */
import { cortes } from '@/shared/tema';

/** En pantalla ancha (web/laptop, ≥ 1024) el mapa tiene alto fijo; en teléfono y tableta, ¾ del ancho. */
const ALTO_ANCHA = 480;
const ALTO_MAXIMO_ANGOSTA = 360;

export function altoDelMapa(anchoVentana: number): number {
  if (anchoVentana >= cortes.laptop) return ALTO_ANCHA;
  return Math.min(Math.round(anchoVentana * 0.75), ALTO_MAXIMO_ANGOSTA);
}
