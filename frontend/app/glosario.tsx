import { ActivityIndicator, FlatList, StyleSheet } from 'react-native';

import { Creditos } from '@/features/glossary';
import { useGlosario } from '@/shared/api/consultas';
import { estadoDeError } from '@/shared/components/textosEstados';
import { espacios, type Colores } from '@/shared/tema';
import { useEstilos, useTema } from '@/shared/useTema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

/**
 * Glosario (F3, #15): términos de `/glosario` y créditos de las fuentes. Los créditos se muestran siempre,
 * aunque el glosario no cargue (no dependen de la red).
 */
export default function Glosario() {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  const glosario = useGlosario();

  const cabecera = glosario.isPending ? (
    <ActivityIndicator color={colores.texto} accessibilityLabel="Cargando el glosario" />
  ) : glosario.isError ? (
    <ErrorGlosario error={glosario.error} reintentar={() => glosario.refetch()} />
  ) : undefined;

  return (
    <FlatList
      style={estilos.fondo}
      contentContainerStyle={estilos.contenido}
      data={glosario.data?.terminos ?? []}
      keyExtractor={(t) => t.termino}
      ListHeaderComponent={cabecera}
      ListFooterComponent={<Creditos />}
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

/** Error con los textos de F3 (§11): título, el mensaje del servidor tal cual y Reintentar. */
function ErrorGlosario({ error, reintentar }: { error: unknown; reintentar: () => void }) {
  const { titulo, mensaje } = estadoDeError(error);
  return (
    <Tarjeta accessibilityRole="alert">
      <Texto variante="cuerpoFuerte">{titulo}</Texto>
      <Texto>{mensaje}</Texto>
      <Boton texto="Reintentar" variante="secundario" onPress={reintentar} />
    </Tarjeta>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    fondo: { flex: 1, backgroundColor: colores.fondo },
    contenido: { padding: espacios.l, gap: espacios.m, maxWidth: 720, width: '100%', alignSelf: 'center' },
    error: { margin: espacios.l },
  });
