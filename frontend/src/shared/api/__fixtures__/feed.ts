// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/simulado/feed.json. No editar a mano.
import type { FeedRespuesta } from '../tipos';

const fixture: FeedRespuesta = {
  "tipo": "fuertes",
  "pagina": 0,
  "por_pagina": 20,
  "total": 1,
  "escaneo": {
    "estado": "completo",
    "celdas_listas": 2,
    "celdas_total": 2
  },
  "tarjetas": [
    {
      "id": "PRECTOTCORR-0",
      "titular": "La lluvia en Piura no muestra tendencia significativa",
      "variable": "PRECTOTCORR",
      "unidad": "mm/día",
      "celda": {
        "lat": -6,
        "lon": -80
      },
      "veredicto": "sin_tendencia",
      "pendiente_decada": -0.008,
      "ic_bajo": -0.05,
      "ic_alto": 0.03,
      "p_ajustado": 0.72,
      "efecto": -0.01,
      "pareja": null
    }
  ]
};

export default fixture;
