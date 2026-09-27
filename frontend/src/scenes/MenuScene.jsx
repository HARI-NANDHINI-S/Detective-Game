import { useGame } from "../GameContext";
import { SCENES, loadSave } from "../constants";
import TorchRunner from "../components/TorchRunner";
import { soundFX } from "../utils/soundFX";

export default function MenuScene() {
  const { caseData, newGame, loadGame, setScene } = useGame();
  if (!caseData) return null;
  const hasSave = !!loadSave();

  const handleNewGame = () => {
    soundFX.playClick();
    newGame();
  };

  const handleContinue = () => {
    soundFX.playClick();
    if (loadGame()) setScene(SCENES.CRIME);
  };

  const handleBoard = () => {
    soundFX.playClick();
    setScene(SCENES.BOARD);
  };

  return (
    <div className="screen" style={{ position: "relative", overflow: "hidden" }}>
      {/* Background Torch Animation */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          width: "100%",
          height: "100%",
          opacity: 0.85,
          pointerEvents: "none",
        }}
      >
        <TorchRunner speed={1.4} autoRun={true} interactive={true} />
      </div>

      <div className="menu-wrap" style={{ position: "relative", zIndex: 2 }}>
        <div>
          <div className="title-font" style={{ fontSize: 52, fontWeight: 700 }}>
            DETECTIVE&apos;S
          </div>
          <div className="title-font gold" style={{ fontSize: 52, fontWeight: 700 }}>
            EVIDENCE BOARD
          </div>
          <div
            style={{
              width: 460,
              height: 2,
              background: "var(--gold-dark)",
              margin: "16px 0 10px",
            }}
          />
          <div className="muted">A Graph Colouring + Backtracking mystery</div>
          <div className="menu-btns" style={{ marginTop: 36 }}>
            <button className="gold" onClick={handleNewGame}>
              NEW INVESTIGATION
            </button>
            <button onClick={handleContinue} disabled={!hasSave}>
              CONTINUE (LOAD CASE)
            </button>
            <button onClick={handleBoard}>EVIDENCE BOARD</button>
          </div>
        </div>
        <div className="panel gold-edge" style={{ background: "rgba(28, 24, 18, 0.92)" }}>
          <div className="gold">CASE FILE {caseData.case_id.replace("_", " ").toUpperCase()}</div>
          <h2 className="title-font" style={{ margin: "8px 0 4px" }}>
            {caseData.title}
          </h2>
          <div className="muted">{caseData.subtitle}</div>
          <div style={{ marginTop: 16 }}>
            {caseData.briefing.map((line) => (
              <p key={line} className="muted" style={{ lineHeight: 1.5, marginBottom: 8 }}>
                {line}
              </p>
            ))}
          </div>
          <div className="gold" style={{ marginTop: 24 }}>
            {caseData.suspects.length} suspects &nbsp; {caseData.locations.length} locations
            &nbsp; {caseData.evidence.length} pieces of evidence
          </div>
        </div>
      </div>
    </div>
  );
}
