# Job Application Tracker

A self-hosted job application tracker built as a Django app: board/tab-based
organization, color-coded application status, salary and interview-round
tracking, JWT authentication, and a small vanilla-JS frontend served
directly by Django - no separate frontend build step required.

![status](https://img.shields.io/badge/status-active-brightgreen)
![python](https://img.shields.io/badge/python-3.12-blue)
![django](https://img.shields.io/badge/django-6.x-092E20)
![license](https://img.shields.io/badge/license-MIT-green)

## Features

- **Boards** - group applications into named tabs (e.g. "Berlin Search",
  "Remote Roles"). Created via a modal, renamed inline, deleted (soft
  delete) with a guard so you always keep at least one.
- **Applications** - company, position, status, salary, interview round,
  and free-text notes per row, all editable inline with debounced
  autosave.
- **Status pipeline** - Applied → Interviewing → Final Round → Offer /
  Rejected / Withdrawn, shown as color-coded pills.
- **Pagination** - server-side, with a configurable page size (10 / 25 /
  50 / 100).
- **JWT authentication** - register (username + email + password,
  confirmed twice) and log in (by username *or* email), with silent
  access-token refresh on expiry.
- **Activity logging** - every create/update/delete on a board or
  application is recorded (who, what, when, what changed).
- **Per-endpoint throttling** - separate rate limits for auth, board, and
  application endpoints, each set directly on its throttle class.

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Django + Django REST Framework |
| Auth | `djangorestframework-simplejwt` |
| Database | PostgreSQL |
| Cache / broker | Redis |
| Background tasks | Celery |
| Filtering | `django-filter` |
| Frontend | Django templates + vanilla JS (no build step, no framework) |
| Deployment | Docker Compose + Nginx + Gunicorn |

## Project structure

```
.
├── apps/
│   ├── base/            # BaseMixin (per-action serializer/permission/
│   │                     # throttle classes), BaseModel/SoftDelete,
│   │                     # custom exception handler, shared middleware
│   ├── logs/             # ActivityLog / ErrorLog / RequestLog +
│   │                     # LoggingViewSetMixin
│   ├── authentication/    # User, Profile, JWT login + registration
│   └── jobtracker/       # Board & Application models, serializers,
│                         # viewsets, and (via page_urls.py) the
│                         # login/register/tracker page views
├── templates/
│   ├── 404.html
│   └── jobtracker/
│       ├── index.html    # main tracker page
│       ├── login.html
│       ├── register.html
│       ├── css/style.css
│       └── js/
│           ├── auth.js    # token storage, authFetch(), refresh-on-401
│           └── tracker.js # boards/applications UI, pagination, modal
├── core/
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── nginx/                # reverse proxy config for production
├── Dockerfile
├── docker-compose.local.yml   # Postgres + Redis only, for local dev
├── docker-compose.prod.yml    # full stack: nginx, api, celery, redis, postgres
├── entrypoint.sh          # migrate → collectstatic → start server
├── .pre-commit-config.yaml
└── manage.py
```

## Setup

### 1. Prerequisites
- Python 3.12+
- Docker (recommended, for Postgres/Redis) - or a local PostgreSQL + Redis install

### 2. Install

```bash
git clone <repo-url>
cd job-tracker
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.sample` to `.env` and fill it in:

```bash
cp .env.sample .env
```

```env
########### DJANGO CONFIGURATION ###########
DEBUG=True
APP_NAME=tracker
TRA_DOMAIN=localhost
SECRET_KEY=change-me

########### DB CONFIGURATION ###########
POSTGRES_DB=tracker
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin

########### CACHE CONFIGURATION ###########
REDIS_HOST=localhost
REDIS_PORT=6379
```

`ALLOWED_HOSTS` also reads from the environment (`ALLOWED_HOSTS=host1,host2`)
and defaults to `["*"]` if unset - fine for local dev, worth tightening for
a real deployment.

### 4. Start Postgres + Redis

The easiest way locally is the bundled compose file, which brings up just
the database and cache (not the app itself):

```bash
docker compose -f docker-compose.local.yml up -d
```

This matches the `POSTGRES_USER=admin` / `POSTGRES_PASSWORD=admin` /
`POSTGRES_DB=tracker` values above, on `localhost:5432` and
`localhost:6379`. If you'd rather run Postgres/Redis natively, just point
the `.env` values at wherever they're listening.

### 5. Migrate and run

```bash
python manage.py migrate
python manage.py runserver
```

Open **http://127.0.0.1:8000/** - you'll land on the tracker page, which
redirects to **/login/** if you're not logged in yet.

## Running with Docker (full stack)

`docker-compose.prod.yml` runs the whole thing - Nginx, the Django app
(via Gunicorn), Celery, Redis, and Postgres - using the same `.env`:

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

`entrypoint.sh` runs automatically on container start: it waits for
Postgres, runs migrations, collects static files, then hands off to
Gunicorn. Nginx proxies `/` to the app and serves `/static/` directly from
the shared `static_volume`.

## API reference

All API responses follow `{"success": bool, "code": ..., "detail": ...}`
on errors (from the shared exception handler).

### Auth - `/v1/auth/`

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/v1/auth/pass/register/` | none | `{username, email, password, password2}` → `{access, refresh}` |
| `POST` | `/v1/auth/pass/login/` | none | `{username, password}` - `username` may be a username *or* email → `{access, refresh}` |
| `POST` | `/v1/auth/refresh/` | none | `{refresh}` → `{access}` |
| `POST` | `/v1/auth/logout/` | none | `{refresh}` - blacklists the refresh token |

### JobTracker - `/v1/jobtracker/`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/jobtracker/boards/` | List your boards, each with `applications_count` |
| `POST` | `/v1/jobtracker/boards/` | Create a board. `{"name": ""}` auto-names it "Job Tracker N" |
| `PATCH` | `/v1/jobtracker/boards/<id>/` | Rename |
| `DELETE` | `/v1/jobtracker/boards/<id>/` | Delete (blocked if it's your last board) |
| `GET` | `/v1/jobtracker/applications/?board=<id>&page=&page_size=&status=` | Paginated list |
| `POST` | `/v1/jobtracker/applications/` | Create. `{board, company, position, status, salary, round, notes}` |
| `PATCH` | `/v1/jobtracker/applications/<id>/` | Partial update (any field except `board`) |
| `DELETE` | `/v1/jobtracker/applications/<id>/` | Delete (soft) |

All `/v1/jobtracker/` endpoints require `Authorization: Bearer <access
token>` and only ever return/modify the authenticated user's own boards
and applications.

## Frontend routes

| Path | Page |
|---|---|
| `/` | Tracker (redirects to `/login/` if not authenticated) |
| `/login/` | Log in |
| `/register/` | Create an account |

## Notes on the implementation

- **Soft delete** - `Board` and `Application` both inherit `SoftDelete`
  (from `apps.base.models`), so deletes are recoverable via the
  `everything` manager and never cascade-destroy data.
- **Status dropdown** - rendered into a dedicated `#status-dropdown-portal`
  at the end of `<body>` and positioned with `position: fixed`, rather
  than as a child of the horizontally-scrolling table wrapper - this
  avoids the dropdown being clipped by `overflow-x: auto` on its
  ancestor.
- **Per-action configuration** - every viewset extends `BaseMixin`, which
  reads `serializer_classes_by_action` / `permission_classes_by_action` /
  `throttle_classes_by_action` dicts keyed by DRF action name
  (`list`, `create`, `retrieve`, `partial_update`, ...).
- **Throttle rates live on the throttle class**, not in
  `DEFAULT_THROTTLE_RATES` - e.g. `BoardAPIRateThrottle.rate = "120/min"`
  - so adding a new scoped throttle doesn't require touching
  `core/settings.py`.
- **Colors are a frontend concern** - the API returns plain status/round
  values plus a human-readable `*_display` label; the color palette
  lives in `tracker.js` and should be kept in sync with
  `apps/jobtracker/choices.py` if those choices ever change.

## Contributing

Contributions are welcome - feel free to open a PR. For anything bigger
than a small fix, opening an issue first to discuss the change is
appreciated but not required.

This repo uses [pre-commit](https://pre-commit.com) (black, flake8,
autoflake, bandit, plus a check that you haven't forgotten a migration).
Install the hooks once after cloning:

```bash
pip install pre-commit
pre-commit install
```

## License

MIT - see [LICENSE](LICENSE).
