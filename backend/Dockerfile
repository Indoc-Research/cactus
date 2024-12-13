FROM python:3.11.11-bookworm AS production-environment

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

COPY poetry.lock pyproject.toml ./

RUN poetry install --only main --no-root --no-interaction


FROM production-environment AS cactus-image

COPY cactus ./cactus

ENTRYPOINT ["python3", "-m", "cactus"]
