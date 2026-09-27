# flask_app

A minimal Flask API scaffold: blueprints under `/api/v1`, SQLAlchemy + Alembic for persistence, Pydantic-validated TOML configuration.

## Requirements

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/)

## Setup

Install dependencies:

```sh
uv sync
```

Create the environment files (both are gitignored, create them yourself):

`.flaskenv`:

```
FLASK_APP=app
FLASK_RUN_PORT=8000
FLASK_DEBUG=1
```

`.env`:

```
APP_CONFIG_FILE=configuration.toml
```

Configuration is a TOML file pointed to by `APP_CONFIG_FILE` and validated against `AppConfig` in [src/app/configuration.py](src/app/configuration.py):

```toml
env = "dev"
port = 8001

[database]
uri = "sqlite:///app.db"
```

## Running

```sh
uv run flask run
```

## Database migrations

Migrations are managed with Alembic (see [migrations/](migrations/) and [alembic.ini](alembic.ini)).

Generate a migration from model changes:

```sh
uv run alembic revision --autogenerate -m "message"
```

Apply migrations (custom Flask CLI command, see [src/app/cli.py](src/app/cli.py)):

```sh
uv run flask init-db
```

## Project layout

```
src/app/
├── __init__.py         # app factory, blueprint registration
├── cli.py              # custom Flask CLI commands
├── configuration.py    # TOML config loading + validation
├── extensions.py       # Flask extensions (SQLAlchemy)
├── errors/             # domain exceptions
├── handlers/           # error handlers
├── models/             # SQLAlchemy models
└── routes/             # API blueprints
```

## API

All routes are mounted under `/api/v1`.

| Method | Path                | Description       |
| ------ | ------------------- | ------------------ |
| GET    | `/health/`           | Liveness check     |
| GET    | `/users/`            | List users         |
| GET    | `/users/<user_id>`   | Get a single user  |

## Tooling

- Lint: `uv run ruff check .`
- Format: `uv run ruff format .`
- Tests: `uv run pytest -q` (no test suite yet)

## License

See [LICENSE](LICENSE).
