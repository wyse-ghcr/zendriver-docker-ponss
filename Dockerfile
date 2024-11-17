FROM debian:sid-slim
LABEL org.opencontainers.image.source="https://github.com/stephanlensky/zendriver-docker"

ARG USER=chrome-user
ARG PUID=1000
ARG PGID=1000
ARG VIDEO_GROUP_GID=107

ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

USER root
RUN groupadd -g $PGID $USER
RUN groupadd -g $VIDEO_GROUP_GID docker_video
RUN useradd -ms /bin/bash -u $PUID -g $PGID $USER
RUN usermod -aG docker_video $USER

# Install Chromium and dependencies for running under wayland with VNC support
RUN apt-get update && apt-get install -y --no-install-recommends \
    sway xwayland wayvnc openssh-client openssl chromium \
    && rm -rf /var/lib/apt/lists/*

# Copy sway/wayvnc configs
COPY --chown=$USER:$USER docker/sway/config /home/$USER/.config/sway/config
COPY --chown=$USER:$USER docker/wayvnc/config /home/$USER/.config/wayvnc/config

# Make directory for wayvnc certs
RUN mkdir /certs
RUN chown -R $USER:$USER /certs

# Make directory for the app
RUN mkdir /app
RUN chown $USER:$USER /app

# Switch to the non-root user
USER $USER

# Set the working directory
WORKDIR /app

# Install python
RUN uv python install 3.13

# Install the Python project's dependencies using the lockfile and settings
COPY --chown=$USER:$USER pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/home/$USER/.cache/uv,uid=$PUID,gid=$PGID \
    uv sync --frozen --no-install-project

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY --chown=$USER:$USER . /app

# Add binaries from the project's virtual environment to the PATH
ENV PATH="/app/.venv/bin:$PATH"

# Sync the project's dependencies and install the project
RUN --mount=type=cache,target=/home/$USER/.cache/uv,uid=$PUID,gid=$PGID \
    uv sync --frozen

# Copy and set the entrypoint script
COPY --chown=$USER:$USER docker/entrypoint.sh /
ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
