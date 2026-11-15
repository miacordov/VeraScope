/**
 * Interruptor "Quitar El Niño" (frontend/CLAUDE.md §10, `enso-toggle`).
 * Solo cambia `quitarElNino` en el store: el gráfico y el veredicto eligen otra parte de la respuesta
 * que ya llegó. No hace ninguna petición de red. Dueña: F2 (`fe/graficos-enso`).
 */
import { useState } from 'react';
import { AccessibilityInfo, Pressable, StyleSheet, View } from 'react-native';

import { useEstado } from '@/estado/store';
import { colores, espacios, radios, TOQUE_MIN } from '@/shared/tema';
import { Texto } from '@/shared/ui';

type Props = {
  /** `vinculo_el_nino.rezago_meses` de la respuesta. */
  rezagoMeses: number;
};

export function textoRezago(rezagoMeses: number): string {
  const meses = rezagoMeses === 1 ? '1 mes' : `${rezagoMeses} meses`;
  return rezagoMeses === 0
    ? 'Quita la parte de la serie que explica El Niño, en el mismo mes.'
    : `Quita la parte de la serie que explica El Niño, con ${meses} de retraso.`;
}

export function InterruptorElNino({ rezagoMeses }: Props) {
  const activo = useEstado((e) => e.quitarElNino);
  const alternar = useEstado((e) => e.alternarElNino);
  const [enfocado, setEnfocado] = useState(false);

  const alPresionar = () => {
    alternar();
    AccessibilityInfo.announceForAccessibility(
      activo ? 'Se muestra la serie original.' : 'Se muestra la serie sin El Niño.',
    );
  };

  return (
    <View style={estilos.contenedor}>
      <Pressable
        accessibilityRole="switch"
        accessibilityLabel="Quitar El Niño"
        accessibilityHint={textoRezago(rezagoMeses)}
        accessibilityState={{ checked: activo }}
        onPress={alPresionar}
        onFocus={() => setEnfocado(true)}
        onBlur={() => setEnfocado(false)}
        style={({ pressed }) => [estilos.fila, pressed && estilos.presionado, enfocado && estilos.foco]}>
        <Texto variante="cuerpoFuerte">Quitar El Niño</Texto>
        <View style={[estilos.riel, activo && estilos.rielActivo]}>
          <View style={[estilos.perilla, activo && estilos.perillaActiva]} />
        </View>
        <Texto variante="etiqueta" style={estilos.estado}>
          {activo ? 'Sí' : 'No'}
        </Texto>
      </Pressable>
      <Texto variante="pequeno" suave>
        {textoRezago(rezagoMeses)}
      </Texto>
    </View>
  );
}

const estilos = StyleSheet.create({
  contenedor: { gap: espacios.xs },
  fila: {
    minHeight: TOQUE_MIN,
    flexDirection: 'row',
    alignItems: 'center',
    gap: espacios.m,
    paddingHorizontal: espacios.s,
    borderRadius: radios.m,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  presionado: { opacity: 0.8 },
  foco: { borderColor: colores.foco },
  riel: {
    width: 48,
    height: 28,
    borderRadius: 14,
    backgroundColor: colores.superficieFuerte,
    borderWidth: 1,
    borderColor: colores.borde,
    justifyContent: 'center',
    paddingHorizontal: 3,
  },
  rielActivo: { backgroundColor: colores.nino, borderColor: colores.nino },
  perilla: { width: 20, height: 20, borderRadius: 10, backgroundColor: colores.textoSuave },
  perillaActiva: { backgroundColor: colores.texto, alignSelf: 'flex-end' },
  estado: { minWidth: 20 },
});
