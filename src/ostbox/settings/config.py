from pathlib import Path
from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


SETTINGS_DIR = Path(__file__).resolve().parent
SRC_DIR = SETTINGS_DIR.parent.parent
PROJECT_ROOT = SRC_DIR.parent


class AppSettings(BaseSettings):
    
    SECRET_KEY: str = Field(..., description="Секретный ключ Django")
    DEBUG: bool = Field(default=False, description="Режим отладки")
    ALLOWED_HOSTS: list[str] = Field(default=["127.0.0.1", "localhost"])
    
    DATABASE_URL: str = Field(default=f"sqlite:///{SRC_DIR}/db.sqlite3")

    PAGE_SIZE: int = Field(default=10, description="Количество элементов на странице")
    
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = AppSettings()
