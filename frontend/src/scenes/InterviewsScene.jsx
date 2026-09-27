import { useState } from "react";
import { useGame } from "../GameContext";
import { locationColor } from "../constants";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";
import { soundFX } from "../utils/soundFX";

export default function InterviewsScene() {
  const { caseData, progress, interview, showToast, readyForBoard } = useGame();
  const [selected, setSelected] = useState(caseData?.suspects[0]?.id);
  if (!caseData) return null;
  const s = caseData.suspects.find((x) => x.id === selected);
  const done = s && progress.interviewed.includes(s.id);
  const loc = progress.assignments[s?.id];

  const handleSelect = (id) => {
    soundFX.playClick();
    setSelected(id);
  };

  const record = () => {
    if (!s || done) return;
    soundFX.playClue();
    interview(s.id);
    showToast(
      `${s.full_name}'s statement recorded - ${s.constraints.length} new edge(s) on the board.`,
      "var(--green)",
      4
    );
  };

  return (
    <div className="screen">
      <Header
        title="SUSPECT INTERVIEWS"
        subtitle="Statements create edges: two suspects who were never together cannot share a location."
      />
      <div className="content row">
        <div className="suspect-list">
          {caseData.suspects.map((sus) => (
            <button
              key={sus.id}
              className={`suspect-btn ${selected === sus.id ? "selected" : ""}`}
              onClick={() => handleSelect(sus.id)}
            >
              <div>{sus.full_name}</div>
              <div className="muted" style={{ fontWeight: 500 }}>
                {sus.role}
              </div>
              {progress.interviewed.includes(sus.id) && (
                <div className="green">RECORDED</div>
              )}
            </button>
          ))}
        </div>
        {s && (
          <div className="panel" style={{ flex: 1 }}>
            <div className="row" style={{ alignItems: "center" }}>
              <div className="avatar" style={{ background: locationColor(loc) }}>
                {s.name}
              </div>
              <div>
                <div className="title-font gold" style={{ fontSize: 26 }}>
                  {s.full_name.toUpperCase()}
                </div>
                <div className="muted">{s.role}</div>
                <p className="muted">{s.profile}</p>
              </div>
            </div>
            <div className="quote">
              {done ? <span>&quot;{s.statement}&quot;</span> : <span className="faint">Statement not taken yet.</span>}
            </div>
            <div className="gold" style={{ marginTop: 16 }}>
              CONSTRAINTS FROM THIS STATEMENT
            </div>
            {s.constraints.map((c) => (
              <div key={c.text} className={done ? "green" : "faint"}>
                - {done ? c.text : "locked"}
              </div>
            ))}
            <button className="gold" style={{ marginTop: 18 }} disabled={done} onClick={record}>
              RECORD STATEMENT
            </button>
            {readyForBoard && (
              <p className="gold">Every constraint is in. Open the Evidence Board.</p>
            )}
          </div>
        )}
      </div>
      <div className="content" style={{ paddingTop: 0 }}>
        <SceneNav />
      </div>
      <ProgressStrip />
    </div>
  );
}
