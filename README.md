# Название проект
Описание.
Приложение будет доступно по адресу: [http://localhost:8080](http://localhost:8080). Swagger-документация [http://localhost:8080/api/openapi](http://localhost:8080/api/openapi).

# Технологии
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* Docker

## Переменные окружения
Создайте файл bot_service/.env используя bot_service/.env.example и внесите требуемые изменения.
Так же создайте tests/.env используя tests/.env.example для тестирования приложения.

## Установка зависимостей

```
poetry install
```

## Локальная разработка
Запустите базы данных
```
make run-db
```
Запустите приложение
```
make run-app
```

## Makefile

Запуск контейнера (приложение + БД)
```
make start
```

Запуск приложения
```
make run-app
```

Запуск БД отдельно
```
make run-db
```

Запуск тестов. Перед запуском тестов дожны быть запущены контейнеры с базами данных(make run-db).
```
make test
```