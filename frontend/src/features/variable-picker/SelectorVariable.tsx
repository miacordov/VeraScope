import { useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, View } from 'react-native';
import { useShallow } from 'zustand/react/shallow';

import { ANIO_INICIO_REGISTRO, useEstado } from '@/estado/store';
import { useSalud, useVariables } from '@/shared/api/consultas';
import type { DefinicionIndice, DefinicionVariable } from '@/shared/api/tipos';
import { estadoDeError, TEXTOS_ACCION } from '@/shared/components/textosEstados';
import { colores, espacios, radios, TOQUE_MIN } from '@/shared/tema';
import { Boton, Tarjeta, Texto } from '@/shared/ui';

import { aniosElegidos, esVentanaCorta, moverAnio, TEXTO_VENTANA_CORTA } from './ventana';

/**
 * Paso 1 de "Investigar" (frontend/CLAUDE.md §10): variable (de `/variables`), ventana de años e índice.
 * Todo cambia el store con sus acciones; los datos del catálogo vienen tal cual de la API.
 */
export function SelectorVariable() {
  const variables = useVariables();
  const salud = useSalud();
  const { variable, indice } = useEstado(useShallow((e) => ({ variable: e.variable, indice: e.indice })));

  if (variables.isPending) {
    return (
      <Tarjeta accessibilityLabel="Cargando las variables">
        <ActivityIndicator color={colores.texto} />
      </Tarjeta>
    );
  }
  if (variables.isError) {
    // Título y mensaje según los textos de F3 (§11); el mensaje del servidor va tal cual. Para el catálogo la única
    // acción que tiene sentido es volver a pedirlo: no hay celda cercana ni otra variable que ofrecer.
    const { titulo, mensaje, accion } = estadoDeError(variables.error);
    return (
      <Tarjeta accessibilityRole="alert">
        <Texto variante="cuerpoFuerte">{titulo}</Texto>
        <Texto>{mensaje}</Texto>
        {accion ? (
          <Boton texto={TEXTOS_ACCION.reintentar} variante="secundario" onPress={() => variables.refetch()} />
        ) : null}
      </Tarjeta>
    );
  }

  return (
    <Tarjeta>
      <Texto variante="subtitulo" accessibilityRole="header">
        Elige qué mirar
      </Texto>
      <View style={estilos.lista} accessibilityRole="radiogroup" accessibilityLabel="Variable">
        {variables.data.variables.map((v) => (
          <OpcionVariable
            key={v.id}
            definicion={v}
            elegida={v.id === variable}
            onPress={() => useEstado.getState().cambiarVariable(v.id)}
          />
        ))}
      </View>

      {salud.data ? <SelectorVentana ventanaFin={salud.data.ventana_fin} /> : null}

      <SelectorIndice indices={variables.data.indices} indice={indice} />
    </Tarjeta>
  );
}

function OpcionVariable({
  definicion,
  elegida,
  onPress,
}: {
  definicion: DefinicionVariable;
  elegida: boolean;
  onPress: () => void;
}) {
  const [enfocada, setEnfocada] = useState(false);
  return (
    <Pressable
      accessibilityRole="radio"
      accessibilityState={{ checked: elegida, selected: elegida }}
      accessibilityLabel={`${definicion.nombre}, en ${definicion.unidad}. ${definicion.definicion}`}
      onPress={onPress}
      onFocus={() => setEnfocada(true)}
      onBlur={() => setEnfocada(false)}
      style={[estilos.opcion, elegida && estilos.opcionElegida, enfocada && estilos.foco]}>
      <View style={estilos.cabecera}>
        {/* La marca de "elegida" es forma + texto, no solo color. */}
        <View style={[estilos.marca, elegida && estilos.marcaElegida]} />
        <Texto variante="cuerpoFuerte">{definicion.nombre}</Texto>
      </View>
      <Texto variante="pequeno" suave>
        {definicion.definicion}
      </Texto>
      <Texto variante="etiqueta" suave>
        {definicion.unidad} · {definicion.fuente}
        {elegida ? ' · elegida' : ''}
      </Texto>
    </Pressable>
  );
}

