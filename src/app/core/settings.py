import os

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    def __init__(self, **data):
        super().__init__(**data)

    server: str = "dev"

    server_host: str
    server_port: int
    server_domain: str = ""

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str
    jwt_access_token_expire_minutes: int
    jwt_refresh_token_expire_days: int

    celery_broker_url: str
    celery_result_backend: str

    libre_url: str

    cors_origins: list[AnyHttpUrl] = []  # ["*"]

    root_dir: str
    static_content_dir: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    @property
    def is_production(self) -> bool:
        return self.server == "production"

    @property
    def media_dir(self) -> str:
        return os.path.join(self.static_content_dir, "media")

    @property
    def domain(self) -> str:
        if not self.server_domain:
            return f"http://{self.server_host}:{self.server_port}"
        return f"https://{self.server_domain}"

    @property
    def allow_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.cors_origins if str(origin)]


settings: Settings = Settings()
