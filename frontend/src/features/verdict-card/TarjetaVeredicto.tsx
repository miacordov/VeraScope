import { useEffect, useRef } from 'react';
import { AccessibilityInfo, StyleSheet, View } from 'react-native';

import { useEstado } from '@/estado/store';
import type { AnalyzeRespuesta } from '@/shared/api/tipos';
import { EtiquetaFuente } from '@/shared/components/EtiquetaFuente';
import { InsigniaVeredicto } from '@/shared/components/InsigniaVeredicto';
import { espacios, radios, type Colores } from '@/shared/tema';
import { Boton, Desplegable, Tarjeta, Texto } from '@/shared/ui';
import { useEstilos } from '@/shared/useTema';

import {
  anuncio,
  atribucion,
  cambioPorcentual,
  direccionSinElNino,
  intervalo,
  pendiente,
  pValorTendencia,
  tendenciaAparente,
  vinculo,
} from './textosTarjeta';

/**
 * Tarjeta de veredicto (F3, #11). Lee `quitarElNino` del store y no hace peticiones:
 * el interruptor solo cambia qué parte de la respuesta ya recibida se muestra.
 * Primero lo esencial (veredicto, pendiente con su intervalo, avisos y fuente); el p-valor y el vínculo con
 * El Niño van en "Ver detalles" para no mostrar todos los números a la vez.
 *
 * `alVerGlosario` (opcional): si la pantalla lo pasa, la tarjeta ofrece "Qué significan estos términos" para ir al
 * glosario (#15). Sin él, la tarjeta se ve igual que antes. La navegación la decide la pantalla, no la tarjeta.
 */
export function TarjetaVeredicto({
  analisis,
  alVerGlosario,
}: {
  analisis: AnalyzeRespuesta;
  alVerGlosario?: () => void;
}) {
  const estilos = useEstilos(crearEstilos);
  const quitarElNino = useEstado((e) => e.quitarElNino);
  const tendencia = quitarElNino ? analisis.tendencia_sin_el_nino : analisis.tendencia_original;
  const { unidad } = analisis;
  const pct = cambioPorcentual(tendencia);
  const enlace = vinculo(analisis.vinculo_el_nino);

  // El cambio de lo que dice la tarjeta se anuncia (no al aparecer por primera vez).
  const texto = anuncio(analisis, quitarElNino);
  const anterior = useRef(texto);
  useEffect(() => {
    if (anterior.current !== texto) AccessibilityInfo.announceForAccessibility(texto);
    anterior.current = texto;
  }, [texto]);

  return (
    <Tarjeta accessibilityLiveRegion="polite">
      <Texto variante="etiqueta" suave>
        {analisis.nombre} · {unidad}
      </Texto>
      <Texto variante="pequeno" suave>
        {atribucion(analisis)}
      </Texto>

      {quitarElNino ? (
        <View style={estilos.bloque}>
          <InsigniaVeredicto veredicto={analisis.veredicto} />
          <DireccionSinElNino texto={direccionSinElNino(tendencia)} />
        </View>
      ) : (
        <TendenciaAparente analisis={analisis} />
      )}

      <Texto variante="pequeno" suave>
        {quitarElNino ? 'Serie sin la parte que explica El Niño.' : 'Serie original, con El Niño incluido.'}
      </Texto>

      <View style={estilos.destacado}>
        <Cifra
          etiqueta="Pendiente por década"
          valor={pendiente(tendencia, unidad)}
          detalle={`Intervalo de 95 %: ${intervalo(tendencia, unidad)}`}
          detalleCorto={intervalo(tendencia, unidad)}
        />
        {pct ? <Cifra etiqueta="Cambio por década" valor={pct} /> : null}
      </View>

      {analisis.avisos.map((a, i) => (
        <View key={`${a.codigo}-${i}`} style={estilos.aviso} accessible accessibilityLabel={`Aviso: ${a.texto}`}>
          <Texto variante="pequeno">{a.texto}</Texto>
        </View>
      ))}

      <Desplegable titulo="Ver detalles" tituloAbierto="Ocultar detalles" resumen="p-valor y vínculo con El Niño">
        <Fila etiqueta="p-valor" valor={pValorTendencia(tendencia, analisis.veredicto.origen)} />
        <Fila
          etiqueta="Vínculo con El Niño"
          valor={enlace.indicativo ? `${enlace.texto} · indicativo` : enlace.texto}
        />
      </Desplegable>

      <EtiquetaFuente analisis={analisis} />

      {alVerGlosario ? (
        <Boton
          texto="Qué significan estos términos"
          variante="secundario"
          etiqueta="Abrir el glosario: qué significan pendiente, intervalo, p-valor y veredicto"
          onPress={alVerGlosario}
        />
      ) : null}
    </Tarjeta>
  );
}

