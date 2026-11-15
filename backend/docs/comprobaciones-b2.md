# Comprobaciones de B2 contra NASA POWER (S0)

Consultas reales al endpoint mensual por punto (`/api/temporal/monthly/point`, `community=AG`).

| Comprobación | Resultado | Fecha | Estado |
|---|---|---|---|
| Último año completo de MERRA-2 | 2025 completo (con mes `13`); 2026 llega hasta septiembre y octubre–noviembre vienen en `-999`. `VERASCOPE_FIN=2025` (valor por defecto) | 2026-11-14 | ✅ Verificado |
| `PRECTOTCORR` mensual en mm/día | `parameters.PRECTOTCORR.units = "mm/day"` en (-5.0, -80.5), 2024–2025 | 2026-11-14 | ✅ Verificado |
| Aparece el mes `"13"` | Las llaves llegan hasta `202513` (promedio anual, 0.7 mm/día en 2025 frente a 0.02 de diciembre). El cliente debe ignorarlo | 2026-11-14 | ✅ Verificado |
| Celda oceánica → `-999` en `GWETROOT` | En (0.0, -120.0), 2024: `GWETROOT` solo `-999`; `GWETTOP` llega en `1.0` constante (no `-999`). La regla de desviación nula es la que descarta `GWETTOP` sobre el mar | 2026-11-14 | ✅ Verificado |
| `0.5·round(x/0.5)` cae en la misma celda que POWER | Latitud: sí (celdas de 0.5° centradas en múltiplos de 0.5). Longitud: **no**; POWER usa la malla nativa de MERRA-2 de 0.625° (centros en −180 + k·0.625): −77.0 y −76.6 devuelven la misma serie y −76.5 la de la vecina | 2026-11-14 | ✅ Verificado · decisión abajo |
| Prueba rápida del panel (índices NOAA + 3 demos POWER) | Sin registro. Abrir `verascope_datos/abrir-panel.sh` (o `Abrir-panel.bat`) y correr **Prueba rápida**; anotar aquí el resultado | — | ⏳ Pendiente |
| Latencia desde la sede | Medida solo desde la laptop (`latencia-power.md`). Repetir con 20 celdas desde la sede | — | ⏳ Pendiente |

## Decisión: malla de 0.5° en longitud

**Se mantiene la celda de 0.5° (regla C3) y se declara la diferencia.** No cambia el contrato,
ni `celdas.py`, ni la rejilla de 4235 celdas, ni las llaves del casillero.

Consecuencias que hay que declarar:

- En longitud, el dato de POWER cubre 0.625°, así que el rectángulo de 0.5° que dibuja la app
  no es la huella exacta del dato.
- Dos celdas vecinas de 0.5° pueden traer la misma serie de POWER.
- Debe aparecer en el glosario o en la ficha de fuente («MERRA-2 vía NASA POWER, malla nativa
  0.5° × 0.625°»).
