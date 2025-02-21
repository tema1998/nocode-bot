start:
	docker compose up --build

start-celery:
	celery --broker=amqp://user:pass@127.0.0.1:5672// --result-backend=redis://:redis_pass@127.0.0.1:6379/0 -A src.celery.tasks worker -l info  --concurrency=2

run-db:
	docker compose up db

run-app:
	uvicorn src.main:app --reload --env-file .env.local

test:
	cd tests/functional/src/ && pytest test_documents.py -o log_cli=true -s


