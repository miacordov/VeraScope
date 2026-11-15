"""Veredicto de cuatro estados, dirección y avisos (cálculos C12 y C13).

Funciones puras: reciben escalares o arreglos (sirven para miles de celdas a la vez),
sin red, sin disco y sin FastAPI. Los valores de texto son exactamente los del
contrato (`EstadoVeredicto`, `Direccion`, `CodigoAviso`); una prueba lo comprueba.
"""

import numpy as np

from app.estadistica.constantes import (
    ALFA,
    AVISO_POTENCIA_MESES,
    COLINEALIDAD_MAX,
    NEFF_MIN_PRUEBA_T,
)

CAMBIO_ROBUSTO = "cambio_robusto"
SENSIBLE_A_EL_NINO = "sensible_a_el_nino"
CAMBIO_OCULTO = "cambio_oculto"
SIN_TENDENCIA = "sin_tendencia"
ESTADOS = (CAMBIO_ROBUSTO, SENSIBLE_A_EL_NINO, CAMBIO_OCULTO, SIN_TENDENCIA)

SUBE = "sube"
BAJA = "baja"
PLANA = "plana"

AVISO_COLINEALIDAD = "colinealidad"
AVISO_POTENCIA = "potencia_baja"
AVISO_MUESTRA = "muestra_efectiva_baja"


def _salida(resultado: np.ndarray):
    # Un escalar de entrada devuelve un escalar de Python; un arreglo, un arreglo.
    return resultado.item() if resultado.ndim == 0 else resultado


def significativa(p, alfa: float = ALFA):
    """Cálculo C13: la tendencia es significativa si `p < alfa`.

    Con celdas de ScanMap se le pasa el p ajustado por BH (cálculo C14). Un p NaN
    (sin dato) nunca es significativo. Escalar → bool; arreglo → arreglo de bool.
    """
    p = np.asarray(p, dtype=float)
    with np.errstate(invalid="ignore"):
        return _salida(np.isfinite(p) & (p < alfa))


def estado(sig_original, sig_sin_el_nino):
    """Cálculo C13: veredicto de cuatro estados a partir de las dos significancias.

    Ambas → `cambio_robusto`; solo la original → `sensible_a_el_nino`; solo la sin
    El Niño → `cambio_oculto`; ninguna → `sin_tendencia` (un hallazgo válido).
    Escalar → str; arreglo → arreglo de str.
    """
    orig = np.asarray(sig_original, dtype=bool)
    sin = np.asarray(sig_sin_el_nino, dtype=bool)
    resultado = np.select(
        [orig & sin, orig, sin],
        [CAMBIO_ROBUSTO, SENSIBLE_A_EL_NINO, CAMBIO_OCULTO],
        SIN_TENDENCIA,
    )
    return _salida(resultado)


def direccion(pendiente, es_significativa):
    """Cálculo C13 (corrección C9): dirección según el signo de la pendiente.

    Para el veredicto se usa la pendiente de la serie sin El Niño. Si la tendencia
    no es significativa, o la pendiente es cero o falta, la dirección es `plana`.
    Escalar → str; arreglo → arreglo de str.
    """
    pendiente = np.asarray(pendiente, dtype=float)
    sig = np.asarray(es_significativa, dtype=bool)
    with np.errstate(invalid="ignore"):
        resultado = np.select([sig & (pendiente > 0), sig & (pendiente < 0)], [SUBE, BAJA], PLANA)
    return _salida(resultado)


def _menor(valor, limite) -> bool:
    return valor is not None and bool(np.isfinite(valor)) and valor < limite


def avisos(meses_analizados, colinealidad, n_efectivo) -> list[tuple[str, str]]:
    """Cálculo C12: avisos con regla numérica, como (código, texto en español sencillo).

    - `colinealidad` si |corr(índice rezagado, tiempo)| > COLINEALIDAD_MAX.
    - `potencia_baja` si hay menos de AVISO_POTENCIA_MESES meses analizados.
    - `muestra_efectiva_baja` si el tamaño efectivo es menor que NEFF_MIN_PRUEBA_T.
    Un valor ausente (None o NaN) no genera aviso. `respuesta_no_lineal`,
    `nino_costero` y `fuera_de_rejilla` no salen de aquí (L13). Una celda por llamada.
    """
    lista = []
    if colinealidad is not None and np.isfinite(colinealidad):
        if abs(colinealidad) > COLINEALIDAD_MAX:
            lista.append(
                (
                    AVISO_COLINEALIDAD,
                    "En esta ventana, El Niño y el paso del tiempo avanzan de forma "
                    "parecida, así que separar la tendencia de El Niño es menos seguro.",
                )
            )
    if _menor(meses_analizados, AVISO_POTENCIA_MESES):
        anios = AVISO_POTENCIA_MESES // 12
        lista.append(
            (
                AVISO_POTENCIA,
                f"Se analizan menos de {anios} años. Con pocos años cuesta ver una "
                "tendencia: si no aparece, puede existir y no alcanzar a notarse.",
            )
        )
    if _menor(n_efectivo, NEFF_MIN_PRUEBA_T):
        lista.append(
            (
                AVISO_MUESTRA,
                "Los meses se parecen mucho a sus vecinos y equivalen a menos de "
                f"{NEFF_MIN_PRUEBA_T} datos independientes; el vínculo con El Niño "
                "es poco confiable.",
            )
        )
    return lista
