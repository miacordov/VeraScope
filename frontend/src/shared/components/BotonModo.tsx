import { useState } from 'react';
import { Pressable, StyleSheet } from 'react-native';
import Svg, { Circle, Line, Path } from 'react-native-svg';

import { useEstilos, useTema } from '@/shared/useTema';
import { radios, TOQUE_MIN, type Colores } from '@/shared/tema';

const RAYOS = [0, 45, 90, 135, 180, 225, 270, 315];

/** Botón para pasar de modo oscuro a claro y al revés. Muestra el modo al que lleva (sol → claro, luna → oscuro). */
export function BotonModo() {
  const { modo, colores, alternarModo } = useTema();
  const estilos = useEstilos(crearEstilos);
  const [enfocado, setEnfocado] = useState(false);
  const haciaClaro = modo === 'oscuro';
  const etiqueta = haciaClaro ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={etiqueta}
      onPress={alternarModo}
      onFocus={() => setEnfocado(true)}
      onBlur={() => setEnfocado(false)}
      style={({ pressed }) => [estilos.boton, pressed && estilos.presionado, enfocado && estilos.foco]}>
      <Svg width={22} height={22} viewBox="0 0 24 24">
        {haciaClaro ? (
          <>
            <Circle cx={12} cy={12} r={4.5} fill="none" stroke={colores.institucional} strokeWidth={2} />
            {RAYOS.map((grados) => {
              const rad = (grados * Math.PI) / 180;
              return (
                <Line
                  key={grados}
                  x1={12 + Math.cos(rad) * 7.5}
                  y1={12 + Math.sin(rad) * 7.5}
                  x2={12 + Math.cos(rad) * 10}
                  y2={12 + Math.sin(rad) * 10}
                  stroke={colores.institucional}
                  strokeWidth={2}
                  strokeLinecap="round"
                />
              );
            })}
          </>
        ) : (
          <Path
            d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"
            fill="none"
            stroke={colores.institucional}
            strokeWidth={2}
            strokeLinejoin="round"
          />
        )}
      </Svg>
    </Pressable>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    boton: {
      width: TOQUE_MIN,
      height: TOQUE_MIN,
      borderRadius: radios.m,
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 2,
      borderColor: 'transparent',
    },
    presionado: { opacity: 0.7 },
    foco: { borderColor: colores.foco },
  });
