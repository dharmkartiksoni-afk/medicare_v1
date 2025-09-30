from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import tiktoken

from .config import get_settings


@dataclass
class TextChunk:
    id: str
    text: str
    start_token: int
    end_token: int


class ChapterChunker:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk(self, chapter_id: str, text: str) -> list[TextChunk]:
        tokens = self.encoding.encode(text)
        max_tokens = self.settings.max_chunk_tokens
        min_tokens = self.settings.min_chunk_tokens
        overlap = self.settings.overlap_tokens

        chunks: list[TextChunk] = []
        start = 0
        chunk_index = 0
        total = len(tokens)

        while start < total:
            end = min(start + max_tokens, total)
            chunk_tokens = tokens[start:end]
            if len(chunk_tokens) < min_tokens and chunks:
                previous = chunks[-1]
                merged = self.encoding.encode(previous.text) + chunk_tokens
                previous.text = self.encoding.decode(merged)
                previous.end_token = end
                break

            chunk_text = self.encoding.decode(chunk_tokens)
            chunk_id = f"{chapter_id}-{chunk_index:03d}"
            chunks.append(TextChunk(id=chunk_id, text=chunk_text, start_token=start, end_token=end))
            chunk_index += 1

            if end >= total:
                break
            start = end - overlap
            if start < 0:
                start = 0

        return chunks


def chunk_chapter(chapter_id: str, text: str) -> list[TextChunk]:
    return ChapterChunker().chunk(chapter_id, text)


__all__ = ["TextChunk", "ChapterChunker", "chunk_chapter"]
