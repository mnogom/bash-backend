FROM python:3.12-slim AS base

ARG POETRY_HOME=/etc/poetry

ARG USER_NAME=konstantin
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG USER_HOME=/home/${USER_NAME}

ARG GUEST_NAME=guest
ARG GUEST_UID=2000
ARG GUEST_GID=$GUEST_UID

ENV PATH="${PATH}:${POETRY_HOME}/bin"
ENV TERM=linux

WORKDIR /app

# Install `curl`, `gpg`
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing curl gpg

# Prepare to install `glow`
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://repo.charm.sh/apt/gpg.key | gpg --dearmor -o /etc/apt/keyrings/charm.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/charm.gpg] https://repo.charm.sh/apt/ * *" | tee /etc/apt/sources.list.d/charm.list

# Install user deps
RUN apt-get update && apt-get install -y --no-install-recommends --fix-missing tini sudo procps nano vim tree glow bat && \
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_HOME} python - --version 1.8.2

# Setup users
RUN groupadd --gid $USER_GID $USER_NAME && \
    useradd --uid $USER_UID --gid $USER_GID --create-home $USER_NAME

RUN groupadd --gid $GUEST_GID $GUEST_NAME && \
    useradd --uid $GUEST_UID --gid $GUEST_GID $GUEST_NAME

# Setup app
COPY poetry.lock pyproject.toml ./

# Make konstantin use bash for guest without password
# src: https://askubuntu.com/a/159009
# src: https://ru.wikipedia.org/wiki/Chown
RUN echo 'konstantin ALL = (guest) NOPASSWD: /bin/bash' >> /etc/sudoers

FROM base AS development

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache && \
    rm -rf ~/.cache

COPY ./src ./src
COPY ./main.py ./

WORKDIR /home/$USER_NAME

ENTRYPOINT ["tini", "--" ]
CMD ["python", "/app/main.py"]

FROM base AS production

# Setup users access to bin
# src: https://ru.hexlet.io/courses/cli-basics/lessons/permissions/theory_unit

# Access to app
RUN chown -R :$USER_NAME /app && chmod -R 750 /app && \
    # Disable access to python
    chown :$USER_NAME -R /usr/local && chmod -R 750 /usr/local && \
    # Disable access to sh
    chmod 750 /usr/bin/sh

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-cache --without dev && \
    rm -rf ~/.cache

# Cleanup, uninstall `curl`, `gpg` and charm source
RUN apt-get remove -y curl gpg && \
    rm -rf /var/lib/apt/lists/* && \
    rm /etc/apt/keyrings/charm.gpg && \
    rm /etc/apt/sources.list.d/charm.list && \
    rm -rf /root/.local/share/charm && \
    rm poetry.lock pyproject.toml && \
    pip uninstall poetry

COPY ./src ./src
COPY ./main.py ./

# Remove all tmp dirs
RUN rm -rf /var/tmp /tmp

USER $USER_NAME
WORKDIR /home/$USER_NAME

ENTRYPOINT ["tini", "--" ]
CMD ["python", "/app/main.py"]
