import { useState, type ReactNode } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';

import { espacios, radios, TOQUE_MIN, type Colores } from '@/shared/tema';
import { useEstilos } from '@/shared/useTema';

import { Texto } from './Texto';

type Props = {
  /** Texto del botón cuando está cerrado ("Ver detalles"). */
  titulo: string;
  /** Texto del botón cuando está abierto; por defecto, el mismo título. */
  tituloAbierto?: string;
  /** Una línea con lo esencial, visible aunque esté cerrado. */
  resumen?: string;
  abiertoAlInicio?: boolean;
  children: ReactNode;
};

/**
 * Sección que se abre y se cierra para no mostrar todos los datos a la vez. Lo que hay dentro no cambia: solo se
 * esconde hasta que el usuario lo pide. Rol de botón con estado `expanded`, zona táctil ≥ 44 y foco visible.
 */
export function Desplegable({ titulo, tituloAbierto, resumen, abiertoAlInicio = false, children }: Props) {
  const estilos = useEstilos(crearEstilos);
  const [abierto, setAbierto] = useState(abiertoAlInicio);
  const [enfocado, setEnfocado] = useState(false);
  const texto = abierto ? (tituloAbierto ?? titulo) : titulo;

  return (
    <View style={estilos.contenedor}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={texto}
        accessibilityState={{ expanded: abierto }}
        onPress={() => setAbierto((a) => !a)}
        onFocus={() => setEnfocado(true)}
        onBlur={() => setEnfocado(false)}
        style={({ pressed }) => [estilos.cabecera, pressed && estilos.presionado, enfocado && estilos.foco]}>
        <View style={estilos.textos}>
          <Texto variante="cuerpoFuerte" style={estilos.titulo}>
            {texto}
          </Texto>
          {resumen && !abierto ? (
            <Texto variante="pequeno" suave numerico>
              {resumen}
            </Texto>
          ) : null}
        </View>
        <Texto variante="subtitulo" style={estilos.flecha} importantForAccessibility="no" accessibilityElementsHidden>
          {abierto ? '−' : '+'}
        </Texto>
      </Pressable>
      {abierto ? <View style={estilos.cuerpo}>{children}</View> : null}
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: {
      borderTopColor: colores.borde,
      borderTopWidth: 1,
      paddingTop: espacios.xs,
    },
    cabecera: {
      minHeight: TOQUE_MIN,
      flexDirection: 'row',
      alignItems: 'center',
      gap: espacios.m,
      borderRadius: radios.s,
      borderWidth: 2,
      borderColor: 'transparent',
      paddingVertical: espacios.xs,
    },
    textos: { flex: 1, gap: 2 },
    titulo: { color: colores.info },
    flecha: { color: colores.info, width: 24, textAlign: 'center' },
    presionado: { opacity: 0.7 },
    foco: { borderColor: colores.foco },
    cuerpo: { gap: espacios.s, paddingTop: espacios.xs },
  });
