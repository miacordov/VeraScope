import { StyleSheet, View } from 'react-native';

import { espacios, fuentes, type Colores } from '@/shared/tema';
import { useEstilos } from '@/shared/useTema';

import { Texto } from './Texto';

type Props = {
  /** Número del paso en el recorrido (1, 2, 3); se omite en secciones que no son un paso. */
  paso?: number;
  titulo: string;
  /** Una frase que dice para qué sirve la sección y qué pasa al usarla. */
  ayuda: string;
};

/** Encabezado de sección: número de paso, título y una línea de ayuda en lenguaje simple. */
export function EncabezadoPaso({ paso, titulo, ayuda }: Props) {
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.contenedor}>
      <View style={estilos.fila}>
        {paso !== undefined ? (
          <View style={estilos.numero} accessibilityLabel={`Paso ${paso}`}>
            <Texto variante="etiqueta" style={estilos.textoNumero}>
              {paso}
            </Texto>
          </View>
        ) : null}
        <Texto variante="subtitulo" accessibilityRole="header" style={estilos.titulo}>
          {titulo}
        </Texto>
      </View>
      <Texto variante="pequeno" suave>
        {ayuda}
      </Texto>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: { gap: espacios.xs, paddingBottom: espacios.xs },
    fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    numero: {
      width: 22,
      height: 22,
      borderRadius: 11,
      borderWidth: 1,
      borderColor: colores.borde,
      backgroundColor: colores.superficieFuerte,
      alignItems: 'center',
      justifyContent: 'center',
    },
    textoNumero: { fontFamily: fuentes.seminegrita, color: colores.texto },
    titulo: { fontSize: 18, lineHeight: 24, letterSpacing: -0.2 },
  });
