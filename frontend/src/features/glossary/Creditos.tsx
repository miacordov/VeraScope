import { StyleSheet, View } from 'react-native';

import { espacios } from '@/shared/tema';
import { Tarjeta, Texto } from '@/shared/ui';

/** Fuentes de lo que muestra la app (frontend/CLAUDE.md §3 y §9; issue #15). Texto fijo: no depende de la red. */
export const CREDITOS = [
  { que: 'Datos del clima', fuente: 'MERRA-2 vía NASA POWER (lluvia, temperatura, humedad del suelo y del aire)' },
  { que: 'Índices de El Niño', fuente: 'ONI y Niño 1+2, publicados por el Climate Prediction Center de NOAA (NOAA CPC)' },
  { que: 'Costas del mapa', fuente: 'Natural Earth, 1:110 m (dominio público)' },
] as const;

export function Creditos() {
  return (
    <Tarjeta accessibilityLabel="Créditos y fuentes de los datos">
      <Texto variante="cuerpoFuerte" accessibilityRole="header">
        Créditos y fuentes
      </Texto>
      {CREDITOS.map((c) => (
        <View key={c.que} style={estilos.fila} accessible accessibilityLabel={`${c.que}: ${c.fuente}`}>
          <Texto variante="pequeno" suave>
            {c.que}
          </Texto>
          <Texto variante="pequeno">{c.fuente}</Texto>
        </View>
      ))}
      <Texto variante="pequeno" suave>
        VeraScope detecta tendencias y coincidencias en estos datos; no atribuye causas.
      </Texto>
    </Tarjeta>
  );
}

const estilos = StyleSheet.create({
  fila: { gap: 2, paddingTop: espacios.xs },
});
