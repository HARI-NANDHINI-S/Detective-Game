import { useEffect, useMemo, useRef, useState } from "react";
import { soundFX } from "../utils/soundFX";

const BASE_INTERVAL = 550;

export default function AlgorithmVisualizer({
  title,
  subtitle,
  steps = [],
  loading = false,
  error = "",
  renderFrame,
  extraStatus,
  onComplete,
  completeKinds = ["DONE", "SUCCESS", "FOUND", "PATH"],
}) {
  const [index, setIndex] = useState(-1);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1.5);
  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    if (steps && steps.length > 0) {
      setIndex(0);
    } else {
      setIndex(-1);
    }
    setPlaying(false);
  }, [steps]);

  const step = index >= 0 && index < steps.length ? steps[index] : null;

  useEffect(() => {
    if (index >= 0 && index < steps.length) {
      soundFX.playStep();
    }
  }, [index, steps.length]);

  useEffect(() => {
    if (!playing) return undefined;
    const id = window.setInterval(() => {
      setIndex((i) => {
        if (i >= steps.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
      setAutoScroll(true);
    }, BASE_INTERVAL / speed);
    return () => window.clearInterval(id);
  }, [playing, speed, steps.length]);

  const doneRef = useRef(false);
  useEffect(() => {
    doneRef.current = false;
  }, [steps]);
  useEffect(() => {
    if (!step || doneRef.current) return;
    if (completeKinds.includes(step.kind) && index === steps.length - 1) {
      doneRef.current = true;
      soundFX.playSuccess();
      onComplete?.(step);
    }
  }, [step, index, steps.length, completeKinds, onComplete]);

  const shown = useMemo(() => steps.slice(0, Math.max(0, index + 1)), [steps, index]);

  const restart = () => {
    soundFX.playClick();
    setIndex(steps.length > 0 ? 0 : -1);
    setPlaying(false);
    setAutoScroll(true);
  };

  const stepOnce = () => {
    soundFX.playClick();
    setPlaying(false);
    setIndex((i) => (i < 0 ? 0 : Math.min(i + 1, steps.length - 1)));
    setAutoScroll(true);
  };

  const runToEnd = () => {
    soundFX.playClick();
    setPlaying(false);
    setIndex(steps.length - 1);
    setAutoScroll(true);
  };

  const toggle = () => {
    soundFX.playClick();
    if (!steps.length) return;
    if (index >= steps.length - 1) {
      setIndex(0);
      setPlaying(true);
      return;
    }
    if (index === -1) {
      setIndex(0);
    }
    setPlaying((p) => !p);
  };

  return (
    <div>
      {title && (
        <div style={{ marginBottom: 8 }}>
          <strong className="gold">{title}</strong>
          {subtitle && <div className="muted">{subtitle}</div>}
        </div>
      )}
      {loading && <div className="muted">Running solver on the backend…</div>}
      {error && <div className="red">{error}</div>}
      {renderFrame?.(step, index, steps)}
      <div className="viz-controls">
        <button className="gold" onClick={toggle} disabled={!steps.length}>
          {playing ? "PAUSE" : "PLAY"}
        </button>
        <button onClick={stepOnce} disabled={!steps.length}>
          STEP
        </button>
        <button onClick={restart}>RESTART</button>
        <button onClick={runToEnd} disabled={!steps.length}>
          RUN TO END
        </button>
        <label className="muted">
          Speed {speed.toFixed(1)}x
          <input
            type="range"
            min="0.25"
            max="6"
            step="0.05"
            value={speed}
            onChange={(e) => setSpeed(Number(e.target.value))}
            style={{ marginLeft: 8, verticalAlign: "middle" }}
          />
        </label>
        {extraStatus}
      </div>
      <div
        className="log"
        style={{ height: 220, marginTop: 12 }}
        onWheel={() => setAutoScroll(false)}
        ref={(el) => {
          if (el && autoScroll) el.scrollTop = el.scrollHeight;
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span className="gold">ALGORITHM LOG</span>
          <span className="muted">
            {Math.max(index + 1, 0)} / {steps.length} steps
          </span>
        </div>
        {shown.map((s, i) => (
          <div key={i} style={{ marginTop: 6, paddingLeft: (s.depth || 0) * 12 }}>
            <span className="kind" style={{ color: kindColor(s.kind) }}>
              {s.kind}
            </span>
            <span>{s.message}</span>
          </div>
        ))}
        {!shown.length && (
          <div className="faint" style={{ marginTop: 8 }}>
            Press PLAY (or STEP) to watch the solver.
          </div>
        )}
      </div>
    </div>
  );
}

function kindColor(kind) {
  const map = {
    CHECK: "var(--text-dim)",
    ASSIGN: "var(--green)",
    CONFLICT: "var(--red)",
    BACKTRACK: "var(--amber)",
    SUCCESS: "var(--gold)",
    FAIL: "var(--red)",
    FOUND: "var(--green)",
    UNION: "var(--green)",
    SKIP_CYCLE: "var(--red)",
    CELL: "var(--text-dim)",
    DONE: "var(--gold)",
    SPLIT: "var(--blue)",
    COMPARE: "var(--amber)",
    EXTRACT: "var(--blue)",
    UPDATE: "var(--green)",
    PATH: "var(--gold)",
    MID: "var(--blue)",
    GO_LEFT: "var(--amber)",
    GO_RIGHT: "var(--amber)",
  };
  return map[kind] || "var(--text)";
}
