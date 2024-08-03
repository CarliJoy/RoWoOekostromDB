#!/usr/bin/env bash
set -ex;

# https://stackoverflow.com/a/3355423/3813064
cd -- "$(dirname -- "$0")"
export DEBUG=1
python manage.py runserver $DJANGO_INTERFACE