import { StyleSheet, Text, type TextProps } from 'react-native';

import { colores, tipografia } from '@/shared/tema';

export type VarianteTexto = keyof typeof tipografia;

/** Texto con la escala del tema. `suave` usa el color secundario. */
export function Texto({
  variante = 'cuerpo',
  suave = false,
  numerico = false,
  style,
  ...resto
}: TextProps & { variante?: VarianteTexto; suave?: boolean; numerico?: boolean }) {
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

const estilos = StyleSheet.create({
  base: { color: colores.texto },
  suave: { color: colores.textoSuave },
  numerico: { fontVariant: ['tabular-nums'] },
});
