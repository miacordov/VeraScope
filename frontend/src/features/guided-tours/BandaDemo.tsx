import { useEffect } from 'react';
import { AccessibilityInfo, StyleSheet, View } from 'react-native';

import { useEstado } from '@/estado/store';
import type { DemoId } from '@/shared/api/tipos';
import { estadoDeError } from '@/shared/components/textosEstados';
import { useEstilos } from '@/shared/useTema';
import { espacios, type Colores } from '@/shared/tema';
import { Boton, Texto } from '@/shared/ui';

import { irAlPaso, PASO_PENDIENTE, salirDeDemo } from './acciones';
import { useDemo } from './useDemo';

const DEMOS: readonly DemoId[] = ['efecto-espejo', 'senal-o-ruido'];
const esDemoId = (id: string): id is DemoId => (DEMOS as readonly string[]).includes(id);

/**
 * Banda de la demo guiada (F3, #15). Aparece en toda la app mientras `demo` del store no es `null`, como la banda
 * "Datos simulados", así no necesita un hueco en las pantallas de otros. Muestra el texto del paso tal como viene
 * del guion y los controles Anterior / Siguiente / Salir. Cambiar de paso no pide datos: el guion ya llegó.
 */
export function BandaDemo() {
  const estilos = useEstilos(crearEstilos);
  const demo = useEstado((e) => e.demo);
  const id = demo && esDemoId(demo.id) ? demo.id : null;
  const guion = useDemo(id);
  const paso = demo?.paso ?? PASO_PENDIENTE;

  // Primer paso: se aplica una sola vez, cuando llega el guion (después, `irAlPaso` deja el paso en 0).
  useEffect(() => {
    if (guion.data && id !== null && paso === PASO_PENDIENTE) irAlPaso(guion.data, 0);
  }, [guion.data, id, paso]);

  const texto = paso >= 0 ? (guion.data?.pasos[paso]?.texto ?? null) : null;
  useEffect(() => {
    if (texto) AccessibilityInfo.announceForAccessibility(texto);
  }, [texto]);

  if (demo === null) return null;

  if (id === null || guion.isError) {
    const { titulo, mensaje } =
      id === null
        ? { titulo: 'Demo no disponible', mensaje: 'Esta demo no existe en esta versión de la app.' }
        : estadoDeError(guion.error);
    return (
      <View style={estilos.banda} accessibilityRole="alert">
        <View style={estilos.textos}>
          <Texto variante="cuerpoFuerte">{titulo}</Texto>
          <Texto variante="pequeno">{mensaje}</Texto>
        </View>
        <View style={estilos.botones}>
          {id !== null ? <Boton texto="Reintentar" variante="secundario" onPress={() => guion.refetch()} /> : null}
          <Boton texto="Salir" variante="secundario" etiqueta="Salir de la demo" onPress={salirDeDemo} />
        </View>
      </View>
    );
  }

  if (!guion.data || texto === null) {
    return (
      <View style={estilos.banda} accessibilityRole="progressbar" accessibilityLabel="Cargando la demo">
        <View style={estilos.textos}>
          <Texto variante="pequeno">Cargando la demo…</Texto>
        </View>
        <Boton texto="Salir" variante="secundario" etiqueta="Salir de la demo" onPress={salirDeDemo} />
      </View>
    );
  }

  const datos = guion.data;
  const total = datos.pasos.length;

  return (
    <View style={estilos.banda} accessibilityRole="toolbar" accessibilityLabel={`Demo guiada: ${datos.titulo}`}>
      <View style={estilos.textos}>
        <Texto variante="etiqueta" suave>
          Demo · {datos.titulo} · paso {paso + 1} de {total}
        </Texto>
        <Texto variante="cuerpoFuerte" accessibilityLiveRegion="polite">
          {texto}
        </Texto>
      </View>
      <View style={estilos.botones}>
        <Boton
          texto="Anterior"
          variante="secundario"
          etiqueta="Paso anterior"
          disabled={paso === 0}
          onPress={() => irAlPaso(datos, paso - 1)}
        />
        <Boton
          texto="Siguiente"
          etiqueta="Paso siguiente"
          disabled={paso >= total - 1}
          onPress={() => irAlPaso(datos, paso + 1)}
        />
        <Boton texto="Salir" variante="secundario" etiqueta="Salir de la demo" onPress={salirDeDemo} />
      </View>
    </View>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    banda: {
      backgroundColor: colores.superficieFuerte,
      borderBottomColor: colores.borde,
      borderBottomWidth: 1,
      paddingHorizontal: espacios.l,
      paddingVertical: espacios.m,
      flexDirection: 'row',
      flexWrap: 'wrap',
      alignItems: 'center',
      gap: espacios.m,
    },
    textos: { flexGrow: 1, flexShrink: 1, flexBasis: 280, gap: espacios.xs },
    botones: { flexDirection: 'row', flexWrap: 'wrap', gap: espacios.s },
  });
