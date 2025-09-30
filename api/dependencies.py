from __future__ import annotations

from fastapi import Depends

from pipeline.config import Settings, get_settings


def get_config(settings: Settings = Depends(get_settings)) -> Settings:
    return settings


__all__ = ["get_config"]
