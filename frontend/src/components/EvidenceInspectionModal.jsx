import { useEffect, useState } from "react";
import { soundFX } from "../utils/soundFX";

export default function EvidenceInspectionModal({ evidence, onClose, onConfirmCollect }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [progress, setProgress] = useState(0);

  const startAnalysis = () => {
    soundFX.playTorchWhoosh();
    setAnalyzing(true);
    let p = 0;
    const interval = setInterval(() => {
      p += 10;
      setProgress(p);
      soundFX.playStep();
      if (p >= 100) {
        clearInterval(interval);
        setAnalyzing(false);
        setAnalyzed(true);
        soundFX.playSuccess();
      }
    }, 150);
  };

  const handleCollect = () => {
    soundFX.playClue();
    onConfirmCollect();
    onClose();
  };

  if (!evidence) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        backgroundColor: "rgba(8, 10, 15, 0.88)",
        backdropFilter: "blur(8px)",
        zIndex: 100,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 20,
      }}
    >
      <div
        className="panel gold-edge"
        style={{
          width: "100%",
          maxWidth: 780,
          background: "linear-gradient(135deg, #181d28 0%, #0e1118 100%)",
          boxShadow: "0 20px 50px rgba(0, 0, 0, 0.9), 0 0 30px rgba(214, 172, 88, 0.2)",
          position: "relative",
          borderRadius: 14,
          padding: 24,
          animation: "modalFade 0.3s ease-out",
        }}
      >
        {/* Modal Close Button */}
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            top: 16,
            right: 18,
            padding: "4px 10px",
            background: "#241818",
            borderColor: "var(--red)",
            color: "var(--red)",
          }}
        >
          ✕ CLOSE
        </button>

        {/* Modal Title Banner */}
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              fontSize: 12,
              fontWeight: 900,
              letterSpacing: 2,
              color: "var(--gold)",
              background: "rgba(214, 172, 88, 0.15)",
              padding: "4px 12px",
              borderRadius: 4,
              border: "1px solid var(--gold-dark)",
            }}
          >
            🔬 FORENSIC EVIDENCE ANALYSIS ROOM
          </div>
        </div>

        <h2 className="title-font gold" style={{ fontSize: 28, margin: "12px 0 4px" }}>
          EXAMINING: {evidence.object.toUpperCase()}
        </h2>
        <div className="muted">{evidence.name}</div>

        {/* Interactive Animation Screen Container */}
        <div
          style={{
            height: 280,
            background: "#080a0f",
            border: "2px solid var(--panel-edge)",
            borderRadius: 10,
            margin: "18px 0",
            position: "relative",
            overflow: "hidden",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          {evidence.id === "display_case" && <InteractiveDisplayCaseAnim progress={progress} analyzed={analyzed} />}
          {evidence.id === "camera" && <InteractiveCameraAnim progress={progress} analyzed={analyzed} />}
          {evidence.id === "fingerprints" && <InteractiveFingerprintsAnim progress={progress} analyzed={analyzed} />}
          {evidence.id === "footprints" && <InteractiveFootprintsAnim progress={progress} analyzed={analyzed} />}
          {evidence.id === "note" && <InteractiveTornNoteAnim progress={progress} analyzed={analyzed} />}
          {evidence.id === "badge" && <InteractiveBadgeAnim progress={progress} analyzed={analyzed} />}

          {/* Analysis Scanning Overlay */}
          {analyzing && (
            <div
              style={{
                position: "absolute",
                inset: 0,
                background: "rgba(0, 229, 255, 0.08)",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <div
                style={{
                  width: "80%",
                  height: 12,
                  background: "#182030",
                  borderRadius: 6,
                  border: "1px solid var(--blue)",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${progress}%`,
                    height: "100%",
                    background: "linear-gradient(90deg, var(--blue), #00e5ff)",
                    transition: "width 0.15s ease",
                  }}
                />
              </div>
              <div className="blue" style={{ marginTop: 10, fontWeight: 800, fontSize: 13 }}>
                SCANNING MOLECULAR & STRUCTURAL PATTERNS... {progress}%
              </div>
            </div>
          )}
        </div>

        {/* Clue Text & Results */}
        <div style={{ background: "var(--panel)", padding: 14, borderRadius: 8, border: "1px solid var(--panel-edge)" }}>
          <p style={{ margin: 0, lineHeight: 1.5 }}>{evidence.description}</p>
          {analyzed && (
            <div style={{ marginTop: 12 }}>
              <strong className="green">✓ FORENSIC FINDING UNLOCKED:</strong>
              <p className="gold" style={{ margin: "4px 0 0", fontWeight: 700 }}>
                &quot;{evidence.clue}&quot;
              </p>
            </div>
          )}
        </div>

        {/* Action Controls */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 18 }}>
          {!analyzed ? (
            <button className="gold" onClick={startAnalysis} disabled={analyzing}>
              {analyzing ? "ANALYZING..." : "🔬 RUN FORENSIC SCAN"}
            </button>
          ) : (
            <button
              className="gold"
              onClick={handleCollect}
              style={{ background: "var(--green)", color: "#14161c", borderColor: "#88e0a8" }}
            >
              📥 LOG INTO CASE FILE (+100 PTS)
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

// 1. Display Case Solvent Dissolution Interactive Screen
function InteractiveDisplayCaseAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      {/* Background Gallery Wall */}
      <rect width="500" height="240" fill="#121620" />
      {/* Plinth */}
      <rect x="180" y="140" width="140" height="80" fill="#3a3028" stroke="#d4c8b8" strokeWidth="3" rx="4" />
      <text x="250" y="185" fill="#d4c8b8" fontSize="12" textAnchor="middle" fontWeight="bold">
        CHOLA BRONZE PLINTH
      </text>
      {/* Empty Seal Marks */}
      <rect x="200" y="120" width="100" height="20" fill="rgba(86, 178, 122, 0.2)" stroke="#56b27a" strokeWidth="2" strokeDasharray="4,4" />
      {/* Solvent Bottle Dropper */}
      <g transform="translate(320, 40)">
        <path d="M 10 0 L 20 0 L 20 40 L 15 55 L 10 40 Z" fill="#78a0c8" opacity="0.8" />
        <circle cx="15" cy="-4" r="8" fill="#ce4c4a" />
      </g>

      {/* Solvent Dissolving Effect when Analyzed */}
      {analyzed && (
        <g>
          <text x="250" y="60" fill="#56b27a" fontSize="14" textAnchor="middle" fontWeight="bold">
            SOLVENT CABINET LOG MATCH: MAYA RAO
          </text>
          <circle cx="230" cy="130" r="8" fill="#56b27a" opacity="0.7">
            <animate attributeName="r" values="4;14;4" dur="1.2s" repeatCount="indefinite" />
          </circle>
          <circle cx="270" cy="130" r="10" fill="#56b27a" opacity="0.7">
            <animate attributeName="r" values="6;16;6" dur="1.2s" repeatCount="indefinite" />
          </circle>
        </g>
      )}
    </svg>
  );
}

// 2. CCTV Terminal Video Playback Screen
function InteractiveCameraAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      {/* Monitor Frame */}
      <rect width="500" height="240" fill="#080c14" />
      {/* CCTV Scanlines */}
      <line x1="0" y1="60" x2="500" y2="60" stroke="rgba(0, 229, 255, 0.15)" strokeWidth="40" />
      <line x1="0" y1="180" x2="500" y2="180" stroke="rgba(0, 229, 255, 0.15)" strokeWidth="40" />
      {/* Digital Timestamp */}
      <text x="20" y="30" fill="#ce4c4a" fontSize="14" fontFamily="monospace" fontWeight="bold">
        ● CAM 04 - GALLERY CORRIDOR [22:40:15]
      </text>
      {/* Intruder Motion Box */}
      <rect x="220" y="80" width="60" height="100" fill="none" stroke="#00e5ff" strokeWidth="2" strokeDasharray="6,4">
        <animate attributeName="x" values="200;240;200" dur="3s" repeatCount="indefinite" />
      </rect>
      <path d="M 235 100 L 265 100 L 250 170 Z" fill="#2a3240" opacity="0.8">
        <animate attributeName="transform" type="translate" values="-20,0; 20,0; -20,0" dur="3s" repeatCount="indefinite" />
      </path>

      {analyzed && (
        <g>
          <rect x="110" y="195" width="280" height="30" fill="rgba(86, 140, 214, 0.3)" stroke="#568cd6" rx="4" />
          <text x="250" y="215" fill="#e2e8f0" fontSize="12" textAnchor="middle" fontWeight="bold">
            VICTOR SNEAD NEVER CROSSED THRESHOLD
          </text>
        </g>
      )}
    </svg>
  );
}

// 3. Forensics Lab UV Neon Fingerprint Screen
function InteractiveFingerprintsAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      <rect width="500" height="240" fill="#090b10" />
      {/* Archive Keypad Frame */}
      <rect x="180" y="30" width="140" height="180" fill="#1c202a" stroke="#d4c8b8" strokeWidth="3" rx="8" />
      {/* Keypad Buttons */}
      {[50, 90, 130].map((y, row) =>
        [200, 240, 280].map((x, col) => (
          <rect key={`${row}-${col}`} x={x} y={y} width="24" height="24" fill="#283044" stroke="#568cd6" rx="3" />
        ))
      )}

      {/* Latent Fingerprints under UV */}
      {analyzed && (
        <g stroke="#00e5ff" fill="none" strokeWidth="2" filter="drop-shadow(0 0 6px #00e5ff)">
          <path d="M 212 62 C 212 56, 224 56, 224 62 C 224 70, 212 70, 212 76" />
          <path d="M 252 102 C 252 96, 264 96, 264 102 C 264 110, 252 110, 252 116" />
          <text x="250" y="225" fill="#00e5ff" fontSize="13" textAnchor="middle" fontWeight="bold">
            NO PRIYA / DANIEL PRINTS FOUND ON LAYER
          </text>
        </g>
      )}
    </svg>
  );
}

// 4. Wet Lab Floor Torch Flashlight Inspection Screen
function InteractiveFootprintsAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      <rect width="500" height="240" fill="#0c0e14" />
      {/* Floor Grid */}
      {[0, 100, 200, 300, 400].map((x) => (
        <line key={x} x1={x} y1="0" x2={x} y2="240" stroke="#1c2434" strokeWidth="1" />
      ))}
      {[0, 80, 160].map((y) => (
        <line key={y} x1="0" y1={y} x2="500" y2={y} stroke="#1c2434" strokeWidth="1" />
      ))}

      {/* Muddy Boot Print Soles */}
      <g fill="#967637" opacity="0.8">
        <ellipse cx="160" cy="100" rx="10" ry="22" transform="rotate(-20 160 100)" />
        <ellipse cx="240" cy="140" rx="10" ry="22" transform="rotate(15 240 140)" />
        <ellipse cx="320" cy="110" rx="10" ry="22" transform="rotate(-10 320 110)" />
      </g>

      {analyzed && (
        <g>
          {/* Forensic Calipers */}
          <line x1="140" y1="75" x2="180" y2="125" stroke="#de9e46" strokeWidth="2" strokeDasharray="3,3" />
          <text x="250" y="210" fill="#de9e46" fontSize="13" textAnchor="middle" fontWeight="bold">
            EXCLUDED: ARJUN'S REGULATION SECURITY BOOTS
          </text>
        </g>
      )}
    </svg>
  );
}

// 5. Torn Note Paper Alignment Screen
function InteractiveTornNoteAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      <rect width="500" height="240" fill="#121018" />
      {/* Left Slip */}
      <path d="M 120 40 L 245 40 L 235 120 L 255 200 L 120 200 Z" fill="#f4efe6" stroke="#c0b098" strokeWidth="2" />
      {/* Right Slip */}
      <path d={analyzed ? "M 245 40 L 370 40 L 370 200 L 255 200 L 235 120 Z" : "M 275 40 L 400 40 L 400 200 L 285 200 L 265 120 Z"} fill="#f4efe6" stroke="#c0b098" strokeWidth="2" style={{ transition: "all 0.6s ease" }} />

      {analyzed && (
        <g>
          <text x="250" y="110" fill="#ce4c4a" fontSize="14" fontFamily="monospace" textAnchor="middle" fontWeight="bold">
            COUNTERSIGNATURE MATCHED: ARCHIVE STAFF
          </text>
          <text x="250" y="225" fill="#56b27a" fontSize="13" textAnchor="middle" fontWeight="bold">
            VICTOR SANDS NOT SIGNED IN ARCHIVE LOG
          </text>
        </g>
      )}
    </svg>
  );
}

// 6. Security Badge RFID Scanner Decryption Screen
function InteractiveBadgeAnim({ analyzed }) {
  return (
    <svg width="100%" height="100%" viewBox="0 0 500 240">
      <rect width="500" height="240" fill="#080c14" />
      {/* Badge Scanner Slot */}
      <rect x="180" y="40" width="140" height="160" fill="#1c2434" stroke="#568cd6" strokeWidth="3" rx="8" />
      <rect x="200" y="70" width="100" height="100" fill="#101622" stroke="#d6ac58" strokeWidth="2" rx="4" />
      {/* RFID Waves */}
      <circle cx="250" cy="120" r="30" fill="none" stroke="#56b27a" strokeWidth="2" opacity="0.6">
        <animate attributeName="r" values="10;45" dur="1.2s" repeatCount="indefinite" />
      </circle>

      {analyzed && (
        <g>
          <text x="250" y="125" fill="#00e5ff" fontSize="13" textAnchor="middle" fontWait="bold">
            BLANK CURATOR BADGE CLONE DECRYPTED
          </text>
        </g>
      )}
    </svg>
  );
}
