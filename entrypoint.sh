#!/usr/bin/env bash
set -ex;

# https://stackoverflow.com/a/3355423/3813064
cd -- "$(dirname -- "$0")"
cd oekostrom_db

python wait_for_connection.py

echo "PostgreSQL started"

# Run database migrations
python manage.py migrate

exec "$@"