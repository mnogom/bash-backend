FROM python:3.12-slim AS base

WORKDIR /app
ARG POETRY_HOME=/etc/poetry
ENV PATH="${PATH}:${POETRY_HOME}/bin"

RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing tini curl procps nano vim tree && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python - --version 1.8.2

RUN apt-get remove -y curl && \
    rm -rf /var/lib/apt/lists/*

COPY poetry.lock pyproject.toml ./

FROM base AS development

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache && \
    rm -rf ~/.cache

COPY ./src ./src
COPY ./main.py ./

ENTRYPOINT ["tini", "--" ]
CMD ["python", "main.py"]
