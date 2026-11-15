import { altoDelMapa } from '../tamano';

describe('alto del mapa', () => {
  it('en teléfono y tableta es ¾ del ancho, con máximo de 360', () => {
    expect(altoDelMapa(360)).toBe(270);
    expect(altoDelMapa(800)).toBe(360);
  });

  it('en pantalla ancha (≥ 1024) es fijo', () => {
    expect(altoDelMapa(1024)).toBe(480);
    expect(altoDelMapa(1600)).toBe(480);
  });
});