function SelectorVentana({ ventanaFin }: { ventanaFin: number }) {
  const ventana = useEstado((e) => e.ventana);
  const { inicio, fin } = aniosElegidos(ventana, ventanaFin);
  const corta = esVentanaCorta(ventana, ventanaFin);
  const mover = (extremo: 'inicio' | 'fin', paso: number) =>
    useEstado.getState().fijarVentana(moverAnio(ventana, ventanaFin, extremo, paso));

  return (
    <View style={estilos.bloque}>
      <Texto variante="cuerpoFuerte" accessibilityRole="header">
        Años
      </Texto>
      <View style={estilos.fila}>
        <Anio titulo="Desde" valor={inicio} mover={(paso) => mover('inicio', paso)} />
        <Anio titulo="Hasta" valor={fin} mover={(paso) => mover('fin', paso)} />
      </View>
      {ventana.inicio !== ANIO_INICIO_REGISTRO || ventana.fin !== null ? (
        <Boton
          texto="Usar todo el registro"
          variante="secundario"
          onPress={() => useEstado.getState().fijarVentana({ inicio: ANIO_INICIO_REGISTRO, fin: null })}
        />
      ) : (
        <Texto variante="pequeno" suave>
          Todo el registro, de {ANIO_INICIO_REGISTRO} a {ventanaFin}.
        </Texto>
      )}
      {corta ? (
        <Texto variante="cuerpoFuerte" accessibilityRole="alert">
          {TEXTO_VENTANA_CORTA}
        </Texto>
      ) : null}
    </View>
  );
}

function Anio({ titulo, valor, mover }: { titulo: string; valor: number; mover: (paso: number) => void }) {
  return (
    <View
      style={estilos.anio}
      accessible
      accessibilityRole="adjustable"
      accessibilityLabel={`${titulo} el año`}
      accessibilityValue={{ text: String(valor) }}
      accessibilityActions={[{ name: 'increment' }, { name: 'decrement' }]}
      onAccessibilityAction={(e) => mover(e.nativeEvent.actionName === 'increment' ? 1 : -1)}>
      <Texto variante="etiqueta" suave>
        {titulo}
      </Texto>
      <View style={estilos.fila}>
        <Boton texto="−" etiqueta={`${titulo}: un año menos`} variante="secundario" onPress={() => mover(-1)} />
        <Texto variante="cuerpoFuerte" numerico>
          {valor}
        </Texto>
        <Boton texto="＋" etiqueta={`${titulo}: un año más`} variante="secundario" onPress={() => mover(1)} />
      </View>
    </View>
  );
}

function SelectorIndice({ indices, indice }: { indices: readonly DefinicionIndice[]; indice: string }) {
  // Niño 1+2 solo aparece si el backend lo ofrece en `/variables`.
  if (indices.length < 2) return null;
  return (
    <View style={estilos.bloque} accessibilityRole="radiogroup" accessibilityLabel="Índice de El Niño">
      <Texto variante="cuerpoFuerte" accessibilityRole="header">
        Índice de El Niño
      </Texto>
      <View style={estilos.fila}>
        {indices.map((i) => (
          <Boton
            key={i.id}
            texto={i.id === indice ? `${i.nombre} ✓` : i.nombre}
            etiqueta={i.nombre}
            variante={i.id === indice ? 'principal' : 'secundario'}
            accessibilityRole="radio"
            accessibilityState={{ checked: i.id === indice }}
            onPress={() => useEstado.getState().fijarIndice(i.id)}
          />
        ))}
      </View>
      {indices
        .filter((i) => i.id === indice)
        .map((i) => (
          <Texto key={i.id} variante="pequeno" suave>
            {i.definicion} Fuente: {i.fuente}.
          </Texto>
        ))}
    </View>
  );
}

const estilos = StyleSheet.create({
  lista: { gap: espacios.s },
  opcion: {
    minHeight: TOQUE_MIN,
    padding: espacios.m,
    gap: espacios.xs,
    borderRadius: radios.m,
    borderWidth: 2,
    borderColor: colores.borde,
    backgroundColor: colores.superficieFuerte,
  },
  opcionElegida: { borderColor: colores.texto },
  foco: { outlineStyle: 'solid', outlineWidth: 2, outlineColor: colores.foco },
  cabecera: { flexDirection: 'row', alignItems: 'center', gap: espacios.s },
  marca: { width: 16, height: 16, borderRadius: 8, borderWidth: 2, borderColor: colores.textoSuave },
  marcaElegida: { borderColor: colores.texto, backgroundColor: colores.texto },
  bloque: { gap: espacios.s, paddingTop: espacios.s },
  fila: { flexDirection: 'row', flexWrap: 'wrap', alignItems: 'center', gap: espacios.m },
  anio: { gap: espacios.xs },
});
