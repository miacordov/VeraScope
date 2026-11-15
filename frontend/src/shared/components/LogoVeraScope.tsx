import { Image, StyleSheet } from 'react-native';

// Ruta relativa con `require`: Expo no declara tipos para imágenes y Jest no conoce el alias `@/assets`.
const logo = require('../../../assets/marca/verascope-logo.jpg');

/**
 * Logo oficial de VeraScope (`assets/marca/verascope-logo.jpg`). No se redibuja ni se recolorea:
 * solo se recorta en círculo para que no se vean las esquinas claras del archivo sobre el fondo grafito.
 */
export function LogoVeraScope({ tamano = 40 }: { tamano?: number }) {
  return (
    <Image
      source={logo}
      resizeMode="cover"
      accessibilityRole="image"
      accessibilityLabel="Logo de VeraScope"
      style={[estilos.base, { width: tamano, height: tamano, borderRadius: tamano / 2 }]}
    />
  );
}

const estilos = StyleSheet.create({
  base: { overflow: 'hidden' },
});
