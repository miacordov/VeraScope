#!/usr/bin/env node
/**
 * Convierte las tierras de Natural Earth 110m (GeoJSON, dominio público) en `assets/geo/tierra.json`,
 * el formato compacto que dibuja `src/features/map/` (frontend/CLAUDE.md §9).
 *
 * Uso (una sola vez; el resultado se guarda en el repo):
 *   node scripts/costas.js ruta/a/ne_110m_land.geojson
 *
 * Descarga: https://github.com/nvkelso/natural-earth-vector/blob/v5.1.2/geojson/ne_110m_land.geojson
 *
 * - Las longitudes se dejan en −180..180, como vienen: el mapa dibuja cada anillo dos veces
 *   (desplazamiento 0 y +360). Convertirlas con `lon360` dibujaría rayas de lado a lado.
 * - Si dos vértices seguidos están a más de 180° de longitud, el anillo se parte ahí (en 110m solo pasa con
 *   la Antártida, en ±180), así ningún trazo cruza el mapa. Un anillo partido queda abierto.
 * - Coordenadas redondeadas a 0.01° (a esta escala no se nota) para que el archivo pese poco.
 */
const fs = require('node:fs');
const path = require('node:path');

const DECIMALES = 100;
const redondear = (x) => Math.round(x * DECIMALES) / DECIMALES;

/** Parte un anillo [[lon, lat], …] donde un salto de longitud supera 180°. */
function partirAnillo(anillo) {
  const partes = [];
  let actual = [];
  for (const [lon, lat] of anillo) {
    const previo = actual[actual.length - 1];
    if (previo && Math.abs(lon - previo[0]) > 180) {
      if (actual.length > 1) partes.push(actual);
      actual = [];
    }
    actual.push([redondear(lon), redondear(lat)]);
  }
  if (actual.length > 1) partes.push(actual);
  // Un anillo cerrado que se partió (la Antártida, que da la vuelta en ±180) queda como UNA línea abierta:
  // el último trozo termina donde empieza el primero, así que se unen. El mapa no la cierra con una raya.
  const [a0, b0] = anillo[0];
  const [a1, b1] = anillo[anillo.length - 1];
  if (partes.length > 1 && a0 === a1 && b0 === b1) {
    const ultimo = partes.pop();
    partes[0] = [...ultimo, ...partes[0].slice(1)];
  }
  return partes;
}

function convertir(geojson) {
  const anillos = [];
  for (const { geometry } of geojson.features) {
    const poligonos = geometry.type === 'Polygon' ? [geometry.coordinates] : geometry.coordinates;
    for (const poligono of poligonos) {
      for (const anillo of poligono) anillos.push(...partirAnillo(anillo));
    }
  }
  return {
    fuente: 'Natural Earth 1:110m, land (v5.1.2)',
    licencia: 'Dominio público',
    // Cada anillo es una lista plana [lon0, lat0, lon1, lat1, …] en −180..180.
    anillos: anillos.map((a) => a.flat()),
  };
}

if (require.main === module) {
  const entrada = process.argv[2];
  if (!entrada) {
    console.error('Uso: node scripts/costas.js ruta/a/ne_110m_land.geojson');
    process.exit(1);
  }
  const salida = path.join(__dirname, '..', 'assets', 'geo', 'tierra.json');
  const tierra = convertir(JSON.parse(fs.readFileSync(entrada, 'utf8')));
  fs.mkdirSync(path.dirname(salida), { recursive: true });
  fs.writeFileSync(salida, JSON.stringify(tierra) + '\n');
  const puntos = tierra.anillos.reduce((n, a) => n + a.length / 2, 0);
  console.log(`tierra.json: ${tierra.anillos.length} anillos, ${puntos} puntos`);
}

module.exports = { convertir, partirAnillo };
