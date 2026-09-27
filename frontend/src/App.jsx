import { GameProvider, useGame } from "./GameContext";
import { SCENES } from "./constants";
import Toast from "./components/Toast";
import MenuScene from "./scenes/MenuScene";
import CrimeScene from "./scenes/CrimeScene";
import CaseFileScene from "./scenes/CaseFileScene";
import InterviewsScene from "./scenes/InterviewsScene";
import BoardScene from "./scenes/BoardScene";
import AnalysisScene from "./scenes/AnalysisScene";
import ResultScene from "./scenes/ResultScene";
import DaaScene from "./scenes/DaaScene";
import BinarySearchScene from "./scenes/BinarySearchScene";
import KruskalScene from "./scenes/KruskalScene";
import KnapsackScene from "./scenes/KnapsackScene";
import MergeSortScene from "./scenes/MergeSortScene";
import DijkstraScene from "./scenes/DijkstraScene";

function Shell() {
  const { scene, error, toast, caseData } = useGame();
  if (error) {
    return (
      <div className="error-banner">
        Could not reach the FastAPI backend at /api. Start it with:
        <pre>python -m uvicorn backend_app:app --reload --port 8000</pre>
        {error}
      </div>
    );
  }
  if (!caseData) {
    return <div className="content muted">Loading case file…</div>;
  }
  const scenes = {
    [SCENES.MENU]: MenuScene,
    [SCENES.CRIME]: CrimeScene,
    [SCENES.CASEFILE]: CaseFileScene,
    [SCENES.INTERVIEWS]: InterviewsScene,
    [SCENES.BINARY]: BinarySearchScene,
    [SCENES.KRUSKAL]: KruskalScene,
    [SCENES.KNAPSACK]: KnapsackScene,
    [SCENES.MERGESORT]: MergeSortScene,
    [SCENES.DIJKSTRA]: DijkstraScene,
    [SCENES.BOARD]: BoardScene,
    [SCENES.ANALYSIS]: AnalysisScene,
    [SCENES.RESULT]: ResultScene,
    [SCENES.DAA]: DaaScene,
  };
  const Scene = scenes[scene] || MenuScene;
  return (
    <>
      <Scene />
      <Toast toast={toast} />
    </>
  );
}

export default function App() {
  return (
    <GameProvider>
      <Shell />
    </GameProvider>
  );
}
