# Etapa 1: instala la API y sus dependencias en un entorno virtual aislado.
FROM python:3.11-slim AS construccion

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /src
COPY pyproject.toml ./
COPY app ./app
RUN pip install .

# Etapa 2: imagen final, solo el entorno instalado y un usuario sin privilegios.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    VERASCOPE_DATOS=/data \
    PORT=8000

RUN useradd --system --uid 10001 --home-dir /srv verascope \
    && mkdir -p /data \
    && chown verascope /data

COPY --from=construccion /opt/venv /opt/venv

WORKDIR /srv
USER verascope
VOLUME ["/data"]
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ.get(\"PORT\", \"8000\")}/api/v1/salud', timeout=4)"

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]
