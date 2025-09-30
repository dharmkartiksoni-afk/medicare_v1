from __future__ import annotations

from typing import Iterable

from .chunker import TextChunk
from .llm import LLMClient
from .models import ChunkSummary, RelationTriple


class SummarizationPipeline:
    def __init__(self, client: LLMClient | None = None) -> None:
        self.client = client or LLMClient()

    def summarize(self, chunks: Iterable[TextChunk]) -> tuple[list[ChunkSummary], list[RelationTriple]]:
        summaries: list[ChunkSummary] = []
        relations: list[RelationTriple] = []

        for chunk in chunks:
            summary_payload = self.client.summarize_chunk(chunk.id, chunk.text)
            chunk_summary = ChunkSummary(
                chunk_id=summary_payload.get("chunk_id", chunk.id),
                summary=summary_payload.get("summary", ""),
                key_points=summary_payload.get("key_points", []),
                entities=summary_payload.get("entities", []),
                qa_pairs=summary_payload.get("qa_pairs", []),
            )
            summaries.append(chunk_summary)

            relations_payload = self.client.extract_relations(
                chunk.id,
                chunk_summary.summary,
                chunk_summary.key_points,
                chunk_summary.entities,
            )
            for rel in relations_payload.get("relations", []):
                relations.append(
                    RelationTriple(
                        source=rel.get("source", ""),
                        target=rel.get("target", ""),
                        relation=rel.get("relation", "associated_with"),
                        evidence_chunk=rel.get("evidence_chunk", chunk.id),
                    )
                )

        return summaries, relations


__all__ = ["SummarizationPipeline"]
