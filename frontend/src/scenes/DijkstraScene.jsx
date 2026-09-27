import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import MapNetwork from "../components/MapNetwork";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

export default function DijkstraScene() {
  const { caseData, markStage, addScore } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .dijkstra({ case_id: caseData.case_id })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData]);

  const handleComplete = () => {
    markStage("dijkstra");
    addScore?.(200, "Completed Dijkstra Alibi Walk Verification");
  };

  const alibi = data?.alibi || caseData?.alibi;

  return (
    <div className="screen">
      <Header
        title="ALIBI WALK — DIJKSTRA"
        subtitle="Fastest route between two rooms. If the walk is longer than the claim, the alibi fails."
      />
      <div className="content">
        {alibi && <p className="muted">{alibi.statement}</p>}
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          completeKinds={["PATH", "UNREACHABLE"]}
          onComplete={handleComplete}
          renderFrame={(step) => {
            const p = step?.payload || {};
            const dist = {};
            Object.entries(p.dist || {}).forEach(([k, v]) => {
              dist[k] = v >= 1e8 ? null : v;
            });
            return (
              <div className="row">
                <MapNetwork
                  nodes={data?.nodes || []}
                  edges={(data?.edges || []).map((e) => ({
                    ...e,
                    cost: e.minutes,
                  }))}
                  path={p.path || []}
                  dist={dist}
                  current={p.current}
                  neighbor={p.neighbor}
                />
                <div className="panel" style={{ width: 320 }}>
                  <div className="gold">Claim vs shortest path</div>
                  <p>Claimed: {data?.claimed_minutes} minutes</p>
                  <p>Computed: {data?.minutes ?? "—"} minutes</p>
                  {step?.kind === "PATH" && (
                    <p className={data?.possible ? "green" : "red"}>
                      {data?.possible
                        ? "The claimed timing is physically possible."
                        : "The walk takes longer than claimed — the alibi does not hold."}
                    </p>
                  )}
                  <div className="muted">{(p.path || []).join(" → ")}</div>
                </div>
              </div>
            );
          }}
        />
      </div>
      <div className="content" style={{ paddingTop: 0 }}>
        <SceneNav />
      </div>
      <ProgressStrip />
    </div>
  );
}
