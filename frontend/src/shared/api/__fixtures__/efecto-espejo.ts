// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/simulado/efecto-espejo.json. No editar a mano.
import type { DemoRespuesta } from '../tipos';

const fixture: DemoRespuesta = {
  "id": "efecto-espejo",
  "titulo": "El efecto espejo de El Niño",
  "variable": "PRECTOTCORR",
  "celda": {
    "lat": -6,
    "lon": -80
  },
  "pasos": [
    {
      "n": 1,
      "texto": "Piura, en la costa norte del Perú, recibe más lluvia durante El Niño.",
      "acciones": [
        {
          "tipo": "seleccionar_variable",
          "variable": "PRECTOTCORR"
        },
        {
          "tipo": "seleccionar_celda",
          "lat": -6,
          "lon": -80
        },
        {
          "tipo": "quitar_el_nino",
          "valor": false
        }
      ]
    },
    {
      "n": 2,
      "texto": "La lluvia en Piura y la sequía en el norte de Australia ocurren a la vez; ambas responden a El Niño, no significa que un lugar cause lo que sucede en el otro.",
      "acciones": [
        {
          "tipo": "ir_al_mes",
          "fecha": "1998-01"
        },
        {
          "tipo": "reproducir"
        }
      ]
    },
    {
      "n": 3,
      "texto": "Observa el destino opuesto y compara con Piura.",
      "acciones": [
        {
          "tipo": "detener"
        },
        {
          "tipo": "ir_a_destino",
          "lat": -14,
          "lon": 132
        }
      ]
    }
  ]
};

export default fixture;
