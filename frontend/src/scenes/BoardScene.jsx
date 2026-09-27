import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import { locationColor, SCENES } from "../constants";
import GraphBoard from "../components/GraphBoard";
import Header from "../components/Header";
import SceneNav from "../components/SceneNav";
import { soundFX } from "../utils/soundFX";

export default function BoardScene() {
  const { caseData, progress, setProgress, setScene, showToast, readyForBoard } = useGame();
  const [selected, setSelected] = useState(null);
  const [message, setMessage] = useState("");
  const [messageColor, setMessageColor] = useState("var(--text-dim)");
  const [conflictPair, setConflictPair] = useState(null);
  const [constraints, setConstraints] = useState([]);

  useEffect(() => {
    const onKey = (e) => {
      if (!selected) return;
      const keys = ["1", "2", "3", "4"];
      if (keys.includes(e.key)) {
        const loc = caseData.locations[Number(e.key) - 1];
        if (loc) assign(loc.id);
      }
      if (e.key === "Backspace" || e.key === "Delete" || e.key === "0") {
        unassign(selected);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selected, caseData, progress.assignments]);

  useEffect(() => {
    if (!caseData) return;
    api
      .count({
        found_evidence: progress.found_evidence,
        interviewed: progress.interviewed,
        cap: 3,
      })
      .then((r) => setConstraints(r.constraints || []))
      .catch(() => {});
  }, [caseData, progress.found_evidence, progress.interviewed]);

  if (!caseData) return null;
  const edges = constraints.filter((c) => c.type === "edge").map((c) => [c.a, c.b]);

  const assign = async (locationId) => {
    soundFX.playClick();
    if (!selected) {
      setMessage("Pick a suspect on the board first.");
      setMessageColor("var(--amber)");
      return;
    }
    try {
      const res = await api.validate({
        found_evidence: progress.found_evidence,
        interviewed: progress.interviewed,
        suspect: selected,
        location: locationId,
        assignment: progress.assignments,
      });
      if (!res.valid) {
        soundFX.playConflict();
        setMessage(res.pretty || res.reason);
        setMessageColor("var(--red)");
        showToast(res.pretty || res.reason, "var(--red)", 3.6);
        setConflictPair(res.blame ? [selected, res.blame] : null);
        return;
      }
      soundFX.playClick();
      setConflictPair(null);
      setProgress({
        ...progress,
        assignments: { ...progress.assignments, [selected]: locationId },
      });
      const name = caseData.suspects.find((s) => s.id === selected)?.name;
      const loc = caseData.locations.find((l) => l.id === locationId)?.name;
      setMessage(`Valid: ${name} placed in the ${loc}.`);
      setMessageColor("var(--green)");
    } catch (e) {
      showToast(e.message, "var(--red)");
    }
  };

  const unassign = (sid) => {
    soundFX.playClick();
    const next = { ...progress.assignments };
    delete next[sid];
    setProgress({ ...progress, assignments: next });
    setConflictPair(null);
  };

  const checkBoard = () => {
    soundFX.playClick();
    if (!readyForBoard) {
      showToast(
        "Some evidence or statements are still missing - the board is under-constrained.",
        "var(--amber)",
        4
      );
    }
    const missing = caseData.suspects.filter((s) => !progress.assignments[s.id]);
    if (missing.length) {
      soundFX.playConflict();
      setMessage("Still unplaced: " + missing.map((s) => s.name).join(", "));
      setMessageColor("var(--amber)");
      return;
    }
    soundFX.playClue();
    setMessage(
      "Every constraint is satisfied. Click SUBMIT VERDICT to check if you won!"
    );
    setMessageColor("var(--green)");
    showToast("Consistent board! Now click SUBMIT VERDICT.", "var(--green)", 4);
  };

  const handleSubmitVerdict = async () => {
    soundFX.playClick();
    const missing = caseData.suspects.filter((s) => !progress.assignments[s.id]);
    if (missing.length > 0) {
      soundFX.playConflict();
      setMessage("Cannot submit: Unplaced suspects: " + missing.map((s) => s.name).join(", "));
      setMessageColor("var(--amber)");
      showToast("Place all suspects on the Evidence Board before submitting your verdict!", "var(--amber)", 4);
      return;
    }
    try {
      const solverRes = await api.graphColoring({
        case_id: caseData.case_id,
        found_evidence: progress.found_evidence,
        interviewed: progress.interviewed,
      });
      setProgress({
        ...progress,
        submitted_verdict: true,
        algorithm_solution: solverRes.assignment || {},
      });
      showToast("Verdict Submitted! Evaluating Case Result...", "var(--green)", 3);
      setScene(SCENES.RESULT);
    } catch (e) {
      showToast("Error computing verdict: " + e.message, "var(--red)");
    }
  };

  return (
    <div className="screen">
      <Header
        title="EVIDENCE BOARD"
        subtitle="Left click a suspect, then pick a location (or 1-4). Right click removes a placement."
        right={
          <button onClick={() => { soundFX.playClick(); setScene(SCENES.MENU); }}>MENU</button>
        }
      />
      <div className="content row">
        <div>
          <GraphBoard
            caseData={caseData}
            edges={edges}
            assignments={progress.assignments}
            selected={selected}
            conflictPair={conflictPair}
            onSelect={(sid, right) => {
              if (right) unassign(sid);
              else { soundFX.playClick(); setSelected(sid); }
            }}
          />
          <div
            className="panel"
            style={{ marginTop: 12, borderColor: messageColor }}
          >
            {message || "Place all five suspects so that no constraint is broken, then click SUBMIT VERDICT."}
          </div>
        </div>
        <div className="col" style={{ width: 420 }}>
          <div className="panel">
            <div className="gold">LOCATIONS (COLOURS)</div>
            {caseData.locations.map((loc, i) => (
              <div key={loc.id} style={{ marginTop: 8 }}>
                <span
                  className="legend-swatch"
                  style={{ background: locationColor(loc.id) }}
                />
                {i + 1}. {loc.name}
              </div>
            ))}
          </div>
          <div className="gold">
            {selected
              ? `SELECTED: ${caseData.suspects.find((s) => s.id === selected)?.name.toUpperCase()}`
              : "SELECT A SUSPECT"}
          </div>
          <div className="row" style={{ flexWrap: "wrap" }}>
            {caseData.locations.map((loc, i) => (
              <button
                key={loc.id}
                disabled={!selected}
                className={progress.assignments[selected] === loc.id ? "selected" : ""}
                onClick={() => assign(loc.id)}
                style={{ flex: "1 1 45%", background: "#1a2420" }}
              >
                {i + 1}. {loc.name}
              </button>
            ))}
          </div>
          <div className="panel" style={{ maxHeight: 180, overflow: "auto" }}>
            <div className="gold">ACTIVE CONSTRAINTS</div>
            {!constraints.length && (
              <div className="muted">Nothing yet - investigate first.</div>
            )}
            {constraints.map((c) => (
              <div key={c.text + c.source} style={{ marginTop: 6 }}>
                <span
                  style={{
                    color: c.type === "edge" ? "var(--red-soft)" : "var(--blue)",
                  }}
                >
                  ●
                </span>{" "}
                <span className="muted">{c.text}</span>
              </div>
            ))}
          </div>

          {/* SUBMIT VERDICT BUTTON */}
          <button
            className="gold"
            style={{
              width: "100%",
              padding: "14px",
              fontSize: "16px",
              fontWeight: 900,
              background: "linear-gradient(135deg, #d6ac58 0%, #b8860b 100%)",
              color: "#1a1612",
              boxShadow: "0 0 16px rgba(214, 172, 88, 0.4)",
              marginBottom: 10,
              letterSpacing: 1,
              cursor: "pointer",
            }}
            onClick={handleSubmitVerdict}
          >
            🚨 SUBMIT VERDICT (ACCUSE THIEF) 🚨
          </button>

          <div className="row">
            <button
              onClick={() => {
                soundFX.playClick();
                if (!readyForBoard) {
                  showToast(
                    "Collect all evidence and statements first - otherwise the solver may find more than one answer.",
                    "var(--amber)",
                    4.2
                  );
                }
                setScene(SCENES.ANALYSIS);
              }}
            >
              ANALYZE EVIDENCE
            </button>
            <button onClick={checkBoard}>CHECK BOARD</button>
            <button
              onClick={() => {
                soundFX.playClick();
                setProgress({ ...progress, assignments: {} });
                setMessage("Board cleared.");
              }}
            >
              CLEAR
            </button>
          </div>
        </div>
      </div>
      <div className="content" style={{ paddingTop: 0 }}>
        <SceneNav />
      </div>
    </div>
  );
}
