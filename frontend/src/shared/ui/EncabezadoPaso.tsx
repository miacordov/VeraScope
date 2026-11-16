import { StyleSheet, View } from 'react-native';

import { espacios, type Colores } from '@/shared/tema';
import { useEstilos } from '@/shared/useTema';

import { Texto } from './Texto';

/**
 * Título de una sección con su número de paso (Investigar: 1 Variable → 2 Lugar → 3 Resultado, §10).
 * El número es forma + texto; el lector de pantalla oye "Paso 1: Elige qué mirar".
 */
export function EncabezadoPaso({ numero, titulo, ayuda }: { numero: number; titulo: string; ayuda?: string }) {
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.contenedor}>
      <View style={estilos.fila} accessible accessibilityRole="header" accessibilityLabel={`Paso ${numero}: ${titulo}`}>
        <View style={estilos.numero}>
          <Texto variante="cuerpoFuerte" style={estilos.textoNumero} numerico>
            {numero}
          </Texto>
        </View>
        <Texto variante="subtitulo">{titulo}</Texto>
      </View>
      {ayuda ? (
        <Texto variante="pequeno" suave>
          {ayuda}
        </Texto>
      ) : null}
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: { gap: espacios.xs },
    fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    numero: {
      width: 28,
      height: 28,
      borderRadius: 14,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: colores.info,
    },
    textoNumero: { color: colores.textoSobreAccion, lineHeight: 20 },
  });
