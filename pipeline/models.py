from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class ChunkSummary(BaseModel):
    chunk_id: str
    summary: str
    key_points: list[str]
    entities: list[str]
    qa_pairs: list[dict[str, str]]


class RelationTriple(BaseModel):
    source: str
    target: str
    relation: str
    evidence_chunk: str


class GraphNode(BaseModel):
    id: str
    label: str
    type: Literal["concept", "condition", "treatment", "anatomy", "other"] = "concept"
    chunk_ids: list[str] = Field(default_factory=list)


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    relation: str
    weight: float = 1.0
    evidence_chunk: str


class EmbeddingRecord(BaseModel):
    chunk_id: str
    vector: list[float]


class ChapterArtifacts(BaseModel):
    chapter_id: str
    source_path: Path
    created_at: datetime
    chunks: list[ChunkSummary]
    relations: list[RelationTriple]
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    embeddings: list[EmbeddingRecord]


__all__ = [
    "ChunkSummary",
    "RelationTriple",
    "GraphNode",
    "GraphEdge",
    "EmbeddingRecord",
    "ChapterArtifacts",
]
