import { useRouter } from 'expo-router';
import { ScrollView, StyleSheet, View } from 'react-native';

import { colores, espacios } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

/**
 * Inicio MÍNIMO del esqueleto (`chore/contratos`). La página completa (demos, Escanear,
 * "Usar demo sin conexión") es de F3 en `fe/veredicto-feed`.
 */
export default function Inicio() {
  const router = useRouter();
  return (
    <ScrollView style={estilos.fondo} contentContainerStyle={estilos.contenido}>
      <View style={estilos.bloque}>
        <Texto variante="titulo" accessibilityRole="header">
          VeraScope
        </Texto>
        <Texto suave>Descubre si un cambio en el clima es una tendencia real o solo El Niño.</Texto>
      </View>
      <View style={estilos.botones}>
        <Boton texto="Investigar" onPress={() => router.push('/espacio')} />
        <Boton texto="Glosario" variante="secundario" onPress={() => router.push('/glosario')} />
      </View>
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  fondo: { flex: 1, backgroundColor: colores.fondo },
  contenido: { padding: espacios.xl, gap: espacios.xl, maxWidth: 720, width: '100%', alignSelf: 'center' },
  bloque: { gap: espacios.s, paddingTop: espacios.xxl },
  botones: { gap: espacios.m },
});
