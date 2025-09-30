from __future__ import annotations

from typing import Iterable

from .llm import LLMClient
from .models import ChunkSummary, EmbeddingRecord


def generate_embeddings(
    summaries: Iterable[ChunkSummary], client: LLMClient | None = None
) -> list[EmbeddingRecord]:
    llm_client = client or LLMClient()
    texts = [f"{summary.summary}\nKey points: {'; '.join(summary.key_points)}" for summary in summaries]
    vectors = llm_client.embed_texts(texts)
    records = [
        EmbeddingRecord(chunk_id=s.chunk_id, vector=vec)
        for s, vec in zip(summaries, vectors, strict=True)
    ]
    return records


__all__ = ["generate_embeddings"]
