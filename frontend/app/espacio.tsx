import { ActivityIndicator, ScrollView, StyleSheet, useWindowDimensions, View } from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { parametrosAnalyze } from '@/estado/seleccion';
import { useEstado } from '@/estado/store';
import { InterruptorElNino } from '@/features/enso-toggle/InterruptorElNino';
import { MapaPacifico } from '@/features/map/MapaPacifico';
import { altoDelMapa } from '@/features/map/tamano';
import { PanelSeries } from '@/features/series-charts/PanelSeries';
import { SelectorVariable } from '@/features/variable-picker/SelectorVariable';
import { esErrorApi } from '@/shared/api/cliente';
import { useAnalyze, useSalud } from '@/shared/api/consultas';
import { EtiquetaFuente } from '@/shared/components/EtiquetaFuente';
import { InsigniaVeredicto } from '@/shared/components/InsigniaVeredicto';
import { EJEMPLO_SIMULADO } from '@/shared/ejemploSimulado';
import { celda as textoCelda } from '@/shared/format';
import { colores, cortes, espacios } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

/**
 * Espacio de trabajo (F1). Mapa del Pacífico y selector de variable y ventana (`fe/mapa-celda`, #9); pide
 * `analyze` y muestra el veredicto y la fuente. En pantallas anchas (≥ 1024) el mapa va al lado del panel.
 * Las features de F2 y F3 entran por su hueco, debajo del veredicto.
 */
export default function Espacio() {
  const salud = useSalud();
  const seleccion = useEstado(
    useShallow((e) => ({ variable: e.variable, celda: e.celda, ventana: e.ventana, indice: e.indice })),
  );
  const parametros = parametrosAnalyze(seleccion, salud.data?.ventana_fin);
  const analisis = useAnalyze(parametros);
  const { width } = useWindowDimensions();
  const ancha = width >= cortes.laptop;
  const altoMapa = altoDelMapa(width);
  // El servidor es la autoridad: si la celda de la respuesta difiere de la calculada, se dibuja la de la respuesta.
  const celdaDibujada = analisis.data ? analisis.data.celda : seleccion.celda;

  const usarEjemplo = () => {
    const { cambiarVariable, fijarVentana, fijarIndice, seleccionarCelda } = useEstado.getState();
    cambiarVariable(EJEMPLO_SIMULADO.variable);
    fijarVentana({ ...EJEMPLO_SIMULADO.ventana });
    fijarIndice(EJEMPLO_SIMULADO.indice);
    seleccionarCelda({ ...EJEMPLO_SIMULADO.celda });
  };

  return (
    <ScrollView
      style={estilos.fondo}
      contentContainerStyle={[estilos.contenido, ancha && estilos.contenidoAncho]}>
      <View style={ancha ? estilos.columnaMapa : undefined}>
        <Tarjeta>
          <Texto variante="subtitulo" accessibilityRole="header">
            Elige un lugar
          </Texto>
          <MapaPacifico
            celda={celdaDibujada}
            alto={altoMapa}
            onElegirCelda={(c) => useEstado.getState().seleccionarCelda(c)}
          />
          <Texto suave accessibilityLiveRegion="polite">
            {seleccion.celda
              ? `Celda elegida: ${textoCelda(seleccion.celda)}`
              : 'Toca el mapa para elegir un lugar.'}
          </Texto>
          {salud.data?.simulado ? (
            <Boton
              texto={`Ver el ejemplo simulado: ${EJEMPLO_SIMULADO.nombre}`}
              variante="secundario"
              onPress={usarEjemplo}
            />
          ) : null}
        </Tarjeta>
      </View>

      <View style={ancha ? estilos.columnaPanel : estilos.columna}>
        <SelectorVariable />

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
      </View>
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
  contenidoAncho: { maxWidth: 1440, flexDirection: 'row', alignItems: 'flex-start' },
  columna: { gap: espacios.l },
  columnaMapa: { flex: 3, gap: espacios.l },
  columnaPanel: { flex: 2, gap: espacios.l },
  esqueleto: { height: 16, borderRadius: 4, backgroundColor: colores.superficieFuerte },
  esqueletoCorto: { width: '60%' },
});
