import { ActivityIndicator, ScrollView, StyleSheet, View } from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { parametrosAnalyze } from '@/estado/seleccion';
import { useEstado } from '@/estado/store';
import { InterruptorElNino } from '@/features/enso-toggle/InterruptorElNino';
import { PanelSeries } from '@/features/series-charts/PanelSeries';
import { esErrorApi } from '@/shared/api/cliente';
import { useAnalyze, useSalud } from '@/shared/api/consultas';
import { EtiquetaFuente } from '@/shared/components/EtiquetaFuente';
import { InsigniaVeredicto } from '@/shared/components/InsigniaVeredicto';
import { EJEMPLO_SIMULADO } from '@/shared/ejemploSimulado';
import { celda as textoCelda } from '@/shared/format';
import { colores, espacios } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

/**
 * Espacio de trabajo (F1). En este esqueleto (`chore/contratos`) pide `analyze` y muestra el veredicto
 * y la fuente. El mapa, el selector y el diseño adaptable llegan en `fe/mapa-celda` (#9).
 */
export default function Espacio() {
  const salud = useSalud();
  const seleccion = useEstado(
    useShallow((e) => ({ variable: e.variable, celda: e.celda, ventana: e.ventana, indice: e.indice })),
  );
  const parametros = parametrosAnalyze(seleccion, salud.data?.ventana_fin);
  const analisis = useAnalyze(parametros);

  const usarEjemplo = () => {
    const { cambiarVariable, fijarVentana, fijarIndice, seleccionarCelda } = useEstado.getState();
    cambiarVariable(EJEMPLO_SIMULADO.variable);
    fijarVentana({ ...EJEMPLO_SIMULADO.ventana });
    fijarIndice(EJEMPLO_SIMULADO.indice);
    seleccionarCelda({ ...EJEMPLO_SIMULADO.celda });
  };

  return (
    <ScrollView style={estilos.fondo} contentContainerStyle={estilos.contenido}>
      <Tarjeta>
        <Texto variante="subtitulo" accessibilityRole="header">
          Elige un lugar
        </Texto>
        <Texto suave>
          {seleccion.celda
            ? `Celda elegida: ${textoCelda(seleccion.celda)}`
            : 'Toca el mapa para elegir un lugar. El mapa llega en la siguiente versión.'}
        </Texto>
        {salud.data?.simulado ? (
          <Boton
            texto={`Ver el ejemplo simulado: ${EJEMPLO_SIMULADO.nombre}`}
            variante="secundario"
            onPress={usarEjemplo}
          />
        ) : null}
      </Tarjeta>

      {salud.isError ? <ErrorConReintento error={salud.error} reintentar={() => salud.refetch()} /> : null}

      {parametros === null ? null : analisis.isPending ? (
        <Tarjeta accessibilityLabel="Cargando el análisis de la celda" accessibilityRole="progressbar">
          <ActivityIndicator color={colores.texto} />
          <View style={estilos.esqueleto} />
          <View style={[estilos.esqueleto, estilos.esqueletoCorto]} />
        </Tarjeta>
      ) : analisis.isError ? (
        <ErrorConReintento error={analisis.error} reintentar={() => analisis.refetch()} />
      ) : (
        <>
          <Tarjeta accessibilityLiveRegion="polite">
            <Texto variante="etiqueta" suave>
              {analisis.data.nombre} · {analisis.data.unidad}
            </Texto>
            <InsigniaVeredicto veredicto={analisis.data.veredicto} />
            <EtiquetaFuente analisis={analisis.data} />
          </Tarjeta>
          {/* Hueco de F2 (#10): interruptor y panel Causa · Consecuencia · Realidad. */}
          <Tarjeta>
            <InterruptorElNino rezagoMeses={analisis.data.vinculo_el_nino.rezago_meses} />
          </Tarjeta>
          <PanelSeries analisis={analisis.data} />
        </>
      )}
    </ScrollView>
  );
}

function ErrorConReintento({ error, reintentar }: { error: unknown; reintentar: () => void }) {
  const mensaje = esErrorApi(error) ? error.message : 'Algo salió mal al pedir los datos. Inténtalo de nuevo.';
  return (
    <Tarjeta accessibilityRole="alert">
      <Texto variante="cuerpoFuerte">No se pudo cargar</Texto>
      <Texto>{mensaje}</Texto>
      <Boton texto="Reintentar" variante="secundario" onPress={reintentar} />
    </Tarjeta>
  );
}

const estilos = StyleSheet.create({
  fondo: { flex: 1, backgroundColor: colores.fondo },
  contenido: { padding: espacios.l, gap: espacios.l, maxWidth: 960, width: '100%', alignSelf: 'center' },
  esqueleto: { height: 16, borderRadius: 4, backgroundColor: colores.superficieFuerte },
  esqueletoCorto: { width: '60%' },
});
