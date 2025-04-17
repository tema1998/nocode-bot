start:
	docker compose up --build

start-dev:
	docker compose -f docker-compose.dev.yml up --build

run-bot-service-db:
	docker compose -f docker-compose.dev.yml up bot_service_db

run-user-service-db:
	docker compose -f docker-compose.dev.yml up user_service_db

run-bot-service:
	uvicorn bot_service.main:app --reload --host 0.0.0.0 --port 8080

run-user-service:
	cd user_service && python manage.py runserver

run-user-service-tests:
	cd user_service && python manage.py test  --settings=bot_management.settings_test

run-bot-service-tests:
	cd bot_service && pytest

run-tests:
	cd bot_service && pytest && cd .. && cd user_service && python manage.py test  --settings=bot_management.settings_test