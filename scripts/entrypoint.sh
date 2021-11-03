#!/bin/sh

set -e

python manage.py collectstatic --noinput

uwsgi --socket :8082 --master --enable-threads --module app.wsgi

