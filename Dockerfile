# Use the official Python image from the Docker Hub
FROM python:3.12-slim-bookworm AS BASE
ARG UID
ARG GID

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Add system packages required to RUN your application here.
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
      gpg \
      gpg-agent \
      dirmngr \
      libpq5; \
    rm -rf /var/lib/apt/lists/*

# Create user

RUN set -ex; \
    groupadd --gid $GID app; \
    useradd --create-home --uid $UID --gid app app

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
    set -ex; \
    python -m venv /home/app/venv; \
    . /home/app/venv/bin/activate; \
    pip install --upgrade pip; \
    pip install --no-cache-dir -r /home/app/requirements.txt

ENV VIRTUAL_ENV="/home/app/venv" \
    PATH="/home/app/venv/bin:$PATH"

RUN \
  --mount=type=bind,source=oekostrom_db,target=/home/app/oekostrom_db \
    set -ex; \
    python /home/app/oekostrom_db/manage.py collectstatic --no-input


# Image containing the application.
FROM base AS app

ENV VIRTUAL_ENV="/home/app/venv" \
    PATH="/home/app/venv/bin:$PATH"

COPY log_key.asc /home/app
COPY entrypoint.sh /home/app/entrypoint.sh
COPY oekostrom-recherche/scraped_data /home/app/oekostrom-recherche/scraped_data

RUN set -ex; \
    mkdir -p /home/app/.gnupg; \
    chmod 700 /home/app/.gnupg; \
    echo "use-agent: no\n" >> /home/app/.gnupg/gpg.conf; \
    chown -R app:app /home/app; \
    chmod a+rx /home/app/entrypoint.sh

USER app

RUN gpg --batch --import /home/app/log_key.asc

# Copy the virtual environment from the builder.
COPY --from=builder /home/app/venv /home/app/venv

# Set up entrypoint
ENTRYPOINT ["/home/app/entrypoint.sh"]

EXPOSE 8000

# Develop
FROM app as development

CMD ["/home/app/oekostrom_db/dev.sh" ]


FROM nginx:mainline-bookworm as nginx

# copy non root config
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx_site.conf.template /etc/nginx/templates/default.conf.template

RUN mkdir -p /home/app

COPY --from=builder /home/app/static /home/app/static
COPY favicon.ico /home/app/static/favicon.ico

# ensure write permisisons are okay
RUN set -ex; \
    chmod -R a+rX /home; \
    chown -R nginx:nginx /etc/nginx/; \
    chmod -R u+rwX /etc/nginx

# TODO create a docker-entrypoint script that makes config ro again

USER nginx


# PRODUCTION
FROM app as production

# Copy project
COPY oekostrom_db /home/app/oekostrom_db

EXPOSE 8000

WORKDIR /home/app

# Command to run Daphne server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "oekostrom_db.asgi:application"]
