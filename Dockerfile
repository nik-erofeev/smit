FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=10 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    LC_ALL=C.UTF-8 \
    LANG=C.UTF-8

WORKDIR /smit_app

RUN apt-get update && apt-get install -y curl && apt-get clean

COPY app /smit_app/app
COPY docker /smit_app/docker
COPY migrations /smit_app/migrations
COPY main.py ./
COPY alembic.ini ./
COPY pyproject.toml poetry.lock* ./



RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry install --no-dev



RUN chmod +x /smit_app/docker/app.sh

EXPOSE 8000

