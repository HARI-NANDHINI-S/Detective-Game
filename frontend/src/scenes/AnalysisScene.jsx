import { useCallback, useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import { SCENES } from "../constants";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import GraphBoard from "../components/GraphBoard";
import Header from "../components/Header";

function pretty(msg, caseData) {
  let out = msg;
  caseData.suspects.forEach((s) => {
    out = out.replaceAll(s.id, s.name);
  });
  caseData.locations.forEach((l) => {
    out = out.replaceAll(l.id, l.name);
  });
  return out;
}

export default function AnalysisScene() {
  const { caseData, progress, setProgress, setScene, showToast } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .graphColoring({
        found_evidence: progress.found_evidence,
        interviewed: progress.interviewed,
      })
      .then((r) => {
        setData({
          ...r,
          steps: r.steps.map((s) => ({
            ...s,
            message: pretty(s.message, caseData),
          })),
        });
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData, progress.found_evidence, progress.interviewed]);

  useEffect(() => {
    load();
  }, [load]);

  if (!caseData) return null;

  const onComplete = (step) => {
    if (step.kind === "SUCCESS") {
      setProgress({
        ...progress,
        solved_by_algorithm: true,
        algorithm_solution: step.assignment || data.assignment,
      });
      showToast("Solution found by backtracking. Open the case result.", "var(--green)", 4.5);
    }
    if (step.kind === "FAIL") {
      showToast("No valid colouring exists with the current constraints.", "var(--red)", 4.5);
    }
  };

  return (
    <div className="screen">
      <Header
        title="EVIDENCE ANALYSIS - BACKTRACKING GRAPH COLOURING"
        subtitle="Every line below is emitted by the real recursive solver while it runs."
        right={<button onClick={() => setScene(SCENES.MENU)}>MENU</button>}
      />
      <div className="content">
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          completeKinds={["SUCCESS", "FAIL"]}
          onComplete={onComplete}
          extraStatus={
            <div className="row">
              <button onClick={() => setScene(SCENES.BOARD)}>BACK TO BOARD</button>
              <button onClick={() => setScene(SCENES.DAA)}>DAA EXPLANATION</button>
              <button
                className="gold"
                disabled={!progress.solved_by_algorithm}
                onClick={() => setScene(SCENES.RESULT)}
              >
                CASE RESULT &gt;
              </button>
            </div>
          }
          renderFrame={(step) => {
            const assignment = step?.assignment || {};
            const conflictPair =
              step?.kind === "CONFLICT" && step.blame ? [step.suspect, step.blame] : null;
            return (
              <div className="row">
                <GraphBoard
                  caseData={caseData}
                  edges={data?.edges || []}
                  assignments={assignment}
                  active={step?.suspect}
                  conflictNode={step?.kind === "CONFLICT" ? step.suspect : null}
                  conflictPair={conflictPair}
                  title="SEARCH STATE"
                  width={620}
                  height={440}
                />
                <div className="panel" style={{ flex: 1 }}>
                  <div className="muted">
                    depth {step?.depth ?? 0} · nodes explored {data?.nodes_explored ?? "—"} ·
                    backtracks {data?.backtracks ?? "—"}
                  </div>
                  <p>{step?.message || "Press PLAY to watch the solver search the graph."}</p>
                </div>
              </div>
            );
          }}
        />
      </div>
    </div>
  );
}
