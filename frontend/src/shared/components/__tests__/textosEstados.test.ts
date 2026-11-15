import { ErrorApi, type CodigoErrorCliente } from '@/shared/api/cliente';

import {
  avanceEscaneo,
  estadoDeError,
  lineasDesdeCeldaCercana,
  TEXTOS_ACCION,
  TEXTOS_ERROR,
  TEXTOS_ESTADO,
} from '../textosEstados';

const CODIGOS: CodigoErrorCliente[] = [
  'ventana_corta',
  'fuera_de_rango',
  'sin_datos_tierra',
  'power_lento',
  'power_error',
  'escaneo_en_curso',
  'sin_conexion',
  'tiempo_agotado',
  'respuesta_invalida',
];

function todosLosTextos(): string[] {
  const deErrores = Object.values(TEXTOS_ERROR).flatMap((t) => [t.titulo, t.mensajeRespaldo]);
  const deEstados = Object.values(TEXTOS_ESTADO).flatMap((t) => (typeof t === 'string' ? [t] : Object.values(t)));
  return [...deErrores, ...deEstados, ...Object.values(TEXTOS_ACCION)];
}

function error(codigo: CodigoErrorCliente, mensaje: string, celdaCercana: { lat: number; lon: number } | null = null) {
  return new ErrorApi({ estado: 500, codigo, mensaje, celdaCercana, tipo: 'servidor' });
}

describe('textos de los estados (§11)', () => {
  it('cada código de error tiene título y mensaje de respaldo', () => {
    for (const codigo of CODIGOS) {
      expect(TEXTOS_ERROR[codigo].titulo.length).toBeGreaterThan(0);
      expect(TEXTOS_ERROR[codigo].mensajeRespaldo.length).toBeGreaterThan(0);
    }
  });

  it('sin disculpas, sin redacción causal y sin "sin resultados"', () => {
    const prohibidas = /lo sentimos|perd[oó]n|disculpa|caus[óoa]|provoca|prueba el calentamiento|sin resultados/i;
    for (const texto of todosLosTextos()) expect(texto).not.toMatch(prohibidas);
  });

  it('sin mayúsculas sostenidas (salvo siglas como NASA)', () => {
    for (const texto of todosLosTextos()) {
      const palabras = texto.match(/\b[A-ZÁÉÍÓÚÑ]{2,}\b/g) ?? [];
      expect(palabras.filter((p) => !['NASA', 'POWER'].includes(p))).toEqual([]);
    }
  });

  it('muestra el mensaje del servidor tal cual', () => {
    const r = estadoDeError(error('ventana_corta', 'Mensaje del servidor.'));
    expect(r).toEqual({ titulo: 'Elige al menos 10 años', mensaje: 'Mensaje del servidor.', accion: null });
  });

  it('usa el respaldo si el error llega sin mensaje', () => {
    expect(estadoDeError(error('power_error', '')).mensaje).toBe(TEXTOS_ERROR.power_error.mensajeRespaldo);
  });

  it('power_lento ofrece la celda cercana solo si llegó', () => {
    expect(estadoDeError(error('power_lento', 'x', { lat: -5, lon: -80 })).accion).toBe('celda_cercana');
    expect(estadoDeError(error('power_lento', 'x', null)).accion).toBe('reintentar');
  });

  it('sin_datos_tierra sugiere la lluvia', () => {
    expect(estadoDeError(error('sin_datos_tierra', 'x')).accion).toBe('usar_lluvia');
  });

  it('un error desconocido nunca muestra una traza', () => {
    const r = estadoDeError(new TypeError('Cannot read properties of undefined'));
    expect(r.mensaje).not.toMatch(/undefined|TypeError/);
    expect(r.accion).toBe('reintentar');
  });

  it('el avance del escaneo y la distancia solo dan formato, sin porcentajes', () => {
    expect(avanceEscaneo(1200, 4235)).toBe('1,200 de 4,235 lugares listos');
    expect(avanceEscaneo(1200, 4235)).not.toMatch(/%/);
    expect(lineasDesdeCeldaCercana(120)).toBe('Las líneas salen del punto de ScanMap más cercano, a 120 km.');
  });

  it('la banda sin conexión usa el texto obligatorio exacto', () => {
    expect(TEXTOS_ESTADO.bandaSinConexion).toBe('Sin conexión · mostrando la demo guardada en la app');
  });
});
