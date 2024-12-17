FROM python:3.11.11-bookworm AS backend-environment

ENV PYTHONDONTWRITEBYTECODE=true \
    PYTHONIOENCODING=UTF-8 \
    POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false

ENV PATH="${POETRY_HOME}/bin:${PATH}"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app/backend

COPY backend/poetry.lock backend/pyproject.toml ./

RUN poetry install --only main --no-root --no-interaction


FROM node:22.12-bookworm AS frontend-environment

WORKDIR /frontend

COPY frontend ./

RUN npm install


FROM backend-environment AS cactus-image

COPY backend/cactus ./cactus
COPY --from=frontend-environment /frontend /app/frontend

ENTRYPOINT ["python3", "-m", "cactus"]
