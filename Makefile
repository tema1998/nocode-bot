start:
	docker compose up --build

start-celery:
	celery --broker=amqp://user:pass@127.0.0.1:5672// --result-backend=redis://:redis_pass@127.0.0.1:6379/0 -A bot_service.celery.tasks worker -l info  --concurrency=2

run-bot-service-db:
	docker compose up bot_service_db

run-user-service-db:
	docker compose up user_service_db

run-bot-service:
	uvicorn bot_service.main:app --reload --host 0.0.0.0 --port 8080

run-user-service:
	cd user_service && python manage.py runserver


