from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from openai import OpenAI

from .config import get_settings


class LLMClient:
    def __init__(self) -> None:
        settings = get_settings()
        client_kwargs: dict[str, Any] = {"api_key": settings.openai_api_key}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        self.client = OpenAI(**client_kwargs)
        self.settings = settings

    def _call_model(self, prompt: str) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.settings.summary_model,
            input=prompt,
            timeout=self.settings.request_timeout,
        )
        content = response.output_text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError as exc:  # pragma: no cover
                    raise ValueError(f"Failed to parse JSON from model response: {content}") from exc
            raise ValueError(f"Failed to parse JSON from model response: {content}")

    def summarize_chunk(self, chunk_id: str, text: str) -> dict[str, Any]:
        prompt = f"""
You are a careful medical editor assisting in study note generation.
Return valid JSON matching:
{{
  "chunk_id": string,
  "summary": string,
  "key_points": string[],
  "entities": string[],
  "qa_pairs": {{"question": string, "answer": string}}[]
}}

Rules:
- Stick closely to the source.
- Use empty lists when unsure.
- Keep answers short.

Chunk ID: {chunk_id}
Text:```\n{text}\n```
"""
        return self._call_model(prompt)

    def extract_relations(self, chunk_id: str, summary: str, key_points: List[str], entities: List[str]) -> dict[str, Any]:
        prompt = f"""
Analyze the medical notes and output JSON with a top-level key `relations` containing objects:
{{"source": string, "relation": string, "target": string, "evidence_chunk": string}}

Guidelines:
- Only include relations explicit or strongly implied.
- Use entity labels whenever possible.
- Choose relation verbs like causes, treats, associated_with, contraindicated_in, part_of, located_in.
- Set evidence_chunk to {chunk_id}.
- Return {{"relations": []}} when nothing confident is found.

Chunk ID: {chunk_id}
Summary: {summary}
Key Points: {key_points}
Entities: {entities}
"""
        return self._call_model(prompt)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.settings.embedding_model,
            input=texts,
            timeout=self.settings.request_timeout,
        )
        return [item.embedding for item in response.data]


__all__ = ["LLMClient"]
