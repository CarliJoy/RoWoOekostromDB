# Use the official Python image from the Docker Hub
FROM python:3.12-slim-bookworm AS BASE

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add system packages required to RUN your application here.
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      libpq5; \
    rm -rf /var/lib/apt/lists/*

# Create user

RUN set -ex; \
    groupadd --gid 1000 app; \
    useradd --create-home --uid 1000 --gid app app

# Set work directory
WORKDIR /home/app

# BUILDER
# Creates a virtual environment with all dependencies.
FROM base AS builder

# Add system packages required to BUILD your application here.
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      build-essential \
      pkg-config \
      libpq-dev \
    ; \
    rm -rf /var/lib/apt/lists/*

USER app

RUN \
  --mount=type=bind,source=requirements.txt,target=/home/app/requirements.txt \
  --mount=type=bind,source=oekostrom_db,target=/home/app/oekostrom_db \
    set -ex; \
    python -m venv /home/app/venv; \
    . /home/app/venv/bin/activate; \
    pip install --no-cache-dir -r /home/app/requirements.txt ;\
    python /home/app/oekostrom_db/manage.py collectstatic --no-input

# Image containing the application.
FROM base AS app

ENV VIRTUAL_ENV="/home/app/venv" \
    PATH="/home/app/venv/bin:$PATH"

COPY entrypoint.sh /home/app/entrypoint.sh

RUN set -ex; \
    chown app:app /home/app/entrypoint.sh; \
    chmod a+rx /home/app/entrypoint.sh

USER app

# Copy the virtual environment from the builder.
COPY --from=builder /home/app/venv /home/app/venv

# Set up entrypoint
ENTRYPOINT ["/home/app/entrypoint.sh"]

EXPOSE 8000

# Develop
FROM app as development

CMD ["/home/app/oekostrom_db/dev.sh" ]

## PRODUCTION
#FROM app as production
#
## Copy project
#COPY oekostrom_db /home/app/oekostrom_db
#
## Create a directory for static files
#RUN \
#    set -ex; \
#    mkdir -p /home/app/static; \
#    find /home/app | grep -v /home/app/venv; \

# TODO
# - cache pip deps https://stackoverflow.com/questions/58018300/using-a-pip-cache-directory-in-docker-builds
# - create nginx based image for static files
# -
