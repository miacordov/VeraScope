"""Motor estadístico (informe estadístico, cálculos C2–C14). Es el mismo que usa la API en vivo."""
import numpy as np
import pymannkendall as mk
from scipy.stats import false_discovery_control, norm, t as tdist

ALFA = 0.05
MIN_MESES = 120


def anomalias(valores, meses_calendario):
    v = np.asarray(valores, float); m = np.asarray(meses_calendario)
    out = np.full_like(v, np.nan)
    for k in range(1, 13):
        s = m == k
        if s.any():
            out[s] = v[s] - np.nanmean(v[s])
    return out


def rellenar_huecos(y, max_hueco=2, max_faltante=0.10):
    y = np.asarray(y, float).copy(); malo = np.isnan(y)
    if not malo.any():
        return y
    if malo.mean() > max_faltante:
        return None
    racha = 0
    for b in malo:
        racha = racha + 1 if b else 0
        if racha > max_hueco:
            return None
    i = np.arange(y.size); y[malo] = np.interp(i[malo], i[~malo], y[~malo])
    return y


def tendencia(y, alfa=ALFA, lag=12):
    """C4–C7: Theil-Sen + Mann-Kendall Hamed-Rao + intervalo con la misma varianza corregida."""
    y = np.asarray(y, float); n = len(y); t = np.arange(n)
    hr = mk.hamed_rao_modification_test(y, lag=lag)
    i, j = np.triu_indices(n, 1)
    b = np.sort((y[j] - y[i]) / (t[j] - t[i])); N = b.size
    var0 = n * (n - 1) * (2 * n + 5) / 18
    var = hr.var_s if np.isfinite(hr.var_s) and hr.var_s > 0 else var0
    z = (hr.s - np.sign(hr.s)) / np.sqrt(var); p = 2 * norm.sf(abs(z))
    C = norm.ppf(1 - alfa / 2) * np.sqrt(var)
    lo = b[int(max(round((N - C) / 2) - 1, 0))]; hi = b[int(min(round((N + C) / 2), N - 1))]
    return {"pendiente_dec": float(np.median(b) * 120), "ic": (float(lo * 120), float(hi * 120)), "p": float(p)}


def r1(x):
    x = np.asarray(x, float); return float(np.corrcoef(x[:-1], x[1:])[0, 1])


def p_correlacion(r, r1x, r1y, n):
    rr = np.asarray(r1x) * np.asarray(r1y)
    ne = np.clip(n * (1 - rr) / (1 + rr), 3, n)
    tt = np.asarray(r) * np.sqrt((ne - 2) / np.maximum(1 - np.asarray(r) ** 2, 1e-12))
    return 2 * tdist.sf(np.abs(tt), ne - 2)


def quitar_enso(a, indice, max_rezago=6):
    """C9–C11: rezago de mayor |r|, regresión conjunta tendencia + índice, serie sin El Niño."""
    a = np.asarray(a, float); e = np.asarray(indice, float); n = len(a); mejor = None
    for L in range(max_rezago + 1):
        r = np.corrcoef(e[: n - L], a[L:])[0, 1]
        if mejor is None or abs(r) > abs(mejor[1]):
            mejor = (L, r)
    L, r = mejor
    ee, y, t = e[: n - L], a[L:], np.arange(n - L)
    X = np.column_stack([np.ones_like(t), t, ee - ee.mean()])
    g = np.linalg.lstsq(X, y, rcond=None)[0][2]
    return {"limpia": y - g * (ee - ee.mean()), "rezago": int(L), "r": float(r),
            "p_r": float(p_correlacion(r, r1(ee), r1(y), len(y))), "colinealidad": float(np.corrcoef(ee, t)[0, 1])}


def veredicto(sig_original, sig_limpia):
    if sig_original and sig_limpia:
        return "cambio_robusto"
    if sig_original:
        return "sensible_a_el_nino"
    if sig_limpia:
        return "cambio_oculto"
    return "sin_tendencia"


def fdr(p):
    p = np.asarray(p, float); adj = np.full(p.size, np.nan); ok = np.isfinite(p)
    if ok.any():
        adj[ok] = false_discovery_control(p[ok], method="bh")
    return adj


def analizar(valores, oni, meses_calendario):
    """Una celda y una variable: devuelve el diccionario de resultados o None si la serie no sirve."""
    a = rellenar_huecos(anomalias(valores, meses_calendario))
    if a is None or a.size < MIN_MESES or np.nanstd(a) == 0:
        return None
    o = tendencia(a); en = quitar_enso(a, oni); l = tendencia(en["limpia"])
    return {"pendiente_original": o["pendiente_dec"], "p_original": o["p"],
            "pendiente": l["pendiente_dec"], "ic_bajo": l["ic"][0], "ic_alto": l["ic"][1], "p": l["p"],
            "rezago": en["rezago"], "r_enso": en["r"], "p_enso": en["p_r"], "colinealidad": en["colinealidad"],
            "efecto": l["pendiente_dec"] / float(np.std(a)), "meses": int(a.size)}
