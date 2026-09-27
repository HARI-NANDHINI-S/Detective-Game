import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

const EVIDENCE_PHOTO_ICONS = {
  display_case: "🍷",
  camera: "📹",
  fingerprints: "🖐️",
  footprints: "👣",
  note: "📜",
  badge: "🎴",
};

const SUSPECT_PHOTO_ICONS = {
  maya: "👩‍🔬",
  arjun: "👮‍♂️",
  daniel: "🕵️‍♂️",
  priya: "👩‍💼",
  victor: "👨‍💼",
};

export default function CaseFileScene() {
  const { caseData, progress, readyForBoard } = useGame();
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (!caseData) return;
    api
      .count({
        case_id: caseData.case_id,
        found_evidence: progress.found_evidence,
        interviewed: progress.interviewed,
        cap: 3,
      })
      .then(setStats)
      .catch(() => {});
  }, [caseData, progress.found_evidence, progress.interviewed]);

  if (!caseData) return null;
  const logged = caseData.evidence.filter((e) => progress.found_evidence.includes(e.id));
  const spoken = caseData.suspects.filter((s) => progress.interviewed.includes(s.id));

  return (
    <div className="screen">
      <Header
        title={`CASE FILE DOSSIER - ${caseData.case_id.toUpperCase()}`}
        subtitle="Official investigation binder containing physical evidence photos & recorded statements."
      />

      <div className="content">
        {/* Animated Leather Book Binder */}
        <div className="book-binder">
          {/* Center Binder Rings */}
          <div className="binder-rings">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="binder-ring" />
            ))}
          </div>

          {/* Left Notebook Page: Physical Evidence & Photos */}
          <div className="notebook-page left" style={{ maxHeight: 540, overflow: "auto" }}>
            <div className="paperclip" />
            <h3 className="title-font" style={{ marginTop: 0, color: "#7a2a1e", borderBottom: "2px solid #e2d9cc", paddingBottom: 6 }}>
              📁 LOGGED PHYSICAL EVIDENCE ({logged.length}/{caseData.evidence.length})
            </h3>

            {!logged.length && (
              <p className="muted" style={{ fontStyle: "italic", marginTop: 20 }}>
                No evidence collected yet. Return to the crime scene to examine objects and take photos.
              </p>
            )}

            {logged.map((ev) => (
              <div
                key={ev.id}
                style={{
                  background: "#fff",
                  border: "1px solid #d4c8b8",
                  borderRadius: 6,
                  padding: 12,
                  marginTop: 12,
                  boxShadow: "0 2px 6px rgba(0,0,0,0.08)",
                }}
              >
                {/* Polaroid Photo Tag */}
                <div className="case-photo-tag">
                  <div className="case-photo-img">
                    <span style={{ fontSize: 28 }}>{EVIDENCE_PHOTO_ICONS[ev.id] || "🔍"}</span>
                  </div>
                  <div style={{ fontSize: 9, fontWeight: 800, marginTop: 2, color: "#3a3028" }}>
                    EVID #{ev.id.slice(0, 4).toUpperCase()}
                  </div>
                </div>

                <div style={{ overflow: "hidden" }}>
                  <strong style={{ color: "#7a2a1e" }}>{ev.object.toUpperCase()}</strong>
                  <div style={{ fontSize: 12, color: "#645040", fontWeight: 600 }}>{ev.name}</div>
                  <p style={{ fontSize: 13, margin: "6px 0", color: "#2a221c" }}>{ev.clue}</p>

                  {ev.constraints.map((c) => (
                    <div key={c.text} style={{ fontSize: 12, color: "#2d7a48", fontWeight: 700 }}>
                      ✓ {c.text}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Right Notebook Page: Suspect Statements & Graph Status */}
          <div className="notebook-page" style={{ maxHeight: 540, overflow: "auto" }}>
            <h3 className="title-font" style={{ marginTop: 0, color: "#1e3a7a", borderBottom: "2px solid #e2d9cc", paddingBottom: 6 }}>
              👥 SUSPECT STATEMENTS ({spoken.length}/{caseData.suspects.length})
            </h3>

            {!spoken.length && (
              <p className="muted" style={{ fontStyle: "italic", marginTop: 20 }}>
                No suspect statements recorded yet. Visit Suspect Interviews.
              </p>
            )}

            {spoken.map((s) => (
              <div
                key={s.id}
                style={{
                  background: "#f4f0e6",
                  border: "1px solid #c8bca8",
                  borderRadius: 6,
                  padding: 12,
                  marginTop: 12,
                  boxShadow: "0 2px 6px rgba(0,0,0,0.06)",
                }}
              >
                {/* Suspect Photo Avatar Tag */}
                <div className="case-photo-tag" style={{ transform: "rotate(2deg)", marginRight: 12 }}>
                  <div className="case-photo-img" style={{ background: "#3a4458" }}>
                    <span style={{ fontSize: 28 }}>{SUSPECT_PHOTO_ICONS[s.id] || "👤"}</span>
                  </div>
                  <div style={{ fontSize: 9, fontWeight: 800, marginTop: 2, color: "#1a1612" }}>
                    {s.name.toUpperCase()}
                  </div>
                </div>

                <div style={{ overflow: "hidden" }}>
                  <strong style={{ color: "#1e3a7a" }}>{s.full_name.toUpperCase()} ({s.role})</strong>
                  <p style={{ fontSize: 13, fontStyle: "italic", margin: "4px 0", color: "#1a1612" }}>
                    &quot;{s.statement}&quot;
                  </p>
                  {s.constraints.map((c) => (
                    <div key={c.text} style={{ fontSize: 12, color: "#2d7a48", fontWeight: 700 }}>
                      ✓ {c.text}
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {/* Board Graph Constraint Summary */}
            <div
              style={{
                marginTop: 20,
                background: "#eef2f8",
                border: "2px dashed #568cd6",
                borderRadius: 8,
                padding: 12,
              }}
            >
              <strong style={{ color: "#1e3a7a" }}>📊 GRAPH COLOURING STATUS</strong>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginTop: 6 }}>
                <span>Active Edges: <strong>{stats?.edges ?? "—"}</strong></span>
                <span>Forbidden Rules: <strong>{stats?.forbids ?? "—"}</strong></span>
              </div>
              <p style={{ fontSize: 12, margin: "6px 0 0", color: readyForBoard ? "#2d7a48" : "#a8403e", fontWeight: 700 }}>
                {readyForBoard
                  ? "✓ Graph has 1 unique colouring solution! Open the Evidence Board."
                  : "⚠ More evidence needed for unique graph solution."}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="content" style={{ paddingTop: 0 }}>
        <SceneNav />
      </div>
      <ProgressStrip />
    </div>
  );
}
