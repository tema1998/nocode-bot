FROM python:3.12

RUN apt-get update && apt-get install -y libpq-dev gunicorn &&\
  apt-get install --no-install-recommends -y wget make wait-for-it\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app
COPY /.env ./

COPY /bot_service/start.sh ./

COPY /bot_service/alembic.ini ./bot_service/
COPY /bot_service/poetry.lock /bot_service/pyproject.toml ./bot_service/


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    cd bot_service && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

COPY ./bot_service /srv/app/bot_service/

ENV PYTHONPATH "${PYTHONPATH}:/"

EXPOSE 8000

CMD ["/bin/bash", "start.sh"]
