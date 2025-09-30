import { ChunkSummary } from "../api";

type Props = {
  chunk: ChunkSummary | null;
};

const ChunkDetail = ({ chunk }: Props) => {
  if (!chunk) {
    return (
      <div className="chunk-detail empty">
        <p>Select a node or search result to see details.</p>
      </div>
    );
  }

  return (
    <div className="chunk-detail">
      <h3>{chunk.chunk_id}</h3>
      <p className="summary">{chunk.summary}</p>
      <div className="key-points">
        <h4>Key Points</h4>
        <ul>
          {chunk.key_points.map((point, index) => (
            <li key={index}>{point}</li>
          ))}
        </ul>
      </div>
      <div className="qa">
        <h4>Flashcards</h4>
        <ul>
          {chunk.qa_pairs.map((pair, index) => (
            <li key={index}>
              <strong>Q:</strong> {pair.question}
              <br />
              <strong>A:</strong> {pair.answer}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default ChunkDetail;
