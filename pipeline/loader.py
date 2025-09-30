from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .config import get_settings


def read_chapter(chapter_path: Path | str) -> str:
    path = Path(chapter_path)
    if not path.exists():
        settings = get_settings()
        default_path = settings.input_dir / str(chapter_path)
        if default_path.exists():
            path = default_path
        else:
            raise FileNotFoundError(f"Chapter file not found: {chapter_path}")

    return path.read_text(encoding="utf-8")


def normalize_text(text: str) -> str:
    normalized_lines: Iterable[str] = []
    lines = text.splitlines()
    cleaned: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            cleaned.append("")
            continue
        line = " ".join(line.split())
        cleaned.append(line)
    normalized_lines = cleaned
    return "\n".join(normalized_lines)


__all__ = ["read_chapter", "normalize_text"]
