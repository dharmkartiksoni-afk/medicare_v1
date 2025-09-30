from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .config import get_settings
from .models import ChapterArtifacts, ChunkSummary, EmbeddingRecord, GraphEdge, GraphNode, RelationTriple


def save_artifacts(
    chapter_id: str,
    source_path: Path,
    chunks: list[ChunkSummary],
    relations: list[RelationTriple],
    nodes: list[GraphNode],
    edges: list[GraphEdge],
    embeddings: list[EmbeddingRecord],
) -> Path:
    settings = get_settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    payload = ChapterArtifacts(
        chapter_id=chapter_id,
        source_path=source_path,
        created_at=datetime.utcnow(),
        chunks=chunks,
        relations=relations,
        nodes=nodes,
        edges=edges,
        embeddings=embeddings,
    )
    output_path = settings.output_dir / f"{chapter_id}.json"
    output_path.write_text(payload.model_dump_json(indent=2), encoding="utf-8")
    return output_path


def load_artifacts(chapter_id: str) -> ChapterArtifacts:
    settings = get_settings()
    path = settings.output_dir / f"{chapter_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Artifacts for chapter '{chapter_id}' not found at {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    return ChapterArtifacts(**data)


__all__ = ["save_artifacts", "load_artifacts"]
