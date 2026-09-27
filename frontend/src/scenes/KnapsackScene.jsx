import { useEffect, useState } from "react";
import { api } from "../api";
import { useGame } from "../GameContext";
import AlgorithmVisualizer from "../components/AlgorithmVisualizer";
import Header from "../components/Header";
import ProgressStrip from "../components/ProgressStrip";
import SceneNav from "../components/SceneNav";

export default function KnapsackScene() {
  const { caseData, markStage, addScore } = useGame();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!caseData) return;
    setLoading(true);
    api
      .knapsack({ case_id: caseData.case_id })
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [caseData]);

  const handleComplete = () => {
    markStage("knapsack");
    addScore?.(200, "Completed 0/1 Knapsack Budget Optimization");
  };

  const items = data?.items || [];
  const cap = data?.capacity || 0;

  return (
    <div className="screen">
      <Header
        title="INVESTIGATION BUDGET — 0/1 KNAPSACK"
        subtitle="You have limited hours. Choose leads that maximise evidence value without exceeding the budget."
      />
      <div className="content">
        <AlgorithmVisualizer
          steps={data?.steps || []}
          loading={loading}
          error={error}
          onComplete={handleComplete}
          renderFrame={(step, index, steps) => {
            const p = step?.payload || {};
            let table = data?.table || [];
            for (let i = index; i >= 0; i -= 1) {
              if (steps[i]?.payload?.table) {
                table = steps[i].payload.table;
                break;
              }
            }
            return (
              <div className="row">
                <div style={{ overflow: "auto", flex: 1.4 }}>
                  <table className="dp-grid">
                    <thead>
                      <tr>
                        <th>i\\W</th>
                        {Array.from({ length: cap + 1 }, (_, w) => (
                          <th key={w}>{w}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {table.map((row, i) => (
                        <tr key={i}>
                          <th>{i === 0 ? "∅" : items[i - 1]?.name.slice(0, 10)}</th>
                          {row.map((v, w) => (
                            <td
                              key={w}
                              className={p.i === i && p.w === w ? "hot" : ""}
                            >
                              {v}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="panel" style={{ width: 320 }}>
                  <div className="gold">Leads</div>
                  {items.map((it) => (
                    <div
                      key={it.id}
                      className={
                        (p.chosen || []).some((c) => c.id === it.id) ? "green" : "muted"
                      }
                      style={{ marginTop: 8 }}
                    >
                      {it.name} — cost {it.cost}, value {it.value}
                    </div>
                  ))}
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
