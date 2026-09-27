from os import environ
from pathlib import Path
from tomllib import TOMLDecodeError, loads
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, ValidationError

from .errors import ConfigError

CONF_ENV_VAR = "APP_CONFIG_FILE"


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DatabaseConfig(_Base):
    uri: str


class AppConfig(_Base):
    env: Literal["dev"]
    port: int = 8000
    database: DatabaseConfig

    @property
    def SQLALCHEMY_DATABASE_URI(self: Self) -> str:
        return self.database.uri


def load_configuration(path: str | None = None) -> AppConfig:
    if not (path := path or environ.get(CONF_ENV_VAR)):
        raise ConfigError(f"{CONF_ENV_VAR} is not set")

    try:
        configuration = loads(Path(path).read_text(encoding="utf-8"))
        return AppConfig.model_validate(configuration)
    except (OSError, TOMLDecodeError) as e:
        raise ConfigError(f"Error while reading {path}: {e}") from e
    except ValidationError as e:
        raise ConfigError(f"Invalid configuration: {e}") from e
