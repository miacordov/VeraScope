/**
 * Botón "Mostrar mosaico", estado de la consulta `scan/layer` y leyenda en texto (frontend/CLAUDE.md §9 y §11).
 * El mosaico solo se pide cuando está visible. Es lo cuarto que se recorta si el mapa va lento (§18).
 */
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import type { LayerRespuesta, Variable } from '@/shared/api/tipos';
import { estadoDeError, TEXTOS_ACCION } from '@/shared/components/textosEstados';
import { useEstilos, useTema } from '@/shared/useTema';
import { espacios, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

import { CLASES_MOSAICO, estiloMosaico, nombreClase } from './mosaico';

type Props = {
  visible: boolean;
  onAlternar: () => void;
  variable: Variable;
  datos: LayerRespuesta | undefined;
  cargando: boolean;
  error: unknown;
  reintentar: () => void;
};

export function ControlMosaico({ visible, onAlternar, variable, datos, cargando, error, reintentar }: Props) {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.bloque}>
      <Boton
        texto={visible ? 'Ocultar el mosaico de ScanMap' : 'Mostrar el mosaico de ScanMap'}
        variante="secundario"
        accessibilityState={{ checked: visible }}
        onPress={onAlternar}
      />
      {!visible ? null : cargando ? (
        <View accessibilityLabel="Cargando el mosaico" accessibilityRole="progressbar">
          <ActivityIndicator color={colores.texto} />
        </View>
      ) : error ? (
        <ErrorMosaico error={error} reintentar={reintentar} />
      ) : datos ? (
        <Leyenda variable={variable} />
      ) : null}
    </View>
  );
}

function ErrorMosaico({ error, reintentar }: { error: unknown; reintentar: () => void }) {
  const estilos = useEstilos(crearEstilos);
  const { titulo, mensaje, accion } = estadoDeError(error);
  return (
    <View accessibilityRole="alert" style={estilos.bloque}>
      <Texto variante="cuerpoFuerte">{titulo}</Texto>
      <Texto>{mensaje}</Texto>
      {accion === 'reintentar' ? (
        <Boton texto={TEXTOS_ACCION.reintentar} variante="secundario" onPress={reintentar} />
      ) : null}
    </View>
  );
}

function Leyenda({ variable }: { variable: Variable }) {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.bloque} accessibilityLabel="Leyenda del mosaico de ScanMap">
      <Texto variante="etiqueta" suave>
        Mosaico de ScanMap: veredicto del escaneo en cada celda de 2° (todo el registro, índice ONI).
      </Texto>
      <View style={estilos.leyenda}>
        {CLASES_MOSAICO.map((clase) => {
          const { color, opacidad } = estiloMosaico(clase, variable, colores);
          return (
            <View key={clase} style={estilos.item}>
              <View style={[estilos.muestra, { backgroundColor: color, opacity: Math.max(opacidad, 0.25) }]} />
              <Texto variante="etiqueta">{nombreClase(clase)}</Texto>
            </View>
          );
        })}
      </View>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    bloque: { gap: espacios.s },
    leyenda: { flexDirection: 'row', flexWrap: 'wrap', gap: espacios.m },
    item: { flexDirection: 'row', alignItems: 'center', gap: espacios.xs },
    muestra: {
      width: 14,
      height: 14,
      borderWidth: 1,
      borderColor: colores.borde,
    },
  });
