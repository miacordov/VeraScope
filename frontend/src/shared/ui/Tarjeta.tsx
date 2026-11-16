import { StyleSheet, View, type ViewProps } from 'react-native';

import { useEstilos } from '@/shared/useTema';
import { espacios, radios, type Colores } from '@/shared/tema';

export function Tarjeta({ style, ...resto }: ViewProps) {
  const estilos = useEstilos(crearEstilos);
  return <View style={[estilos.tarjeta, style]} {...resto} />;
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    tarjeta: {
      backgroundColor: colores.superficie,
      borderColor: colores.borde,
      borderWidth: 1,
      borderRadius: radios.l,
      padding: espacios.l,
      gap: espacios.s,
    },
  });
