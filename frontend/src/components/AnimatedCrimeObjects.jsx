import { useEffect, useState } from "react";
import { soundFX } from "../utils/soundFX";

export default function AnimatedCrimeObjects({ objectId, isLogged, isSelected, onClick }) {
  const [animating, setAnimating] = useState(false);

  const handleClick = () => {
    soundFX.playClick();
    setAnimating(true);
    setTimeout(() => setAnimating(false), 1200);
    onClick?.();
  };

  return (
    <div
      onClick={handleClick}
      className={`hotspot ${isSelected ? "active" : ""} ${isLogged ? "logged" : ""}`}
      style={{
        position: "relative",
        overflow: "hidden",
        cursor: "pointer",
        transition: "all 0.25s ease",
      }}
    >
      {!isLogged && <span className="pulse" />}
      {isLogged && (
        <span className="green" style={{ position: "absolute", right: 10, top: 8, fontSize: 11, fontWeight: 800 }}>
          LOGGED ✓
        </span>
      )}

      {/* Render Custom Animated Scene Graphics for each Object Type */}
      <div className="icon-box" style={{ height: 80, position: "relative" }}>
        {objectId === "display_case" && <DisplayCaseAnim animating={animating} isLogged={isLogged} />}
        {objectId === "camera" && <CameraAnim animating={animating} isLogged={isLogged} />}
        {objectId === "fingerprints" && <FingerprintsAnim animating={animating} isLogged={isLogged} />}
        {objectId === "footprints" && <FootprintsAnim animating={animating} isLogged={isLogged} />}
        {objectId === "note" && <TornNoteAnim animating={animating} isLogged={isLogged} />}
        {objectId === "badge" && <SecurityBadgeAnim animating={animating} isLogged={isLogged} />}
      </div>

      <strong style={{ display: "block", marginTop: 6 }}>
        {objectId.replace("_", " ").toUpperCase()}
      </strong>
    </div>
  );
}

// 1. Broken Display Case Animation
function DisplayCaseAnim({ animating }) {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Plinth */}
      <rect x="12" y="44" width="40" height="14" fill="#3a3028" stroke="#d4c8b8" strokeWidth="2" rx="2" />
      {/* Glass Case Frame */}
      <rect x="16" y="14" width="32" height="30" fill="rgba(180, 220, 255, 0.15)" stroke="#78a0c8" strokeWidth="2" rx="2" />
      {/* Glass Cracks */}
      <path d="M 24 14 L 32 28 L 22 36 M 32 28 L 44 20" fill="none" stroke="#e0f0ff" strokeWidth="1.5" strokeDasharray="2,2" />
      {/* Solvent Glow droplets when animating */}
      {animating && (
        <g>
          <circle cx="28" cy="24" r="3" fill="#56b27a">
            <animate attributeName="cy" values="24;40" dur="0.8s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="1;0" dur="0.8s" repeatCount="indefinite" />
          </circle>
          <circle cx="36" cy="20" r="2.5" fill="#56b27a">
            <animate attributeName="cy" values="20;38" dur="0.6s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="1;0" dur="0.6s" repeatCount="indefinite" />
          </circle>
        </g>
      )}
    </svg>
  );
}

// 2. Security Camera Scanning Animation
function CameraAnim() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Wall Bracket */}
      <path d="M 8 16 L 24 16 L 24 28" fill="none" stroke="#647084" strokeWidth="4" strokeLinecap="round" />
      {/* Camera Body */}
      <g>
        <rect x="20" y="24" width="28" height="18" fill="#2a3240" stroke="#d6ac58" strokeWidth="2" rx="3" />
        {/* Lens */}
        <circle cx="48" cy="33" r="6" fill="#141820" stroke="#568cd6" strokeWidth="2" />
        {/* REC LED Dot */}
        <circle cx="26" cy="29" r="2.5" fill="#ce4c4a">
          <animate attributeName="opacity" values="1;0.2;1" dur="1s" repeatCount="indefinite" />
        </circle>
      </g>
      {/* Laser Scan Cone Beam */}
      <polygon points="48,33 64,20 64,46" fill="rgba(86, 140, 214, 0.25)">
        <animate attributeName="opacity" values="0.2;0.6;0.2" dur="1.5s" repeatCount="indefinite" />
      </polygon>
    </svg>
  );
}

