import { StyleSheet, View } from 'react-native';

import { useSalud } from '@/shared/api/consultas';
import { colores, espacios } from '@/shared/tema';
import { Texto } from '@/shared/ui';

/** Banda obligatoria en toda la interfaz cuando `salud.simulado` es verdadero (§11). */
export function BandaSimulado() {
  const { data } = useSalud();
  if (!data?.simulado) return null;
  return (
    <View
      style={estilos.banda}
      accessible
      accessibilityRole="alert"
      accessibilityLabel="Datos simulados. Estos resultados son de ejemplo, no son datos reales.">
      <Texto variante="cuerpoFuerte" style={estilos.texto}>
        Datos simulados
      </Texto>
      <Texto variante="pequeno" style={estilos.texto}>
        Estos resultados son de ejemplo, no son datos reales.
      </Texto>
    </View>
  );
}

const estilos = StyleSheet.create({
  banda: {
    backgroundColor: colores.aviso,
    borderBottomColor: colores.sequia,
    borderBottomWidth: 2,
    paddingHorizontal: espacios.l,
    paddingVertical: espacios.s,
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'baseline',
    columnGap: espacios.s,
  },
  texto: { color: colores.texto },
});
