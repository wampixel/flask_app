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


@mark.parametrize(
    ("overrides", "debug", "https_forced", "hsts_enabled"),
    [
        ('env = "dev"\n', True, False, False),
        ('env = "dev"\nforce_https = true\n', True, True, False),
        ('env = "dev"\nstrict_transport_security = true\n', True, False, True),
        ('env = "prod"\n', False, True, True),
        ('env = "prod"\nforce_https = false\nstrict_transport_security = false\n', False, False, False),
    ],
    ids=["dev", "dev_https", "dev_hsts", "prod", "prod_behind_proxy"],
)
def test_env_drives_debug_and_https(
    tmp_path: Path, overrides: str, debug: bool, https_forced: bool, hsts_enabled: bool
) -> None:
    configuration = load_configuration(write_config(tmp_path, overrides + '[database]\nuri = "sqlite://"\n'))
    assert configuration.DEBUG is debug
    assert configuration.https_forced is https_forced
    assert configuration.hsts_enabled is hsts_enabled


def test_unknown_env_is_rejected(tmp_path: Path) -> None:
    with raises(ConfigError) as excinfo:
        load_configuration(write_config(tmp_path, VALID.replace('"dev"', '"staging"')))
    assert excinfo.value.kind is ConfigErrorKind.INVALID_SCHEMA
