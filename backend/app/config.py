from typing import List, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "sqlite:///./dev.db"

    # LLM provider: "auto" picks Groq if GROQ_API_KEY is set, else Gemini if
    # GEMINI_API_KEY is set, else the rule-based fallback. "none" forces fallback.
    LLM_PROVIDER: Literal["auto", "groq", "gemini", "none"] = "auto"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"
    LLM_TIMEOUT_SECONDS: float = 20.0

    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    PORT: int = 8000

    def cors_origins_list(self) -> List[str]:
        return [x.strip() for x in self.CORS_ORIGINS.split(",") if x.strip()]

    def resolved_provider(self) -> str:
        if self.LLM_PROVIDER == "groq":
            return "groq" if self.GROQ_API_KEY else "none"
        if self.LLM_PROVIDER == "gemini":
            return "gemini" if self.GEMINI_API_KEY else "none"
        if self.LLM_PROVIDER == "auto":
            if self.GROQ_API_KEY:
                return "groq"
            if self.GEMINI_API_KEY:
                return "gemini"
        return "none"


settings = Settings()
