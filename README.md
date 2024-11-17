# Zendriver + Docker ❤️

**Run [Zendriver](https://github.com/stephanlensky/zendriver) in a virtual display from a Docker container! Includes VNC support for easy debugging.**

This repository demonstrates running [Zendriver](https://github.com/stephanlensky/zendriver) in a graphical Wayland session under Docker. This allows for automating a real, GPU-accelerated Chrome browser (not headless) in a Docker container with 0 dependendencies on X11 or Wayland on your host machine.

This deployment method is ideal for running Zendriver on a headless server, as it allows Chrome to run on an entirely virtual display, accessible via VNC, and does not require any existing graphical session on the host.

Based on [`stephanlensky/swayvnc-chrome`](https://github.com/stephanlensky/swayvnc-chrome).

**Linux-only.**

## How to use this repository

This repository is a full project template, ready for production use. To use this template for your own project, just fork or clone it and then proceed to [First-time setup](#first-time-setup).

**Note:** if you want your repository to be private, forking via GitHub will not work, as you cannot change the visibility of forks. Instead, manually create a new repository and then copy the contents there.

## First-time setup

After forking or cloning the repository, you may need to adjust the configuration in order to enable GPU support. Running full GUI apps under Docker is a bit tricky (especially once you add GPUs to the mix), so please bear with me here.

### Prerequisites

- **You are running some variant of Linux on your host machine.** Mac may also work, but I am not able to test. Windows will not work without additional modification.
- Make sure your system has a GPU available (integrated or dedicated) and that you have the latest firmware and drivers installed!

### Instructions

1. First, identify the DRM rendering node under `/dev/dri` which we will use to give Docker access to our GPU

   ```
   $ ls /dev/dri
   by-path  card0  card1  renderD128
   ```

   Typically, rendering nodes will have names like `renderDXXX`. In this case, `/dev/dri/renderD128` is the rendering node for my GPU.

   If you have multiple GPUs installed (ex. an integrated GPU and dedicated GPU), you may see multiple rendering nodes. In this case, a tool like [drm_info](https://gitlab.freedesktop.org/emersion/drm_info) may help you determine which to use.

2. Once you have your desired rendering node, determine the GID of the group which owns it.

   ```
   $ stat /dev/dri/renderD128 -c "%G %g"
   render 107
   ```

   On my Debian system, this file is owned by the `render` group, which has a GID of 107.

3. In [`docker-compose.yml`](https://github.com/stephanlensky/zendriver-docker/blob/main/docker-compose.yml), make the following two changes:

   1. Under `devices`, update the entry to point to the `/dev/dri/renderDXXX` device you found in step 1. Both parts of the string should be updated, so for example if your device is `/dev/dri/renderD129`, the new entry should read

      ```
      - "/dev/dri/renderD129:/dev/dri/renderD129"
      ```

   2. Under `environment`, update `RENDER_GROUP_GID=107` to the GID you found in step 2.

After making these changes, you should be able to run the demo app with

```
docker compose up --build app
```

## Usage

This project is packaged with [`uv`](https://github.com/astral-sh/uv), linted with [`ruff`](https://github.com/astral-sh/ruff), and type-checked with [`mypy`](https://mypy-lang.org/).

To get started, [install `uv`](https://docs.astral.sh/uv/getting-started/installation/) and run

```
uv sync
```

to install development dependencies.

The project is fully built with Docker, so this is not technically necessary, but running this command on your host machine will allow for proper IDE integration as you work.

### Running the app

After completing the [First-time setup](#first-time-setup), start the app with [Docker Compose](https://docs.docker.com/compose/).

```
docker compose up --build app
```

This will automatically launch a VNC server which can be used to monitor or debug the running browser instance. To connect to it, use a VNC client (such as [RealVNC](https://www.realvnc.com/en/connect/download/viewer/) for Windows) and connect to `localhost:5910` using the credentials defined in [`docker-compose.yml`](https://github.com/stephanlensky/zendriver-docker/blob/main/docker-compose.yml).

### Linting/formatting

To autoformat:

```
./scripts/format.sh
```

To lint:

```
./scripts/lint.sh
```
