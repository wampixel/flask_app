# flask_app

[![CI](https://github.com/wampixel/flask_app/actions/workflows/ci.yml/badge.svg)](https://github.com/wampixel/flask_app/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/wampixel/flask_app/graph/badge.svg)](https://codecov.io/gh/wampixel/flask_app)
[![Release](https://img.shields.io/github/v/release/wampixel/flask_app)](https://github.com/wampixel/flask_app/releases)

A minimal Flask API scaffold with a Vue front-end skeleton.

- Versioned API blueprints under `/api/v1`.
- SQLAlchemy models and Alembic migrations through Flask-Migrate.
- TOML configuration validated by Pydantic.
- Bearer token authentication backed by a database session table.

## Requirements

- Python 3.14 or newer. The exact version is pinned in [.python-version](.python-version).
- [uv](https://docs.astral.sh/uv/getting-started/installation/). It installs the right Python version for you if it is missing.
- Git.

## Quick start

These steps take a fresh clone to a running API with demo data.

```sh
git clone https://github.com/wampixel/flask_app.git
cd flask_app
uv sync
```

`uv sync` creates `.venv/`, installs the runtime and dev dependencies, and installs the `app` package in editable mode.

Create the two environment files at the project root. Both are gitignored.

`.flaskenv` holds the Flask CLI settings:

```sh
cat > .flaskenv <<'EOF'
FLASK_APP=app
FLASK_RUN_PORT=8000
FLASK_DEBUG=1
EOF
```

`.env` points to the configuration file:

```sh
cat > .env <<'EOF'
APP_CONFIG_FILE=configuration.toml
EOF
```

Both files are loaded automatically by `python-dotenv`, a dev dependency, whenever you run a `flask` command.

Create the database schema, then load the demo data:

```sh
uv run flask init-db
uv run flask seed-db
```

Start the development server:

```sh
uv run flask run
```

Check that it answers:

```sh
curl http://127.0.0.1:8000/api/v1/health
# {"message": "healthy service"}
```

## Configuration

The app reads a TOML file. Its path comes from the `APP_CONFIG_FILE` environment variable. The app refuses to start if the variable is missing, the file is unreadable, or the content is invalid.

The schema is `AppConfig` in [src/app/configuration.py](src/app/configuration.py). Unknown keys are rejected.

| Key                         | Type    | Default    | Description                                                       |
| --------------------------- | ------- | ---------- | ----------------------------------------------------------------- |
| `env`                       | string  | required   | Only `"dev"` is accepted for now.                                 |
| `port`                      | integer | `8000`     | Validated but not used by `flask run`. Use `FLASK_RUN_PORT`.      |
| `provide_automatic_options` | boolean | `false`    | Lets Flask answer `OPTIONS` requests automatically on each route. |
| `database.uri`              | string  | required   | SQLAlchemy database URI.                                          |

The committed [configuration.toml](configuration.toml) works out of the box:

```toml
env = "dev"
port = 8080
provide_automatic_options = false

[database]
uri = "sqlite:///app.db"
```

A relative SQLite path resolves inside the Flask instance folder. With the default configuration, the database file is `src/instance/app.db`. Delete it to start from scratch, then rerun `init-db` and `seed-db`.

## Authentication

Every route under `/api/v1` requires a bearer token, except the ones marked public: `GET /health` and `POST /auth/token`.

Get a token with HTTP Basic credentials:

```sh
curl -X POST -u jdoe:'Changeme12345!' http://127.0.0.1:8000/api/v1/auth/token
# {"access_token": "...", "token_type": "Bearer", "expires_at": "..."}
```

Use it on protected routes:

```sh
curl -H "Authorization: Bearer <access_token>" http://127.0.0.1:8000/api/v1/users
```

Session rules:

- A token expires 8 hours after it is issued.
- A token is also rejected after 30 minutes without use.
- Only the SHA-512 hash of the token is stored. Passwords are hashed with Argon2.
- Usernames are matched in lowercase.

## Demo data

`flask seed-db` creates the following records, only if the tables are empty.

| Username | Tenant          | Password         |
| -------- | --------------- | ---------------- |
| `jdoe`   | `acme`          | `Changeme12345!` |
| `jdont`  | `Umbrella corp` | `Changeme12345!` |

These credentials are for local development only.

## Database migrations

Migrations live in [migrations/](migrations/) and run through the Flask-Migrate CLI, so they use the database from your configuration file.

Generate a migration after changing a model:

```sh
uv run flask db migrate -m "describe the change"
```

Review the generated file in [migrations/versions/](migrations/versions/), then apply it:

```sh
uv run flask init-db
```

`init-db` is a custom command from [src/app/cli.py](src/app/cli.py). It runs the same upgrade as `flask db upgrade`.

## Project layout

```
src/app/
├── __init__.py         # app factory, blueprint registration
├── cli.py              # custom Flask CLI commands (init-db, seed-db)
├── configuration.py    # TOML config loading and validation
├── extensions.py       # Flask extensions (SQLAlchemy, Migrate)
├── handlers.py         # error handlers
├── decorators/         # route decorators (@public)
├── errors/             # domain exceptions
├── middlewares/        # authentication and security middlewares
├── models/             # SQLAlchemy models
├── routes/             # API blueprints
├── schemas/            # Pydantic response schemas
└── utils/              # hashing helpers
migrations/             # Alembic environment and versions
tests/                  # pytest suite
```

## Development

| Task          | Command                     |
| ------------- | --------------------------- |
| Lint          | `uv run ruff check .`       |
| Format        | `uv run ruff format .`      |
| Tests         | `uv run pytest`             |

Tests use an in-memory SQLite database and a temporary configuration file. They need neither `.env` nor `.flaskenv`.

`pytest` also measures coverage and fails under 70 %. The threshold is set in [pyproject.toml](pyproject.toml).

## Continuous integration and delivery

The [.github/workflows/ci.yml](.github/workflows/ci.yml) workflow runs on every push to `main`, every pull request, and every `v*.*.*` tag.

1. **Lint** — `ruff check` and `ruff format --check`.
2. **Test** — `pytest` with coverage. The report is uploaded to [Codecov](https://codecov.io), which requires a `CODECOV_TOKEN` repository secret.
3. **Build** — `uv build`. The wheel is kept as an artifact.
4. **Release** — only on a `v*.*.*` tag. It publishes the wheel built in the previous step to the matching GitHub Release, without rebuilding it.

Pushing a `vX.Y.Z` tag therefore runs the full chain, then publishes the wheel, provided lint and tests pass.

## License

See [LICENSE](LICENSE).
