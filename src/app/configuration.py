from enum import StrEnum
from os import environ
from pathlib import Path
from tomllib import TOMLDecodeError, loads
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, ValidationError

CONF_ENV_VAR = "APP_CONFIG_FILE"


class ConfigErrorKind(StrEnum):
    MISSING_PATH = "missing_path"
    UNREADABLE = "unreadable"
    INVALID_TOML = "invalid_toml"
    INVALID_SCHEMA = "invalid_schema"


class ConfigError(RuntimeError):
    def __init__(self: Self, kind: ConfigErrorKind, message: str) -> None:
        super().__init__(message)
        self.kind = kind


class _Base(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class DatabaseConfig(_Base):
    uri: str


class AppConfig(_Base):
    env: Literal["dev", "prod"]
    port: int = 8000
    provide_automatic_options: bool = False
    force_https: bool | None = None
    strict_transport_security: bool | None = None
    database: DatabaseConfig

    @property
    def is_dev(self: Self) -> bool:
        return self.env == "dev"

    @property
    def https_forced(self: Self) -> bool:
        return self.force_https if self.force_https is not None else not self.is_dev

    @property
    def hsts_enabled(self: Self) -> bool:
        if self.strict_transport_security is not None:
            return self.strict_transport_security
        return not self.is_dev

    @property
    def DEBUG(self: Self) -> bool:
        return self.is_dev

    @property
    def SQLALCHEMY_DATABASE_URI(self: Self) -> str:
        return self.database.uri

    @property
    def PROVIDE_AUTOMATIC_OPTIONS(self: Self) -> bool:
        return self.provide_automatic_options


def load_configuration(path: str | None = None) -> AppConfig:
    if not (path := path or environ.get(CONF_ENV_VAR)):
        raise ConfigError(ConfigErrorKind.MISSING_PATH, f"{CONF_ENV_VAR} is not set")

    try:
        configuration = loads(Path(path).read_text(encoding="utf-8"))
        return AppConfig.model_validate(configuration)
    except OSError as e:
        raise ConfigError(ConfigErrorKind.UNREADABLE, f"Error while reading {path}: {e}") from e
    except TOMLDecodeError as e:
        raise ConfigError(ConfigErrorKind.INVALID_TOML, f"Error while reading {path}: {e}") from e
    except ValidationError as e:
        raise ConfigError(ConfigErrorKind.INVALID_SCHEMA, f"Invalid configuration: {e}") from e
