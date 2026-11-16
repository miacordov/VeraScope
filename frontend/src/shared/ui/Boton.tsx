import { useState } from 'react';
import { Pressable, StyleSheet, type PressableProps } from 'react-native';

import { useEstilos } from '@/shared/useTema';
import { espacios, radios, TOQUE_MIN, type Colores } from '@/shared/tema';

import { Texto } from './Texto';

type Props = Omit<PressableProps, 'children'> & {
  texto: string;
  variante?: 'principal' | 'secundario';
  /** Etiqueta para lectores de pantalla, si debe decir más que el texto visible. */
  etiqueta?: string;
};

/** Botón con rol, etiqueta, estado, zona táctil ≥ 44 × 44 y foco visible en web. */
export function Boton({ texto, variante = 'principal', etiqueta, disabled, style, ...resto }: Props) {
  const estilos = useEstilos(crearEstilos);
  const [enfocado, setEnfocado] = useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={etiqueta ?? texto}
      accessibilityState={{ disabled: !!disabled }}
      disabled={disabled}
      onFocus={() => setEnfocado(true)}
      onBlur={() => setEnfocado(false)}
      style={(estado) => [
        estilos.base,
        variante === 'principal' ? estilos.principal : estilos.secundario,
        estado.pressed && estilos.presionado,
        enfocado && estilos.foco,
        disabled && estilos.deshabilitado,
        typeof style === 'function' ? style(estado) : style,
      ]}
      {...resto}>
      <Texto variante="cuerpoFuerte" style={variante === 'principal' ? estilos.textoPrincipal : undefined}>
        {texto}
      </Texto>
    </Pressable>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    base: {
      minHeight: TOQUE_MIN,
      minWidth: TOQUE_MIN,
      paddingHorizontal: espacios.l,
      paddingVertical: espacios.s,
      borderRadius: radios.m,
      alignItems: 'center',
      justifyContent: 'center',
      borderWidth: 1,
      borderColor: 'transparent',
    },
    principal: { backgroundColor: colores.accion },
    secundario: { backgroundColor: 'transparent', borderColor: colores.borde },
    textoPrincipal: { color: colores.textoSobreAccion },
    presionado: { opacity: 0.75 },
    foco: { borderColor: colores.foco, outlineStyle: 'solid', outlineWidth: 2, outlineColor: colores.foco },
    deshabilitado: { opacity: 0.45 },
  });
