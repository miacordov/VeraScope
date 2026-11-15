"""`instalar` no debe dañar el casillero si la API lo tiene abierto, ni aplicarle un `-wal` viejo."""
import hashlib
import io
import sqlite3
import tarfile

import numpy as np
import pytest

from verascope_datos import config
from verascope_datos.almacen import Casillero
from verascope_datos.paquete import empaquetar, instalar


def _sha(ruta):
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _integridad(ruta):
    con = sqlite3.connect(ruta)
    try:
        return con.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        con.close()


@pytest.fixture
def paquete(tmp_path):
    """Un paquete chico con casillero, una matriz de `tabla/` y su manifiesto."""
    origen = config.rutas(tmp_path / "origen")
    Casillero(origen.casillero).cerrar()
    con = sqlite3.connect(origen.casillero)
    con.execute("CREATE TABLE relleno (x BLOB)")
    con.executemany("INSERT INTO relleno VALUES (?)", [(bytes(4000),)] * 300)
    con.commit()
    con.close()
    np.save(origen.tabla / "ONI.npy", np.arange(12, dtype="float32"))
    nombre, _ = empaquetar(origen)
    return nombre


def _api_con_cambios_sin_volcar(ruta):
    """Conexión como la de la API: modo WAL, con escrituras que aún no pasaron al archivo principal."""
    con = sqlite3.connect(ruta)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA wal_autocheckpoint=0")
    con.execute("CREATE TABLE IF NOT EXISTS resultados (llave TEXT, datos BLOB)")
    con.executemany("INSERT INTO resultados VALUES (?, ?)", [(str(i), bytes(4000)) for i in range(300)])
    con.commit()
    return con


def test_instalar_con_la_api_abierta_no_dana_el_casillero(paquete, tmp_path):
    destino = config.rutas(tmp_path / "destino")
    instalar(paquete, destino)
    api = _api_con_cambios_sin_volcar(destino.casillero)

    manifiesto = instalar(paquete, destino)  # reinstalar con la API corriendo
    api.close()  # al apagarse, la API vuelca su -wal

    assert _integridad(destino.casillero) == "ok"
    assert _sha(destino.casillero) == manifiesto["archivos"]["casillero.sqlite"]


def test_instalar_descarta_un_wal_viejo_de_una_api_cortada(paquete, tmp_path):
    destino = config.rutas(tmp_path / "destino")
    instalar(paquete, destino)
    api = _api_con_cambios_sin_volcar(destino.casillero)
    wal = destino.casillero.with_name("casillero.sqlite-wal")
    shm = destino.casillero.with_name("casillero.sqlite-shm")
    copia_wal, copia_shm = wal.read_bytes(), shm.read_bytes()
    api.close()
    wal.write_bytes(copia_wal)  # lo que deja una API cortada de golpe (kill -9)
    shm.write_bytes(copia_shm)

    manifiesto = instalar(paquete, destino)

    assert not wal.exists() and not shm.exists()
    assert _integridad(destino.casillero) == "ok"
    con = sqlite3.connect(destino.casillero)
    tablas = {f for (f,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert "resultados" not in tablas  # no se aplicó el -wal viejo
    assert _sha(destino.casillero) == manifiesto["archivos"]["casillero.sqlite"]


def test_instalar_rechaza_un_paquete_danado_sin_tocar_los_datos(paquete, tmp_path):
    destino = config.rutas(tmp_path / "destino")
    instalar(paquete, destino)
    antes = _sha(destino.casillero)
    danado = tmp_path / "danado.tar.gz"
    with tarfile.open(paquete) as tar, tarfile.open(danado, "w:gz") as nuevo:
        for m in tar.getmembers():
            datos = tar.extractfile(m).read()
            if m.name == "casillero.sqlite":  # contenido que no coincide con el manifiesto
                datos = b"X" * len(datos)
            nuevo.addfile(m, io.BytesIO(datos))

    with pytest.raises(RuntimeError, match="dañados"):
        instalar(danado, destino)
    assert _sha(destino.casillero) == antes  # lo instalado sigue intacto
    assert not list(destino.base.glob(".instalando-*"))  # no quedan restos
