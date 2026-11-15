// Generado por `npm run fixtures:copiar` desde backend/app/catalogo/variables.json. No editar a mano.
import type { VariablesRespuesta } from '../tipos';

const fixture: VariablesRespuesta = {
  "variables": [
    {
      "id": "PRECTOTCORR",
      "nombre": "Lluvia",
      "definicion": "Precipitación que llega a la superficie, como promedio mensual.",
      "unidad": "mm/día",
      "fuente": "MERRA-2 vía NASA POWER"
    },
    {
      "id": "T2M",
      "nombre": "Temperatura del aire a 2 m",
      "definicion": "Temperatura del aire a dos metros sobre la superficie; no se expresa como cambio porcentual.",
      "unidad": "°C",
      "fuente": "MERRA-2 vía NASA POWER"
    },
    {
      "id": "GWETROOT",
      "nombre": "Humedad del suelo, zona de raíces",
      "definicion": "Agua disponible para las raíces en los primeros 100 cm de suelo, entre 0 y 1. No se interpreta sobre el mar.",
      "unidad": "0 a 1",
      "fuente": "MERRA-2 vía NASA POWER"
    },
    {
      "id": "GWETTOP",
      "nombre": "Humedad del suelo, superficie",
      "definicion": "Humedad de los primeros centímetros de suelo, entre 0 y 1. No se interpreta sobre el mar.",
      "unidad": "0 a 1",
      "fuente": "MERRA-2 vía NASA POWER"
    },
    {
      "id": "RH2M",
      "nombre": "Humedad relativa a 2 m",
      "definicion": "Vapor de agua del aire frente al máximo posible a esa temperatura, entre 0 y 100 %.",
      "unidad": "%",
      "fuente": "MERRA-2 vía NASA POWER"
    }
  ],
  "indices": [
    {
      "id": "ONI",
      "nombre": "Índice Oceánico de El Niño",
      "definicion": "Anomalía de temperatura en Niño 3.4, promediada en tres meses y asignada al mes central.",
      "unidad": "°C",
      "fuente": "ONI, NOAA CPC"
    },
    {
      "id": "NINO12",
      "nombre": "Niño 1+2",
      "definicion": "Anomalía mensual frente a la costa de Perú y Ecuador, disponible desde 1982.",
      "unidad": "°C",
      "fuente": "Niño 1+2, NOAA CPC"
    }
  ]
};

export default fixture;
