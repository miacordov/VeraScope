import { useRouter } from 'expo-router';
import { ScrollView, StyleSheet, View } from 'react-native';

import { LogoVeraScope } from '@/shared/components/LogoVeraScope';
import { colores, espacios } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

/**
 * Inicio (F3, #11): logo, qué es VeraScope en una frase, Investigar y el glosario.
 * Sin "Escanear" (el feed está recortado) ni "Usar demo sin conexión" (espera las respuestas empaquetadas del
 * backend, #8, y el cliente con fuente `empaquetada`).
 */
export default function Inicio() {
  const router = useRouter();

  return (
    <ScrollView style={estilos.fondo} contentContainerStyle={estilos.contenido}>
      <View style={estilos.bloque}>
        <View style={estilos.marca}>
          <LogoVeraScope tamano={56} />
          <Texto variante="titulo" accessibilityRole="header">
            VeraScope
          </Texto>
        </View>
        <Texto suave>Descubre si un cambio en el clima es una tendencia real o solo El Niño.</Texto>
      </View>
      <View style={estilos.botones}>
        <Boton
          texto="Investigar"
          etiqueta="Investigar: elige una variable y un lugar"
          onPress={() => router.navigate('/espacio')}
        />
        <Boton texto="Glosario" variante="secundario" onPress={() => router.navigate('/glosario')} />
      </View>
    </ScrollView>
  );
}

const estilos = StyleSheet.create({
  fondo: { flex: 1, backgroundColor: colores.fondo },
  contenido: { padding: espacios.xl, gap: espacios.xl, maxWidth: 720, width: '100%', alignSelf: 'center' },
  bloque: { gap: espacios.s, paddingTop: espacios.xxl },
  marca: { flexDirection: 'row', alignItems: 'center', gap: espacios.m },
  botones: { gap: espacios.m },
});
