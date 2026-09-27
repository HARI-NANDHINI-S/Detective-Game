import { useEffect } from "react";
import { useGame } from "../GameContext";
import { locationColor, SCENES } from "../constants";
import Header from "../components/Header";
import { soundFX } from "../utils/soundFX";

export default function ResultScene() {
  const { caseData, progress, setScene, saveGame, setProgress, score, scoreHistory, addScore } = useGame();
  const solution = progress.algorithm_solution || {};

  if (!caseData) return null;

  // True culprit computed by the Graph Coloring backtracking algorithm
  const culpritId = Object.entries(solution).find(
    ([, loc]) => loc === caseData.culprit_location
  )?.[0];
  const culprit = caseData.suspects.find((s) => s.id === culpritId);

  // Player's placed suspect in culprit location
  const playerCulpritId = Object.entries(progress.assignments || {}).find(
    ([, loc]) => loc === caseData.culprit_location
  )?.[0];
  const playerCulprit = caseData.suspects.find((s) => s.id === playerCulpritId);

  // Match condition: Player won if their placement in culprit_location matches culprit, or if algorithm solved it
  const isWon = (playerCulpritId && playerCulpritId === culpritId) || (progress.solved_by_algorithm && culpritId);

  useEffect(() => {
    if (isWon) {
      soundFX.playSuccess();
      if (!progress.case_closed) {
        setProgress((p) => ({ ...p, case_closed: true }));
        addScore(500, "YOU WON THE GAME — Case Solved!");
      }
    } else {
      soundFX.playConflict();
    }
  }, [isWon]);

  // Calculate Rank Grade
  let rank = "B";
  let rankTitle = "Detective Inspector";
  let rankColor = "var(--gold)";
  if (score >= 1200) {
    rank = "S";
    rankTitle = "MASTER DETECTIVE";
    rankColor = "var(--green)";
  } else if (score >= 800) {
    rank = "A";
    rankTitle = "SENIOR INVESTIGATOR";
    rankColor = "var(--blue)";
  }

  const culpritLocName = caseData.locations.find((l) => l.id === caseData.culprit_location)?.name.toUpperCase() || "CRIME LOCATION";

  return (
    <div className="screen">
      <Header title="CASE VERDICT & INVESTIGATION SCORECARD" subtitle={caseData.title} />
      <div className="content">
        {/* Animated Win / Lose Status Header Banner */}
        <div
          className="panel"
          style={{
            textAlign: "center",
            padding: "20px",
            marginBottom: "20px",
            background: isWon ? "rgba(30, 80, 45, 0.92)" : "rgba(80, 20, 25, 0.92)",
            borderColor: isWon ? "var(--green)" : "var(--red)",
            boxShadow: isWon ? "0 0 24px rgba(86, 178, 122, 0.4)" : "0 0 24px rgba(206, 76, 74, 0.4)",
            animation: "pulse 2s infinite alternate",
          }}
        >
          <h1
            className="title-font"
            style={{
              fontSize: 38,
              margin: 0,
              color: isWon ? "var(--green)" : "var(--red-soft)",
              letterSpacing: 2,
              textShadow: isWon ? "0 0 10px rgba(86, 178, 122, 0.6)" : "0 0 10px rgba(206, 76, 74, 0.6)",
            }}
          >
            {isWon ? "🏆 YOU WON THE GAME! 🏆" : "❌ YOU LOST THE GAME! ❌"}
          </h1>
          <div style={{ fontSize: 18, fontWeight: 700, marginTop: 8, color: "#fff" }}>
            {isWon
              ? `CASE SOLVED: Your evidence board correctly identified ${culprit?.full_name || "the culprit"} in the ${culpritLocName}!`
              : playerCulprit
              ? `WRONG ACCUSATION: You placed ${playerCulprit.full_name} in the ${culpritLocName}, but the true culprit was ${culprit?.full_name || "another suspect"}!`
              : `UNSOLVED: No suspect was placed in the ${culpritLocName}!`}
          </div>
        </div>

        {!Object.keys(solution).length ? (
          <div className="panel" style={{ borderColor: "var(--amber)", maxWidth: 720, margin: "20px auto", textAlign: "center" }}>
            <p className="amber" style={{ fontSize: 16 }}>
              No complete graph colouring solution has been evaluated yet.
            </p>
            <p className="muted">
              Open the Evidence Board, place all suspects or click <strong>ANALYZE EVIDENCE</strong> to let the solver verify placements.
            </p>
          </div>
        ) : (
          <div className="row">
            {/* Scorecard & Rank Card */}
            <div className="panel gold-edge" style={{ width: 340 }}>
              <div style={{ textAlign: "center", padding: "12px 0" }}>
                <div className="muted" style={{ fontSize: 13, letterSpacing: 1 }}>INVESTIGATOR RANK</div>
                <div className="title-font" style={{ fontSize: 64, color: rankColor, fontWeight: 900, lineHeight: 1 }}>
                  {rank}
                </div>
                <div style={{ color: rankColor, fontWeight: 800, marginTop: 4 }}>{rankTitle}</div>
                <div style={{ fontSize: 28, color: "var(--gold)", fontWeight: 900, marginTop: 12 }}>
                  {score} PTS
                </div>
              </div>

              <div className="gold" style={{ marginTop: 16 }}>SCORE BREAKDOWN</div>
              <div className="log" style={{ height: 180, marginTop: 6, fontSize: 12 }}>
                {scoreHistory.map((h, i) => (
                  <div key={i} style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                    <span className="muted">{h.reason}</span>
                    <strong className="green">+{h.pts}</strong>
                  </div>
                ))}
                {!scoreHistory.length && <div className="faint">No score actions recorded.</div>}
              </div>
            </div>

            {/* Suspect Placements */}
            <div className="panel" style={{ flex: 1 }}>
              <div className="gold">SUSPECT PLACEMENTS & SOLUTION</div>
              {caseData.suspects.map((s) => {
                const lid = solution[s.id];
                const isC = s.id === culpritId;
                const isPlayerChoice = s.id === playerCulpritId;
                return (
                  <div
                    key={s.id}
                    className="entry"
                    style={{
                      marginTop: 10,
                      background: isC ? "rgba(100, 20, 25, 0.4)" : undefined,
                      borderColor: isC ? "var(--red)" : undefined,
                    }}
                  >
                    <div className="row" style={{ alignItems: "center" }}>
                      <div
                        className="avatar"
                        style={{ width: 52, height: 52, background: locationColor(lid) }}
                      >
                        {s.name.slice(0, 2)}
                      </div>
                      <div style={{ flex: 1 }}>
                        <strong>{s.full_name}</strong>
                        <div className="muted">{s.role}</div>
                      </div>
                      <div className={isC ? "red" : "gold"} style={{ fontWeight: 800, textAlign: "right" }}>
                        {caseData.locations.find((l) => l.id === lid)?.name.toUpperCase()}
                        {isC && <div style={{ fontSize: 11, color: "var(--red)" }}>TRUE THIEF (AT CRIME SITE)</div>}
                        {isPlayerChoice && !isC && <div style={{ fontSize: 11, color: "var(--amber)" }}>YOUR ACCUSATION</div>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Verdict Details */}
            <div className="panel gold-edge card-list" style={{ flex: 1 }}>
              <div className="title-font gold" style={{ fontSize: 24 }}>
                {isWon ? "CASE CLOSED — VICTORY ✓" : "CASE UNRESOLVED — DEFEAT ✗"}
              </div>
              <div className={isWon ? "green" : "red"} style={{ fontSize: 18, fontWeight: 900 }}>
                THE THIEF: {culprit ? `${culprit.full_name.toUpperCase()} (${culprit.role.toUpperCase()})` : "UNSOLVED"}
              </div>
              <p>
                The board places exactly one person inside the {culpritLocName} during the theft window ({caseData.theft_window}):{" "}
                <strong>{culprit?.full_name}</strong>.
              </p>
              <div className="gold">HOW IT WAS DONE</div>
              <p className="muted">{caseData.conclusion?.how}</p>
              <p className="muted">{caseData.conclusion?.why}</p>
            </div>
          </div>
        )}

        <div className="nav-row" style={{ marginTop: 20 }}>
          <button className={!isWon ? "gold" : ""} onClick={() => setScene(SCENES.BOARD)}>
            {isWon ? "EVIDENCE BOARD" : "TRY AGAIN (BACK TO BOARD)"}
          </button>
          <button onClick={() => setScene(SCENES.DAA)}>DAA EXPLANATION</button>
          <button onClick={() => setScene(SCENES.ANALYSIS)}>RE-RUN ANALYSIS</button>
          <button onClick={saveGame}>SAVE CASE</button>
        </div>
      </div>
    </div>
  );
}

