import { useEffect } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, useWindowDimensions, View } from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { parametrosAnalyze } from '@/estado/seleccion';
import { useEstado } from '@/estado/store';
import { InterruptorElNino } from '@/features/enso-toggle/InterruptorElNino';
import { ControlMosaico } from '@/features/map/ControlMosaico';
import { MapaPacifico } from '@/features/map/MapaPacifico';
import { altoDelMapa } from '@/features/map/tamano';
import { PanelSeries } from '@/features/series-charts/PanelSeries';
import { ControlTiempo } from '@/features/time-comparator/ControlTiempo';
import { ListaLineas } from '@/features/teleconnection-lines/ListaLineas';
import { SelectorVariable } from '@/features/variable-picker/SelectorVariable';
import { TarjetaVeredicto } from '@/features/verdict-card';
import { esErrorApi } from '@/shared/api/cliente';
import { useAnalyze, useLayer, useSalud, useTeleconnect } from '@/shared/api/consultas';
import { estadoDeError, TEXTOS_ACCION } from '@/shared/components/textosEstados';
import { EJEMPLO_SIMULADO } from '@/shared/ejemploSimulado';
import { celda as textoCelda } from '@/shared/format';
import { useEstilos, useTema } from '@/shared/useTema';
import { cortes, espacios, type Colores } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

/**
 * Espacio de trabajo (F1). Mapa del Pacífico y selector de variable y ventana (`fe/mapa-celda`, #9); elegir una celda
 * pide `analyze` y `teleconnect` en paralelo (§6, regla 1) y muestra la tarjeta de veredicto (F3). Las líneas
 * causa → consecuencia y el mosaico de ScanMap (`fe/lineas-mosaico`, #13) van en la columna del mapa. En pantallas
 * anchas (≥ 1024) el mapa va al lado del panel.
 * Las features de F2 y F3 entran por su hueco.
 */
export default function Espacio() {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  const salud = useSalud();
  const seleccion = useEstado(
    useShallow((e) => ({ variable: e.variable, celda: e.celda, ventana: e.ventana, indice: e.indice })),
  );
  const parametros = parametrosAnalyze(seleccion, salud.data?.ventana_fin);
  const analisis = useAnalyze(parametros);
  const { destino, mesVisible, mosaicoVisible } = useEstado(
    useShallow((e) => ({ destino: e.destino, mesVisible: e.mesVisible, mosaicoVisible: e.mosaicoVisible })),
  );
  const teleconexion = useTeleconnect(
    seleccion.celda ? { variable: seleccion.variable, lat: seleccion.celda.lat, lon: seleccion.celda.lon } : null,
  );
  const mosaico = useLayer(seleccion.variable, mosaicoVisible);
  // Al llegar `teleconnect` sin destino se elige la primera línea de efecto opuesto (§7); también cuando el destino
  // se reinicia al volver a una celda cuya respuesta ya está en caché.
  const lineas = teleconexion.data?.lineas;
  useEffect(() => {
    if (lineas && destino === null) useEstado.getState().destinoPorDefecto(lineas);
  }, [lineas, destino]);
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
            teleconexion={
              teleconexion.data
                ? {
                    origen: teleconexion.data.origen,
                    lineas: teleconexion.data.lineas,
                    destino,
                    mesVisible,
                    onElegirLinea: (l) => useEstado.getState().elegirDestino({ lat: l.lat, lon: l.lon }),
                  }
                : null
            }
            mosaico={mosaicoVisible && mosaico.data ? { datos: mosaico.data, variable: seleccion.variable } : null}
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
          <ControlMosaico
            visible={mosaicoVisible}
            onAlternar={() => useEstado.getState().alternarMosaico()}
            variable={seleccion.variable}
            datos={mosaico.data}
            cargando={mosaico.isFetching && !mosaico.data}
            error={mosaico.isError ? mosaico.error : null}
            reintentar={() => mosaico.refetch()}
          />
        </Tarjeta>
        {seleccion.celda ? (
          <ListaLineas
            respuesta={teleconexion.data}
            cargando={teleconexion.isPending}
            error={teleconexion.isError ? teleconexion.error : null}
            destino={destino}
            reintentar={() => teleconexion.refetch()}
          />
        ) : null}
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
            {/* Hueco de F3 (#11): tarjeta de veredicto; sigue al interruptor sin pedir datos. */}
            <TarjetaVeredicto analisis={analisis.data} />
            {/* Hueco de F2 (#10 y #14): interruptor, reproducción en el tiempo y panel Causa · Consecuencia · Realidad. */}
            <Tarjeta>
              <InterruptorElNino rezagoMeses={analisis.data.vinculo_el_nino.rezago_meses} />
              <ControlTiempo fechas={analisis.data.fechas} />
            </Tarjeta>
            <PanelSeries analisis={analisis.data} />
          </>
        )}
      </View>
    </ScrollView>
  );
}

/**
 * Error de una consulta con el título, el mensaje y el botón que decide `estadoDeError` (textos de F3, §11).
 * El mensaje del servidor se muestra tal cual. Sin botón cuando el usuario debe corregir su elección.
 */
function ErrorConReintento({ error, reintentar }: { error: unknown; reintentar: () => void }) {
  const { titulo, mensaje, accion } = estadoDeError(error);
  const celdaCercana = esErrorApi(error) ? error.celdaCercana : null;

  const actuar = () => {
    if (accion === 'celda_cercana' && celdaCercana) useEstado.getState().seleccionarCelda(celdaCercana);
    // Cambiar solo la variable conserva la celda (§7).
    else if (accion === 'usar_lluvia') useEstado.getState().cambiarVariable('PRECTOTCORR');
    else reintentar();
  };

  return (
    <Tarjeta accessibilityRole="alert">
      <Texto variante="cuerpoFuerte">{titulo}</Texto>
      <Texto>{mensaje}</Texto>
      {accion ? <Boton texto={TEXTOS_ACCION[accion]} variante="secundario" onPress={actuar} /> : null}
    </Tarjeta>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    fondo: { flex: 1, backgroundColor: colores.fondo },
    contenido: { padding: espacios.l, gap: espacios.l, maxWidth: 960, width: '100%', alignSelf: 'center' },
    contenidoAncho: { maxWidth: 1440, flexDirection: 'row', alignItems: 'flex-start' },
    columna: { gap: espacios.l },
    columnaMapa: { flex: 3, gap: espacios.l },
    columnaPanel: { flex: 2, gap: espacios.l },
    esqueleto: { height: 16, borderRadius: 4, backgroundColor: colores.superficieFuerte },
    esqueletoCorto: { width: '60%' },
  });
