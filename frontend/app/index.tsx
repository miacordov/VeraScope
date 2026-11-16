import { useRouter } from 'expo-router';
import { ScrollView, StyleSheet, View } from 'react-native';

import { iniciarDemo } from '@/features/guided-tours';
import { BotonModo } from '@/shared/components/BotonModo';
import { LogoVeraScope } from '@/shared/components/LogoVeraScope';
import { useEstilos } from '@/shared/useTema';
import { espacios, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

/**
 * Inicio (F3, #11 y #15): logo, qué es VeraScope en una frase, Investigar, la demo guiada y el glosario.
 * Sin "Escanear" (el feed está recortado) ni "Usar demo sin conexión" (espera las respuestas empaquetadas del
 * backend, #8, y el cliente con fuente `empaquetada`).
 */
export default function Inicio() {
  const estilos = useEstilos(crearEstilos);
  const router = useRouter();

  const verDemo = () => {
    iniciarDemo('efecto-espejo');
    router.navigate('/espacio');
  };

  return (
    <ScrollView style={estilos.fondo} contentContainerStyle={estilos.contenido}>
      <View style={estilos.barra}>
        <BotonModo />
      </View>
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
        <Boton
          texto="Ver la demo: El efecto espejo de El Niño"
          variante="secundario"
          etiqueta="Ver la demo guiada: El efecto espejo de El Niño"
          onPress={verDemo}
        />
        <Boton texto="Glosario" variante="secundario" onPress={() => router.navigate('/glosario')} />
      </View>
    </ScrollView>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    fondo: { flex: 1, backgroundColor: colores.fondo },
    contenido: { padding: espacios.xl, gap: espacios.xl, maxWidth: 720, width: '100%', alignSelf: 'center' },
    barra: { alignItems: 'flex-end' },
    bloque: { gap: espacios.s },
    marca: { flexDirection: 'row', alignItems: 'center', gap: espacios.m },
    botones: { gap: espacios.m },
  });
