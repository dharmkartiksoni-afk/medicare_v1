from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    summary_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-large"
    max_chunk_tokens: int = 900
    min_chunk_tokens: int = 400
    overlap_tokens: int = 120
    output_dir: Path = Path("data/output")
    input_dir: Path = Path("data/input")
    cache_dir: Path = Path(".cache")
    request_timeout: float = 45.0
    openai_base_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


__all__ = ["Settings", "get_settings"]
