#!/usr/bin/env bash

alembic upgrade head
gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8080 --reload
