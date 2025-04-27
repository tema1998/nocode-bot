#!/usr/bin/env bash

cd bot_service && alembic upgrade head && cd ..
gunicorn -k uvicorn.workers.UvicornWorker bot_service.main:app --bind 0.0.0.0:8080 --workers 3 --reload