function TendenciaAparente({ analisis }: { analisis: AnalyzeRespuesta }) {
  const estilos = useEstilos(crearEstilos);
  const { simbolo, texto } = tendenciaAparente(analisis.tendencia_original);
  return (
    <View style={estilos.bloque} accessible accessibilityRole="summary" accessibilityLabel={`Tendencia aparente: ${texto}`}>
      <Texto variante="etiqueta" suave>
        Tendencia aparente
      </Texto>
      <View style={estilos.fila}>
        <Texto variante="subtitulo" importantForAccessibility="no" accessibilityElementsHidden>
          {simbolo}
        </Texto>
        <Texto variante="subtitulo">{texto}</Texto>
      </View>
      {analisis.veredicto.origen === 'individual' ? (
        <View style={estilos.chip}>
          <Texto variante="etiqueta">análisis individual</Texto>
        </View>
      ) : null}
    </View>
  );
}

function DireccionSinElNino({ texto }: { texto: string | null }) {
  return texto ? <Texto>{texto}</Texto> : null;
}

/** Número principal en grande, con su incertidumbre debajo (el intervalo nunca se esconde). */
function Cifra({
  etiqueta,
  valor,
  detalle,
  detalleCorto,
}: {
  etiqueta: string;
  valor: string;
  detalle?: string;
  detalleCorto?: string;
}) {
  const estilos = useEstilos(crearEstilos);
  return (
    <View
      style={estilos.cifra}
      accessible
      accessibilityLabel={detalle ? `${etiqueta}: ${valor}. ${detalle}` : `${etiqueta}: ${valor}`}>
      <Texto variante="etiqueta" suave>
        {etiqueta}
      </Texto>
      <Texto variante="subtitulo" numerico>
        {valor}
      </Texto>
      {detalleCorto ? (
        <Texto variante="pequeno" suave numerico>
          {detalleCorto}
        </Texto>
      ) : null}
    </View>
  );
}

function Fila({ etiqueta, valor }: { etiqueta: string; valor: string }) {
  const estilos = useEstilos(crearEstilos);
  return (
    <View style={estilos.filaDato} accessible accessibilityLabel={`${etiqueta}: ${valor}`}>
      <Texto variante="pequeno" suave>
        {etiqueta}
      </Texto>
      <Texto variante="cuerpo" numerico>
        {valor}
      </Texto>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    bloque: { gap: espacios.s },
    fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
    destacado: { flexDirection: 'row', flexWrap: 'wrap', gap: espacios.l, paddingTop: espacios.xs },
    cifra: {
      flexGrow: 1,
      minWidth: 140,
      gap: 2,
      padding: espacios.m,
      borderRadius: radios.m,
      backgroundColor: colores.superficieFuerte,
    },
    filaDato: { gap: 2 },
    aviso: {
      borderLeftColor: colores.sequia,
      borderLeftWidth: 3,
      backgroundColor: colores.superficieFuerte,
      borderRadius: radios.s,
      padding: espacios.s,
    },
    chip: {
      alignSelf: 'flex-start',
      borderColor: colores.borde,
      borderWidth: 1,
      borderRadius: radios.s,
      paddingHorizontal: espacios.s,
      paddingVertical: espacios.xs,
    },
  });
