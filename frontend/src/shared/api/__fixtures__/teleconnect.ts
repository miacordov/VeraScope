// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/simulado/teleconnect.json. No editar a mano.
import type { TeleconnectRespuesta } from '../tipos';

const fixture: TeleconnectRespuesta = {
  "variable": "PRECTOTCORR",
  "origen": {
    "lat": -6,
    "lon": -80,
    "distancia_a_clic_km": 120,
    "r_el_nino": 0.62
  },
  "lineas": [
    {
      "tipo": "opuesto",
      "lat": -18,
      "lon": 142,
      "r": -0.8,
      "p_ajustado": 0.000001,
      "distancia_km": 14800,
      "r_el_nino_origen": 0.62,
      "r_el_nino_destino": -0.55,
      "meses_coincidencia": [
        {
          "fecha": "1990-01",
          "fase": "nino"
        }
      ]
    }
  ],
  "mensaje_vacio": null
};

export default fixture;
