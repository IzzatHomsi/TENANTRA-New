# backend/Dockerfile
# Hardened multi-stage image for Tenantra backend API.

FROM python:3.11-slim-bookworm@sha256:b4f780a9b29a58d2061370794cb3e354f9d06057fe78a46424732a7cd7ec3cf9 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
 && apt-get dist-upgrade -y \
 && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gosu \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

FROM base AS deps

COPY backend/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

FROM base AS runtime

RUN useradd --create-home --home-dir /app --shell /usr/sbin/nologin --uid 1000 appuser

COPY --from=deps /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=deps /usr/local/bin /usr/local/bin

COPY backend /app

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl -fsS http://127.0.0.1:5000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
