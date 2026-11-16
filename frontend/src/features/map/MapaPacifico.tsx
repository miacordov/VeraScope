import { useEffect, useMemo, useRef, useState } from 'react';
import { Animated, StyleSheet, View, type LayoutChangeEvent } from 'react-native';
import {
  GestureDetector,
  usePanGesture,
  usePinchGesture,
  useSimultaneousGestures,
  useTapGesture,
} from 'react-native-gesture-handler';
import Svg, { Line, Path, Rect } from 'react-native-svg';

import { arcoLinea, lineaTocada, type Arco } from '@/features/teleconnection-lines/arco';
import { CapaLineas } from '@/features/teleconnection-lines/CapaLineas';
import type { LayerRespuesta, Linea, Variable } from '@/shared/api/tipos';
import { cuantizarCelda, type Coordenadas } from '@/shared/geo';
import { useEstilos, useTema } from '@/shared/useTema';
import { espacios, radios, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

import { BORDE_CELDA, rectanguloCelda } from './celda';
import { trazadoCostas } from './costas';
import { LUGARES } from './lugares';
import { estiloMosaico, gruposMosaico } from './mosaico';
import { useZoomConRueda, type RefLienzo } from './rueda';
import {
  acercar,
  aMapa,
  aPantalla,
  centrarEn,
  desplazar,
  vistaInicial,
  type Punto,
  type Tamano,
  type Vista,
} from './proyeccion';

/** Cuánto acercan o alejan los botones ＋ / −. */
const PASO_ZOOM = 1.6;
/** Un toque falla si el dedo se mueve más de esto (px); el arrastre empieza un poco después. */
const DISTANCIA_TOQUE = 8;
const DISTANCIA_ARRASTRE = 10;
/** Paralelos y meridianos de referencia, cada 30°. */
const RETICULA = 30;

type Props = {
  /** Celda a dibujar: la de la respuesta si ya llegó (el servidor manda), si no la del store. */
  celda: Coordenadas | null;
  /** Recibe la celda de 0.5° ya cuantizada, con `lon` en −180..180. */
  onElegirCelda: (celda: Coordenadas) => void;
  alto: number;
  /** Líneas causa → consecuencia de `teleconnect` (salen de la celda de ScanMap `origen`). */
  teleconexion?: {
    origen: Coordenadas;
    lineas: readonly Linea[];
    destino: Coordenadas | null;
    mesVisible: string | null;
    onElegirLinea: (linea: Linea) => void;
  } | null;
  /** Mosaico de ScanMap (`scan/layer`); solo cuando está visible. */
  mosaico?: { datos: LayerRespuesta; variable: Variable } | null;
};

const SIN_LINEAS: readonly Linea[] = [];

/**
 * Mapa propio en SVG centrado en el Pacífico (frontend/CLAUDE.md §9). Tocar = elegir celda; arrastrar y pellizcar
 * mueven la vista. Durante el gesto solo se transforma el contenedor; al soltar se confirma la vista y se redibuja
 * nítido. Siempre hay botones ＋ / −, "Restablecer vista" y "Lugares" (sin gestos).
 */
export function MapaPacifico({ celda, onElegirCelda, alto, teleconexion = null, mosaico = null }: Props) {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  const [ancho, setAncho] = useState(0);
  const tamano: Tamano = useMemo(() => ({ ancho, alto }), [ancho, alto]);
  const [vistaPropia, setVista] = useState<Vista | null>(null);
  const vista = vistaPropia ?? vistaInicial(tamano);

  const lineas = teleconexion?.lineas ?? SIN_LINEAS;
  const origenLineas = teleconexion?.origen ?? null;
  const arcos: Arco[] = useMemo(
    () => (ancho > 0 && origenLineas ? lineas.map((l) => arcoLinea(vista, tamano, origenLineas, l)) : []),
    [vista, tamano, ancho, origenLineas, lineas],
  );

  // Las funciones de los gestos leen la vista, el tamaño y las líneas más recientes sin volver a crearse.
  const actual = useRef({ vista, tamano, arcos, lineas, alElegirLinea: teleconexion?.onElegirLinea });
  useEffect(() => {
    actual.current = { vista, tamano, arcos, lineas, alElegirLinea: teleconexion?.onElegirLinea };
  });

  // Transformación barata del contenedor mientras dura el gesto (Animated de React Native, sin re-render).
  const [gesto] = useState(() => ({
    tx: new Animated.Value(0),
    ty: new Animated.Value(0),
    escala: new Animated.Value(1),
  }));
  const estiloGesto = {
    transform: [{ translateX: gesto.tx }, { translateY: gesto.ty }, { scale: gesto.escala }],
  };
  const moverGesto = (x: number, y: number, escala = 1) => {
    gesto.tx.setValue(x);
    gesto.ty.setValue(y);
    gesto.escala.setValue(escala);
  };

  const tocar = useTapGesture({
    runOnJS: true,
    maxDistance: DISTANCIA_TOQUE,
    testID: 'mapa-toque',
    onActivate: (e) => {
      const { vista: v, tamano: t, arcos: a, lineas: ls, alElegirLinea } = actual.current;
      // Tocar una línea (zona de ≥ 24 px) elige su destino; si no, el toque elige la celda.
      const i = alElegirLinea ? lineaTocada({ x: e.x, y: e.y }, a) : -1;
      const linea = i >= 0 ? ls[i] : undefined;
      if (linea && alElegirLinea) alElegirLinea(linea);
      else onElegirCelda(cuantizarCelda(aMapa(v, t, { x: e.x, y: e.y })));
    },
  });

  const arrastrar = usePanGesture({
    runOnJS: true,
    minDistance: DISTANCIA_ARRASTRE,
    maxPointers: 1,
    onUpdate: (e) => moverGesto(e.translationX, e.translationY),
    onDeactivate: (e) => {
      const { vista: v, tamano: t } = actual.current;
      setVista(desplazar(v, t, e.translationX, e.translationY));
      moverGesto(0, 0);
    },
  });

  const foco = useRef<Punto>({ x: 0, y: 0 });
  const pellizcar = usePinchGesture({
    runOnJS: true,
    onUpdate: (e) => {
      const { tamano: t } = actual.current;
      foco.current = { x: e.focalX, y: e.focalY };
      // Escala alrededor del punto entre los dedos (el contenedor escala desde su centro).
      moverGesto((e.focalX - t.ancho / 2) * (1 - e.scale), (e.focalY - t.alto / 2) * (1 - e.scale), e.scale);
    },
    onDeactivate: (e) => {
      const { vista: v, tamano: t } = actual.current;
      setVista(acercar(v, t, e.scale, foco.current));
      moverGesto(0, 0);
    },
  });

  // Rueda del ratón (solo web): acerca o aleja dejando quieto el punto bajo el cursor. Se encadena sobre la vista
  // anterior, así varios giros seguidos no se pisan aunque aún no se haya vuelto a dibujar.
  const lienzo: RefLienzo = useRef(null);
  useZoomConRueda(lienzo, (factor, focoRueda) => {
    const { tamano: t } = actual.current;
    if (t.ancho === 0) return;
    setVista((previa) => acercar(previa ?? vistaInicial(t), t, factor, focoRueda));
  });

  // Los tres escuchan a la vez; las distancias no se cruzan: si el dedo se mueve, el toque falla antes de que
  // empiece el arrastre (con "Competing" o "Exclusive" el arrastre o el toque se bloqueaban en web).
  const gestos = useSimultaneousGestures(tocar, pellizcar, arrastrar);

  const costas = useMemo(() => (ancho > 0 ? trazadoCostas(vista, tamano) : ''), [vista, tamano, ancho]);
  const reticula = useMemo(() => {
    if (ancho === 0) return [];
    const lineas: { clave: string; x1: number; y1: number; x2: number; y2: number; ecuador: boolean }[] = [];
    for (let lat = -60; lat <= 60; lat += RETICULA) {
      const y = aPantalla(vista, tamano, 0, lat).y;
      lineas.push({ clave: `lat${lat}`, x1: 0, y1: y, x2: ancho, y2: y, ecuador: lat === 0 });
    }
    for (let lon = -180; lon <= 540; lon += RETICULA) {
      const x = aPantalla(vista, tamano, lon, 0).x;
      if (x >= 0 && x <= ancho) lineas.push({ clave: `lon${lon}`, x1: x, y1: 0, x2: x, y2: alto, ecuador: false });
    }
    return lineas;
  }, [vista, tamano, ancho, alto]);

  // Depende de los datos y la variable, no del objeto `mosaico` (que se crea en cada render del padre).
  const datosMosaico = mosaico?.datos ?? null;
  const variableMosaico = mosaico?.variable ?? null;
  const capasMosaico = useMemo(
    () =>
      datosMosaico && variableMosaico && ancho > 0
        ? gruposMosaico(datosMosaico, vista, tamano).map((g) => ({ ...g, ...estiloMosaico(g.clase, variableMosaico) }))
        : [],
    [datosMosaico, variableMosaico, vista, tamano, ancho],
  );

  const rect = celda && ancho > 0 ? rectanguloCelda(vista, tamano, celda) : null;
  const confirmar = (nueva: Vista) => setVista(nueva);

  return (
    <View style={estilos.contenedor}>
      <GestureDetector gesture={gestos}>
        <View
          ref={lienzo}
          testID="mapa-lienzo"
          style={[estilos.lienzo, { height: alto }]}
          onLayout={(e: LayoutChangeEvent) => setAncho(Math.round(e.nativeEvent.layout.width))}
          accessible
          accessibilityRole="image"
          accessibilityLabel="Mapa del océano Pacífico. Toca un lugar para elegir su celda de 0.5 grados; toca una línea para ver la región del otro extremo. También puedes usar los botones y la lista de líneas de abajo.">
          {ancho > 0 ? (
            <Animated.View style={[StyleSheet.absoluteFill, estiloGesto]}>
              <Svg width={ancho} height={alto} testID="mapa-svg">
                {reticula.map((l) => (
                  <Line
                    key={l.clave}
                    x1={l.x1}
                    y1={l.y1}
                    x2={l.x2}
                    y2={l.y2}
                    stroke={colores.textoSuave}
                    strokeOpacity={0.35}
                    strokeWidth={l.ecuador ? 1.5 : 1}
                    strokeDasharray={l.ecuador ? undefined : '2 4'}
                  />
                ))}
                <Path
                  d={costas}
                  fill={colores.mapaTierra}
                  stroke={colores.textoSuave}
                  strokeWidth={0.75}
                  testID="mapa-costas"
                />
                {capasMosaico.map((g) => (
                  <Path key={g.clase} d={g.d} fill={g.color} fillOpacity={g.opacidad} testID={`mosaico-${g.clase}`} />
                ))}
                {teleconexion ? (
                  <CapaLineas
                    lineas={lineas}
                    arcos={arcos}
                    mesVisible={teleconexion.mesVisible}
                    destino={teleconexion.destino}
                  />
                ) : null}
                {rect ? (
                  <Rect
                    x={rect.x}
                    y={rect.y}
                    width={rect.ancho}
                    height={rect.alto}
                    fill="none"
                    stroke={colores.info}
                    strokeWidth={BORDE_CELDA}
                    testID="mapa-celda"
                  />
                ) : null}
              </Svg>
            </Animated.View>
          ) : null}
        </View>
      </GestureDetector>

      <View style={estilos.controles}>
        <Boton
          texto="＋"
          etiqueta="Acercar el mapa"
          variante="secundario"
          onPress={() => confirmar(acercar(vista, tamano, PASO_ZOOM))}
        />
        <Boton
          texto="−"
          etiqueta="Alejar el mapa"
          variante="secundario"
          onPress={() => confirmar(acercar(vista, tamano, 1 / PASO_ZOOM))}
        />
        <Boton texto="Restablecer vista" variante="secundario" onPress={() => setVista(null)} />
      </View>
      <View style={estilos.controles}>
        <Texto variante="etiqueta" suave>
          Lugares
        </Texto>
        {LUGARES.map((l) => (
          <Boton
            key={l.nombre}
            texto={l.nombre}
            etiqueta={`Centrar el mapa en ${l.nombre}`}
            variante="secundario"
            onPress={() => confirmar(centrarEn(vista, tamano, l.centro))}
          />
        ))}
      </View>
      <Texto variante="etiqueta" suave>
        Costas: Natural Earth (dominio público)
      </Texto>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: { gap: espacios.s },
    lienzo: {
      width: '100%',
      overflow: 'hidden',
      borderRadius: radios.m,
      backgroundColor: colores.mapaOceano,
      borderWidth: 1,
      borderColor: colores.borde,
    },
    controles: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: espacios.s },
  });
