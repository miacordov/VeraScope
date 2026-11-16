/**
 * Líneas causa → consecuencia dibujadas dentro del SVG del mapa (frontend/CLAUDE.md §9). Solo dibuja: el toque
 * lo resuelve el mapa con `lineaTocada` (un `onPress` del SVG chocaría con el gesto de elegir celda), con una zona
 * táctil de `2 · TOLERANCIA_TOQUE` (≥ 24 px) alrededor de cada arco; por eso no hace falta un trazo invisible.
 */
import { Circle, G, Path } from 'react-native-svg';

import type { Linea } from '@/shared/api/tipos';
import { mismaCelda, type Coordenadas } from '@/shared/geo';
import { colores } from '@/shared/tema';

import type { Arco } from './arco';
import { estiloLinea } from './estilo';

type Props = {
  lineas: readonly Linea[];
  /** Un arco por línea, en el mismo orden. */
  arcos: readonly Arco[];
  mesVisible: string | null;
  destino: Coordenadas | null;
};

export function CapaLineas({ lineas, arcos, mesVisible, destino }: Props) {
  const origen = arcos[0]?.inicio;
  return (
    <G testID="mapa-lineas">
      {lineas.map((linea, i) => {
        const arco = arcos[i];
        if (!arco) return null;
        const elegida = mismaCelda(destino, linea);
        const estilo = estiloLinea(linea, mesVisible, elegida);
        return (
          <G key={`${linea.tipo}-${linea.lat}-${linea.lon}`} testID={`linea-${i}`}>
            <Path
              testID={`linea-trazo-${i}`}
              d={arco.d}
              fill="none"
              stroke={estilo.color}
              strokeWidth={estilo.grosor}
              strokeOpacity={estilo.opacidad}
              strokeDasharray={estilo.punteado}
              strokeLinecap="round"
            />
            <Circle
              cx={arco.fin.x}
              cy={arco.fin.y}
              r={elegida ? 6 : 4}
              fill={elegida ? estilo.color : colores.fondo}
              stroke={estilo.color}
              strokeWidth={2}
              opacity={estilo.opacidad}
            />
          </G>
        );
      })}
      {origen ? (
        <Circle cx={origen.x} cy={origen.y} r={4} fill={colores.texto} stroke={colores.fondo} strokeWidth={1.5} />
      ) : null}
    </G>
  );
}
