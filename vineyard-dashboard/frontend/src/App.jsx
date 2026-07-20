import { useState } from "react";
import Dashboard from "./components/Dashboard.jsx";
import BlockDetail from "./components/BlockDetail.jsx";

export default function App() {
  const [selectedBlockId, setSelectedBlockId] = useState(null);

  const today = new Date().toLocaleDateString(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
  });

  return (
    <div className="app-shell">
      <header className="app-header">
        <div>
          <h1 className="app-title">Vineyard Irrigation Dashboard</h1>
          <div className="app-subtitle">ET-GEO Hackathon 2026 · block-level water use</div>
        </div>
        <div className="app-date">{today}</div>
      </header>

      {selectedBlockId ? (
        <BlockDetail blockId={selectedBlockId} onBack={() => setSelectedBlockId(null)} />
      ) : (
        <Dashboard onSelect={setSelectedBlockId} />
      )}
    </div>
  );
}
