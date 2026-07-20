import StressBadge from "./StressBadge.jsx";
import MoistureGauge from "./MoistureGauge.jsx";

export default function BlockCard({ block, onSelect }) {
  const r = block.latest_reading;

  return (
    <div
      className="block-card"
      role="button"
      tabIndex={0}
      onClick={() => onSelect(block.id)}
      onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && onSelect(block.id)}
    >
      <div className="block-card-top">
        <div>
          <h3 className="block-name">{block.name}</h3>
          <div className="block-variety">
            {block.variety} · {block.area_ha} ha
          </div>
        </div>
        {r && <StressBadge flag={r.stress_flag} />}
      </div>

      <MoistureGauge ratio={r?.stress_ratio} flag={r?.stress_flag} />

      <div className="block-meta-row">
        <span>{r ? r.date : "no data yet"}</span>
        {r && (
          <span className={`block-action ${r.action}`}>
            {r.action === "irrigate"
              ? `Irrigate ${r.recommended_mm} mm`
              : "Hold"}
          </span>
        )}
      </div>
    </div>
  );
}
