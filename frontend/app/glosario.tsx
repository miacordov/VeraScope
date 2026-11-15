import { ActivityIndicator, FlatList, StyleSheet } from 'react-native';

import { useGlosario } from '@/shared/api/consultas';
import { colores, espacios } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

/** Glosario MÍNIMO del esqueleto: lista los términos de `/glosario`. La página completa es de F3. */
export default function Glosario() {
  const glosario = useGlosario();

  if (glosario.isPending) {
    return <ActivityIndicator style={estilos.fondo} color={colores.texto} accessibilityLabel="Cargando el glosario" />;
  }
  if (glosario.isError) {
    return (
      <Tarjeta style={estilos.error} accessibilityRole="alert">
        <Texto>{glosario.error.message}</Texto>
        <Boton texto="Reintentar" variante="secundario" onPress={() => glosario.refetch()} />
      </Tarjeta>
    );
  }
  return (
    <FlatList
      style={estilos.fondo}
      contentContainerStyle={estilos.contenido}
      data={glosario.data.terminos}
      keyExtractor={(t) => t.termino}
      renderItem={({ item }) => (
        <Tarjeta>
          <Texto variante="cuerpoFuerte" accessibilityRole="header">
            {item.termino}
          </Texto>
          <Texto>{item.definicion}</Texto>
        </Tarjeta>
      )}
    />
  );
}

const estilos = StyleSheet.create({
  fondo: { flex: 1, backgroundColor: colores.fondo },
  contenido: { padding: espacios.l, gap: espacios.m, maxWidth: 720, width: '100%', alignSelf: 'center' },
  error: { margin: espacios.l },
});
