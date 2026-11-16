/**
 * Control de tiempo: Reproducir/Pausa y barra de tiempo propia (frontend/CLAUDE.md §10, `time-comparator`).
 * La barra es `adjustable` (aumentar/disminuir un mes con lector de pantalla y con flechas en web) y se arrastra
 * con el dedo. Solo cambia `mesVisible` y `reproduciendo`: no hace peticiones. Dueña: F2 (`fe/tiempo-comparador`).
 */
import { useState } from 'react';
import {
  Pressable,
  StyleSheet,
  View,
  type AccessibilityActionEvent,
  type GestureResponderEvent,
  type LayoutChangeEvent,
} from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { useEstado } from '@/estado/store';
import { useEstilos } from '@/shared/useTema';
import { espacios, radios, TOQUE_MIN, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

import { useReproduccion } from './useReproduccion';

type Props = { fechas: readonly string[] };

export function ControlTiempo({ fechas }: Props) {
  const estilos = useEstilos(crearEstilos);
  useReproduccion(fechas);
  const { mesVisible, reproduciendo } = useEstado(
    useShallow((e) => ({ mesVisible: e.mesVisible, reproduciendo: e.reproduciendo })),
  );
  const [ancho, setAncho] = useState(0);
  const [enfocado, setEnfocado] = useState(false);

  const n = fechas.length;
  const posicion = mesVisible === null ? n - 1 : Math.max(fechas.indexOf(mesVisible), 0);
  const avance = n > 1 ? posicion / (n - 1) : 1;
  const textoMes = mesVisible ?? (n > 0 ? `${fechas[0]} a ${fechas[n - 1]} (completo)` : 'sin datos');

  const irA = (i: number) => {
    const { irAlMes, detener } = useEstado.getState();
    detener();
    const limitado = Math.min(Math.max(i, 0), n - 1);
    irAlMes(limitado === n - 1 ? null : (fechas[limitado] ?? null));
  };

  const alTocar = (e: GestureResponderEvent) => {
    if (ancho === 0 || n === 0) return;
    irA(Math.round((e.nativeEvent.locationX / ancho) * (n - 1)));
  };

  const alAccion = (e: AccessibilityActionEvent) => {
    if (e.nativeEvent.actionName === 'increment') irA(posicion + 1);
    if (e.nativeEvent.actionName === 'decrement') irA(posicion - 1);
  };

  const alternar = () => {
    const { reproducir, detener } = useEstado.getState();
    if (reproduciendo) detener();
    else reproducir();
  };

  return (
    <View style={estilos.contenedor}>
      <View style={estilos.fila}>
        <Boton
          texto={reproduciendo ? 'Pausa' : 'Reproducir'}
          etiqueta={reproduciendo ? 'Pausar la reproducción' : 'Reproducir la serie en el tiempo'}
          variante="secundario"
          onPress={alternar}
          disabled={n === 0}
        />
        <Texto variante="cuerpoFuerte" numerico accessibilityLiveRegion="polite">
          {textoMes}
        </Texto>
      </View>
      <Pressable
        accessible
        accessibilityRole="adjustable"
        accessibilityLabel="Barra de tiempo"
        accessibilityValue={{ min: 0, max: Math.max(n - 1, 0), now: posicion, text: textoMes }}
        accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
        onAccessibilityAction={alAccion}
        onFocus={() => setEnfocado(true)}
        onBlur={() => setEnfocado(false)}
        onLayout={(e: LayoutChangeEvent) => setAncho(e.nativeEvent.layout.width)}
        onStartShouldSetResponder={() => true}
        onMoveShouldSetResponder={() => true}
        onResponderGrant={alTocar}
        onResponderMove={alTocar}
        style={[estilos.barra, enfocado && estilos.foco]}>
        <View style={estilos.riel}>
          <View style={[estilos.relleno, { width: `${avance * 100}%` }]} />
        </View>
        <View style={[estilos.perilla, { left: `${avance * 100}%` }]} />
      </Pressable>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: { gap: espacios.s },
    fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.m, flexWrap: 'wrap' },
    barra: {
      minHeight: TOQUE_MIN,
      justifyContent: 'center',
      borderRadius: radios.s,
      borderWidth: 2,
      borderColor: 'transparent',
    },
    foco: { borderColor: colores.foco },
    riel: { height: 6, borderRadius: 3, backgroundColor: colores.superficieFuerte, overflow: 'hidden' },
    relleno: { height: 6, backgroundColor: colores.info },
    perilla: {
      position: 'absolute',
      width: 18,
      height: 18,
      marginLeft: -9,
      borderRadius: 9,
      backgroundColor: colores.info,
    },
  });
