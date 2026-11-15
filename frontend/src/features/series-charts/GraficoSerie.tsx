/**
 * GraficoSerie: el único componente de gráfico de la app (frontend/CLAUDE.md §10, `series-charts`).
 * react-native-svg + d3-scale para los ejes y d3-shape `line().defined()` para que los `null` sean huecos.
 * No calcula estadística: dibuja lo que manda la API. Dueña: F2 (`fe/graficos-enso`).
 */
import { scaleLinear } from 'd3-scale';
import { line } from 'd3-shape';
import { useState } from 'react';
import { StyleSheet, View, type GestureResponderEvent, type LayoutChangeEvent } from 'react-native';
import Svg, { Circle, Defs, G, Line, Path, Pattern, Rect, Text as SvgText } from 'react-native-svg';

import type { Fase } from '@/shared/api/tipos';
import { numero } from '@/shared/format';
import { colores, espacios, fuentes } from '@/shared/tema';
import { Texto } from '@/shared/ui';

import { useLectura } from './lectura';

export type SerieDibujo = {
  id: string;
  valores: readonly (number | null)[];
  color: string;
  grosor?: number;
  punteada?: boolean;
  /** `false` = se dibuja completa aunque se esté reproduciendo (la recta de tendencia, §8 regla 3). */
  recortar?: boolean;
};

export type PuntoMarcado = { fecha: string; valor: number; etiqueta: string };

type Props = {
  titulo: string;
  unidad: string;
  fechas: readonly string[];
  series: readonly SerieDibujo[];
  /** Fase de El Niño mes a mes: franjas de El Niño (color) y La Niña (trama). */
  fases?: readonly Fase[];
  /** Líneas horizontales de referencia (por ejemplo ±0.5 del índice). */
  referencias?: readonly number[];
  puntos?: readonly PuntoMarcado[];
  /** Mes "AAAA-MM" hasta el que se dibuja; `null` = serie completa. */
  mesVisible: string | null;
  /** Resumen en texto para lectores de pantalla. */
  resumen: string;
  alto?: number;
};

const MARGEN = { izq: 44, der: 8, arriba: 8, abajo: 22 } as const;

export const NOMBRE_FASE: Record<Fase, string> = { nino: 'El Niño', nina: 'La Niña', neutro: 'Neutro' };

/** Índice del último mes dibujado según `mesVisible`. */
export function indiceVisible(fechas: readonly string[], mesVisible: string | null): number {
  if (mesVisible === null) return fechas.length - 1;
  const i = fechas.indexOf(mesVisible);
  return i === -1 ? fechas.length - 1 : i;
}

/** Trazo SVG de una serie: los `null` cortan la línea (huecos, no ceros). */
export function trazoSerie(
  valores: readonly (number | null)[],
  x: (i: number) => number,
  y: (v: number) => number,
): string {
  const generador = line<number | null>()
    .defined((v) => v !== null && Number.isFinite(v))
    .x((_, i) => x(i))
    .y((v) => y(v as number));
  return generador(valores as (number | null)[]) ?? '';
}

