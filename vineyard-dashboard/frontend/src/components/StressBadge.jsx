const LABELS = {
  none: "No stress",
  mild: "Mild stress",
  severe: "Severe stress",
};

export default function StressBadge({ flag }) {
  const key = flag && LABELS[flag] ? flag : "none";
  return (
    <span className={`stress-badge ${key}`}>
      <span className="dot" />
      {LABELS[key]}
    </span>
  );
}
