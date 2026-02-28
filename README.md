# Instagram Sync Service

Тестовый сервис на Django + DRF:
- синхронизирует посты из Instagram Graph API в PostgreSQL
- отдает список постов с cursor pagination
- публикует комментарий к посту
- сохраняет комментарий локально

## Стек
- Python 3.13
- Django 5.2
- djangorestframework 3.16
- gunicorn 23.0
- psycopg[binary] 3.2.13
- httpx 0.28
- python-decouple 3.8
- PostgreSQL 17
- Docker + Docker Compose v2

## Переменные окружения
Скопировать шаблон:

```bash
cp .env.example .env
```

Обязательные поля в `.env`:
- `DJANGO_SECRET_KEY`
- `DEBUG`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `INSTAGRAM_ACCESS_TOKEN`
- `INSTAGRAM_USER_ID`
- `INSTAGRAM_BASE_URL`

## Запуск через Docker

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f web
```

Остановка:

```bash
docker compose down
```

Полная очистка (контейнеры + volume + локальный image):

```bash
docker compose down --volumes --remove-orphans --rmi local
```

## Тесты

```bash
docker compose exec web uv run python manage.py test instagram.tests.test_comments
```

## Локальный запуск без Docker

```bash
uv venv
source .venv/bin/activate
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

## API
- `POST /api/sync/` — синхронизация постов из Instagram
- `GET /api/posts/` — список постов (CursorPagination, `-timestamp`, page size 20)
- `POST /api/posts/<id>/comment/` — создать комментарий к посту

Пример тела запроса для комментария:

```json
{
  "text": "Hello"
}
```
