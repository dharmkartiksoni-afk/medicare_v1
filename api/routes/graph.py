from __future__ import annotations

from fastapi import APIRouter, HTTPException

from pipeline.storage import load_artifacts

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/{chapter_id}")
def get_graph(chapter_id: str):
    try:
        artifacts = load_artifacts(chapter_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "chapter_id": artifacts.chapter_id,
        "nodes": [node.model_dump() for node in artifacts.nodes],
        "edges": [edge.model_dump() for edge in artifacts.edges],
        "chunks": [chunk.model_dump() for chunk in artifacts.chunks],
    }