// 3. Fingerprints UV Scanner Animation
function FingerprintsAnim({ animating }) {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Keypad Base */}
      <rect x="18" y="10" width="28" height="44" fill="#1c202a" stroke="#d4c8b8" strokeWidth="2" rx="4" />
      {/* Keypad Buttons */}
      <rect x="22" y="14" width="6" height="6" fill="#568cd6" rx="1" />
      <rect x="30" y="14" width="6" height="6" fill="#568cd6" rx="1" />
      <rect x="38" y="14" width="6" height="6" fill="#568cd6" rx="1" />
      {/* Fingerprint Loops */}
      <g stroke="#568cd6" fill="none" strokeWidth="1.5">
        <path d="M 26 34 C 26 28, 38 28, 38 34 C 38 42, 26 42, 26 48" />
        <path d="M 29 34 C 29 31, 35 31, 35 34 C 35 39, 29 39, 29 44" />
      </g>
      {/* UV Neon Blue Scanner Bar */}
      <line x1="16" y1="20" x2="48" y2="20" stroke="#00e5ff" strokeWidth="2.5" filter="drop-shadow(0 0 4px #00e5ff)">
        <animate attributeName="y1" values="14;48;14" dur="2s" repeatCount="indefinite" />
        <animate attributeName="y2" values="14;48;14" dur="2s" repeatCount="indefinite" />
      </line>
    </svg>
  );
}

// 4. Footprints Muddy Step Animation
function FootprintsAnim() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Lab Tile Grid */}
      <line x1="8" y1="32" x2="56" y2="32" stroke="#3a4458" strokeWidth="1" strokeDasharray="3,3" />
      <line x1="32" y1="8" x2="32" y2="56" stroke="#3a4458" strokeWidth="1" strokeDasharray="3,3" />
      {/* Boot Soles */}
      <g fill="#967637" opacity="0.85">
        {/* Foot 1 */}
        <ellipse cx="24" cy="24" rx="6" ry="12" transform="rotate(-15 24 24)" />
        <ellipse cx="22" cy="34" rx="4" ry="5" transform="rotate(-15 22 34)" />
        {/* Foot 2 */}
        <ellipse cx="40" cy="40" rx="6" ry="12" transform="rotate(10 40 40)" />
        <ellipse cx="42" cy="50" rx="4" ry="5" transform="rotate(10 42 50)" />
      </g>
      {/* Ripple Splash Ring */}
      <circle cx="40" cy="40" r="14" fill="none" stroke="#d6ac58" strokeWidth="1.5" opacity="0">
        <animate attributeName="r" values="6;18" dur="1.4s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.8;0" dur="1.4s" repeatCount="indefinite" />
      </circle>
    </svg>
  );
}

// 5. Torn Note Paper Alignment Animation
function TornNoteAnim({ animating }) {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Torn Half Left */}
      <path d="M 14 12 L 30 12 L 28 24 L 32 36 L 27 52 L 14 52 Z" fill="#f4efe6" stroke="#c0b098" strokeWidth="1.5" />
      {/* Torn Half Right */}
      <path d="M 34 12 L 50 12 L 50 52 L 31 52 L 36 36 L 32 24 Z" fill="#f4efe6" stroke="#c0b098" strokeWidth="1.5">
        {animating && (
          <animateTransform attributeName="transform" type="translate" values="6,0; 0,0" dur="0.5s" />
        )}
      </path>
      {/* Handwritten Slip Lines */}
      <line x1="18" y1="20" x2="26" y2="20" stroke="#3a3028" strokeWidth="1.5" />
      <line x1="38" y1="20" x2="46" y2="20" stroke="#3a3028" strokeWidth="1.5" />
      <line x1="18" y1="30" x2="24" y2="30" stroke="#ce4c4a" strokeWidth="1.5" />
      <line x1="36" y1="30" x2="44" y2="30" stroke="#ce4c4a" strokeWidth="1.5" />
    </svg>
  );
}

// 6. Security Badge RFID Pulse Animation
function SecurityBadgeAnim() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64">
      {/* Badge Card */}
      <rect x="16" y="18" width="32" height="40" fill="#283244" stroke="#d6ac58" strokeWidth="2" rx="3" />
      {/* Lanyard Clip Hole */}
      <rect x="28" y="12" width="8" height="4" fill="#94a0b4" rx="1" />
      {/* Photo Placeholder */}
      <rect x="22" y="24" width="20" height="16" fill="#3a4458" rx="2" />
      {/* RFID Chip Symbol */}
      <path d="M 24 46 A 8 8 0 0 1 40 46" fill="none" stroke="#56b27a" strokeWidth="2">
        <animate attributeName="stroke" values="#56b27a;#00e5ff;#56b27a" dur="1s" repeatCount="indefinite" />
      </path>
      {/* Radio Signal Pulse Waves */}
      <circle cx="32" cy="46" r="16" fill="none" stroke="#56b27a" strokeWidth="1.5" opacity="0">
        <animate attributeName="r" values="4;20" dur="1.2s" repeatCount="indefinite" />
        <animate attributeName="opacity" values="0.9;0" dur="1.2s" repeatCount="indefinite" />
      </circle>
    </svg>
  );
}
