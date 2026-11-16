/**
 * Alternativa en texto de las líneas del mapa (frontend/CLAUDE.md §9 y §13): así las usa un lector de pantalla.
 * Cada línea es un botón que hace lo mismo que tocarla en el mapa (`elegirDestino`). Debajo, la franja fija con el
 * detalle de la línea elegida. Sin líneas se muestra `mensaje_vacio` (es un resultado, no un error).
 */
import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';

import { useEstado } from '@/estado/store';
import type { Linea, TeleconnectRespuesta } from '@/shared/api/tipos';
import {
  estadoDeError,
  lineasDesdeCeldaCercana,
  TEXTOS_ACCION,
  TEXTOS_ESTADO,
} from '@/shared/components/textosEstados';
import { celda as textoCelda } from '@/shared/format';
import { mismaCelda, type Coordenadas } from '@/shared/geo';
import { colores, espacios, radios, TOQUE_MIN } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

import { detalleLinea, etiquetaLinea, FRASE_LINEAS, LEYENDA_LINEAS, NOMBRE_TIPO, textoLinea } from './textos';

type Props = {
  respuesta: TeleconnectRespuesta | undefined;
  cargando: boolean;
  error: unknown;
  destino: Coordenadas | null;
  reintentar: () => void;
};

export function ListaLineas({ respuesta, cargando, error, destino, reintentar }: Props) {
  return (
    <Tarjeta>
      <Texto variante="cuerpoFuerte" accessibilityRole="header">
        Líneas causa → consecuencia
      </Texto>
      {cargando ? (
        <View accessibilityLabel="Cargando las líneas" accessibilityRole="progressbar">
          <ActivityIndicator color={colores.texto} />
        </View>
      ) : error ? (
        <ErrorLineas error={error} reintentar={reintentar} />
      ) : respuesta ? (
        <Contenido respuesta={respuesta} destino={destino} />
      ) : null}
    </Tarjeta>
  );
}

function ErrorLineas({ error, reintentar }: { error: unknown; reintentar: () => void }) {
  // El mensaje del servidor va tal cual (§11); 503 `escaneo_en_curso` no lleva botón: hay que esperar al escaneo.
  const { titulo, mensaje, accion } = estadoDeError(error);
  const actuar = () => {
    if (accion === 'usar_lluvia') useEstado.getState().cambiarVariable('PRECTOTCORR');
    else reintentar();
  };
  return (
    <View accessibilityRole="alert" style={estilos.bloque}>
      <Texto variante="cuerpoFuerte">{titulo}</Texto>
      <Texto>{mensaje}</Texto>
      {accion === 'reintentar' || accion === 'usar_lluvia' ? (
        <Boton texto={TEXTOS_ACCION[accion]} variante="secundario" onPress={actuar} />
      ) : null}
    </View>
  );
}

function Contenido({ respuesta, destino }: { respuesta: TeleconnectRespuesta; destino: Coordenadas | null }) {
  const { origen, lineas, mensaje_vacio } = respuesta;
  const elegida = lineas.find((l) => mismaCelda(destino, l)) ?? null;

  return (
    <View style={estilos.bloque}>
      {origen.distancia_a_clic_km > 0 ? (
        <Texto variante="pequeno" suave>
          {lineasDesdeCeldaCercana(origen.distancia_a_clic_km)} Celda de origen: {textoCelda(origen)}.
        </Texto>
      ) : null}

      {lineas.length === 0 ? (
        <Texto>{mensaje_vacio ?? TEXTOS_ESTADO.sinLineasRespaldo}</Texto>
      ) : (
        <>
          <Texto variante="pequeno" suave>
            {LEYENDA_LINEAS} {FRASE_LINEAS}
          </Texto>
          <View style={estilos.lista}>
            {lineas.map((linea) => (
              <OpcionLinea
                key={`${linea.tipo}-${linea.lat}-${linea.lon}`}
                linea={linea}
                elegida={elegida === linea}
                onPress={() => useEstado.getState().elegirDestino({ lat: linea.lat, lon: linea.lon })}
              />
            ))}
          </View>
          {elegida ? (
            <View
              style={[estilos.franja, elegida.tipo === 'mismo' && estilos.franjaMismo]}
              accessibilityLiveRegion="polite"
              testID="franja-linea">
              <Texto variante="cuerpoFuerte">{textoLinea(elegida)}</Texto>
              <Texto variante="pequeno">
                Destino: celda {textoCelda(elegida)}. {FRASE_LINEAS}
              </Texto>
            </View>
          ) : (
            <Texto variante="pequeno" suave>
              Toca una línea en el mapa o en esta lista para ver su detalle.
            </Texto>
          )}
        </>
      )}
    </View>
  );
}

function OpcionLinea({ linea, elegida, onPress }: { linea: Linea; elegida: boolean; onPress: () => void }) {
  const [enfocada, setEnfocada] = useState(false);
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ selected: elegida }}
      accessibilityLabel={etiquetaLinea(linea)}
      onPress={onPress}
      onFocus={() => setEnfocada(true)}
      onBlur={() => setEnfocada(false)}
      style={[estilos.opcion, elegida && estilos.opcionElegida, enfocada && estilos.foco]}>
      {/* La marca repite la forma de la línea del mapa (continua o punteada), no solo el color. */}
      <View style={[estilos.marca, linea.tipo === 'opuesto' ? estilos.marcaOpuesto : estilos.marcaMismo]} />
      <View style={estilos.textoOpcion}>
        <Texto variante="cuerpoFuerte">
          {NOMBRE_TIPO[linea.tipo]}
          {elegida ? ' · elegida' : ''}
        </Texto>
        <Texto variante="pequeno" suave numerico>
          {textoCelda(linea)} · {detalleLinea(linea)}
        </Texto>
      </View>
    </Pressable>
  );
}

const estilos = StyleSheet.create({
  bloque: { gap: espacios.s },
  lista: { gap: espacios.s },
  opcion: {
    minHeight: TOQUE_MIN,
    flexDirection: 'row',
    alignItems: 'center',
    gap: espacios.m,
    padding: espacios.m,
    borderRadius: radios.m,
    borderWidth: 2,
    borderColor: colores.borde,
    backgroundColor: colores.superficieFuerte,
  },
  opcionElegida: { borderColor: colores.texto },
  foco: { outlineStyle: 'solid', outlineWidth: 2, outlineColor: colores.foco },
  textoOpcion: { flex: 1, gap: espacios.xs },
  marca: { width: 28, height: 0, borderTopWidth: 3 },
  marcaOpuesto: { borderColor: colores.nino, borderStyle: 'solid' },
  marcaMismo: { borderColor: colores.texto, borderStyle: 'dashed' },
  franja: {
    gap: espacios.xs,
    padding: espacios.m,
    borderRadius: radios.m,
    borderLeftWidth: 4,
    borderLeftColor: colores.nino,
    backgroundColor: colores.superficieFuerte,
  },
  franjaMismo: { borderLeftColor: colores.texto },
});
