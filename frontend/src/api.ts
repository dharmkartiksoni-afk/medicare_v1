import axios from "axios";

const client = axios.create({
  baseURL: "/api"
});

export type GraphNode = {
  id: string;
  label: string;
  type: string;
  chunk_ids: string[];
};

export type GraphEdge = {
  id: string;
  source: string;
  target: string;
  relation: string;
  weight: number;
  evidence_chunk: string;
};

export type ChunkSummary = {
  chunk_id: string;
  summary: string;
  key_points: string[];
  entities: string[];
  qa_pairs: { question: string; answer: string }[];
};

export async function fetchGraph(chapterId: string) {
  const { data } = await client.get<{ chapter_id: string; nodes: GraphNode[]; edges: GraphEdge[]; chunks: ChunkSummary[] }>(
    `/graph/${chapterId}`
  );
  return data;
}

export async function triggerIngest(chapterId: string, sourcePath?: string) {
  const { data } = await client.post(`/ingest`, { chapter_id: chapterId, source_path: sourcePath });
  return data;
}

export async function semanticSearch(chapterId: string, query: string) {
  const { data } = await client.post<{ results: { chunk_id: string; score: number; summary: string; key_points: string[] }[] }>(
    `/search`,
    { chapter_id: chapterId, query }
  );
  return data;
}
