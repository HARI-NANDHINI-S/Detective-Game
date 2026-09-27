import { useGame } from "../GameContext";

export default function Header({ title, subtitle, right }) {
  const { casesList, selectedCaseId, changeCase, score } = useGame();

  return (
    <header className="header" style={{ alignItems: "center" }}>
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        {/* Score Badge */}
        <div
          style={{
            background: "rgba(214, 172, 88, 0.15)",
            border: "1px solid var(--gold)",
            borderRadius: 6,
            padding: "4px 12px",
            color: "var(--gold)",
            fontWeight: 800,
            fontSize: 14,
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          🏆 SCORE: {score} PTS
        </div>

        {/* Case Selector Dropdown */}
        {casesList && casesList.length > 0 && (
          <select
            value={selectedCaseId}
            onChange={(e) => changeCase(e.target.value)}
            style={{
              background: "var(--panel-light)",
              border: "1px solid var(--gold-dark)",
              color: "var(--gold)",
              fontWeight: 700,
              padding: "6px 10px",
              borderRadius: 6,
              cursor: "pointer",
            }}
          >
            {casesList.map((c, i) => (
              <option key={c.case_id} value={c.case_id}>
                CASE {i + 1}: {c.title}
              </option>
            ))}
          </select>
        )}

        {right}
      </div>
    </header>
  );
}
