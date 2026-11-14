#!/usr/bin/env bash
# Doble clic en Mac (o ./abrir-panel.sh en Linux): prepara el programa la primera vez y abre el panel.
cd "$(dirname "$0")" || exit 1
VERSION="1.1.0"
fallo() { echo; echo "  Algo falló durante la instalación. Copia el texto de arriba y mándaselo a quien te ayuda."; read -r -p "  Pulsa Enter para cerrar"; exit 1; }

echo; echo "  VeraScope · Centro de datos"; echo
PY=""
for c in python3 python; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "  No encuentro Python 3.10 o más nuevo."
  echo "  Instálalo desde https://www.python.org/downloads/ y vuelve a abrir este archivo."
  read -r -p "  Pulsa Enter para cerrar"; exit 1
fi
if [ ! -x .venv/bin/python ]; then
  echo "  Primera vez: preparando el programa. Puede tardar unos minutos…"
  "$PY" -m venv .venv || fallo
fi
if [ ! -f ".venv/.listo-$VERSION" ]; then
  echo "  Instalando las piezas necesarias. Hace falta internet…"
  .venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1
  .venv/bin/python -m pip install -e . || fallo
  touch ".venv/.listo-$VERSION"
fi
# Dentro del repo VeraScope, los datos van a backend/data (la misma carpeta que lee la API).
if [ -z "${VERASCOPE_DATOS:-}" ] && [ -d ../data ]; then
  VERASCOPE_DATOS="$(cd ../data && pwd)"; export VERASCOPE_DATOS
fi
echo "  Abriendo el panel en tu navegador."
echo "  NO cierres esta ventana mientras uses el panel."; echo
.venv/bin/python -m verascope_datos panel
echo; echo "  El panel se cerró. Puedes cerrar esta ventana."
