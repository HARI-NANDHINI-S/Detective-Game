import { useGame } from "../GameContext";
import { SCENES } from "../constants";

export default function ProgressStrip({ extra }) {
  const { caseData, progress, saveGame, setScene } = useGame();
  if (!caseData) return null;
  return (
    <div className="progress">
      <span>
        Evidence {progress.found_evidence.length}/{caseData.evidence.length}
      </span>
      <span>
        Interviews {progress.interviewed.length}/{caseData.suspects.length}
      </span>
      {extra}
      <span className="hint">
        <button onClick={saveGame} style={{ marginRight: 8 }}>
          SAVE
        </button>
        <button onClick={() => setScene(SCENES.MENU)}>MENU</button>
      </span>
    </div>
  );
}
