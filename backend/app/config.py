from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./dev.db"
    HUGGINGFACE_API_TOKEN: str = ""
    HUGGINGFACE_MODEL: str = "google/gemma-2-9b-it"
    USE_HUGGINGFACE: bool = False
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    PORT: int = 8000

    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]


settings = Settings()
