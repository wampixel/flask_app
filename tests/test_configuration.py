from pathlib import Path

from pytest import MonkeyPatch, mark, raises

from app.configuration import CONF_ENV_VAR, AppConfig, ConfigError, ConfigErrorKind, load_configuration

VALID = """
[database]
uri = "sqlite://"
"""


def write_config(tmp_path: Path, content: str) -> str:
    path = tmp_path / "configuration.toml"
    path.write_text(content, encoding="utf-8")
    return str(path)


def test_valid_file_loads(tmp_path: Path) -> None:
    configuration = load_configuration(write_config(tmp_path, VALID))
    assert isinstance(configuration, AppConfig)
    assert configuration.SQLALCHEMY_DATABASE_URI == "sqlite://"


def test_missing_path_is_typed(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv(CONF_ENV_VAR, raising=False)
    with raises(ConfigError, match=f"{CONF_ENV_VAR} is not set") as excinfo:
        load_configuration()
    assert excinfo.value.kind is ConfigErrorKind.MISSING_PATH


def test_unreadable_file_is_typed(tmp_path: Path) -> None:
    with raises(ConfigError, match="absent.toml") as excinfo:
        load_configuration(str(tmp_path / "absent.toml"))
    assert excinfo.value.kind is ConfigErrorKind.UNREADABLE


@mark.parametrize(
    ("content", "kind", "message"),
    [
        ("force_https = ", ConfigErrorKind.INVALID_TOML, "configuration.toml"),
        ("force_https = true", ConfigErrorKind.INVALID_SCHEMA, "Invalid configuration"),
        (VALID + 'unknown = "x"\n', ConfigErrorKind.INVALID_SCHEMA, "Invalid configuration"),
    ],
    ids=["malformed", "missing_database", "unknown_key"],
)
def test_bad_content_is_typed(tmp_path: Path, content: str, kind: ConfigErrorKind, message: str) -> None:
    with raises(ConfigError, match=message) as excinfo:
        load_configuration(write_config(tmp_path, content))
    assert excinfo.value.kind is kind


def test_defaults_are_production_safe(tmp_path: Path) -> None:
    configuration = load_configuration(write_config(tmp_path, VALID))
    assert configuration.force_https is True
    assert configuration.strict_transport_security is True
