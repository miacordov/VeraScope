import {
  Inter_400Regular,
  Inter_500Medium,
  Inter_600SemiBold,
  Inter_700Bold,
  useFonts,
} from '@expo-google-fonts/inter';
import { Stack } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { StatusBar } from 'expo-status-bar';
import { useEffect } from 'react';
import { StyleSheet } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';

import { ProveedorConsultas } from '@/estado/ProveedorConsultas';
import { BandaSimulado } from '@/shared/components/BandaSimulado';
import { BotonModo } from '@/shared/components/BotonModo';
import { ProveedorTema } from '@/shared/ProveedorTema';
import { useEstilos, useTema } from '@/shared/useTema';
import { fuentes, type Colores } from '@/shared/tema';

// La pantalla de arranque se mantiene hasta que carga Inter (va dentro de la app, no se descarga).
SplashScreen.preventAutoHideAsync().catch(() => {});

export default function Raiz() {
  const [fuentesListas, errorFuentes] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    Inter_700Bold,
  });
  const listo = fuentesListas || errorFuentes !== null;

  useEffect(() => {
    if (listo) SplashScreen.hideAsync().catch(() => {});
  }, [listo]);

  if (!listo) return null;

  return (
    <ProveedorTema>
      <Contenido />
    </ProveedorTema>
  );
}

function Contenido() {
  const { modo, colores } = useTema();
  const estilos = useEstilos(crearEstilos);

  return (
    <GestureHandlerRootView style={estilos.raiz}>
      <SafeAreaProvider>
        <ProveedorConsultas>
          <StatusBar style={modo === 'oscuro' ? 'light' : 'dark'} />
          <SafeAreaView style={estilos.raiz} edges={['top', 'left', 'right']}>
            <BandaSimulado />
            <Stack
              screenOptions={{
                headerStyle: { backgroundColor: colores.fondo },
                headerTintColor: colores.institucional,
                headerTitleStyle: { fontFamily: fuentes.seminegrita },
                headerShadowVisible: false,
                headerRight: () => <BotonModo />,
                contentStyle: { backgroundColor: colores.fondo },
              }}>
              <Stack.Screen name="index" options={{ title: 'VeraScope', headerShown: false }} />
              <Stack.Screen name="espacio" options={{ title: 'Espacio de trabajo' }} />
              <Stack.Screen name="glosario" options={{ title: 'Glosario' }} />
            </Stack>
          </SafeAreaView>
        </ProveedorConsultas>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

const crearEstilos = (colores: Colores) =>
  StyleSheet.create({
    raiz: { flex: 1, backgroundColor: colores.fondo },
  });
