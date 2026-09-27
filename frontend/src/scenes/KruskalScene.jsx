import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import MapNetwork from "../components/MapNetwork";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

export default function KruskalScene() {
  const { caseData, markStage, addScore } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .kruskal({ case_id: caseData.case_id })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData]);

  const handleComplete = () => {
    markStage("kruskal");
    addScore?.(200, "Completed Kruskal MST Network Analysis");
  };

  return (
    <div className="screen">
      <Header
        title="CAMERA NETWORK — KRUSKAL MST"
        subtitle="Build the cheapest cable tree that still connects every room. Rejected links are blind-spot corridors."
      />
      <div className="content">
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          onComplete={handleComplete}
          renderFrame={(step) => {
            const p = step?.payload || {};
            return (
              <div className="row">
                <MapNetwork
                  nodes={data?.nodes || []}
                  edges={data?.edges || []}
                  mst={p.mst || []}
                  rejected={p.rejected || []}
                  highlight={p.edge}
                />
                <div className="panel" style={{ flex: 1 }}>
                  <div className="gold">Network so far</div>
                  {(p.mst || []).map((e) => (
                    <div key={e.label} className="green">
                      + {e.label} ({e.cost})
                    </div>
                  ))}
                  {(p.rejected || []).map((e) => (
                    <div key={e.label} className="red">
                      × {e.label} — cycle
                    </div>
                  ))}
                  {step?.kind === "DONE" && (
                    <p className="amber">
                      Blind spots: unused corridors still exist physically but sit outside the
                      minimum network (cost {data?.total_cost}).
                    </p>
                  )}
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
