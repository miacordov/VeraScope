/**
 * Proyección ortográfica del globo del Inicio (el planeta visto desde el espacio). Funciones puras: no dibujan.
 *
 * El globo es una ilustración, no una vista de análisis: el mapa con celdas, gestos y mosaico sigue en
 * `features/map` (equirrectangular). Esta proyección solo ubica las costas y el arco de la demo sobre la esfera.
 */
export type Centro = { lon: number; lat: number };
export type PuntoGlobo = { x: number; y: number; visible: boolean };

const RAD = Math.PI / 180;

/**
 * Proyecta (lon, lat) sobre un globo de radio `radio`, con centro en (0, 0), mirando hacia `centro`.
 * `visible` es falso en la cara oculta. Esos puntos se llevan al borde del planeta: así una tierra que se
 * ve solo en parte se cierra por el borde en vez de cruzarlo.
 */
export function proyectar(lon: number, lat: number, centro: Centro, radio: number): PuntoGlobo {
  const l = lat * RAD;
  const dl = (lon - centro.lon) * RAD;
  const l0 = centro.lat * RAD;
  const x = Math.cos(l) * Math.sin(dl);
  const y = Math.cos(l0) * Math.sin(l) - Math.sin(l0) * Math.cos(l) * Math.cos(dl);
  const cosc = Math.sin(l0) * Math.sin(l) + Math.cos(l0) * Math.cos(l) * Math.cos(dl);
  if (cosc >= 0) return { x: x * radio, y: -y * radio, visible: true };
  const n = Math.hypot(x, y) || 1;
  return { x: (x / n) * radio, y: (-y / n) * radio, visible: false };
}

const r1 = (v: number) => Math.round(v * 10) / 10;

const VUELTA = 2 * Math.PI;
/** Ángulo en (−π, π]. */
const normalizar = (a: number) => a - VUELTA * Math.ceil((a - Math.PI) / VUELTA);
const angulo = (p: PuntoGlobo) => Math.atan2(p.y, p.x);

/**
 * Arco del borde del planeta que reemplaza un tramo oculto: va de `desde` (último punto visible) a `hasta`
 * (siguiente punto visible) por el lado más corto. Con costas densas los dos quedan pegados al horizonte, y la
 * tierra sigue por detrás del borde más cercano; los puntos ocultos no sirven para elegir el lado, porque al
 * proyectarlos pueden caer del lado opuesto del planeta.
 */
function arcoDeBorde(desde: PuntoGlobo, hasta: PuntoGlobo, radio: number): PuntoGlobo[] {
  const giro = normalizar(angulo(hasta) - angulo(desde));
  const a0 = angulo(desde);
  const pasos = Math.max(1, Math.ceil(Math.abs(giro) / (5 * RAD)));
  const salida: PuntoGlobo[] = [];
  for (let k = 0; k <= pasos; k++) {
    const a = a0 + (giro * k) / pasos;
    salida.push({ x: Math.cos(a) * radio, y: Math.sin(a) * radio, visible: true });
  }
  return salida;
}

const aTrazado = (puntos: PuntoGlobo[]) =>
  puntos.map((p, i) => `${i === 0 ? 'M' : 'L'}${r1(p.x)} ${r1(p.y)}`).join('') + 'Z';

/**
 * `d` de un solo `<Path>` con las costas (`[lon0, lat0, lon1, lat1, …]`) vistas desde `centro`.
 * Cada tramo oculto de un anillo se reemplaza por un arco del borde del planeta (`arcoDeBorde`). Nunca se
 * dibujan los puntos ocultos: proyectados al borde pueden caer del lado opuesto y tapar el océano.
 */
export function trazadoTierra(anillos: readonly (readonly number[])[], centro: Centro, radio: number): string {
  const partes: string[] = [];
  for (const a of anillos) {
    const puntos: PuntoGlobo[] = [];
    for (let i = 0; i + 1 < a.length; i += 2) puntos.push(proyectar(a[i], a[i + 1], centro, radio));
    const primero = puntos.findIndex((p) => p.visible);
    if (primero < 0) continue;
    if (puntos.every((p) => p.visible)) {
      partes.push(aTrazado(puntos));
      continue;
    }
    // Recorre el anillo en ciclo empezando por un punto visible.
    const ciclo = [...puntos.slice(primero), ...puntos.slice(0, primero)];
    const salida: PuntoGlobo[] = [];
    let oculto = false;
    for (const p of [...ciclo, ciclo[0]]) {
      if (!p.visible) {
        oculto = true;
        continue;
      }
      if (oculto) salida.push(...arcoDeBorde(salida[salida.length - 1], p, radio));
      oculto = false;
      salida.push(p);
    }
    salida.pop(); // el último es `ciclo[0]`, que ya abre el trazado
    partes.push(aTrazado(salida));
  }
  return partes.join('');
}

/** Puntos del círculo máximo de `a` a `b` (interpolación esférica): `pasos + 1` puntos. */
export function circuloMaximo(a: Centro, b: Centro, pasos = 64): Centro[] {
  const v = (p: Centro) => {
    const l = p.lat * RAD;
    const o = p.lon * RAD;
    return [Math.cos(l) * Math.cos(o), Math.cos(l) * Math.sin(o), Math.sin(l)];
  };
  const [p, q] = [v(a), v(b)];
  const omega = Math.acos(Math.min(1, Math.max(-1, p[0] * q[0] + p[1] * q[1] + p[2] * q[2])));
  if (omega === 0) return [a, b];
  const salida: Centro[] = [];
  for (let i = 0; i <= pasos; i++) {
    const t = i / pasos;
    const s1 = Math.sin((1 - t) * omega) / Math.sin(omega);
    const s2 = Math.sin(t * omega) / Math.sin(omega);
    const [x, y, z] = [0, 1, 2].map((k) => s1 * p[k] + s2 * q[k]);
    salida.push({ lon: Math.atan2(y, x) / RAD, lat: Math.atan2(z, Math.hypot(x, y)) / RAD });
  }
  return salida;
}

/** `d` de la parte visible de un arco de círculo máximo (nunca salta por la cara oculta). */
export function trazadoArco(a: Centro, b: Centro, centro: Centro, radio: number): string {
  let d = '';
  let abierto = false;
  for (const p of circuloMaximo(a, b)) {
    const q = proyectar(p.lon, p.lat, centro, radio);
    if (!q.visible) {
      abierto = false;
      continue;
    }
    d += `${abierto ? 'L' : 'M'}${r1(q.x)} ${r1(q.y)}`;
    abierto = true;
  }
  return d;
}
