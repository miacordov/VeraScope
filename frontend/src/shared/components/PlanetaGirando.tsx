/**
 * Planeta de fondo del Inicio: la Tierra en líneas finas (costas de Natural Earth, las mismas del mapa) que gira
 * despacio, con el eje inclinado. Es decoración: no se anuncia a lectores de pantalla ni recibe toques.
 *
 * - Proyección ortográfica hecha a mano (sin librerías): cada punto de costa es un vector 3D que se rota.
 * - Con "reducir movimiento" activado, o si `girando` es falso (pantalla sin foco), se queda quieto.
 * - Una vuelta cada ~90 s, a ~12 cuadros por segundo: suave para algo tan lento y liviano para el teléfono.
 */

import { useEffect, useMemo, useState } from 'react';
import { AccessibilityInfo, AppState, StyleSheet, View } from 'react-native';
import Svg, { Circle, Defs, Path, RadialGradient, Stop } from 'react-native-svg';

import { tierra } from '@/features/map/costas';
import { useTema } from '@/shared/useTema';

type Punto3D = readonly [number, number, number];

const INCLINACION = (-23.4 * Math.PI) / 180;
const PASO_GRADOS = 0.48; // por cuadro → 360° en 750 cuadros ≈ 90 s a 12 fps
const MS_POR_CUADRO = 83;
/** Longitud que se ve de frente al empezar: el Pacífico (160° O), con Sudamérica a la derecha. */
const CENTRO_INICIAL = 200;

function aVector(lon: number, lat: number): Punto3D {
  const l = (lon * Math.PI) / 180;
  const f = (lat * Math.PI) / 180;
  return [Math.cos(f) * Math.sin(l), Math.sin(f), Math.cos(f) * Math.cos(l)];
}

/** Costas simplificadas (uno de cada dos puntos; sin anillos diminutos) como líneas de vectores 3D. */
function lineasCostas(): Punto3D[][] {
  return tierra.anillos
    .filter((a) => a.length >= 16)
    .map((a) => {
      const linea: Punto3D[] = [];
      for (let i = 0; i < a.length; i += 4) linea.push(aVector(a[i], a[i + 1]));
      linea.push(aVector(a[0], a[1]));
      return linea;
    });
}

/** Meridianos cada 30° y paralelos cada 30°, muestreados cada 6°. */
function lineasReticula(): Punto3D[][] {
  const lineas: Punto3D[][] = [];
  for (let lon = 0; lon < 360; lon += 30) {
    const m: Punto3D[] = [];
    for (let lat = -90; lat <= 90; lat += 6) m.push(aVector(lon, lat));
    lineas.push(m);
  }
  for (let lat = -60; lat <= 60; lat += 30) {
    const p: Punto3D[] = [];
    for (let lon = 0; lon <= 360; lon += 6) p.push(aVector(lon, lat));
    lineas.push(p);
  }
  return lineas;
}

/** `d` de las líneas rotadas `giro` grados; solo dibuja la cara visible (corta la línea en el borde). */
function trazado(lineas: Punto3D[][], giro: number, radio: number): string {
  const g = (giro * Math.PI) / 180;
  const cg = Math.cos(g);
  const sg = Math.sin(g);
  const ci = Math.cos(INCLINACION);
  const si = Math.sin(INCLINACION);
  const partes: string[] = [];
  for (const linea of lineas) {
    let dibujando = false;
    for (const [x, y, z] of linea) {
      // Giro sobre el eje polar y luego inclinación del eje.
      const x1 = x * cg + z * sg;
      const z1 = -x * sg + z * cg;
      const y2 = y * ci - z1 * si;
      const z2 = y * si + z1 * ci;
      if (z2 <= 0) {
        dibujando = false;
        continue;
      }
      const px = (radio + x1 * radio).toFixed(1);
      const py = (radio - y2 * radio).toFixed(1);
      partes.push(`${dibujando ? 'L' : 'M'}${px} ${py}`);
      dibujando = true;
    }
  }
  return partes.join('');
}

