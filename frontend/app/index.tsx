import { useIsFocused, useRouter } from 'expo-router';
import { ScrollView, StyleSheet, useWindowDimensions, View } from 'react-native';

import { iniciarDemo } from '@/features/guided-tours';
import { BotonModo } from '@/shared/components/BotonModo';
import { LogoVeraScope } from '@/shared/components/LogoVeraScope';
import { PlanetaGirando } from '@/shared/components/PlanetaGirando';
import { espacios, radios, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';
import { useEstilos } from '@/shared/useTema';

const PASOS = [
  { titulo: 'Elige qué mirar', texto: 'Lluvia, temperatura o humedad, desde 1981.' },
  { titulo: 'Toca un lugar', texto: 'Cualquier punto del mapa del océano Pacífico.' },
  { titulo: 'Quita El Niño', texto: 'Y mira si queda una tendencia de fondo.' },
] as const;

/**
 * Inicio (F3, #11 y #15): logo, qué es VeraScope en una frase, Investigar, la demo guiada y el glosario, con el
 * planeta girando de fondo.
 * Sin "Escanear" (el feed está recortado) ni "Usar demo sin conexión" (espera las respuestas empaquetadas del
 * backend, #8, y el cliente con fuente `empaquetada`).
 */
export default function Inicio() {
  const router = useRouter();
  const enfocada = useIsFocused();
  const estilos = useEstilos(crearEstilos);
  const { width } = useWindowDimensions();
  const tamanoPlaneta = Math.min(width * 1.15, 640);

  const verDemo = () => {
    iniciarDemo('efecto-espejo');
    router.navigate('/espacio');
  };

  return (
    <View style={estilos.fondo}>
      {/* Fondo fijo: el planeta no se desplaza con el contenido y la pantalla lo recorta. */}
      <View style={[estilos.zonaPlaneta, { left: (width - tamanoPlaneta) / 2, top: -tamanoPlaneta * 0.12 }]}>
        <PlanetaGirando tamano={tamanoPlaneta} girando={enfocada} />
      </View>
      <ScrollView style={estilos.desplazable} contentContainerStyle={estilos.contenido}>
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
          <Texto style={estilos.frase}>Descubre si un cambio en el clima es una tendencia real o solo El Niño.</Texto>
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

        <View style={estilos.pasos}>
          <Texto variante="cuerpoFuerte" accessibilityRole="header">
            Cómo funciona
          </Texto>
          {PASOS.map((p, i) => (
            <View
              key={p.titulo}
              style={estilos.paso}
              accessible
              accessibilityLabel={`Paso ${i + 1}: ${p.titulo}. ${p.texto}`}>
              <View style={estilos.numero}>
                <Texto variante="cuerpoFuerte" style={estilos.textoNumero} numerico>
                  {i + 1}
                </Texto>
              </View>
              <View style={estilos.textoPaso}>
                <Texto variante="cuerpoFuerte">{p.titulo}</Texto>
                <Texto variante="pequeno" suave>
                  {p.texto}
                </Texto>
              </View>
            </View>
          ))}
        </View>
      </ScrollView>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    fondo: { flex: 1, backgroundColor: colores.fondo, overflow: 'hidden' },
    desplazable: { flex: 1 },
    contenido: { padding: espacios.xl, gap: espacios.xl, maxWidth: 720, width: '100%', alignSelf: 'center' },
    // El planeta va detrás del título, centrado y algo recortado por arriba; no ocupa espacio en el flujo.
    zonaPlaneta: { position: 'absolute' },
    barra: { alignItems: 'flex-end' },
    bloque: { gap: espacios.m, paddingTop: espacios.xxl },
    marca: { flexDirection: 'row', alignItems: 'center', gap: espacios.m },
    frase: { fontSize: 18, lineHeight: 26 },
    botones: { gap: espacios.m },
    pasos: {
      gap: espacios.m,
      padding: espacios.l,
      borderRadius: radios.l,
      borderWidth: 1,
      borderColor: colores.borde,
      backgroundColor: colores.superficie,
    },
    paso: { flexDirection: 'row', alignItems: 'flex-start', gap: espacios.m },
    numero: {
      width: 28,
      height: 28,
      borderRadius: 14,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colores.info,
    },
    textoNumero: { color: colores.textoSobreAccion, lineHeight: 20 },
    textoPaso: { flex: 1, gap: 2 },
  });
