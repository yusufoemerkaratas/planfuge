FROM python:3.12-slim-bookworm

ARG APP_UID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-deu \
        tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --requirement requirements.txt

COPY server ./server
COPY src ./src
COPY scripts ./scripts
COPY --chmod=0755 docker/backend-entrypoint.sh /usr/local/bin/planfuge-entrypoint

RUN useradd --uid "${APP_UID}" --create-home planfuge \
    && mkdir -p /app/data /app/outputs \
    && chown -R planfuge:planfuge /app

USER planfuge

EXPOSE 8000

ENTRYPOINT ["planfuge-entrypoint"]
CMD ["python", "-m", "uvicorn", "server.app.api:app", "--host", "0.0.0.0", "--port", "8000"]
