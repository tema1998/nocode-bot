#!/usr/bin/env bash

gunicorn --bind 0.0.0.0:8000 --reload bot_management.wsgi:application
