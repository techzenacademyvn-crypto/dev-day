from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "TZ Shop"
    ENV: str = "development"
    DEBUG: bool = True

    # Database — required, no default: missing .env causes ValidationError at startup
    DATABASE_URL: str

    # Security & JWT — required, no default: app refuses to start without a real secret key
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Business settings
    TIMEZONE: str = "Asia/Ho_Chi_Minh"
    DEFAULT_PAGE_SIZE: int = 20

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
