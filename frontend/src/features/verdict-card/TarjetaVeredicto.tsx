import { useEffect, useRef } from 'react';
import { AccessibilityInfo, StyleSheet, View } from 'react-native';

import { useEstado } from '@/estado/store';
import type { AnalyzeRespuesta } from '@/shared/api/tipos';
import { EtiquetaFuente } from '@/shared/components/EtiquetaFuente';
import { InsigniaVeredicto } from '@/shared/components/InsigniaVeredicto';
import { colores, espacios, radios } from '@/shared/tema';
import { Tarjeta, Texto } from '@/shared/ui';

import {
  anuncio,
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
 */
export function TarjetaVeredicto({ analisis }: { analisis: AnalyzeRespuesta }) {
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

      <View style={estilos.filas}>
        <Fila etiqueta="Pendiente por década" valor={pendiente(tendencia, unidad)} />
        <Fila etiqueta="Intervalo de 95 %" valor={intervalo(tendencia, unidad)} />
        {pct ? <Fila etiqueta="Cambio por década" valor={pct} /> : null}
        <Fila etiqueta="p-valor" valor={pValorTendencia(tendencia, analisis.veredicto.origen)} />
        <Fila
          etiqueta="Vínculo con El Niño"
          valor={enlace.indicativo ? `${enlace.texto} · indicativo` : enlace.texto}
        />
      </View>

      {analisis.avisos.map((a, i) => (
        <View key={`${a.codigo}-${i}`} style={estilos.aviso} accessible accessibilityLabel={`Aviso: ${a.texto}`}>
          <Texto variante="pequeno">{a.texto}</Texto>
        </View>
      ))}

      <EtiquetaFuente analisis={analisis} />
    </Tarjeta>
  );
}

function TendenciaAparente({ analisis }: { analisis: AnalyzeRespuesta }) {
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

function Fila({ etiqueta, valor }: { etiqueta: string; valor: string }) {
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

const estilos = StyleSheet.create({
  bloque: { gap: espacios.s },
  fila: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
  filas: { gap: espacios.s, paddingTop: espacios.xs },
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
