import { useMemo, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import GraphView from "./components/GraphView";
import SearchPanel from "./components/SearchPanel";
import ChunkDetail from "./components/ChunkDetail";
import { ChunkSummary, fetchGraph, triggerIngest } from "./api";

const DEFAULT_CHAPTER = "chapter1";

const App = () => {
  const [chapterId, setChapterId] = useState(DEFAULT_CHAPTER);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedChunkId, setSelectedChunkId] = useState<string | null>(null);

  const graphQuery = useQuery({
    queryKey: ["graph", chapterId],
    queryFn: () => fetchGraph(chapterId),
    staleTime: 60_000
  });

  const ingestMutation = useMutation({
    mutationFn: (variables: { chapterId: string; sourcePath?: string }) =>
      triggerIngest(variables.chapterId, variables.sourcePath),
    onSuccess: () => {
      graphQuery.refetch();
    }
  });

  const chunkMap = useMemo(() => {
    const record: Record<string, ChunkSummary> = {};
    graphQuery.data?.chunks.forEach((chunk) => {
      record[chunk.chunk_id] = chunk;
    });
    return record;
  }, [graphQuery.data?.chunks]);

  const selectedChunk = selectedChunkId ? chunkMap[selectedChunkId] ?? null : null;

  const handleNodeSelect = (nodeId: string) => {
    setSelectedNodeId(nodeId);
    const chunkId = graphQuery.data?.nodes.find((node) => node.id === nodeId)?.chunk_ids[0];
    if (chunkId) {
      setSelectedChunkId(chunkId);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <header>
          <h1>Medical Knowledge Graph</h1>
          <p>Generate study notes and explore relationships across the chapter.</p>
        </header>
        <div className="controls">
          <label htmlFor="chapter">Chapter ID</label>
          <input
            id="chapter"
            value={chapterId}
            onChange={(event) => setChapterId(event.target.value)}
            placeholder="chapter1"
          />
          <button
            onClick={() => ingestMutation.mutate({ chapterId, sourcePath: `data/input/${chapterId}.txt` })}
            disabled={ingestMutation.isPending}
          >
            {ingestMutation.isPending ? "Generating…" : "Generate / Refresh"}
          </button>
          {ingestMutation.data && <small className="hint">Pipeline queued. Refresh to see new data.</small>}
          {graphQuery.isError && <p className="error">Load a chapter to view the graph.</p>}
        </div>
        <SearchPanel
          chapterId={chapterId}
          onSelectChunk={(chunkId) => {
            setSelectedChunkId(chunkId);
            setSelectedNodeId(null);
          }}
        />
        <ChunkDetail chunk={selectedChunk} />
      </aside>
      <main className="graph-area">
        {graphQuery.isLoading && <p className="loading">Loading graph…</p>}
        {graphQuery.data && graphQuery.data.nodes.length > 0 ? (
          <GraphView
            nodes={graphQuery.data.nodes}
            edges={graphQuery.data.edges}
            selectedNodeId={selectedNodeId}
            onNodeSelect={handleNodeSelect}
          />
        ) : (
          !graphQuery.isLoading && <p className="empty-state">Run the pipeline to visualize the graph.</p>
        )}
      </main>
    </div>
  );
};

export default App;
