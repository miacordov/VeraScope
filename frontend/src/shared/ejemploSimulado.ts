/**
 * Única combinación que sirve el backend en modo simulado (`VERASCOPE_SIMULADO=1`):
 * `backend/app/catalogo/simulado/analyze.json` (Piura, lluvia, 1981–1990, ONI). Otra combinación recibe 422.
 * Solo se ofrece cuando `salud.simulado` es verdadero; desaparece con la API real.
 */
export const EJEMPLO_SIMULADO = {
  nombre: 'Piura (Perú)',
  variable: 'PRECTOTCORR',
  celda: { lat: -5.0, lon: -80.5 },
  ventana: { inicio: 1981, fin: 1990 },
  indice: 'ONI',
} as const;
