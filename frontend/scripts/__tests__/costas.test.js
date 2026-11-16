const { convertir, partirAnillo } = require('../costas');

describe('partirAnillo', () => {
  it('deja intacto un anillo sin saltos y redondea a 0.01°', () => {
    expect(partirAnillo([[10.123, 5.456], [11, 6], [10.123, 5.456]])).toEqual([[[10.12, 5.46], [11, 6], [10.12, 5.46]]]);
  });

  it('une en una línea abierta un anillo cerrado que salta de 180 a −180', () => {
    const anillo = [[0, -70], [90, -75], [180, -90], [-180, -90], [-90, -75], [0, -70]];
    expect(partirAnillo(anillo)).toEqual([[[-180, -90], [-90, -75], [0, -70], [90, -75], [180, -90]]]);
  });
});

describe('convertir', () => {
  it('aplana Polygon y MultiPolygon en anillos [lon, lat, …]', () => {
    const geojson = {
      features: [
        { geometry: { type: 'Polygon', coordinates: [[[0, 0], [1, 0], [0, 0]]] } },
        { geometry: { type: 'MultiPolygon', coordinates: [[[[2, 2], [3, 2], [2, 2]]], [[[4, 4], [5, 4], [4, 4]]]] } },
      ],
    };
    expect(convertir(geojson).anillos).toEqual([
      [0, 0, 1, 0, 0, 0],
      [2, 2, 3, 2, 2, 2],
      [4, 4, 5, 4, 4, 4],
    ]);
  });
});
