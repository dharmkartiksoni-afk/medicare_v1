from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

from .models import ChunkSummary, GraphEdge, GraphNode, RelationTriple


NODE_TYPE_HINTS = {
    "disease": "condition",
    "syndrome": "condition",
    "therapy": "treatment",
    "drug": "treatment",
    "medication": "treatment",
    "anatomy": "anatomy",
    "organ": "anatomy",
    "nerve": "anatomy",
}


def _infer_node_type(label: str) -> str:
    lowered = label.lower()
    for hint, node_type in NODE_TYPE_HINTS.items():
        if hint in lowered:
            return node_type
    return "concept"


def build_graph(
    summaries: Iterable[ChunkSummary], relations: Iterable[RelationTriple]
) -> tuple[list[GraphNode], list[GraphEdge]]:
    entity_counter: Counter[str] = Counter()
    entity_chunks: defaultdict[str, set[str]] = defaultdict(set)

    for summary in summaries:
        for entity in summary.entities:
            normalized = entity.strip()
            if not normalized:
                continue
            entity_counter[normalized] += 1
            entity_chunks[normalized].add(summary.chunk_id)

    nodes: list[GraphNode] = []
    for entity, count in entity_counter.most_common():
        node = GraphNode(
            id=entity,
            label=entity,
            type=_infer_node_type(entity),
            chunk_ids=sorted(entity_chunks[entity]),
        )
        nodes.append(node)

    edges: list[GraphEdge] = []
    edge_counts: Counter[tuple[str, str, str]] = Counter()
    for rel in relations:
        key = (rel.source, rel.relation, rel.target)
        edge_counts[key] += 1
        edge = GraphEdge(
            id=f"{rel.source}->{rel.relation}->{rel.target}-{edge_counts[key]}",
            source=rel.source,
            target=rel.target,
            relation=rel.relation,
            weight=float(edge_counts[key]),
            evidence_chunk=rel.evidence_chunk,
        )
        edges.append(edge)

    return nodes, edges


__all__ = ["build_graph"]
