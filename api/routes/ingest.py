from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Body

from pipeline.runner import run_pipeline

router = APIRouter(prefix="/ingest", tags=["ingest"])


def _run(chapter_id: str, source_path: str | None) -> None:
    path = Path(source_path) if source_path else None
    run_pipeline(chapter_id, path)


@router.post("")
def ingest_chapter(
    background_tasks: BackgroundTasks,
    payload: dict = Body(..., example={"chapter_id": "chapter1", "source_path": "data/input/chapter1.txt"}),
):
    chapter_id = payload.get("chapter_id")
    source_path = payload.get("source_path")
    if not chapter_id:
        return {"status": "error", "message": "chapter_id is required"}

    background_tasks.add_task(_run, chapter_id, source_path)
    return {"status": "queued", "chapter_id": chapter_id}
