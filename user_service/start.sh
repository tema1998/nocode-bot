#!/usr/bin/env bash

python manage.py collectstatic  --noinput

gunicorn --bind 0.0.0.0:8000 --reload --timeout 120 --workers 4 --worker-class sync bot_management.wsgi:application
