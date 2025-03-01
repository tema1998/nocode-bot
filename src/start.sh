#!/usr/bin/env bash

cd src && alembic upgrade head && cd ..
gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:8080 --reload
