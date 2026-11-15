"""Tendencia de una serie mensual de anomalías (informe estadístico, cálculos C4–C7).

Implementación única: la usan la ruta `analyze`, el job de ScanMap y el preparador.
Funciones puras: sin red, sin disco y sin FastAPI. Los umbrales salen solo de
`constantes.py`. Prohibidos aquí (sección 2 de la guía): Mann-Kendall original,
`scipy.stats.theilslopes` para el intervalo y `pymannkendall.seasonal_test`.
"""

from dataclasses import dataclass

import numpy as np
import pymannkendall as mk
from scipy.stats import norm

from app.estadistica.constantes import ALFA, ESCALA_DECADA, LAG_HAMED_RAO

# El cero de Celsius es arbitrario: la temperatura nunca lleva cambio porcentual.
_SIN_CAMBIO_PORCENTUAL = frozenset({"T2M"})


@dataclass(frozen=True)
class ResultadoTendencia:
    """Tendencia de una serie (cálculos C4–C7). El intervalo va en unidades por década."""

    pendiente_mes: float
    pendiente_decada: float
    ic_bajo: float
    ic_alto: float
    p: float
    var_s: float
    n: int
    intercepto: float


def _serie(y) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    if y.ndim != 1 or y.size < 3:
        raise ValueError("la serie debe ser un arreglo de al menos 3 meses")
    if not np.all(np.isfinite(y)):
        raise ValueError("la serie no puede tener faltantes: rellena los huecos antes")
    return y


def theil_sen(y) -> tuple[np.ndarray, float]:
    """Cálculo C4: pendientes entre todos los pares de meses, ordenadas, y su mediana.

    Se calcula a mano (`numpy.triu_indices`), no con `scipy.stats.theilslopes`.
    Supone meses consecutivos sin faltantes; la pendiente queda en unidades por mes.
    Aplica a las cinco variables.
    """
    y = _serie(y)
    t = np.arange(y.size)
    i, j = np.triu_indices(y.size, 1)
    pendientes = np.sort((y[j] - y[i]) / (t[j] - t[i]))
    return pendientes, float(np.median(pendientes))


def mann_kendall_hr(y, lag: int = LAG_HAMED_RAO) -> tuple[float, float, float, float]:
    """Cálculos C5–C6: Mann-Kendall con la varianza corregida de Hamed-Rao (12 rezagos).

    Devuelve `(S, Var′(S), Z, p)` con `Z = (S − sgn S)/√Var′(S)` y `p = 2·(1 − Φ(|Z|))`.
    La varianza usada es `max(var_s de Hamed-Rao, var0)`, con la varianza sin
    corregir `var0 = n(n−1)(2n+5)/18` (decisión L14): pymannkendall solo suma las
    autocorrelaciones significativas y a veces achicaba la varianza, con lo que la
    cobertura del IC caía a ~92–93 %. Así Hamed-Rao solo puede ensanchar el
    intervalo. Si `var_s` no es finita o es ≤ 0, se usa `var0`. Este cambio de
    método corresponde a `VERSION_METODO = 2`. Hamed-Rao solo corrige la varianza,
    no la pendiente. Aplica a las cinco variables (anomalías, sin ciclo estacional).
    """
    y = _serie(y)
    n = y.size
    var0 = n * (n - 1) * (2 * n + 5) / 18
    hr = mk.hamed_rao_modification_test(y, lag=lag)
    s = float(hr.s)
    var_s = float(hr.var_s)
    var_s = max(var_s, var0) if np.isfinite(var_s) and var_s > 0 else var0
    z = (s - np.sign(s)) / np.sqrt(var_s)
    p = 2 * norm.sf(abs(z))
    return s, float(var_s), float(z), float(p)


def tendencia(y, alfa: float = ALFA) -> ResultadoTendencia:
    """Cálculos C4–C7: Theil-Sen, Hamed-Rao e intervalo coherente con el p-valor.

    Intervalo (cálculo C7, corrección C8): `C = z₁₋α/₂·√Var′(S)` con **la misma**
    varianza que el p-valor, `max(Hamed-Rao, sin corregir)`: Hamed-Rao solo puede
    ensanchar el intervalo, nunca achicarlo (decisión L14, `VERSION_METODO = 2`).
    Va de la pendiente de orden `(N−C)/2` a la de orden
    `(N+C)/2 + 1` (rangos redondeados y acotados a `[1, N]`) sobre las N pendientes
    ordenadas. Así excluye el 0 si y solo si `p < alfa`. Pendiente e intervalo se
    expresan por década (`× ESCALA_DECADA`); el intercepto es `mediana(y − b·t)` con
    `t = 0` en el primer mes analizado. Aplica a las cinco variables.
    """
    y = _serie(y)
    pendientes, mediana = theil_sen(y)
    _, var_s, _, p = mann_kendall_hr(y)
    total = pendientes.size
    c = norm.ppf(1 - alfa / 2) * np.sqrt(var_s)
    bajo = pendientes[int(max(round((total - c) / 2) - 1, 0))]
    alto = pendientes[int(min(round((total + c) / 2), total - 1))]
    intercepto = float(np.median(y - mediana * np.arange(y.size)))
    return ResultadoTendencia(
        pendiente_mes=mediana,
        pendiente_decada=mediana * ESCALA_DECADA,
        ic_bajo=float(bajo * ESCALA_DECADA),
        ic_alto=float(alto * ESCALA_DECADA),
        p=p,
        var_s=var_s,
        n=int(y.size),
        intercepto=intercepto,
    )


def cambio_total(pendiente_mes: float, n: int) -> float:
    """Cambio acumulado en la ventana analizada: `pendiente_por_mes × (n − 1)` (cálculo C4).

    Va en la unidad de la variable. Aplica a las cinco variables.
    """
    return float(pendiente_mes) * (int(n) - 1)


def cambio_pct_decada(pendiente_decada: float, referencia: float, variable: str) -> float | None:
    """Cambio porcentual por década: `100 × pendiente_decada / referencia` (cálculo C4).

    Solo para variables con cero natural y promedio positivo (lluvia y humedades);
    en temperatura (`T2M`) devuelve `None`. `referencia` la pasa quien llama: la guía
    la describe como la climatología (promedio) de la celda en la ventana. Si la
    referencia no es positiva o no es finita, devuelve `None`.
    """
    if variable in _SIN_CAMBIO_PORCENTUAL:
        return None
    referencia = float(referencia)
    if not (np.isfinite(referencia) and referencia > 0):
        return None
    return 100.0 * float(pendiente_decada) / referencia


def recta(resultado: ResultadoTendencia, n_total: int, inicio: int) -> list[float | None]:
    """Recta de Theil-Sen para el gráfico (cálculo C4), del largo de `fechas`.

    La tendencia se calcula sobre los meses analizados (desde el rezago `inicio`);
    los primeros `inicio` valores son `None`. Aplica a las cinco variables.
    """
    if inicio < 0 or n_total - inicio != resultado.n:
        raise ValueError("n_total − inicio debe ser igual a los meses analizados")
    t = np.arange(resultado.n)
    valores = resultado.intercepto + resultado.pendiente_mes * t
    return [None] * inicio + [float(v) for v in valores]
