from __future__ import annotations

import math
from typing import Any

import numpy as np
from fastapi import APIRouter, Body, HTTPException

from pipeline.llm import LLMClient
from pipeline.storage import load_artifacts

router = APIRouter(prefix="/search", tags=["search"])


def _cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    a = np.array(vec_a)
    b = np.array(vec_b)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    if denom == 0:
        return 0.0
    return float(np.dot(a, b) / denom)


@router.post("")
def semantic_search(
    payload: dict[str, Any] = Body(..., example={"chapter_id": "chapter1", "query": "What treats hypertension?"})
):
    chapter_id = payload.get("chapter_id")
    query = payload.get("query")
    if not chapter_id or not query:
        raise HTTPException(status_code=400, detail="chapter_id and query are required")

    try:
        artifacts = load_artifacts(chapter_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    if not artifacts.embeddings:
        raise HTTPException(status_code=400, detail="No embeddings available for this chapter")

    client = LLMClient()
    query_vector = client.embed_texts([query])[0]

    scored_chunks = []
    chunk_map = {chunk.chunk_id: chunk for chunk in artifacts.chunks}
    for record in artifacts.embeddings:
        score = _cosine_similarity(record.vector, query_vector)
        chunk = chunk_map.get(record.chunk_id)
        if chunk:
            scored_chunks.append({
                "chunk_id": record.chunk_id,
                "score": score,
                "summary": chunk.summary,
                "key_points": chunk.key_points,
            })

    scored_chunks.sort(key=lambda item: item["score"], reverse=True)
    return {"results": scored_chunks[:5]}
