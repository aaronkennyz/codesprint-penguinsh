from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "RuralHealth"
    APP_ENV: str = "dev"

    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_EXPIRES_MIN: int = 720

    FERNET_KEY: str

    CORS_ORIGINS: str = ""

    def cors_list(self) -> List[str]:
        if not self.CORS_ORIGINS.strip():
            return []
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

settings = Settings()
