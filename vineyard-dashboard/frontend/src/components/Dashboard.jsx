import { useEffect, useState } from "react";
import { getBlocks } from "../api.js";
import BlockCard from "./BlockCard.jsx";

export default function Dashboard({ onSelect }) {
  const [blocks, setBlocks] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    getBlocks().then(setBlocks).catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="state-msg">
        Couldn't reach the API — is the backend running on :8000? ({error})
      </div>
    );
  }
  if (!blocks) return <div className="state-msg">Loading blocks…</div>;
  if (blocks.length === 0) {
    return (
      <div className="state-msg">
        No blocks yet — run <code>python -m app.seed_data</code> in the backend.
      </div>
    );
  }

  return (
    <div className="block-grid">
      {blocks.map((b) => (
        <BlockCard key={b.id} block={b} onSelect={onSelect} />
      ))}
    </div>
  );
}