function useReducirMovimiento(): boolean {
  const [reducir, setReducir] = useState(false);
  useEffect(() => {
    let vigente = true;
    AccessibilityInfo.isReduceMotionEnabled()
      .then((r) => {
        if (vigente) setReducir(r);
      })
      .catch(() => {});
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReducir);
    return () => {
      vigente = false;
      sub.remove();
    };
  }, []);
  return reducir;
}

function useAppActiva(): boolean {
  const [activa, setActiva] = useState(AppState.currentState !== 'background');
  useEffect(() => {
    const sub = AppState.addEventListener('change', (e) => setActiva(e === 'active'));
    return () => sub.remove();
  }, []);
  return activa;
}

export function PlanetaGirando({ tamano, girando = true }: { tamano: number; girando?: boolean }) {
  const { colores, modo } = useTema();
  const reducir = useReducirMovimiento();
  const activa = useAppActiva();
  const costas = useMemo(() => lineasCostas(), []);
  const reticula = useMemo(() => lineasReticula(), []);
  const [centro, setCentro] = useState(CENTRO_INICIAL);
  const animar = girando && activa && !reducir;

  useEffect(() => {
    if (!animar) return;
    // La Tierra gira de oeste a este: con el norte arriba, su superficie se mueve hacia la derecha, así que la
    // longitud que se ve de frente va bajando.
    const id = setInterval(() => setCentro((c) => (c - PASO_GRADOS + 360) % 360), MS_POR_CUADRO);
    return () => clearInterval(id);
  }, [animar]);

  const radio = tamano / 2;
  // Girar −centro deja esa longitud de frente.
  const dCostas = useMemo(() => trazado(costas, -centro, radio - 1), [costas, centro, radio]);
  const dReticula = useMemo(() => trazado(reticula, -centro, radio - 1), [reticula, centro, radio]);
  const oscuro = modo === 'oscuro';

  return (
    <View
      pointerEvents="none"
      accessibilityElementsHidden
      importantForAccessibility="no-hide-descendants"
      style={[estilos.contenedor, { width: tamano, height: tamano }]}
      testID="planeta-girando">
      <Svg width={tamano} height={tamano}>
        <Defs>
          <RadialGradient id="cuerpo" cx="38%" cy="35%" r="70%">
            <Stop offset="0" stopColor={colores.info} stopOpacity={oscuro ? 0.22 : 0.16} />
            <Stop offset="0.7" stopColor={colores.info} stopOpacity={oscuro ? 0.08 : 0.06} />
            <Stop offset="1" stopColor={colores.institucional} stopOpacity={oscuro ? 0.02 : 0.04} />
          </RadialGradient>
          <RadialGradient id="halo" cx="50%" cy="50%" r="50%">
            <Stop offset="0.86" stopColor={colores.info} stopOpacity={0} />
            <Stop offset="0.95" stopColor={colores.info} stopOpacity={oscuro ? 0.18 : 0.12} />
            <Stop offset="1" stopColor={colores.info} stopOpacity={0} />
          </RadialGradient>
        </Defs>
        <Circle cx={radio} cy={radio} r={radio} fill="url(#halo)" />
        <Circle cx={radio} cy={radio} r={radio * 0.9} fill="url(#cuerpo)" />
        <Path
          d={dReticula}
          transform={`translate(${radio * 0.1} ${radio * 0.1}) scale(0.9)`}
          fill="none"
          stroke={colores.info}
          strokeOpacity={oscuro ? 0.16 : 0.2}
          strokeWidth={0.8}
        />
        <Path
          d={dCostas}
          transform={`translate(${radio * 0.1} ${radio * 0.1}) scale(0.9)`}
          fill="none"
          stroke={colores.info}
          strokeOpacity={oscuro ? 0.55 : 0.6}
          strokeWidth={1.1}
          strokeLinejoin="round"
          strokeLinecap="round"
          testID="planeta-costas"
        />
        <Circle
          cx={radio}
          cy={radio}
          r={radio * 0.9}
          fill="none"
          stroke={colores.info}
          strokeOpacity={oscuro ? 0.3 : 0.35}
          strokeWidth={1}
        />
      </Svg>
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { position: 'absolute' },
});
