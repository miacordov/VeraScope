"""Tendencia de una serie mensual de anomalías (informe estadístico, cálculos C4–C7).

Implementación única: la usan la ruta `analyze`, el job de ScanMap y el preparador.
Funciones puras: sin red, sin disco y sin FastAPI. Los umbrales salen solo de
`constantes.py`. Prohibidos aquí (sección 2 de la guía): Mann-Kendall original
(sin corregir la autocorrelación), `scipy.stats.theilslopes` para el intervalo y
`pymannkendall.seasonal_test`.
"""

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from app.estadistica.constantes import ALFA, ESCALA_DECADA, RHO_MAX_AR1

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


def rho_ar1(y, pendiente_mes: float | None = None) -> float:
    """Autocorrelación de rezago 1 de los residuos de Theil-Sen, insumo del cálculo C5.

    `ρ̂` es la autocorrelación de `y − b·t` (b = pendiente de Theil-Sen por mes), con la
    corrección de sesgo de Marriott-Pope `ρ̂ + (1 + 4ρ̂)/n`: con 120–240 meses, `ρ̂` sin
    corregir sale bajo y el intervalo queda estrecho. Se acota a `[0, RHO_MAX_AR1]`:
    nunca achica la varianza y no explota cerca de la raíz unitaria. Si ya se calculó
    la pendiente, pasarla en `pendiente_mes` evita repetir Theil-Sen.
    """
    y = _serie(y)
    if pendiente_mes is None:
        _, pendiente_mes = theil_sen(y)
    e = y - pendiente_mes * np.arange(y.size)
    e = e - e.mean()
    denominador = float((e * e).sum())
    if denominador <= 0:
        return 0.0
    rho = float((e[:-1] * e[1:]).sum()) / denominador
    rho = rho + (1 + 4 * rho) / y.size
    return float(min(max(rho, 0.0), RHO_MAX_AR1))


def mann_kendall_corregido(
    y, pendiente_mes: float | None = None
) -> tuple[float, float, float, float]:
    """Cálculos C5–C6: Mann-Kendall con la varianza corregida por autocorrelación AR(1).

    `S = Σ sgn(y_j − y_i)` sobre todos los pares `i < j`. La varianza sin corregir es
    `var0 = n(n−1)(2n+5)/18` y la corregida `Var′(S) = var0·(1 + ρ)/(1 − ρ)`, con
    `ρ = rho_ar1(y)`. Devuelve `(S, Var′(S), Z, p)` con `Z = (S − sgn S)/√Var′(S)` y
    `p = 2·(1 − Φ(|Z|))`.

    Reemplaza a Hamed-Rao de pymannkendall (`VERSION_METODO = 3`): ese solo suma las
    autocorrelaciones "significativas" y corregía de menos con ruido AR(1) (≈ 1,63×
    frente a ≈ 1,86× real con ρ = 0,3), así que el IC de 95 % cubría solo el 92–93 %.
    Con esta varianza cubre el 95 % (guía §13). Corrige solo la varianza, no la
    pendiente. Aplica a las cinco variables (anomalías, sin ciclo estacional).
    """
    y = _serie(y)
    n = y.size
    i, j = np.triu_indices(n, 1)
    s = float(np.sign(y[j] - y[i]).sum())
    rho = rho_ar1(y, pendiente_mes)
    var_s = n * (n - 1) * (2 * n + 5) / 18 * (1 + rho) / (1 - rho)
    z = (s - np.sign(s)) / np.sqrt(var_s)
    p = 2 * norm.sf(abs(z))
    return s, float(var_s), float(z), float(p)


def tendencia(y, alfa: float = ALFA) -> ResultadoTendencia:
    """Cálculos C4–C7: Theil-Sen, Mann-Kendall corregido e intervalo coherente con el p.

    Intervalo (cálculo C7, corrección C8): `C = z₁₋α/₂·√Var′(S)` con **la misma**
    varianza corregida que el p-valor (`mann_kendall_corregido`). Va de la pendiente
    de orden `(N−C)/2` a la de orden `(N+C)/2 + 1` (rangos redondeados y acotados a
    `[1, N]`) sobre las N pendientes ordenadas. Así excluye el 0 si y solo si
    `p < alfa`. Pendiente e intervalo se expresan por década (`× ESCALA_DECADA`); el
    intercepto es `mediana(y − b·t)` con `t = 0` en el primer mes analizado. Aplica a
    las cinco variables.
    """
    y = _serie(y)
    pendientes, mediana = theil_sen(y)
    _, var_s, _, p = mann_kendall_corregido(y, mediana)
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
