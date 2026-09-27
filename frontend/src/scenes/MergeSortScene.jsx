import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

export default function MergeSortScene() {
  const { caseData, markStage, addScore } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .mergeSort({ case_id: caseData.case_id })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData]);

  const handleComplete = () => {
    markStage("mergesort");
    addScore?.(200, "Completed Merge Sort Timeline Ordering");
  };

  return (
    <div className="screen">
      <Header
        title="CASE TIMELINE — MERGE SORT"
        subtitle="Split the notes, then merge them back in chronological order."
      />
      <div className="content">
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          onComplete={handleComplete}
          renderFrame={(step) => {
            const p = step?.payload || {};
            const arr = p.array || data?.original || [];
            const hi = new Set(p.highlight || []);
            return (
              <div className="array-row">
                {arr.map((item, i) => (
                  <div
                    key={item.id + i}
                    className={`chip ${hi.has(i) ? "hi" : ""}`}
                    style={{
                      opacity:
                        p.lo != null && (i < p.lo || i > p.hi) ? 0.4 : 1,
                      minWidth: 140,
                    }}
                  >
                    <div className="gold">{item.time}</div>
                    <div>{item.source}</div>
                    <div className="muted">{item.text}</div>
                  </div>
                ))}
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
