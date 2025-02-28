FROM python:3.12

RUN apt-get update && apt-get install -y libpq-dev gunicorn &&\
  apt-get install --no-install-recommends -y wget make wait-for-it\
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

WORKDIR /app

COPY /user_service/poetry.lock /user_service/pyproject.toml ./
COPY /user_service/start.sh ./
COPY /.env ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root


COPY /user_service/ /app/

CMD ["/bin/bash", "start.sh"]



