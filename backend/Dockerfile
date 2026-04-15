FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
COPY app /app/app

RUN pip install --no-cache-dir ".[dev,all]"

COPY tests /app/tests

ENV STORAGE_ROOT=/data
RUN mkdir -p /data/uploads

EXPOSE 8000

# Render and other hosts set PORT; default 8000 for local docker run.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
