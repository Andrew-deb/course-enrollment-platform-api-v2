from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "CourseEnrollment"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "DEBUG"

    # Auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = ""                          # sync — used by Alembic
    DATABASE_URL_ASYNC: str = ""                    # async — used by the app

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def is_debug(self) -> bool:
        return self.ENVIRONMENT == "DEBUG"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "PRODUCTION"


settings = Settings()
