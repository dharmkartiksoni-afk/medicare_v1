import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { semanticSearch } from "../api";

type SearchPanelProps = {
  chapterId: string;
  onSelectChunk: (chunkId: string) => void;
};

const SearchPanel = ({ chapterId, onSelectChunk }: SearchPanelProps) => {
  const [query, setQuery] = useState("");

  const searchMutation = useMutation({
    mutationFn: (variables: { chapterId: string; query: string }) =>
      semanticSearch(variables.chapterId, variables.query)
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query) return;
    searchMutation.mutate({ chapterId, query });
  };

  return (
    <div className="search-panel">
      <form onSubmit={handleSubmit} className="search-form">
        <input
          type="text"
          value={query}
          placeholder="Ask something…"
          onChange={(event) => setQuery(event.target.value)}
        />
        <button type="submit" disabled={searchMutation.isPending}>
          {searchMutation.isPending ? "Searching…" : "Search"}
        </button>
      </form>
      <div className="search-results">
        {searchMutation.isError && <p className="error">Unable to search. Try regenerating embeddings.</p>}
        {searchMutation.data?.results.map((result) => (
          <button key={result.chunk_id} className="result-card" onClick={() => onSelectChunk(result.chunk_id)}>
            <div className="score">{result.score.toFixed(2)}</div>
            <div>
              <h4>{result.chunk_id}</h4>
              <p>{result.summary}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default SearchPanel;
