import { useRouter } from 'expo-router';
import { Pressable, ScrollView, StyleSheet, useWindowDimensions, View } from 'react-native';

import { iniciarDemo } from '@/features/guided-tours';
import { GloboPacifico } from '@/features/home';
import { BotonModo } from '@/shared/components/BotonModo';
import { LogoVeraScope } from '@/shared/components/LogoVeraScope';
import { espacios, fuentes, TOQUE_MIN, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';
import { useEstilos } from '@/shared/useTema';

/** Tamaño máximo del globo: en laptop o proyector no debe tapar el titular. */
const GLOBO_MAX = 420;

/**
 * Inicio (F3, #11 y #15), estilo "Dark Minimalist" de la referencia de diseño: barra con la marca y los
 * accesos, el globo centrado en el Pacífico con la línea de la demo 1, el titular y un botón para explorar.
 * Sin "Escanear" (el feed está recortado) ni "Usar demo sin conexión" (espera las respuestas empaquetadas del
 * backend, #8, y el cliente con fuente `empaquetada`).
 */
export default function Inicio() {
  const estilos = useEstilos(crearEstilos);
  const router = useRouter();
  const { width, height } = useWindowDimensions();
  const globo = Math.max(200, Math.min(GLOBO_MAX, width - espacios.xl * 2, height * 0.5));

  const investigar = () => router.navigate('/espacio');
  const verDemo = () => {
    iniciarDemo('efecto-espejo');
    router.navigate('/espacio');
  };

  return (
    <ScrollView style={estilos.fondo} contentContainerStyle={estilos.contenido}>
      <View style={estilos.barra}>
        <View style={estilos.marca}>
          <LogoVeraScope tamano={28} />
          <Texto variante="cuerpoFuerte">VeraScope</Texto>
        </View>
        <View style={estilos.navegacion} accessibilityRole="menubar">
          <Enlace texto="Investigar" etiqueta="Investigar: elige una variable y un lugar" onPress={investigar} />
          <Enlace texto="Demos" etiqueta="Ver la demo guiada: El efecto espejo de El Niño" onPress={verDemo} />
          <Enlace texto="Glosario" onPress={() => router.navigate('/glosario')} />
          <BotonModo />
        </View>
      </View>

      <View style={estilos.centro}>
        <GloboPacifico tamano={globo} />
        <Texto accessibilityRole="header" style={estilos.titular}>
          ¿Cambió de verdad, o es El Niño?
        </Texto>
        <Texto suave style={estilos.bajada}>
          Tendencias en datos de la NASA, sin el ruido de El Niño.
        </Texto>
        <Boton
          texto="Explorar"
          etiqueta="Explorar el mapa: elige una variable y un lugar"
          onPress={investigar}
          style={estilos.explorar}
        />
      </View>
    </ScrollView>
  );
}

/** Acceso de la barra superior: texto discreto con zona táctil de 44 × 44. */
function Enlace({ texto, etiqueta, onPress }: { texto: string; etiqueta?: string; onPress: () => void }) {
  const estilos = useEstilos(crearEstilos);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={etiqueta ?? texto}
      onPress={onPress}
      style={({ pressed }) => [estilos.enlace, pressed && estilos.enlacePresionado]}
    >
      <Texto suave variante="pequeno">
        {texto}
      </Texto>
    </Pressable>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    fondo: { flex: 1, backgroundColor: colores.fondo },
    contenido: { flexGrow: 1, padding: espacios.l, gap: espacios.xl, maxWidth: 1100, width: '100%', alignSelf: 'center' },
    barra: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: espacios.s },
    marca: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    navegacion: { flexDirection: 'row', alignItems: 'center', flexWrap: 'wrap', gap: espacios.xs },
    enlace: { minHeight: TOQUE_MIN, minWidth: TOQUE_MIN, paddingHorizontal: espacios.s, justifyContent: 'center' },
    enlacePresionado: { opacity: 0.6 },
    centro: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: espacios.m, paddingBottom: espacios.xxl },
    titular: { fontFamily: fuentes.normal, fontSize: 34, lineHeight: 42, textAlign: 'center', color: colores.texto },
    bajada: { textAlign: 'center' },
    explorar: { marginTop: espacios.s, minWidth: 160, borderRadius: 999 },
  });
