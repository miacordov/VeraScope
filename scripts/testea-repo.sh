#!/usr/bin/env bash
# Testea todo el repositorio: backend, preparador de datos, frontend y la conexión entre ellos.
# Corre lo mismo que el CI (backend.yml, preparador-datos.yml, frontend.yml) y además levanta la
# API simulada para comprobar que sirve lo que la app espera y que esquema.ts está al día.
#
# Uso (desde cualquier carpeta del repo):
#   scripts/testea-repo.sh            # todo
#   scripts/testea-repo.sh --rapido   # sin `expo export -p web` ni el esquema OpenAPI (los más lentos)
#
# Sale con 0 si todo pasa y con 1 si algo falla. Sigue aunque un paso falle, para ver el cuadro completo.
# Usa backend/.venv (lo crea o lo completa con las dependencias de prueba si hace falta) y
# frontend/node_modules (corre `npm ci` si falta o si cambió package-lock.json).

set -uo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$RAIZ/backend"
FRONTEND="$RAIZ/frontend"
VENV="$BACKEND/.venv"
PY="$VENV/bin/python"
RAPIDO=0
[[ "${1:-}" == "--rapido" ]] && RAPIDO=1

TMP="$(mktemp -d)"
API_PID=""
limpiar() {
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null && wait "$API_PID" 2>/dev/null
  rm -rf "$TMP"
}
trap limpiar EXIT

RESULTADOS=()
FALLOS=0
INICIO_TOTAL=$SECONDS

# paso "nombre" comando…  → corre en silencio, guarda la salida y muestra solo el final si falla.
paso() {
  local nombre="$1"; shift
  local log="$TMP/paso-${#RESULTADOS[@]}.log" inicio=$SECONDS
  printf '▶ %s… ' "$nombre"
  if "$@" >"$log" 2>&1; then
    printf 'ok (%ss)\n' $((SECONDS - inicio))
    RESULTADOS+=("ok     $nombre")
  else
    printf 'FALLA (%ss)\n' $((SECONDS - inicio))
    sed 's/^/    │ /' "$log" | tail -n 40
    RESULTADOS+=("FALLA  $nombre")
    FALLOS=$((FALLOS + 1))
  fi
}

omitir() {
  printf '▷ %s: omitido (%s)\n' "$1" "$2"
  RESULTADOS+=("omit.  $1 — $2")
}

# ── Preparación ────────────────────────────────────────────────────────────────

preparar_venv() {
  local huella marca="$VENV/.testea-repo"
  local suma="sha256sum"
  command -v sha256sum >/dev/null || suma="shasum -a 256"  # macOS
  huella="$(cat "$BACKEND/pyproject.toml" "$BACKEND/verascope_datos/pyproject.toml" | $suma | cut -d' ' -f1)"
  [[ -x "$PY" && -f "$marca" && "$(cat "$marca")" == "$huella" ]] && return 0
  if [[ ! -x "$PY" ]]; then
    if command -v uv >/dev/null; then
      uv venv --python 3.11 "$VENV" || return 1
    else
      local candidato
      for candidato in python3.11 python3 python; do
        command -v "$candidato" >/dev/null && "$candidato" -c 'import sys; sys.exit(sys.version_info < (3, 11))' \
          && "$candidato" -m venv "$VENV" && break
      done
      [[ -x "$PY" ]] || { echo "Hace falta Python 3.11 o superior."; return 1; }
    fi
  fi
  if command -v uv >/dev/null; then
    uv pip install --python "$PY" -e "$BACKEND[dev]" -e "$BACKEND/verascope_datos[pruebas]" || return 1
  else
    "$PY" -m pip install --disable-pip-version-check -q -e "$BACKEND[dev]" \
      -e "$BACKEND/verascope_datos[pruebas]" || return 1
  fi
  echo "$huella" >"$marca"
}

preparar_node() {
  cd "$FRONTEND" || return 1
  if [[ -f node_modules/.package-lock.json && node_modules/.package-lock.json -nt package-lock.json ]]; then
    return 0
  fi
  npm ci --no-audit --no-fund
}

echo "VeraScope · testea-repo  ($(git -C "$RAIZ" branch --show-current 2>/dev/null) @ $(git -C "$RAIZ" rev-parse --short HEAD 2>/dev/null))"
echo
echo "── Preparación"
paso "backend/.venv con dependencias de prueba" preparar_venv
paso "frontend/node_modules (npm ci si cambió el lockfile)" preparar_node

# ── Backend ────────────────────────────────────────────────────────────────────

