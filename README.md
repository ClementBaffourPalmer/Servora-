# Servora — Multi-Service Booking Platform (Django + DRF)

Multi-service booking app where **providers** list services/availability and **customers** book them. Includes a Bootstrap web UI and a token-auth REST API.

## Tech
- Django, Django REST Framework
- Bootstrap templates
- SQLite (dev), PostgreSQL (prod)

## Quick start (development)

Create/activate a virtualenv, then:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

## Web UI
- **Homepage**: `/` (service cards + filter)
- **Service list**: `/services/`
- **Service detail**: `/services/<id>/`
- **Customer dashboard**: `/bookings/me/`
- **Provider dashboard**: `/provider/`

## REST API (token auth)

Base path: `/api/`

- **Register**: `POST /api/auth/register/` → `{ token, user }`
- **Login**: `POST /api/auth/login/` → `{ token }`
- **List services**: `GET /api/services/` (supports `?category=<id>`, paginated)
- **Service details**: `GET /api/services/<id>/`
- **Provider services (CRUD)**: `/api/provider/services/` (provider-only)
- **Customer bookings**: `GET/POST /api/bookings/` (customer-only)
- **Provider bookings**: `GET /api/provider/bookings/` (provider-only)
- **Update booking status**: `PATCH /api/provider/bookings/<id>/status/` with `{ "status": "confirmed|completed|cancelled" }`

## Environment variables

Copy `.env.example` to `.env` and adjust as needed.

## Demo data (Laundry-first)

- **Auto-seeded** on migrate: demo provider + Laundry services.
- Optional fixture load:

```bash
python manage.py loaddata services/fixtures/laundry_initial.json
```

## Production notes

- Use `BookNest.settings.prod`
- Configure `DATABASE_URL`, `SECRET_KEY`, `ALLOWED_HOSTS`, and email settings
- Collect static: `python manage.py collectstatic`
- Run with Gunicorn (example):

```bash
gunicorn servora.wsgi:application
```

