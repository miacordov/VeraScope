import { useEstado } from '@/estado/store';
import type { DemoRespuesta, PasoDemo } from '@/shared/api/tipos';

/**
 * Ejecutor de los guiones de las demos (F3, #15; frontend/CLAUDE.md §12).
 *
 * Cada paso FIJA el estado por código con las acciones del contrato, así la demo no depende de que alguien toque
 * el lugar exacto. El ejecutor no sabe qué cuenta la demo: si el guion cambia (otra celda, otra variable, otro
 * texto), cambia el JSON del backend, no este archivo. No hace peticiones ni calcula nada.
 */

export type AccionDemo = PasoDemo['acciones'][number];

/** Aplica una acción del guion con las acciones del store (los componentes nunca mutan el estado). */
export function aplicarAccion(accion: AccionDemo): void {
  const e = useEstado.getState();
  switch (accion.tipo) {
    case 'seleccionar_variable':
      e.cambiarVariable(accion.variable);
      return;
    case 'seleccionar_celda':
      e.seleccionarCelda({ lat: accion.lat, lon: accion.lon });
      return;
    case 'fijar_ventana':
      e.fijarVentana({ inicio: accion.inicio, fin: accion.fin });
      return;
    case 'quitar_el_nino':
      e.fijarElNino(accion.valor);
      return;
    case 'reproducir':
      e.reproducir();
      return;
    case 'detener':
      e.detener();
      return;
    case 'ir_al_mes':
      e.irAlMes(accion.fecha);
      return;
    case 'ir_a_destino':
      e.elegirDestino({ lat: accion.lat, lon: accion.lon });
      return;
    case 'mostrar_periodos':
      // "Antes y después" está recortado (AVANCE, S4): la acción se acepta y no cambia nada.
      return;
    default: {
      // Si el contrato agrega una acción, `tsc` falla aquí hasta que se maneje.
      const sinManejar: never = accion;
      return sinManejar;
    }
  }
}

/**
 * Lleva la demo al paso `indice` (0 = primer paso). Parte del estado inicial y aplica, en orden, las acciones de
 * todos los pasos hasta ese: el resultado es el mismo se llegue con "Siguiente", con "Anterior" o directo.
 */
export function irAlPaso(demo: DemoRespuesta, indice: number): void {
  const paso = Math.min(Math.max(indice, 0), demo.pasos.length - 1);
  const e = useEstado.getState();
  e.reiniciar();
  for (const p of demo.pasos.slice(0, paso + 1)) {
    for (const accion of p.acciones) aplicarAccion(accion);
  }
  e.fijarDemo({ id: demo.id, paso });
}

/** Paso de una demo que empezó pero cuyo guion todavía no llegó. */
export const PASO_PENDIENTE = -1;

/**
 * Empieza una demo. El paso queda en `PASO_PENDIENTE` hasta que `BandaDemo` recibe el guion y aplica el primero
 * (así no se aplica nada a medias si el guion tarda o falla).
 */
export function iniciarDemo(id: DemoRespuesta['id']): void {
  const e = useEstado.getState();
  e.reiniciar();
  e.fijarDemo({ id, paso: PASO_PENDIENTE });
}

/** "Salir": vuelve al estado inicial. */
export function salirDeDemo(): void {
  useEstado.getState().reiniciar();
}
