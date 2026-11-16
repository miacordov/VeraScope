/**
 * Panel Causa · Consecuencia · Realidad (frontend/CLAUDE.md §10, `series-charts`).
 * Tres GraficoSerie con el mismo eje de tiempo, sincronizados con `mesVisible` y con la lectura compartida.
 * Solo elige qué serie de la respuesta se dibuja: no calcula nada. Dueña: F2 (`fe/graficos-enso`).
 */
import { StyleSheet, View } from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { parametrosAnalyze } from '@/estado/seleccion';
import { useEstado } from '@/estado/store';
import { useAnalyze, useSalud } from '@/shared/api/consultas';
import type { AnalyzeRespuesta } from '@/shared/api/tipos';
import { periodo, celda as textoCelda } from '@/shared/format';
import { useEstilos, useTema } from '@/shared/useTema';
import { espacios, type Colores } from '@/shared/tema';
import { Desplegable, Tarjeta, Texto } from '@/shared/ui';

import { GraficoSerie, NOMBRE_FASE, type PuntoMarcado } from './GraficoSerie';
import { ProveedorLectura } from './lectura';

/** Umbral de las fases de ONI (§17: El Niño ≥ 0.5, La Niña ≤ −0.5). Solo se dibuja como referencia. */
const REFERENCIAS_INDICE = [0.5, -0.5] as const;

export function PanelSeries({ analisis }: { analisis: AnalyzeRespuesta }) {
  const { colores } = useTema();
  const { quitarElNino, mesVisible, destino, variable, ventana, indice } = useEstado(
    useShallow((e) => ({
      quitarElNino: e.quitarElNino,
      mesVisible: e.mesVisible,
      destino: e.destino,
      variable: e.variable,
      ventana: e.ventana,
      indice: e.indice,
    })),
  );
  const salud = useSalud();
  // La serie del destino sale del `analyze` del destino (queda en caché, §8 regla 1).
  const analisisDestino = useAnalyze(
    destino ? parametrosAnalyze({ variable, celda: destino, ventana, indice }, salud.data?.ventana_fin) : null,
  );

  const serieRealidad = quitarElNino ? analisis.serie_sin_el_nino : analisis.serie_original;
  const tendencia = quitarElNino ? analisis.tendencia_sin_el_nino : analisis.tendencia_original;
  const nombreSerie = quitarElNino ? 'sin El Niño' : 'original';

  const puntos: PuntoMarcado[] = analisis.meses_inusuales.flatMap((m) => {
    const valor = serieRealidad[analisis.fechas.indexOf(m.fecha)];
    return valor === null || valor === undefined ? [] : [{ fecha: m.fecha, valor, etiqueta: NOMBRE_FASE[m.fase] }];
  });

  const destinoListo = destino !== null && analisisDestino.data !== undefined;

  return (
    <ProveedorLectura>
      <Tarjeta>
        <Texto variante="subtitulo" accessibilityRole="header">
          Causa · Consecuencia · Realidad
        </Texto>
        <Texto variante="pequeno" suave>
          Tres gráficos con el mismo eje de tiempo. Toca o pasa el cursor sobre uno para leer un mes.
        </Texto>

        <Pregunta texto="¿Cuándo hubo El Niño y La Niña?" />
        <GraficoSerie
          titulo="Causa"
          unidad={analisis.indice.id}
          fechas={analisis.fechas}
          series={[{ id: 'indice', valores: analisis.indice_valores, color: colores.texto }]}
          fases={analisis.fase}
          referencias={REFERENCIAS_INDICE}
          mesVisible={mesVisible}
          resumen={`${analisis.indice.nombre} mes a mes. Las franjas rojas son meses de El Niño y las rayadas, de La Niña.`}
        />
        <Leyenda />

        <Pregunta texto={`¿Qué pasó con la ${analisis.nombre.toLowerCase()} en el lugar?`} />
        <GraficoSerie
          titulo="Consecuencia"
          unidad="anomalía estandarizada (z)"
          fechas={analisis.fechas}
          series={[
            { id: 'z-celda', valores: analisis.serie_z, color: colores.lluvia },
            ...(destinoListo
              ? [{ id: 'z-destino', valores: analisisDestino.data.serie_z, color: colores.sequia, punteada: true }]
              : []),
          ]}
          mesVisible={mesVisible}
          resumen={
            destinoListo
              ? `Anomalía de ${analisis.nombre.toLowerCase()} en la celda ${textoCelda(analisis.celda)} y en el destino ${textoCelda(analisisDestino.data.celda)}.`
              : `Anomalía de ${analisis.nombre.toLowerCase()} en la celda ${textoCelda(analisis.celda)}.`
          }
        />
        <Texto variante="etiqueta" suave>
          {destinoListo
            ? `Línea continua: celda elegida. Punteada: destino ${textoCelda(analisisDestino.data.celda)}. Ocurren a la vez y ambos responden a El Niño.`
            : destino
              ? 'Cargando la serie del destino…'
              : 'Elige una línea en el mapa para comparar con el otro lado del Pacífico.'}
        </Texto>

        <Pregunta texto="¿Queda una tendencia de fondo?" />
        <GraficoSerie
          titulo={`Realidad (${nombreSerie})`}
          unidad={analisis.unidad}
          fechas={analisis.fechas}
          series={[
            { id: 'realidad', valores: serieRealidad, color: colores.texto },
            { id: 'recta', valores: tendencia.recta, color: colores.info, grosor: 2.5, punteada: true, recortar: false },
          ]}
          puntos={puntos}
          mesVisible={mesVisible}
          resumen={`${analisis.nombre} ${nombreSerie} con su recta de tendencia. ${
            puntos.length > 0 ? `${puntos.length} meses inusuales marcados con un punto.` : 'Sin meses inusuales.'
          }`}
        />
        {puntos.length > 0 ? (
          <Desplegable titulo={`Ver meses inusuales (${puntos.length})`} tituloAbierto="Ocultar meses inusuales">
            <Texto variante="etiqueta" suave>
              Meses inusuales: {puntos.map((p) => `${p.fecha} (${p.etiqueta})`).join(', ')}
            </Texto>
          </Desplegable>
        ) : null}

        <Texto variante="etiqueta" suave>
          {`Gráficos: ${analisis.fuente} y ${analisis.indice.fuente} · celda ${textoCelda(analisis.celda)} · ${periodo(analisis.ventana.inicio, analisis.ventana.fin)}`}
        </Texto>
      </Tarjeta>
    </ProveedorLectura>
  );
}

/** Pregunta en lenguaje sencillo que responde cada gráfico (separa visualmente los tres). */
function Pregunta({ texto }: { texto: string }) {
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.pregunta}>
      <Texto variante="cuerpoFuerte">{texto}</Texto>
    </View>
  );
}

function Leyenda() {
  const { colores } = useTema();
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.leyenda} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
      <View style={[estilos.muestra, { backgroundColor: colores.nino }]} />
      <Texto variante="etiqueta" suave>
        El Niño
      </Texto>
      <View style={[estilos.muestra, estilos.muestraNina]} />
      <Texto variante="etiqueta" suave>
        La Niña (rayas)
      </Texto>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    leyenda: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    pregunta: { borderTopColor: colores.borde, borderTopWidth: 1, paddingTop: espacios.m, marginTop: espacios.s },
    muestra: { width: 12, height: 12, borderRadius: 2, opacity: 0.6 },
    muestraNina: { borderWidth: 1, borderColor: colores.nina, borderStyle: 'dashed' },
  });
