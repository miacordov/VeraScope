"""V8 GPM IMERG y V9–V11 GLDAS: archivos binarios (HDF5 / NetCDF4) de GES DISC.

No se descargan archivos globales completos: `earthaccess.open` los abre en la nube y `xarray`
lee solo los bloques de la región pedida. Requiere una cuenta gratuita de NASA Earthdata
(variables EARTHDATA_USERNAME y EARTHDATA_PASSWORD, o un archivo ~/.netrc).
"""
import numpy as np
import xarray as xr

from .region import anio_mes, promedio_caja

IMERG = {"short_name": "GPM_3IMERGM", "version": "07", "grupo": "Grid"}
GLDAS = {"short_name": "GLDAS_NOAH025_M", "version": "2.1", "grupo": None}


def iniciar_sesion():
    import earthaccess
    # Sin preguntas interactivas: así también funciona cuando lo lanza el panel visual.
    for estrategia in ("environment", "netrc"):
        try:
            auth = earthaccess.login(strategy=estrategia, persist=False)
        except Exception:
            continue
        if auth and getattr(auth, "authenticated", False):
            return auth
    raise RuntimeError("No se pudo iniciar sesión en NASA Earthdata. Revisa tu usuario y contraseña "
                       "(en el panel: botón «Mi cuenta de NASA»; en la terminal: EARTHDATA_USERNAME y "
                       "EARTHDATA_PASSWORD, o ~/.netrc).")


def buscar_y_abrir(producto, anio_inicio, anio_fin, lugares):
    import earthaccess
    lats = [l.lat for l in lugares]; lons = [l.lon for l in lugares]
    caja = (min(lons) - 1, min(lats) - 1, max(lons) + 1, max(lats) + 1)
    if caja[2] - caja[0] > 180:          # los lugares cruzan el antimeridiano: caja global en longitud
        caja = (-180, caja[1], 180, caja[3])
    gr = earthaccess.search_data(short_name=producto["short_name"], version=producto["version"],
                                 temporal=(f"{anio_inicio}-01-01", f"{anio_fin}-12-31"), bounding_box=caja)
    if not gr:
        raise RuntimeError(f"No se encontraron archivos de {producto['short_name']} para {anio_inicio}-{anio_fin}")
    return earthaccess.open(gr)


def _mes(ds):
    return anio_mes(np.asarray(ds["time"].values).ravel()[0])


def _abrir(f, grupo):
    kw = {"engine": "h5netcdf"}
    if grupo:
        kw["group"] = grupo
    return xr.open_dataset(f, **kw)


def extraer_imerg(archivos, lugares, avance=None):
    """-> {lugar.id: {AAAA-MM: mm/día}}"""
    out = {l.id: {} for l in lugares}
    for f in archivos:
        with _abrir(f, IMERG["grupo"]) as ds:
            mes = _mes(ds)
            da = ds["precipitation"].isel(time=0)
            for l in lugares:
                out[l.id][mes] = promedio_caja(da, l) * 24.0       # mm/h -> mm/día
        if avance:
            avance()
    return out


def extraer_gldas(archivos, lugares, avance=None):
    """-> {codigo: {lugar.id: {AAAA-MM: valor}}} para evapotranspiración, escorrentía y suelo 0–10 cm."""
    out = {c: {l.id: {} for l in lugares} for c in ("GLDAS_EVAP", "GLDAS_ESCORRENTIA", "GLDAS_SUELO")}
    for f in archivos:
        with _abrir(f, GLDAS["grupo"]) as ds:
            mes = _mes(ds)
            ev = ds["Evap_tavg"].isel(time=0)
            qs = ds["Qs_acc"].isel(time=0) + ds["Qsb_acc"].isel(time=0)
            sm = ds["SoilMoi0_10cm_inst"].isel(time=0)
            for l in lugares:
                out["GLDAS_EVAP"][l.id][mes] = promedio_caja(ev, l) * 86400.0   # kg m-2 s-1 -> mm/día
                out["GLDAS_ESCORRENTIA"][l.id][mes] = promedio_caja(qs, l) * 8.0  # acumulado de 3 h -> mm/día
                out["GLDAS_SUELO"][l.id][mes] = promedio_caja(sm, l)             # kg m-2 = mm
        if avance:
            avance()
    return out
