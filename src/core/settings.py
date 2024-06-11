import os
from pathlib import Path
from typing import (
    Final,
    List,
    Optional,
    Union,
)

from dotenv import find_dotenv, load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv(raise_error_if_not_found=True))

_PathLike = Union[os.PathLike[str], str, Path]


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
PROJECT_NAME = os.getenv("PROJECT_NAME", "")
PROJECT_VERSION = os.getenv("PROJECT_VERSION", "")

LOGGING_FORMAT: Final[str] = "%(asctime)s %(name)s %(levelname)s -> %(message)s"
DATETIME_FORMAT: Final[str] = "%Y.%m.%d %H:%M"


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def path(*paths: _PathLike, base_path: Optional[_PathLike] = None) -> str:
    if base_path is None:
        base_path = root_dir()

    return os.path.join(base_path, *paths)


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="DB_",
        extra="ignore",
    )

    uri: str = Field(default="")
    name: str = Field(default="")
    host: Optional[str] = None
    port: Optional[int] = None
    user: Optional[str] = None
    password: Optional[str] = None
    connection_pool_size: int = 10
    connection_max_overflow: int = 90
    connection_pool_pre_ping: bool = True

    @property
    def url(self) -> str:
        if "sqlite" in self.uri:
            return self.uri.format(self.name)
        return self.uri.format(
            self.user,
            self.password,
            self.host,
            self.port,
            self.name,
        )


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="REDIS_",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 6379
    password: Optional[str] = None


class ServerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SERVER_",
        extra="ignore",
    )
    methods: List[str] = ["*"]
    headers: List[str] = ["*"]
    origins: List[str] = ["*"]
    host: str = "127.0.0.1"
    port: int = 8080


class CipherSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="CIPHER_",
        extra="ignore",
    )
    algorithm: str = ""
    secret_key: str = ""
    public_key: str = ""
    access_token_expire_seconds: int = 0
    refresh_token_expire_seconds: int = 0


class Settings(BaseSettings):
    db: DatabaseSettings
    redis: RedisSettings
    server: ServerSettings
    ciphers: CipherSettings


def load_settings(
    db: Optional[DatabaseSettings] = None,
    redis: Optional[RedisSettings] = None,
    server: Optional[ServerSettings] = None,
    ciphers: Optional[CipherSettings] = None,
) -> Settings:
    return Settings(
        db=db or DatabaseSettings(),
        redis=redis or RedisSettings(),
        server=server or ServerSettings(),
        ciphers=ciphers or CipherSettings(),
    )
