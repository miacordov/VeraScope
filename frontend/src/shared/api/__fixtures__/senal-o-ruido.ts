// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/simulado/senal-o-ruido.json. No editar a mano.
import type { DemoRespuesta } from '../tipos';

const fixture: DemoRespuesta = {
  "id": "senal-o-ruido",
  "titulo": "Señal o ruido (simulado)",
  "variable": "T2M",
  "celda": {
    "lat": -6,
    "lon": -80
  },
  "pasos": [
    {
      "n": 1,
      "texto": "Recorrido de desarrollo con datos simulados: esta celda no es la selección definitiva de la demo real. Compara primero diez años.",
      "acciones": [
        {
          "tipo": "seleccionar_variable",
          "variable": "T2M"
        },
        {
          "tipo": "seleccionar_celda",
          "lat": -6,
          "lon": -80
        },
        {
          "tipo": "fijar_ventana",
          "inicio": 1981,
          "fin": 1990
        }
      ]
    },
    {
      "n": 2,
      "texto": "Quita la parte asociada a El Niño. La tendencia restante no demuestra por sí sola una causa.",
      "acciones": [
        {
          "tipo": "quitar_el_nino",
          "valor": true
        },
        {
          "tipo": "mostrar_periodos"
        }
      ]
    }
  ]
};

export default fixture;
