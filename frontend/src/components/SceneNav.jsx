import { useGame } from "../GameContext";
import { SCENES } from "../constants";

const LINKS = [
  [SCENES.CRIME, "CRIME SCENE"],
  [SCENES.BINARY, "TIMESTAMP LOG"],
  [SCENES.KRUSKAL, "CAMERA NET"],
  [SCENES.KNAPSACK, "BUDGET"],
  [SCENES.MERGESORT, "TIMELINE"],
  [SCENES.INTERVIEWS, "INTERVIEWS"],
  [SCENES.DIJKSTRA, "ALIBI WALK"],
  [SCENES.CASEFILE, "CASE FILE"],
  [SCENES.BOARD, "BOARD"],
];

export default function SceneNav({ extra }) {
  const { setScene, scene } = useGame();
  return (
    <div className="nav-row">
      {LINKS.map(([id, label]) => (
        <button
          key={id}
          className={scene === id ? "selected" : ""}
          onClick={() => setScene(id)}
        >
          {label}
        </button>
      ))}
      {extra}
    </div>
  );
}
