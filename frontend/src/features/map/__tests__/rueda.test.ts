import { renderHook } from '@testing-library/react-native';

import { factorRueda } from '../proyeccion';
import { useZoomConRueda as rueda, type RefLienzo } from '../rueda';
import { useZoomConRueda as ruedaWeb } from '../rueda.web';

/** Nodo del navegador simulado: guarda el escuchador de `wheel` para dispararlo a mano. */
function nodoFalso() {
  const nodo = {
    escuchador: null as ((e: unknown) => void) | null,
    opciones: null as unknown,
    addEventListener: jest.fn((_tipo: string, fn: (e: unknown) => void, opciones: unknown) => {
      nodo.escuchador = fn;
      nodo.opciones = opciones;
    }),
    removeEventListener: jest.fn(),
    getBoundingClientRect: () => ({ left: 10, top: 20 }),
  };
  return nodo;
}

const comoRef = (nodo: object) => ({ current: nodo }) as unknown as RefLienzo;

describe('zoom con la rueda (web)', () => {
  it('impide el desplazamiento de la página y acerca alrededor del cursor', async () => {
    const nodo = nodoFalso();
    const alGirar = jest.fn();
    await renderHook(() => ruedaWeb(comoRef(nodo), alGirar));

    expect(nodo.opciones).toEqual({ passive: false });
    const preventDefault = jest.fn();
    nodo.escuchador?.({ deltaY: -100, deltaMode: 0, clientX: 110, clientY: 70, preventDefault });

    expect(preventDefault).toHaveBeenCalled();
    expect(alGirar).toHaveBeenCalledWith(factorRueda(-100), { x: 100, y: 50 });
  });

  it('quita el escuchador al desmontar', async () => {
    const nodo = nodoFalso();
    const { unmount } = await renderHook(() => ruedaWeb(comoRef(nodo), jest.fn()));
    await unmount();
    expect(nodo.removeEventListener).toHaveBeenCalledWith('wheel', nodo.escuchador);
  });

  it('en el teléfono no escucha nada', async () => {
    const nodo = nodoFalso();
    await renderHook(() => rueda(comoRef(nodo), jest.fn()));
    expect(nodo.addEventListener).not.toHaveBeenCalled();
  });
});
