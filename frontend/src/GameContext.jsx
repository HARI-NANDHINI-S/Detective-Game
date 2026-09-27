import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api } from "./api";
import { emptyProgress, loadSave, SCENES, writeSave } from "./constants";

const GameContext = createContext(null);

export function GameProvider({ children }) {
  const [scene, setScene] = useState(SCENES.MENU);
  const [caseData, setCaseData] = useState(null);
  const [casesList, setCasesList] = useState([]);
  const [selectedCaseId, setSelectedCaseId] = useState("case_001");
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(emptyProgress());
  const [toast, setToast] = useState(null);
  const [score, setScore] = useState(0);
  const [scoreHistory, setScoreHistory] = useState([]);

  // Load cases index
  useEffect(() => {
    api
      .cases()
      .then(setCasesList)
      .catch(() => {});
  }, []);

  // Load selected case
  useEffect(() => {
    api
      .case(selectedCaseId)
      .then(setCaseData)
      .catch((e) => setError(e.message || "Could not load case from the API."));
  }, [selectedCaseId]);

  const showToast = useCallback((text, color = "var(--gold)", seconds = 3.2) => {
    setToast({ text, color, id: Date.now() });
    window.setTimeout(() => setToast((t) => (t && t.text === text ? null : t)), seconds * 1000);
  }, []);

  const changeCase = useCallback((caseId) => {
    setSelectedCaseId(caseId);
    setProgress(emptyProgress());
    setScore(0);
    setScoreHistory([]);
  }, []);

  const addScore = useCallback((pts, reason) => {
    setScore((s) => Math.max(0, s + pts));
    setScoreHistory((h) => [...h, { pts, reason, time: new Date().toLocaleTimeString() }]);
  }, []);

  const updateProgress = useCallback((patch) => {
    setProgress((p) => ({ ...p, ...patch }));
  }, []);

  const collect = useCallback(
    (id) => {
      setProgress((p) => {
        if (p.found_evidence.includes(id)) return p;
        return { ...p, found_evidence: [...p.found_evidence, id] };
      });
    },
    []
  );

  const interview = useCallback((id) => {
    setProgress((p) => {
      if (p.interviewed.includes(id)) return p;
      return { ...p, interviewed: [...p.interviewed, id] };
    });
  }, []);

  const readyForBoard = useMemo(() => {
    if (!caseData) return false;
    return (
      progress.found_evidence.length >= caseData.evidence.length &&
      progress.interviewed.length >= caseData.suspects.length
    );
  }, [caseData, progress]);

  const newGame = () => {
    setProgress(emptyProgress());
    setScore(0);
    setScoreHistory([]);
    setScene(SCENES.CRIME);
  };

  const saveGame = () => {
    if (!caseData) return;
    writeSave({ ...progress, score }, caseData.case_id);
    showToast("Case notes & score saved.", "var(--green)");
  };

  const loadGame = () => {
    const data = loadSave();
    if (!data || (caseData && data.case_id && data.case_id !== caseData.case_id)) {
      showToast("No save file for this case yet.", "var(--red)");
      return false;
    }
    const { case_id, score: savedScore, ...rest } = data;
    setProgress({ ...emptyProgress(), ...rest });
    if (savedScore) setScore(savedScore);
    showToast("Case notes & score loaded.", "var(--green)");
    return true;
  };

  const markStage = (key) => {
    setProgress((p) => ({ ...p, stages_done: { ...p.stages_done, [key]: true } }));
  };

  const value = {
    scene,
    setScene,
    caseData,
    casesList,
    selectedCaseId,
    changeCase,
    error,
    progress,
    setProgress,
    updateProgress,
    collect,
    interview,
    readyForBoard,
    newGame,
    saveGame,
    loadGame,
    toast,
    showToast,
    markStage,
    score,
    scoreHistory,
    addScore,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
}

export function useGame() {
  return useContext(GameContext);
}
