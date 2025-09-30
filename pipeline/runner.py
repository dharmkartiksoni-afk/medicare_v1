from __future__ import annotations

from pathlib import Path

from .chunker import chunk_chapter
from .embeddings import generate_embeddings
from .graph_builder import build_graph
from .loader import normalize_text, read_chapter
from .llm import LLMClient
from .storage import save_artifacts
from .summarizer import SummarizationPipeline


def run_pipeline(chapter_id: str, source_path: Path | None = None) -> Path:
    text = read_chapter(source_path or chapter_id)
    normalized = normalize_text(text)
    chunks = chunk_chapter(chapter_id, normalized)

    client = LLMClient()
    summarizer = SummarizationPipeline(client)
    summaries, relations = summarizer.summarize(chunks)
    nodes, edges = build_graph(summaries, relations)
    embeddings = generate_embeddings(summaries, client)

    return save_artifacts(
        chapter_id=chapter_id,
        source_path=Path(source_path) if source_path else Path(chapter_id),
        chunks=summaries,
        relations=relations,
        nodes=nodes,
        edges=edges,
        embeddings=embeddings,
    )


__all__ = ["run_pipeline"]
