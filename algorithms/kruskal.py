from typing import Dict, List, Any
from .events import AlgoStep

class DisjointSet:
    def __init__(self, items):
        self.parent = {item: item for item in items}

    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]

    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j:
            self.parent[root_i] = root_j
            return True
        return False

DEFAULT_NODES = [
    {"id": "gallery", "name": "Gallery"},
    {"id": "laboratory", "name": "Laboratory"},
    {"id": "archive", "name": "Archive"},
    {"id": "security", "name": "Security Room"},
]

DEFAULT_EDGES = [
    {"from": "gallery", "to": "laboratory", "cost": 15, "label": "Gallery ↔ Lab"},
    {"from": "gallery", "to": "security", "cost": 25, "label": "Gallery ↔ Security"},
    {"from": "laboratory", "to": "archive", "cost": 10, "label": "Lab ↔ Archive"},
    {"from": "archive", "to": "security", "cost": 20, "label": "Archive ↔ Security"},
    {"from": "gallery", "to": "archive", "cost": 30, "label": "Gallery ↔ Archive"},
]

def solve_kruskal(case_id: str = "case_001") -> Dict[str, Any]:
    nodes = DEFAULT_NODES
    edges = DEFAULT_EDGES
    node_ids = [n["id"] for n in nodes]
    sorted_edges = sorted(edges, key=lambda x: x["cost"])

    ds = DisjointSet(node_ids)
    mst: List[dict] = []
    rejected: List[dict] = []
    steps: List[dict] = []

    steps.append(AlgoStep(
        kind="CHECK",
        message="Starting Kruskal's Minimum Spanning Tree algorithm on camera cable network.",
        payload={"mst": [], "rejected": []}
    ).to_dict())

    total_cost = 0
    for edge in sorted_edges:
        u, v = edge["from"], edge["to"]
        if ds.union(u, v):
            mst.append(edge)
            total_cost += edge["cost"]
            steps.append(AlgoStep(
                kind="UNION",
                message=f"Added link {edge['label']} (cost: {edge['cost']}) to MST.",
                payload={"mst": list(mst), "rejected": list(rejected), "edge": edge}
            ).to_dict())
        else:
            rejected.append(edge)
            steps.append(AlgoStep(
                kind="SKIP_CYCLE",
                message=f"Rejected link {edge['label']} — creates a cycle (blind spot corridor).",
                payload={"mst": list(mst), "rejected": list(rejected), "edge": edge}
            ).to_dict())

    steps.append(AlgoStep(
        kind="DONE",
        message=f"MST complete. Total cable cost: {total_cost}.",
        payload={"mst": list(mst), "rejected": list(rejected)}
    ).to_dict())

    return {
        "steps": steps,
        "nodes": nodes,
        "edges": edges,
        "total_cost": total_cost,
    }