echo
echo "── Backend"
if [[ -x "$PY" ]]; then
  paso "ruff check" bash -c "cd '$BACKEND' && '$VENV/bin/ruff' check app tests pyproject.toml"
  paso "ruff format --check" bash -c "cd '$BACKEND' && '$VENV/bin/ruff' format --check app tests"
  paso "pytest (API y motor)" bash -c "cd '$BACKEND' && '$PY' -m pytest -q"
  paso "pytest -m lento (rendimiento)" bash -c "cd '$BACKEND' && '$PY' -m pytest -q -m lento"
  paso "pytest del preparador (verascope_datos)" bash -c "cd '$BACKEND/verascope_datos' && '$PY' -m pytest tests -q"
else
  omitir "backend" "no se pudo preparar backend/.venv"
fi

# ── Frontend ───────────────────────────────────────────────────────────────────

echo
echo "── Frontend"
if [[ -d "$FRONTEND/node_modules" ]]; then
  paso "tsc --noEmit" bash -c "cd '$FRONTEND' && npx tsc --noEmit"
  paso "jest --ci (incluye fixtures = JSON simulados del backend)" bash -c "cd '$FRONTEND' && npm run test -- --ci"
  paso "expo lint" bash -c "cd '$FRONTEND' && npm run lint"
  paso "expo install --check (versiones del SDK 58)" bash -c "cd '$FRONTEND' && npx expo install --check"
  if ((RAPIDO)); then
    omitir "expo export -p web" "--rapido"
  else
    paso "expo export -p web" bash -c "cd '$FRONTEND' && npx expo export -p web --output-dir '$TMP/dist'"
  fi
else
  omitir "frontend" "no hay frontend/node_modules"
fi

# ── Conexión backend ↔ frontend ────────────────────────────────────────────────

echo
echo "── Conexión backend ↔ frontend (API simulada)"
levantar_api() {
  PUERTO="$("$PY" -c 'import socket; s = socket.socket(); s.bind(("127.0.0.1", 0)); print(s.getsockname()[1])')"
  (cd "$BACKEND" && VERASCOPE_SIMULADO=1 exec "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port "$PUERTO" \
    >"$TMP/api.log" 2>&1) &
  API_PID=$!
  local i
  for i in $(seq 1 60); do
    curl -fsS "http://127.0.0.1:$PUERTO/api/v1/salud" >/dev/null 2>&1 && return 0
    kill -0 "$API_PID" 2>/dev/null || break
    sleep 0.5
  done
  cat "$TMP/api.log"
  return 1
}

comparar_esquema() {
  cd "$FRONTEND" || return 1
  npx --yes openapi-typescript@7.13.0 "http://127.0.0.1:$PUERTO/openapi.json" -o "$TMP/esquema.ts" || return 2
  # Los tipos son el contrato: si difieren, falla. Si solo cambian los comentarios (docstrings de
  # las rutas), avisa y sigue.
  local sin_comentarios='^\s*(/\*\*|\*|\*/)'
  if ! diff -q <(grep -vE "$sin_comentarios" src/shared/api/esquema.ts) \
    <(grep -vE "$sin_comentarios" "$TMP/esquema.ts") >/dev/null; then
    echo "Los tipos de esquema.ts no coinciden con /openapi.json de la API (cambio de contrato)."
    echo "Regenéralo con la API en :8000 y \`npm run tipos\`, y revisa el cambio con backend y frontend."
    diff -u src/shared/api/esquema.ts "$TMP/esquema.ts" | head -n 40
    return 1
  fi
  if ! diff -q src/shared/api/esquema.ts "$TMP/esquema.ts" >/dev/null; then
    touch "$TMP/aviso-esquema"
  fi
}

if [[ -x "$PY" ]] && command -v curl >/dev/null; then
  paso "levantar la API simulada" levantar_api
  if kill -0 "${API_PID:-0}" 2>/dev/null; then
    paso "rutas que usa la app = JSON simulados (+ CORS web y error estándar)" \
      node "$RAIZ/scripts/conexion-api.mjs" "http://127.0.0.1:$PUERTO"
    if ((RAPIDO)); then
      omitir "esquema.ts = /openapi.json" "--rapido"
    else
      paso "tipos de esquema.ts = /openapi.json (openapi-typescript 7.13.0)" comparar_esquema
      if [[ -f "$TMP/aviso-esquema" ]]; then
        echo "    aviso: esquema.ts solo difiere en comentarios; \`npm run tipos\` lo deja al día."
        RESULTADOS+=("aviso  esquema.ts: comentarios desactualizados (tipos iguales)")
      fi
    fi
  fi
else
  omitir "conexión" "falta backend/.venv o curl"
fi

# ── Resumen ────────────────────────────────────────────────────────────────────

echo
echo "── Resumen ($((SECONDS - INICIO_TOTAL))s)"
printf '  %s\n' "${RESULTADOS[@]}"
echo
if ((FALLOS)); then
  echo "✗ $FALLOS paso(s) fallaron."
  exit 1
fi
echo "✓ Todo el repositorio está en verde."
