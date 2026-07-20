const RADIUS = 45;
const CIRCUMFERENCE = Math.PI * RADIUS; // half-circle arc length

const FLAG_COLOR = {
  none: "#4d6a56",
  mild: "#c69a2a",
  severe: "#b85a2e",
};

/** Semi-circular dial reading ETa/ETo like a sensor gauge. ratio in [0,1+]. */
export default function MoistureGauge({ ratio, flag }) {
  const clamped = Math.max(0, Math.min(ratio ?? 0, 1.1));
  const offset = CIRCUMFERENCE * (1 - Math.min(clamped, 1));
  const color = FLAG_COLOR[flag] || FLAG_COLOR.none;

  return (
    <div className="gauge-wrap">
      <svg width="120" height="76" viewBox="0 0 120 76">
        <path
          d="M 15 60 A 45 45 0 0 1 105 60"
          fill="none"
          stroke="#c3cabf"
          strokeWidth="8"
          strokeLinecap="round"
        />
        <path
          d="M 15 60 A 45 45 0 0 1 105 60"
          fill="none"
          stroke={color}
          strokeWidth="8"
          strokeLinecap="round"
          strokeDasharray={CIRCUMFERENCE}
          strokeDashoffset={offset}
          style={{ transition: "stroke-dashoffset 0.4s ease" }}
        />
        <text x="60" y="52" textAnchor="middle" className="gauge-value">
          {ratio != null ? ratio.toFixed(2) : "—"}
        </text>
        <text x="60" y="68" textAnchor="middle" className="gauge-label">
          ETa / ETo
        </text>
      </svg>
    </div>
  );
}
