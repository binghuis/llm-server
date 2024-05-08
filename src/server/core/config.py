import secrets
from typing import ClassVar, List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    api_prefix: ClassVar[str] = "/api"
    secret_key: ClassVar[str] = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    access_token_expire_minutes: ClassVar[int] = 60 * 24 * 8
    # cors_origins is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    cors_origins: ClassVar[List[str]] = ["*"]
    # db_url = "postgresql://localhost"
    db_url: ClassVar[str] = "sqlite:///./sql_app.db"
    echo_sql: ClassVar[bool] = True


settings = Settings()
