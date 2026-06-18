"""
Centralised application configuration.

Loads from environment / .env file. Every setting has a safe default so the
service boots without any configuration (in mock mode).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Provider API keys ---
    MARKETAUX_API_KEY: str = ""
    FINNHUB_API_KEY: str = ""
    FMP_API_KEY: str = ""
    ALPHA_VANTAGE_API_KEY: str = ""
    TWELVE_DATA_API_KEY: str = ""
    NGX_API_KEY: str = ""   # NGX Pulse — Nigerian Exchange data (ngxpulse.ng)

    # --- LLM ---
    LLM_API_KEY: str = ""
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"

    # --- Auth ---
    JWT_SECRET: str = "dev-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # --- App ---
    DATABASE_URL: str = "sqlite+aiosqlite:///./nexora.db"
    CACHE_TTL_SECONDS: int = 60
    CORS_ORIGINS: str = "*"
    ENV: str = "development"

    # --- Plan limits ---
    FREE_WATCHLIST_LIMIT: int = 5

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def llm_enabled(self) -> bool:
        return bool(self.LLM_API_KEY)

    def provider_status(self) -> dict:
        """Which providers have keys configured."""
        return {
            "ngx_pulse": bool(self.NGX_API_KEY),
            "marketaux": bool(self.MARKETAUX_API_KEY),
            "finnhub": bool(self.FINNHUB_API_KEY),
            "fmp": bool(self.FMP_API_KEY),
            "alpha_vantage": bool(self.ALPHA_VANTAGE_API_KEY),
            "twelve_data": bool(self.TWELVE_DATA_API_KEY),
            "llm": self.llm_enabled,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
