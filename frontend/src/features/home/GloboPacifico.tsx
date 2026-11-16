import { useMemo } from 'react';
import Svg, { Circle, Defs, G, Path, RadialGradient, Stop } from 'react-native-svg';

import { tierra } from '@/features/map/costas';
import { useTema } from '@/shared/useTema';

import { trazadoArco, trazadoTierra, type Centro } from './ortografica';

/** Mirando al Pacífico: entran Piura y el norte de Australia, los dos extremos de la línea de la demo 1. */
const VISTA: Centro = { lon: -155, lat: 2 };

/** Celdas de la demo 1 (guion `efecto-espejo`): Piura y el destino del norte de Australia. */
const PIURA: Centro = { lon: -80, lat: -6 };
const NORTE_AUSTRALIA: Centro = { lon: 132, lat: -14 };

/**
 * Colores de la ilustración del planeta. Son fijos (no siguen el modo claro/oscuro), igual que el logo:
 * el globo es la marca, no un dato. El arco usa el token `nino`, porque es la línea de El Niño.
 */
const PLANETA = {
  oceanoCentro: '#2F6FA3',
  oceanoBorde: '#0B2340',
  tierra: '#5E7F52',
  costa: '#8FA77F',
  halo: '#5FA8E8',
} as const;

type Props = { tamano: number };

/** Globo centrado en el Pacífico con el arco Piura → norte de Australia (solo ilustración, sin datos). */
export function GloboPacifico({ tamano }: Props) {
  const { colores } = useTema();
  const radio = tamano / 2 - 8;
  const centro = tamano / 2;
  const tierraD = useMemo(() => trazadoTierra(tierra.anillos, VISTA, radio), [radio]);
  const arcoD = useMemo(() => trazadoArco(PIURA, NORTE_AUSTRALIA, VISTA, radio), [radio]);

  return (
    <Svg
      width={tamano}
      height={tamano}
      accessibilityRole="image"
      accessibilityLabel="La Tierra vista desde el Pacífico, con una línea roja que une Piura con el norte de Australia"
    >
      <Defs>
        <RadialGradient id="oceano" cx="40%" cy="35%" r="70%">
          <Stop offset="0" stopColor={PLANETA.oceanoCentro} />
          <Stop offset="1" stopColor={PLANETA.oceanoBorde} />
        </RadialGradient>
        <RadialGradient id="sombra" cx="35%" cy="30%" r="80%">
          <Stop offset="0.55" stopColor="#000000" stopOpacity={0} />
          <Stop offset="1" stopColor="#000000" stopOpacity={0.55} />
        </RadialGradient>
      </Defs>
      <Circle cx={centro} cy={centro} r={radio + 4} fill={PLANETA.halo} opacity={0.12} />
      <G x={centro} y={centro}>
        <Circle r={radio} fill="url(#oceano)" />
        <Path d={tierraD} fill={PLANETA.tierra} stroke={PLANETA.costa} strokeWidth={0.5} />
        <Path d={arcoD} stroke={colores.nino} strokeWidth={6} strokeOpacity={0.25} fill="none" strokeLinecap="round" />
        <Path d={arcoD} stroke={colores.nino} strokeWidth={2} fill="none" strokeLinecap="round" />
        <Circle r={radio} fill="url(#sombra)" />
      </G>
    </Svg>
  );
}
