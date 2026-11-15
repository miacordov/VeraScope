import { StyleSheet, View, type ViewProps } from 'react-native';

import { colores, espacios, radios } from '@/shared/tema';

export function Tarjeta({ style, ...resto }: ViewProps) {
  return <View style={[estilos.tarjeta, style]} {...resto} />;
}

const estilos = StyleSheet.create({
  tarjeta: {
    backgroundColor: colores.superficie,
    borderColor: colores.borde,
    borderWidth: 1,
    borderRadius: radios.l,
    padding: espacios.l,
    gap: espacios.s,
  },
});
