# Medicare Knowledge Graph – Backend & UI Flow

This note documents how the system turns a raw medical chapter into an interactive knowledge graph, how the OpenAI calls are orchestrated, and what the trade-offs of this approach are.

## 1. Backend: pipeline + API endpoints

### Models in use

- **Summarisation & relation extraction** – OpenAI `gpt-4.1-mini` (configurable via `SUMMARY_MODEL`).
- **Embeddings** – OpenAI `text-embedding-3-large` (configurable via `EMBEDDING_MODEL`).
- **API access** – All calls are made through the official Python SDK (`OpenAI` client).

### Pipeline overview

1. **chunker.py** – Splits `data/input/<chapter>.txt` into ~900-token chunks (120-token overlap) so we keep context but stay under model limits. Each chunk receives an ID like `chapter1-003`.
2. **llm.py / summarizer.py** – Makes two OpenAI calls per chunk, using the models above:
   - `summarize_chunk` asks for a JSON payload with `summary`, `key_points[]`, `entities[]`, and `qa_pairs[]`.
   - `extract_relations` asks for structured relations `{ source, relation, target, evidence_chunk }` based on the summary/key points/entities.
3. **graph_builder.py** – Aggregates entities into unique nodes and turns relation triples into edges. Node types are inferred heuristically (checking for substrings such as “syndrome”, “drug”, “nerve”).
4. **embeddings.py** – Uses the embedding model to create vectors for each chunk summary so the search endpoint can do cosine similarity.
5. **storage.py** – Serialises the result into `data/output/<chapter>.json`. This JSON includes nodes, edges, chunk summaries, relation triples, and embedding vectors. The API serves this file; there is no separate database.

### REST endpoints (input/output)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/ingest` | `POST` | `{"chapter_id": "chapter1", "source_path": "data/input/chapter1.txt"}` (body) | `{"status": "queued", "chapter_id": "chapter1"}`. Triggers background ingest; response returns immediately. |
| `/graph/{chapter}` | `GET` | path parameter `chapter` e.g. `chapter1` | `{"chapter_id", "nodes": [...], "edges": [...], "chunks": [...]}` pulled from `data/output/<chapter>.json`. Returns 404 if the artefact isn’t generated yet. |
| `/search` | `POST` | `{"chapter_id": "chapter1", "query": "What treats hypertension?"}` | `{"results": [{"chunk_id", "score", "summary", "key_points"}, ...]}` – top 5 semantic matches. |
| `/healthz` | `GET` | none | `{"status": "ok"}` – health check. |

### How the AI decides nodes, edges, and relationships

- **Chunk IDs** – Determined deterministically during chunking (`chapterId-index`). They map summaries/relations back to the raw text.
- **Entities** – `summarize_chunk` prompt instructs the model to list “unique key medical concepts, drugs, anatomy, or procedures.” Whatever strings come back become candidate node labels.
- **Relations** – `extract_relations` prompt explicitly requests relation triples using verbs like `causes`, `treats`, `associated_with`, etc. Only relations “explicit or strongly implied” in the chunk should be returned. If the model is unsure it should respond with an empty array; we accept whatever the model sends.
- **Node types** – After we receive the entity strings, `graph_builder.py` does simple keyword matching to assign a type: strings containing “therapy/drug” become `treatment`, “syndrome/disease” → `condition`, anatomical keywords → `anatomy`, otherwise `concept` or `other`.
- **Edges** – Every relation becomes a `GraphEdge`. The edge `id` combines `source`, `relation`, `target`, plus a counter so duplicate relations are distinct. `evidence_chunk` tracks the originating chunk ID.

## 2. Frontend: rendering and interaction

1. **Data retrieval** – React Query issues `GET /api/graph/<chapter>` (forwarded to FastAPI). The result provides `nodes`, `edges`, and `chunks` arrays.
2. **Force graph preparation** – `GraphView` constructs:
   ```ts
   const graphData = {
     nodes: nodes.map((node) => ({ ...node, name: node.label })),
     links: edges
       .filter((edge) => nodeMap.has(edge.source) && nodeMap.has(edge.target))
       .map((edge) => ({ ...edge, source: edge.source, target: edge.target }))
   };
   ```
   Filtering protects the renderer from edges that reference missing nodes (rare model hallucinations).
3. **Interactivity** – Hover/selection states adjust node size, link width, and display relation labels via `linkCanvasObject`. Clicking a node centres/zooms the camera (after ensuring the ForceGraph API is ready) and selects the first chunk tied to that node so the detail panel updates.
4. **Search panel** – `POST /api/search` returns relevant chunks using vector similarity. Selecting a hit updates `selectedChunkId`, which fills the flashcard area while the graph remains untouched.

## 3. Strengths and drawbacks of this approach

**What works well**
- Minimal infrastructure: artefacts live as JSON files, so the stack stays simple (no extra DB required).
- Prompt-driven flexibility: adjusting the prompts can quickly tune how granular the notes/relations are without code changes.
- Decoupled UI: the frontend only needs node/edge metadata; it can experiment with layouts or alternate presentations freely.
- Semantic search out of the box: embeddings empower the search endpoint without custom indexing logic.

**Trade-offs / Caveats**
- OpenAI dependency: pipeline quality hinges on the model; hallucinated entities or relations can appear. We filter edges referencing missing nodes, but content accuracy isn’t guaranteed.
- Latency & cost: running through every chunk requires multiple API calls (summaries + relations + embeddings). Large chapters can take a while and incur usage fees.
- No persistence beyond JSON: concurrent edits or multi-user access would need additional storage/locking mechanisms.
- Limited node typing: heuristic string matching labels nodes; complex cases may end up as generic `concept`.
- Background worker: the FastAPI background task runs in-process; for production workloads you’d want a proper job queue so long-running ingests don’t block other requests.

## 4. Opportunities for improvement

### Output fidelity

- Add validation layer comparing relations back to the raw text before accepting them (reduces hallucinations).
- Introduce entity normalisation (e.g., map synonyms or variant spellings) so the graph merges duplicate concepts.
- Expand node typing with a lightweight NER/classifier model instead of substring heuristics.
- Persist embeddings and artefacts in a vector database / relational store to support versioning and multi-user edits.
- Provide provenance snippets (highlight text spans) alongside `evidence_chunk` for better auditability.

### UI / UX

- Offer alternative layouts (hierarchical/clustered) or allow manual reposition and pinning of nodes.
- Add filtering (by node type, relation verb, confidence) and temporal comparison between chapter revisions.
- Include tooltips for nodes with richer metadata (key points, excerpt) without leaving the graph.
- Support offline export (PDF/PNG) and sharing links to a specific node or search query.
- Add status indicators for ingest progress and graceful retry options if OpenAI requests fail.

With these constraints in mind the system is well-suited for rapid prototyping and exploration of medical content, while leaving room to harden the pipeline (e.g., validation passes, richer typing) before production deployment.
