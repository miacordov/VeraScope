"""El casillero: una base SQLite de un solo archivo con todas las series mensuales.

Cada serie se guarda como un bloque binario de float32 (4 bytes por mes) con su mes de inicio.
Llave: (variable, lugar). Ejemplos de lugar: "celda:-6.00:-80.00", "demo:piura", "indice".
"""
import datetime as dt
import sqlite3

import numpy as np

ESQUEMA = """
CREATE TABLE IF NOT EXISTS series (
  variable TEXT NOT NULL, lugar TEXT NOT NULL, lat REAL, lon REAL,
  inicio TEXT NOT NULL, n INTEGER NOT NULL, valores BLOB NOT NULL,
  unidad TEXT, fuente TEXT, actualizado TEXT,
  PRIMARY KEY (variable, lugar));
CREATE TABLE IF NOT EXISTS fallos (
  tarea TEXT NOT NULL, lugar TEXT NOT NULL, error TEXT, cuando TEXT,
  PRIMARY KEY (tarea, lugar));
"""


def lugar_celda(lat, lon):
    return f"celda:{lat:+.2f}:{lon:+.2f}"


def mes_mas(inicio, k):
    y, m = map(int, inicio.split("-"))
    t = y * 12 + (m - 1) + k
    return f"{t // 12}-{t % 12 + 1:02d}"


def meses_entre(a, b):
    ya, ma = map(int, a.split("-")); yb, mb = map(int, b.split("-"))
    return (yb * 12 + mb) - (ya * 12 + ma)


class Casillero:
    def __init__(self, ruta):
        self.db = sqlite3.connect(ruta, timeout=30)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(ESQUEMA)

    def cerrar(self):
        self.db.close()

    def guardar(self, variable, lugar, inicio, valores, lat=None, lon=None, unidad=None, fuente=None):
        v = np.asarray(valores, dtype=np.float32)
        self.db.execute(
            "INSERT OR REPLACE INTO series VALUES (?,?,?,?,?,?,?,?,?,?)",
            (variable, lugar, lat, lon, inicio, int(v.size), v.tobytes(), unidad, fuente,
             dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")))
        self.db.execute("DELETE FROM fallos WHERE lugar = ? AND tarea = ?", (lugar, variable))
        self.db.commit()

    def leer(self, variable, lugar):
        r = self.db.execute("SELECT inicio, valores FROM series WHERE variable=? AND lugar=?", (variable, lugar)).fetchone()
        if r is None:
            return None, None
        return r[0], np.frombuffer(r[1], dtype=np.float32).copy()

    def leer_alineada(self, variable, lugar, meses):
        """Devuelve la serie sobre la ventana `meses` (lista AAAA-MM), con NaN donde no hay dato."""
        inicio, v = self.leer(variable, lugar)
        out = np.full(len(meses), np.nan, dtype=np.float32)
        if v is None:
            return out
        off = meses_entre(meses[0], inicio)
        for k in range(v.size):
            j = off + k
            if 0 <= j < len(meses):
                out[j] = v[k]
        return out

    def existe(self, variable, lugar):
        return self.db.execute("SELECT 1 FROM series WHERE variable=? AND lugar=?", (variable, lugar)).fetchone() is not None

    def lugares(self, variable, prefijo=""):
        return [r[0] for r in self.db.execute(
            "SELECT lugar FROM series WHERE variable=? AND lugar LIKE ?", (variable, prefijo + "%"))]

    def resumen(self):
        return self.db.execute(
            "SELECT variable, COUNT(*), MIN(inicio), MAX(n), MAX(actualizado) FROM series GROUP BY variable").fetchall()

    def fallo(self, tarea, lugar, error):
        self.db.execute("INSERT OR REPLACE INTO fallos VALUES (?,?,?,?)",
                        (tarea, lugar, str(error)[:500], dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")))
        self.db.commit()

    def resuelto(self, tarea, lugar):
        self.db.execute("DELETE FROM fallos WHERE tarea = ? AND lugar = ?", (tarea, lugar))
        self.db.commit()

    def fallos(self):
        return self.db.execute("SELECT tarea, lugar, error, cuando FROM fallos ORDER BY cuando").fetchall()


def compactar(meses, valores):
    """Quita los NaN de los extremos: devuelve (inicio, valores) listos para guardar."""
    v = np.asarray(valores, dtype=np.float32)
    ok = np.where(~np.isnan(v))[0]
    if ok.size == 0:
        return None, None
    return meses[ok[0]], v[ok[0]: ok[-1] + 1]
