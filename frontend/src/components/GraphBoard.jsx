import { locationColor } from "../constants";
import { soundFX } from "../utils/soundFX";

const SUSPECT_ICONS = {
  maya: "👩‍🔬",
  arjun: "👮‍♂️",
  daniel: "🕵️‍♂️",
  priya: "👩‍💼",
  victor: "👨‍💼",
};

// Rotations for realistic polaroid pinned angles
const ROTATIONS = {
  maya: -3,
  arjun: 4,
  daniel: -2,
  priya: 3,
  victor: -4,
};

function layout(ids, width, height) {
  const cx = width / 2;
  const cy = height / 2 + 10;
  const radius = Math.min(width, height) * 0.36;
  const n = Math.max(ids.length, 1);
  const pos = {};
  ids.forEach((sid, i) => {
    const ang = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    pos[sid] = { x: cx + radius * Math.cos(ang), y: cy + radius * Math.sin(ang) };
  });
  return pos;
}

export default function GraphBoard({
  caseData,
  edges = [],
  assignments = {},
  selected,
  active,
  conflictPair,
  conflictNode,
  title = "POLICE EVIDENCE BOARD - SUSPECT CONSTRAINTS",
  onSelect,
  width = 700,
  height = 520,
}) {
  const ids = caseData.suspects.map((s) => s.id);
  const pos = layout(ids, width, height);

  const suspectOf = (id) => caseData.suspects.find((s) => s.id === id);
  const nameOf = (id) => suspectOf(id)?.name || id;
  const locName = (id) => caseData.locations.find((l) => l.id === id)?.name || "Unplaced";

  const allPlaced = ids.every((id) => assignments[id]);

  return (
    <div className="cork" style={{ width, height }}>
      {/* Header Tape Banner */}
      <div className="cork-header-tape">
        📌 {title} 📌
      </div>

      {/* Red Yarn Strings */}
      <svg width={width} height={height} style={{ position: "absolute", inset: 0, zIndex: 2 }}>
        <defs>
          <filter id="stringGlow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
        </defs>

        {edges.map(([a, b], i) => {
          if (!pos[a] || !pos[b]) return null;
          const clash = assignments[a] && assignments[a] === assignments[b];
          const flagged =
            conflictPair &&
            new Set(conflictPair).size === 2 &&
            conflictPair.includes(a) &&
            conflictPair.includes(b);
          const hot = clash || flagged;

          // Curved string calculation (slight sag)
          const midX = (pos[a].x + pos[b].x) / 2;
          const midY = (pos[a].y + pos[b].y) / 2 + 15;
          const pathD = `M ${pos[a].x} ${pos[a].y} Q ${midX} ${midY} ${pos[b].x} ${pos[b].y}`;

          return (
            <g key={i}>
              {/* String Shadow */}
              <path
                d={pathD}
                fill="none"
                stroke="rgba(0, 0, 0, 0.4)"
                strokeWidth={hot ? 6 : 4}
                transform="translate(2, 4)"
              />
              {/* Main Red String */}
              <path
                d={pathD}
                fill="none"
                stroke={hot ? "#ff3333" : "#b0423c"}
                strokeWidth={hot ? 4 : 2.5}
                strokeDasharray={hot ? "8,4" : "none"}
                filter={hot ? "url(#stringGlow)" : undefined}
                style={{
                  transition: "all 0.3s ease",
                }}
              />
            </g>
          );
        })}
      </svg>

      {/* Polaroid Cards for Suspects */}
      {ids.map((sid) => {
        const suspect = suspectOf(sid);
        const loc = assignments[sid];
        const rot = ROTATIONS[sid] || 0;
        const clash = conflictNode === sid || (conflictPair && conflictPair.includes(sid));

        const cls = [
          "polaroid-card",
          selected === sid ? "selected" : "",
          active === sid ? "active" : "",
          clash ? "conflict" : "",
        ].join(" ");

        const isCulprit = allPlaced && loc === caseData.culprit_location;

        return (
          <div
            key={sid}
            className={cls}
            style={{
              left: pos[sid].x,
              top: pos[sid].y,
              transform: `rotate(${rot}deg)`,
              zIndex: selected === sid || active === sid ? 12 : 5,
            }}
            onClick={() => {
              soundFX.playClick();
              onSelect?.(sid);
            }}
            onContextMenu={(e) => {
              e.preventDefault();
              soundFX.playClick();
              onSelect?.(sid, true);
            }}
          >
            {/* Pushpin at top */}
            <div className="pushpin" />

            {/* Photo Avatar */}
            <div
              className="polaroid-photo"
              style={{
                borderColor: loc ? locationColor(loc) : "#d4c8b8",
              }}
            >
              <span style={{ fontSize: 32 }}>{SUSPECT_ICONS[sid] || "👤"}</span>
            </div>

            {/* Suspect Name */}
            <div className="polaroid-label">{nameOf(sid)}</div>

            {/* Room Location Stamp Badge */}
            <div
              className="room-stamp"
              style={{
                background: loc ? locationColor(loc) : "#647084",
              }}
            >
              {loc ? locName(loc) : "UNPLACED"}
            </div>

            {/* Dynamic Rubber Stamps */}
            {isCulprit && <div className="rubber-stamp culprit">THIEF</div>}
            {allPlaced && !isCulprit && <div className="rubber-stamp cleared">CLEARED</div>}
            {clash && <div className="rubber-stamp warning">CONFLICT</div>}
          </div>
        );
      })}
    </div>
  );
}
