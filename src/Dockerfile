FROM python:3.11.11

RUN apt-get update && apt-get install -y libpq-dev gunicorn &&\
  apt-get install --no-install-recommends -y wget make wait-for-it\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /srv/app
COPY /.env ./

COPY /src/start.sh ./

COPY /alembic.ini ./
COPY /src/poetry.lock /src/pyproject.toml ./src/


RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    cd src && \
    poetry config virtualenvs.create false && \
    poetry install

COPY ./src /srv/app/src/

ENV PYTHONPATH "${PYTHONPATH}:/"

EXPOSE 8000

CMD ["/bin/bash", "start.sh"]
