#!/usr/bin/env bash
# Arranque en Render: instala los datos desde el paquete y levanta uvicorn.
set -euo pipefail

cd "$(dirname "$0")/.."

# Instalar datos si no existen aún (Render no tiene disco persistente en el plan gratuito).
if [ ! -f "data/casillero.sqlite" ]; then
  echo "[render] Instalando datos desde paquete..."
  verascope-datos instalar paquete-datos/verascope-datos-20261115.tar.gz
  echo "[render] Datos instalados."
else
  echo "[render] Datos ya presentes, saltando instalación."
fi

# Puerto que asigna Render (default 10000).
PORT="${PORT:-10000}"
echo "[render] Iniciando uvicorn en puerto $PORT"

exec python -m uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
