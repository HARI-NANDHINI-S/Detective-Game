import { useState } from "react";
import { useGame } from "../GameContext";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";
import AnimatedCrimeObjects from "../components/AnimatedCrimeObjects";
import EvidenceInspectionModal from "../components/EvidenceInspectionModal";
import { soundFX } from "../utils/soundFX";

export default function CrimeScene() {
  const { caseData, progress, collect, showToast, addScore } = useGame();
  const [selected, setSelected] = useState(null);
  const [inspectingEv, setInspectingEv] = useState(null);

  if (!caseData) return null;
  const ev = caseData.evidence.find((e) => e.id === selected);
  const found = ev && progress.found_evidence.includes(ev.id);

  const handleSelect = (id) => {
    setSelected(id);
    const target = caseData.evidence.find((e) => e.id === id);
    if (target) {
      setInspectingEv(target);
    }
  };

  const confirmCollect = (itemToCollect) => {
    const target = itemToCollect || ev;
    if (!target) return;
    if (progress.found_evidence.includes(target.id)) return;

    soundFX.playClue();
    collect(target.id);
    addScore?.(100, `Collected Evidence: ${target.name}`);
    showToast(
      `Evidence logged: ${target.name}. +100 PTS! ${target.constraints.length} new constraint(s) added to the board.`,
      "var(--green)",
      4
    );
  };

  return (
    <div className="screen">
      <Header
        title={`CRIME SCENE - ${caseData.title.toUpperCase()}`}
        subtitle="Click an object to enter the interactive forensic analysis room."
      />
      <div className="content row">
        <div className="panel" style={{ flex: 1.15 }}>
          <div className="hotspot-grid">
            {caseData.evidence.map((e) => {
              const logged = progress.found_evidence.includes(e.id);
              return (
                <AnimatedCrimeObjects
                  key={e.id}
                  objectId={e.id}
                  isLogged={logged}
                  isSelected={selected === e.id}
                  onClick={() => handleSelect(e.id)}
                />
              );
            })}
          </div>
        </div>
        <div className="panel" style={{ flex: 0.95 }}>
          {!ev && (
            <>
              <div className="gold">NO OBJECT SELECTED</div>
              <p className="muted">
                {caseData.briefing[0] || "Examine the crime scene to uncover hidden physical evidence."}
              </p>
              <p className="muted">
                Click any of the animated crime scene objects above to launch the interactive Forensic Analysis Lab!
              </p>
            </>
          )}
          {ev && (
            <>
              <div className="title-font gold" style={{ fontSize: 22 }}>
                {ev.object.toUpperCase()}
              </div>
              <div className="muted">{ev.name}</div>
              <p>{ev.description}</p>
              {found ? (
                <>
                  <div className="green">CLUE UNCOVERED</div>
                  <p>{ev.clue}</p>
                  {ev.constraints.length ? (
                    <>
                      <div className="gold">CONSTRAINTS UNLOCKED</div>
                      {ev.constraints.map((c) => (
                        <div key={c.text} className="muted">
                          - {c.text}
                        </div>
                      ))}
                    </>
                  ) : (
                    <div className="faint">No board constraint - context only.</div>
                  )}
                </>
              ) : (
                <div className="amber">Not yet logged. Inspect in the lab to gain +100 points & unlock constraints.</div>
              )}
              <button
                className="gold"
                style={{ marginTop: 16 }}
                onClick={() => setInspectingEv(ev)}
              >
                🔬 LAUNCH INTERACTIVE FORENSIC LAB
              </button>
            </>
          )}
        </div>
      </div>

      {/* Interactive Evidence Examination Modal */}
      {inspectingEv && (
        <EvidenceInspectionModal
          evidence={inspectingEv}
          onClose={() => setInspectingEv(null)}
          onConfirmCollect={() => confirmCollect(inspectingEv)}
        />
      )}

      <div className="content" style={{ paddingTop: 0 }}>
        <SceneNav />
      </div>
      <ProgressStrip />
    </div>
  );
}
