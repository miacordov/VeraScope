// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/glosario.json. No editar a mano.
import type { GlosarioRespuesta } from '../tipos';

const fixture: GlosarioRespuesta = {
  "terminos": [
    {
      "termino": "Tendencia",
      "definicion": "Cambio sostenido de una serie a lo largo del tiempo, distinto del ruido entre meses."
    },
    {
      "termino": "Sin El Niño",
      "definicion": "Serie tras quitar la parte asociada al índice en un ajuste conjunto con el tiempo. No atribuye causas al cambio restante."
    },
    {
      "termino": "Fase mensual",
      "definicion": "Se etiqueta El Niño con índice de al menos 0.5, La Niña con índice de hasta -0.5 y neutro entre ambos. Es una simplificación: NOAA exige cinco estaciones seguidas."
    },
    {
      "termino": "Teleconexión",
      "definicion": "Dos lugares varían a la vez y ambos responden a El Niño; no significa que uno cause el cambio del otro."
    },
    {
      "termino": "Sin tendencia detectable",
      "definicion": "No se detecta una tendencia con estos datos y este método. Es un resultado válido, no un error."
    }
  ]
};

export default fixture;