export function GraficoSerie({
  titulo,
  unidad,
  fechas,
  series,
  fases,
  referencias = [],
  puntos = [],
  mesVisible,
  resumen,
  alto = 150,
}: Props) {
  const [ancho, setAncho] = useState(0);
  const { indice: lectura, fijarIndice } = useLectura();
  const n = fechas.length;
  const ultimo = indiceVisible(fechas, mesVisible);

  // Rango de los ejes: mínimo y máximo de lo que llega (escala del dibujo, no estadística).
  let minimo = Infinity;
  let maximo = -Infinity;
  for (const s of series) {
    for (const v of s.valores) {
      if (v !== null && Number.isFinite(v)) {
        if (v < minimo) minimo = v;
        if (v > maximo) maximo = v;
      }
    }
  }
  for (const r of referencias) {
    minimo = Math.min(minimo, r);
    maximo = Math.max(maximo, r);
  }
  if (!Number.isFinite(minimo)) {
    minimo = 0;
    maximo = 1;
  }

  const x = scaleLinear()
    .domain([0, Math.max(n - 1, 1)])
    .range([MARGEN.izq, Math.max(ancho - MARGEN.der, MARGEN.izq + 1)]);
  const y = scaleLinear()
    .domain([minimo, maximo === minimo ? minimo + 1 : maximo])
    .nice()
    .range([alto - MARGEN.abajo, MARGEN.arriba]);
  const anchoMes = n > 1 ? x(1) - x(0) : 0;

  const alMover = (e: GestureResponderEvent) => {
    if (n === 0 || ancho === 0) return;
    const i = Math.round(x.invert(e.nativeEvent.locationX));
    fijarIndice(Math.min(Math.max(i, 0), n - 1));
  };

  const valorLeido = lectura !== null ? series[0]?.valores[lectura] : null;
  const franjaLectura =
    lectura !== null && fechas[lectura]
      ? `${fechas[lectura]} · ${valorLeido === null || valorLeido === undefined ? 'sin dato' : `${numero(valorLeido)} ${unidad}`}${
          fases?.[lectura] ? ` · ${NOMBRE_FASE[fases[lectura]]}` : ''
        }`
      : null;

  const anios = n > 0 ? [0, Math.floor((n - 1) / 2), n - 1] : [];

  return (
    <View style={estilos.contenedor}>
      <View style={estilos.cabecera}>
        <Texto variante="cuerpoFuerte">{titulo}</Texto>
        <Texto variante="etiqueta" suave>
          {unidad}
        </Texto>
      </View>
      <Texto variante="etiqueta" suave numerico style={estilos.franja} accessibilityLiveRegion="polite">
        {franjaLectura ?? 'Toca o arrastra sobre el gráfico para leer un mes.'}
      </Texto>
      <View
        accessible
        accessibilityRole="image"
        accessibilityLabel={`${titulo}. ${resumen}`}
        onLayout={(e: LayoutChangeEvent) => setAncho(e.nativeEvent.layout.width)}
        onStartShouldSetResponder={() => true}
        onMoveShouldSetResponder={() => true}
        onResponderGrant={alMover}
        onResponderMove={alMover}
        onResponderRelease={() => fijarIndice(null)}
        onResponderTerminate={() => fijarIndice(null)}
        style={{ height: alto }}>
        {ancho > 0 ? (
          <Svg width={ancho} height={alto} testID={`grafico-${titulo}`}>
            <Defs>
              <Pattern id="trama-nina" patternUnits="userSpaceOnUse" width={6} height={6}>
                <Line x1={0} y1={6} x2={6} y2={0} stroke={colores.nina} strokeWidth={1.5} />
              </Pattern>
            </Defs>

            {fases?.map((f, i) =>
              f === 'neutro' ? null : (
                <Rect
                  key={`fase-${i}`}
                  x={x(i) - anchoMes / 2}
                  y={MARGEN.arriba}
                  width={Math.max(anchoMes, 1)}
                  height={alto - MARGEN.arriba - MARGEN.abajo}
                  fill={f === 'nino' ? colores.nino : 'url(#trama-nina)'}
                  opacity={f === 'nino' ? 0.22 : 0.45}
                />
              ),
            )}

            {y.ticks(3).map((t) => (
              <G key={`tick-${t}`}>
                <Line x1={MARGEN.izq} x2={ancho - MARGEN.der} y1={y(t)} y2={y(t)} stroke={colores.borde} strokeWidth={1} />
                <SvgText
                  x={MARGEN.izq - 6}
                  y={y(t) + 4}
                  fontSize={12}
                  fontFamily={fuentes.normal}
                  fill={colores.textoSuave}
                  textAnchor="end">
                  {numero(t, 1)}
                </SvgText>
              </G>
            ))}

            {referencias.map((r) => (
              <Line
                key={`ref-${r}`}
                x1={MARGEN.izq}
                x2={ancho - MARGEN.der}
                y1={y(r)}
                y2={y(r)}
                stroke={colores.textoSuave}
                strokeDasharray="4 4"
                strokeWidth={1}
              />
            ))}

            {series.map((s) => {
              const valores = s.recortar === false ? s.valores : s.valores.map((v, i) => (i <= ultimo ? v : null));
              return (
                <Path
                  key={s.id}
                  testID={`serie-${s.id}`}
                  d={trazoSerie(valores, x, y)}
                  stroke={s.color}
                  strokeWidth={s.grosor ?? 2}
                  strokeDasharray={s.punteada ? '6 4' : undefined}
                  fill="none"
                />
              );
            })}

            {puntos.map((p) => {
              const i = fechas.indexOf(p.fecha);
              if (i === -1 || i > ultimo) return null;
              return <Circle key={`punto-${p.fecha}`} cx={x(i)} cy={y(p.valor)} r={4} fill={colores.texto} stroke={colores.fondo} />;
            })}

            {lectura !== null ? (
              <Line x1={x(lectura)} x2={x(lectura)} y1={MARGEN.arriba} y2={alto - MARGEN.abajo} stroke={colores.texto} strokeWidth={1} />
            ) : null}

            {anios.map((i) => (
              <SvgText
                key={`anio-${i}`}
                x={x(i)}
                y={alto - 6}
                fontSize={12}
                fontFamily={fuentes.normal}
                fill={colores.textoSuave}
                textAnchor={i === 0 ? 'start' : i === n - 1 ? 'end' : 'middle'}>
                {fechas[i]?.slice(0, 4)}
              </SvgText>
            ))}
          </Svg>
        ) : null}
      </View>
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { gap: espacios.xs },
  cabecera: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  franja: { minHeight: 16 },
});
