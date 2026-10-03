from pathlib import Path

from pytest import MonkeyPatch, mark, raises

from app.configuration import CONF_ENV_VAR, AppConfig, ConfigError, ConfigErrorKind, load_configuration

VALID = 'env = "dev"\n[database]\nuri = "sqlite://"\n'


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
    with raises(ConfigError) as excinfo:
        load_configuration()
    assert excinfo.value.kind is ConfigErrorKind.MISSING_PATH


def test_unreadable_file_is_typed(tmp_path: Path) -> None:
    with raises(ConfigError) as excinfo:
        load_configuration(str(tmp_path / "absent.toml"))
    assert excinfo.value.kind is ConfigErrorKind.UNREADABLE


@mark.parametrize(
    ("content", "kind"),
    [
        ("env = ", ConfigErrorKind.INVALID_TOML),
        ('env = "dev"\n', ConfigErrorKind.INVALID_SCHEMA),
        (VALID + 'unknown = "x"\n', ConfigErrorKind.INVALID_SCHEMA),
    ],
    ids=["malformed", "missing_database", "unknown_key"],
)
def test_bad_content_is_typed(tmp_path: Path, content: str, kind: ConfigErrorKind) -> None:
    with raises(ConfigError) as excinfo:
        load_configuration(write_config(tmp_path, content))
    assert excinfo.value.kind is kind
