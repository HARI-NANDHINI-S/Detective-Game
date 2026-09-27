export default function MapNetwork({
  nodes = [],
  edges = [],
  mst = [],
  rejected = [],
  highlight,
  dist = {},
  path = [],
  current,
  neighbor,
  width = 640,
  height = 420,
}) {
  const pad = 48;
  const mstKeys = new Set(mst.map((e) => edgeKey(e.a, e.b)));
  const rejKeys = new Set(rejected.map((e) => edgeKey(e.a, e.b)));
  const pathSet = new Set();
  for (let i = 0; i < path.length - 1; i += 1) pathSet.add(edgeKey(path[i], path[i + 1]));

  const pos = {};
  nodes.forEach((n) => {
    pos[n.id] = { x: pad + n.x * (width - pad * 2), y: pad + n.y * (height - pad * 2), name: n.name };
  });

  return (
    <svg width={width} height={height} className="cork" style={{ display: "block" }}>
      {edges.map((e, i) => {
        const a = pos[e.a];
        const b = pos[e.b];
        if (!a || !b) return null;
        const key = edgeKey(e.a, e.b);
        let stroke = "#8a7060";
        let sw = 2;
        if (rejKeys.has(key)) {
          stroke = "#6a5048";
          sw = 2;
        }
        if (mstKeys.has(key)) {
          stroke = "#56b27a";
          sw = 4;
        }
        if (pathSet.has(key)) {
          stroke = "#d6ac58";
          sw = 5;
        }
        if (
          highlight &&
          ((highlight.a === e.a && highlight.b === e.b) ||
            (highlight.a === e.b && highlight.b === e.a))
        ) {
          stroke = "#568cd6";
          sw = 6;
        }
        return (
          <g key={i}>
            <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={stroke} strokeWidth={sw} />
            <text
              x={(a.x + b.x) / 2}
              y={(a.y + b.y) / 2 - 6}
              fill="#c8b8a0"
              fontSize="11"
              textAnchor="middle"
            >
              {e.cost ?? e.minutes}
            </text>
          </g>
        );
      })}
      {nodes.map((n) => {
        const p = pos[n.id];
        const hot = n.id === current || n.id === neighbor || path.includes(n.id);
        return (
          <g key={n.id}>
            <circle
              cx={p.x}
              cy={p.y}
              r={hot ? 22 : 18}
              fill={n.id === current ? "#d6ac58" : "#2a221c"}
              stroke={hot ? "#f0ece4" : "#c4a882"}
              strokeWidth="2"
            />
            <text x={p.x} y={p.y + 4} textAnchor="middle" fontSize="10" fill="#f2eee6">
              {n.name.split(" ")[0]}
            </text>
            {dist[n.id] != null && dist[n.id] !== undefined && (
              <text x={p.x} y={p.y + 34} textAnchor="middle" fontSize="11" fill="#56b27a">
                {dist[n.id] >= 1e8 || dist[n.id] === null ? "∞" : `${dist[n.id]}m`}
              </text>
            )}
          </g>
        );
      })}
    </svg>
  );
}

function edgeKey(a, b) {
  return [a, b].sort().join("|");
}
