async function request(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

export const api = {
  cases: () => request("/api/cases"),
  case: (caseId = "case_001") => request(`/api/case?case_id=${caseId}`),
  graphColoring: (body = {}) =>
    request("/api/solve/graph-coloring", {
      method: "POST",
      body: JSON.stringify(body || {}),
    }),
  validate: (body = {}) =>
    request("/api/solve/validate", { method: "POST", body: JSON.stringify(body || {}) }),
  count: (body = {}) =>
    request("/api/solve/count", { method: "POST", body: JSON.stringify(body || {}) }),
  binarySearch: (body = {}) =>
    request("/api/solve/binary-search", { method: "POST", body: JSON.stringify(body || {}) }),
  kruskal: (body = {}) =>
    request("/api/solve/kruskal", { method: "POST", body: JSON.stringify(body || {}) }),
  knapsack: (body = {}) =>
    request("/api/solve/knapsack", { method: "POST", body: JSON.stringify(body || {}) }),
  mergeSort: (body = {}) =>
    request("/api/solve/merge-sort", { method: "POST", body: JSON.stringify(body || {}) }),
  dijkstra: (body = {}) =>
    request("/api/solve/dijkstra", { method: "POST", body: JSON.stringify(body || {}) }),
};
