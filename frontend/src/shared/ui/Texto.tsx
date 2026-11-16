import { StyleSheet, Text, type TextProps } from 'react-native';

import { useEstilos } from '@/shared/useTema';
import { tipografia, type Colores } from '@/shared/tema';

export type VarianteTexto = keyof typeof tipografia;

/** Texto con la escala del tema. `suave` usa el color secundario. */
export function Texto({
  variante = 'cuerpo',
  suave = false,
  numerico = false,
  style,
  ...resto
}: TextProps & { variante?: VarianteTexto; suave?: boolean; numerico?: boolean }) {
  const estilos = useEstilos(crearEstilos);
  return (
    <Text
      style={[
        estilos.base,
        tipografia[variante],
        suave && estilos.suave,
        numerico && estilos.numerico,
        style,
      ]}
      {...resto}
    />
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    base: { color: colores.texto },
    suave: { color: colores.textoSuave },
    numerico: { fontVariant: ['tabular-nums'] },
  });
