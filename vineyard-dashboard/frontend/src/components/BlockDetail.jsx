import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import { getBlock, getReadings } from "../api.js";
import StressBadge from "./StressBadge.jsx";

export default function BlockDetail({ blockId, onBack }) {
  const [block, setBlock] = useState(null);
  const [readings, setReadings] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    Promise.all([getBlock(blockId), getReadings(blockId, 30)])
      .then(([b, r]) => {
        if (cancelled) return;
        setBlock(b);
        setReadings(r);
      })
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [blockId]);

  if (error) return <div className="state-msg">Couldn't load this block: {error}</div>;
  if (!block) return <div className="state-msg">Loading block…</div>;

  const latest = readings[readings.length - 1];

  return (
    <div>
      <button className="back-link" onClick={onBack}>
        ← Back to all blocks
      </button>

      <div className="detail-header">
        <div>
          <h2 className="detail-title">{block.name}</h2>
          <div className="detail-sub">
            {block.variety} · {block.area_ha} ha · {block.soil_type}
            {block.planted_year ? ` · planted ${block.planted_year}` : ""}
          </div>
        </div>

        {latest && (
          <div className="recommend-panel">
            <div className="headline">
              {latest.action === "irrigate"
                ? `Irrigate ${latest.recommended_mm} mm today`
                : "Hold — no irrigation needed"}
            </div>
            <div className="figure">
              ETo {latest.eto_mm} mm · ETa {latest.eta_mm} mm
            </div>
            <div style={{ marginTop: "0.5rem" }}>
              <StressBadge flag={latest.stress_flag} />
            </div>
          </div>
        )}
      </div>

      <div className="chart-panel">
        <div className="legend-row">
          <span>
            <span className="legend-swatch" style={{ background: "#c69a2a" }} />
            ETo (reference)
          </span>
          <span>
            <span className="legend-swatch" style={{ background: "#2c6b5b" }} />
            ETa (actual)
          </span>
        </div>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={readings} margin={{ top: 4, right: 12, left: -12, bottom: 0 }}>
            <CartesianGrid stroke="#c3cabf" strokeDasharray="3 3" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#5c6058" }}
              tickFormatter={(d) => d.slice(5)}
            />
            <YAxis
              tick={{ fontFamily: "IBM Plex Mono", fontSize: 11, fill: "#5c6058" }}
              unit="mm"
              width={48}
            />
            <Tooltip
              contentStyle={{
                fontFamily: "IBM Plex Mono",
                fontSize: 12,
                borderRadius: 8,
                border: "1px solid #c3cabf",
              }}
            />
            <Line type="monotone" dataKey="eto_mm" stroke="#c69a2a" strokeWidth={2} dot={false} name="ETo" />
            <Line type="monotone" dataKey="eta_mm" stroke="#2c6b5b" strokeWidth={2.5} dot={false} name="ETa" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <table className="readings-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>ETo (mm)</th>
            <th>ETa (mm)</th>
            <th>Ratio</th>
            <th>Stress</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {[...readings].reverse().map((r) => (
            <tr key={r.id}>
              <td>{r.date}</td>
              <td>{r.eto_mm}</td>
              <td>{r.eta_mm}</td>
              <td>{r.stress_ratio}</td>
              <td><StressBadge flag={r.stress_flag} /></td>
              <td>
                {r.action === "irrigate" ? `Irrigate ${r.recommended_mm} mm` : "Hold"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
