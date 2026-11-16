import { StyleSheet, View } from 'react-native';

import type { AnalyzeRespuesta } from '@/shared/api/tipos';
import { useEstilos } from '@/shared/useTema';
import { espacios, radios, type Colores } from '@/shared/tema';
import { Texto } from '@/shared/ui';

import { TEXTOS_VEREDICTO } from './textosVeredicto';

/**
 * Insignia mínima del veredicto: texto + símbolo de forma; el color solo refuerza (rojo solo para
 * "sensible a El Niño", §13). La tarjeta completa (tendencia aparente, pendiente, IC, avisos) es de F3.
 */
export function InsigniaVeredicto({ veredicto }: { veredicto: AnalyzeRespuesta['veredicto'] }) {
  const estilos = useEstilos(crearEstilos);
  const textos = TEXTOS_VEREDICTO[veredicto.estado];
  const esNino = veredicto.estado === 'sensible_a_el_nino';
  return (
    <View
      style={estilos.contenedor}
      accessible
      accessibilityRole="summary"
      accessibilityLabel={`Veredicto: ${textos.titulo}. ${textos.explicacion}`}>
      <View style={estilos.fila}>
        <Texto
          variante="subtitulo"
          style={esNino ? estilos.simboloNino : undefined}
          importantForAccessibility="no"
          accessibilityElementsHidden>
          {textos.simbolo}
        </Texto>
        <Texto variante="subtitulo">{textos.titulo}</Texto>
      </View>
      <Texto>{textos.explicacion}</Texto>
      {veredicto.origen === 'individual' ? (
        <View style={estilos.chip}>
          <Texto variante="etiqueta">análisis individual</Texto>
        </View>
      ) : null}
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    contenedor: { gap: espacios.s },
    fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    simboloNino: { color: colores.nino },
    chip: {
      alignSelf: 'flex-start',
      borderColor: colores.borde,
      borderWidth: 1,
      borderRadius: radios.s,
      paddingHorizontal: espacios.s,
      paddingVertical: espacios.xs,
    },
  });
