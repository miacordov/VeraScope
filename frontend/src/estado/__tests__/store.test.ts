import { estadoInicial, useEstado } from '../store';

const acciones = () => useEstado.getState();

/** Deja reproducción, mes y destino con valores para ver si se reinician. */
function conAnalisisEnCurso() {
  acciones().seleccionarCelda({ lat: -5, lon: -80.5 });
  acciones().irAlMes('1998-01');
  acciones().reproducir();
  acciones().elegirDestino({ lat: -18, lon: 142 });
  acciones().fijarElNino(true);
}

function expectReiniciado() {
  const e = useEstado.getState();
  expect(e.mesVisible).toBeNull();
  expect(e.reproduciendo).toBe(false);
  expect(e.destino).toBeNull();
}

beforeEach(() => acciones().reiniciar());

describe('estado inicial', () => {
  it('coincide con la §7', () => {
    const e = useEstado.getState();
    expect(e.variable).toBe('PRECTOTCORR');
    expect(e.celda).toBeNull();
    expect(e.ventana).toEqual({ inicio: 1981, fin: null });
    expect(e.quitarElNino).toBe(false);
    expect(e.indice).toBe('ONI');
    expect(e.filtroFeed).toBe('fuertes');
    expect(e.mosaicoVisible).toBe(false);
    expect(e.demo).toBeNull();
  });
});

describe('reglas de reinicio y conservación', () => {
  it('cambiar la celda reinicia mes, reproducción y destino, y conserva quitarElNino', () => {
    conAnalisisEnCurso();
    acciones().seleccionarCelda({ lat: 0.5, lon: 116 });
    expectReiniciado();
    expect(useEstado.getState().quitarElNino).toBe(true);
  });

  it('cambiar la variable reinicia y conserva la celda', () => {
    conAnalisisEnCurso();
    acciones().cambiarVariable('T2M');
    expectReiniciado();
    expect(useEstado.getState().celda).toEqual({ lat: -5, lon: -80.5 });
    expect(useEstado.getState().variable).toBe('T2M');
  });

  it('cambiar la ventana reinicia', () => {
    conAnalisisEnCurso();
    acciones().fijarVentana({ inicio: 1990, fin: 2020 });
    expectReiniciado();
    expect(useEstado.getState().ventana).toEqual({ inicio: 1990, fin: 2020 });
  });

  it('cambiar el índice reinicia', () => {
    conAnalisisEnCurso();
    acciones().fijarIndice('NINO12');
    expectReiniciado();
    expect(useEstado.getState().indice).toBe('NINO12');
  });

  it('el interruptor no toca la selección', () => {
    conAnalisisEnCurso();
    acciones().alternarElNino();
    const e = useEstado.getState();
    expect(e.quitarElNino).toBe(false);
    expect(e.mesVisible).toBe('1998-01');
    expect(e.destino).toEqual({ lat: -18, lon: 142 });
  });
});

describe('celda', () => {
  it('se guarda cuantizada y con lon en −180..180', () => {
    acciones().seleccionarCelda({ lat: -5.12, lon: 279.63 });
    expect(useEstado.getState().celda).toEqual({ lat: -5, lon: -80.5 });
  });

  it('acepta null', () => {
    acciones().seleccionarCelda({ lat: 1, lon: 1 });
    acciones().seleccionarCelda(null);
    expect(useEstado.getState().celda).toBeNull();
  });
});

describe('destino por defecto', () => {
  const lineas = [
    { tipo: 'mismo' as const, lat: 10, lon: 120 },
    { tipo: 'opuesto' as const, lat: -18, lon: 142 },
    { tipo: 'opuesto' as const, lat: 0, lon: 116 },
  ];

  it('toma la primera línea de efecto opuesto si no hay destino', () => {
    acciones().destinoPorDefecto(lineas);
    expect(useEstado.getState().destino).toEqual({ lat: -18, lon: 142 });
  });

  it('no pisa un destino elegido', () => {
    acciones().elegirDestino({ lat: 0, lon: 116 });
    acciones().destinoPorDefecto(lineas);
    expect(useEstado.getState().destino).toEqual({ lat: 0, lon: 116 });
  });

  it('queda null si no hay líneas opuestas', () => {
    acciones().destinoPorDefecto([{ tipo: 'mismo', lat: 10, lon: 120 }]);
    expect(useEstado.getState().destino).toBeNull();
  });
});

describe('otras acciones', () => {
  it('reproducir y detener', () => {
    acciones().reproducir();
    expect(useEstado.getState().reproduciendo).toBe(true);
    acciones().detener();
    expect(useEstado.getState().reproduciendo).toBe(false);
  });

  it('mosaico, feed y demo', () => {
    acciones().alternarMosaico();
    acciones().fijarFiltroFeed('opuestas');
    acciones().fijarDemo({ id: 'efecto-espejo', paso: 1 });
    const e = useEstado.getState();
    expect(e.mosaicoVisible).toBe(true);
    expect(e.filtroFeed).toBe('opuestas');
    expect(e.demo).toEqual({ id: 'efecto-espejo', paso: 1 });
  });

  it('reiniciar vuelve al estado inicial', () => {
    conAnalisisEnCurso();
    acciones().reiniciar();
    const { celda, quitarElNino, mesVisible, destino } = useEstado.getState();
    expect({ celda, quitarElNino, mesVisible, destino }).toEqual({
      celda: estadoInicial.celda,
      quitarElNino: estadoInicial.quitarElNino,
      mesVisible: estadoInicial.mesVisible,
      destino: estadoInicial.destino,
    });
  });
});
