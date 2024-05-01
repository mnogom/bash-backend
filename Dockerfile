FROM python:3.12-slim AS base

ARG POETRY_HOME=/etc/poetry
ARG GITHUB_CV_URL=https://raw.githubusercontent.com/mnogom/mnogom/main/README.md
ARG GITHUB_CV_FILE=00-projects.md

ARG USER_NAME=guest
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_HOME=/home/${USER_NAME}

ENV PATH="${PATH}:${POETRY_HOME}/bin"

WORKDIR /app

# Install `curl`, `gpg`
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing curl gpg

# Prepare to install `glow`
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --dearmor -o /etc/apt/keyrings/charm.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | tee /etc/apt/sources.list.d/charm.list

# Install user deps
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing tini procps nano vim tree glow bat && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python - --version 1.8.2

COPY poetry.lock pyproject.toml ./

FROM base AS development

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache && \
    rm -rf ~/.cache

COPY ./src ./src
COPY ./main.py ./
RUN mkdir -p $USER_HOME && \
    curl $GITHUB_CV_URL > $USER_HOME/$GITHUB_CV_FILE

WORKDIR /home/$USER_NAME

ENTRYPOINT ["tini", "--" ]
CMD ["python", "/app/main.py"]

FROM base as production

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache --without dev && \
    rm -rf ~/.cache

COPY ./src ./src
COPY ./main.py ./
RUN mkdir -p $USER_HOME && \
    curl $GITHUB_CV_URL > $USER_HOME/$GITHUB_CV_FILE

# Cleanup, uninstall `curl`, `gpg` and charm source
RUN apt-get remove -y curl gpg && \
    rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/keyrings/charm.gpg && \
    rm /etc/apt/sources.list.d/charm.list && \
    rm -rf /root/.local/share/charm && \
    pip uninstall -y poetry pip

RUN groupadd --gid $USER_GID $USER_NAME && \
    useradd --uid $USER_UID --gid $USER_GID $USER_NAME && \
    chmod -R 555 /app $USER_HOME

USER $USER_NAME
WORKDIR /home/$USER_NAME

ENTRYPOINT ["tini", "--" ]
CMD ["python", "/app/main.py"]
