import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

export default function BinarySearchScene() {
  const { caseData, markStage, addScore } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .binarySearch({ case_id: caseData.case_id })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData]);

  const handleComplete = () => {
    markStage("binary");
    addScore?.(200, "Completed Binary Search Timestamp Analysis");
  };

  return (
    <div className="screen">
      <Header
        title="TIMESTAMP LOG — BINARY SEARCH"
        subtitle="The camera archive is already sorted by time. Locate the alarm bypass event."
      />
      <div className="content">
        <p className="muted">
          Target Event: <strong className="gold">{caseData?.search_target?.time}</strong> — {caseData?.search_target?.label}
        </p>
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          completeKinds={["FOUND", "NOT_FOUND"]}
          onComplete={handleComplete}
          renderFrame={(step) => {
            const p = step?.payload || {};
            const log = data?.log || caseData?.camera_log || [];
            return (
              <div className="array-row">
                {log.map((row, i) => {
                  const cls = [
                    "chip",
                    p.mid === i ? "mid" : "",
                    i >= (p.lo ?? 0) && i <= (p.hi ?? log.length) ? "hi" : "",
                    p.found_index === i ? "found" : "",
                  ].join(" ");
                  return (
                    <div key={row.id} className={cls}>
                      <div className="gold">{row.time}</div>
                      <div className="muted">{row.camera}</div>
                      {p.mid === i && <div className="blue">MID</div>}
                    </div>
                  );
                })}
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
