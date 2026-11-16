import { useEstado } from '@/estado/store';
import { efectoEspejo } from '@/shared/api/__fixtures__';
import type { DemoRespuesta } from '@/shared/api/tipos';

import { iniciarDemo, irAlPaso, PASO_PENDIENTE, salirDeDemo } from '../acciones';

const estado = () => useEstado.getState();

beforeEach(() => {
  estado().reiniciar();
  global.fetch = jest.fn() as unknown as typeof fetch;
});

describe('ejecutor de guiones (demo 1 sobre el guion de ejemplo)', () => {
  it('cada paso deja el estado esperado', () => {
    irAlPaso(efectoEspejo, 0);
    expect(estado().variable).toBe('PRECTOTCORR');
    expect(estado().celda).toEqual({ lat: -5, lon: -80.5 });
    expect(estado().quitarElNino).toBe(false);
    expect(estado().demo).toEqual({ id: 'efecto-espejo', paso: 0 });

    irAlPaso(efectoEspejo, 1);
    expect(estado().mesVisible).toBe('1990-01');
    expect(estado().reproduciendo).toBe(true);
    expect(estado().celda).toEqual({ lat: -5, lon: -80.5 });

    irAlPaso(efectoEspejo, 2);
    expect(estado().reproduciendo).toBe(false);
    expect(estado().destino).toEqual({ lat: -18, lon: 142 });
    expect(estado().demo).toEqual({ id: 'efecto-espejo', paso: 2 });
  });

  it('volver a un paso anterior deja el mismo estado que llegar a él desde el principio', () => {
    irAlPaso(efectoEspejo, 0);
    const primero = { ...estado() };
    irAlPaso(efectoEspejo, 2);
    irAlPaso(efectoEspejo, 0);
    expect(estado().reproduciendo).toBe(false);
    expect(estado().destino).toBeNull();
    expect(estado().mesVisible).toBeNull();
    expect(estado().celda).toEqual(primero.celda);
    expect(estado().demo).toEqual({ id: 'efecto-espejo', paso: 0 });
  });

  it('parte del estado inicial: lo que el usuario cambió antes no se cuela en la demo', () => {
    estado().alternarElNino();
    estado().fijarVentana({ inicio: 2000, fin: 2015 });
    irAlPaso(efectoEspejo, 0);
    expect(estado().quitarElNino).toBe(false);
    expect(estado().ventana).toEqual(useEstado.getInitialState().ventana);
  });

  it('un paso fuera de rango se lleva al primero o al último', () => {
    irAlPaso(efectoEspejo, 99);
    expect(estado().demo?.paso).toBe(efectoEspejo.pasos.length - 1);
    irAlPaso(efectoEspejo, -5);
    expect(estado().demo?.paso).toBe(0);
  });

  it('no hace peticiones', () => {
    for (let i = 0; i < efectoEspejo.pasos.length; i++) irAlPaso(efectoEspejo, i);
    expect(global.fetch).not.toHaveBeenCalled();
  });
});

describe('vocabulario completo de acciones del contrato', () => {
  // Guion armado solo para la prueba (con todas las acciones); la app nunca inventa guiones.
  const todas: DemoRespuesta = {
    id: 'senal-o-ruido',
    titulo: 'Prueba',
    variable: 'T2M',
    celda: { lat: -6, lon: -80 },
    pasos: [
      {
        n: 1,
        texto: 'uno',
        acciones: [
          { tipo: 'seleccionar_variable', variable: 'T2M' },
          { tipo: 'seleccionar_celda', lat: -6, lon: -80 },
          { tipo: 'fijar_ventana', inicio: 2016, fin: 2025 },
          { tipo: 'quitar_el_nino', valor: true },
          { tipo: 'ir_al_mes', fecha: '1998-01' },
          { tipo: 'reproducir' },
          { tipo: 'detener' },
          { tipo: 'ir_a_destino', lat: 12, lon: -132 },
          { tipo: 'mostrar_periodos' },
        ],
      },
    ],
  };

  it('cada acción usa su acción del store', () => {
    irAlPaso(todas, 0);
    expect(estado()).toMatchObject({
      variable: 'T2M',
      celda: { lat: -6, lon: -80 },
      ventana: { inicio: 2016, fin: 2025 },
      quitarElNino: true,
      mesVisible: '1998-01',
      reproduciendo: false,
      destino: { lat: 12, lon: -132 },
      demo: { id: 'senal-o-ruido', paso: 0 },
    });
  });
});

describe('iniciar y salir', () => {
  it('iniciar deja la demo pendiente del guion; salir vuelve al estado inicial', () => {
    estado().seleccionarCelda({ lat: 10, lon: 120 });
    iniciarDemo('efecto-espejo');
    expect(estado().demo).toEqual({ id: 'efecto-espejo', paso: PASO_PENDIENTE });
    expect(estado().celda).toBeNull();

    irAlPaso(efectoEspejo, 1);
    salirDeDemo();
    expect(estado().demo).toBeNull();
    expect(estado().celda).toBeNull();
    expect(estado().reproduciendo).toBe(false);
  });
});
