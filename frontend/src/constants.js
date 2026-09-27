export const LOCATION_COLORS = {
  gallery: "#ce4c4a",
  laboratory: "#56b27a",
  archive: "#568cd6",
  security: "#d6ac58",
};

export function locationColor(id) {
  if (!id) return "#566074";
  return LOCATION_COLORS[id] || "#9674ce";
}

export const SCENES = {
  MENU: "menu",
  CRIME: "crime_scene",
  CASEFILE: "investigation",
  INTERVIEWS: "interviews",
  BINARY: "binary_search",
  KRUSKAL: "kruskal",
  KNAPSACK: "knapsack",
  MERGESORT: "merge_sort",
  DIJKSTRA: "dijkstra",
  BOARD: "board",
  ANALYSIS: "analysis",
  RESULT: "result",
  DAA: "daa",
};

const SAVE_KEY = "detective-evidence-board-save";

export function emptyProgress() {
  return {
    found_evidence: [],
    interviewed: [],
    assignments: {},
    solved_by_algorithm: false,
    algorithm_solution: {},
    case_closed: false,
    stages_done: {},
  };
}

export function loadSave() {
  try {
    const raw = localStorage.getItem(SAVE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function writeSave(progress, caseId) {
  localStorage.setItem(
    SAVE_KEY,
    JSON.stringify({ case_id: caseId, ...progress })
  );
}
