from typing import Dict, List, Any
import heapq
from .events import AlgoStep

DEFAULT_NODES = [
    {"id": "gallery", "name": "Gallery"},
    {"id": "laboratory", "name": "Laboratory"},
    {"id": "archive", "name": "Archive"},
    {"id": "security", "name": "Security Room"},
]

DEFAULT_EDGES = [
    {"from": "gallery", "to": "laboratory", "minutes": 8, "cost": 8},
    {"from": "gallery", "to": "security", "minutes": 12, "cost": 12},
    {"from": "laboratory", "to": "archive", "minutes": 6, "cost": 6},
    {"from": "archive", "to": "security", "minutes": 10, "cost": 10},
    {"from": "gallery", "to": "archive", "minutes": 15, "cost": 15},
]

DEFAULT_ALIBI = {
    "suspect": "victor",
    "statement": "Victor claimed he walked from the Archive to the Gallery in under 10 minutes at 22:35.",
    "start": "archive",
    "target": "gallery",
    "claimed_minutes": 10
}

def solve_dijkstra(case_id: str = "case_001") -> Dict[str, Any]:
    nodes = DEFAULT_NODES
    edges = DEFAULT_EDGES
    alibi = DEFAULT_ALIBI
    start = alibi["start"]
    target = alibi["target"]
    claimed = alibi["claimed_minutes"]

    node_ids = [n["id"] for n in nodes]

    adj: Dict[str, List[dict]] = {n: [] for n in node_ids}
    for e in edges:
        u, v, w = e["from"], e["to"], e["minutes"]
        adj[u].append({"node": v, "cost": w})
        adj[v].append({"node": u, "cost": w})

    dist = {n: 1e9 for n in node_ids}
    parent = {n: None for n in node_ids}
    dist[start] = 0

    pq = [(0, start)]
    visited = set()

    steps: List[dict] = []

    steps.append(AlgoStep(
        kind="EXTRACT",
        message=f"Starting Dijkstra shortest path from {start} to {target}.",
        payload={"dist": dict(dist), "current": start, "path": [start]}
    ).to_dict())

    while pq:
        d, curr = heapq.heappop(pq)
        if curr in visited:
            continue
        visited.add(curr)

        steps.append(AlgoStep(
            kind="EXTRACT",
            message=f"Visited location '{curr}' (current shortest time: {int(d)} min).",
            payload={"dist": dict(dist), "current": curr}
        ).to_dict())

        if curr == target:
            break

        for edge in adj.get(curr, []):
            nxt = edge["node"]
            w = edge["cost"]
            if nxt in visited:
                continue

            new_d = d + w
            steps.append(AlgoStep(
                kind="COMPARE",
                message=f"Checking corridor {curr} <-> {nxt} (walk time: {w} min).",
                payload={"dist": dict(dist), "current": curr, "neighbor": nxt}
            ).to_dict())

            if new_d < dist[nxt]:
                dist[nxt] = new_d
                parent[nxt] = curr
                heapq.heappush(pq, (new_d, nxt))
                steps.append(AlgoStep(
                    kind="UPDATE",
                    message=f"Updated shortest time to '{nxt}': {int(new_d)} min.",
                    payload={"dist": dict(dist), "current": curr, "neighbor": nxt}
                ).to_dict())

    # Reconstruct path
    path = []
    curr = target
    if dist[target] < 1e8:
        while curr:
            path.append(curr)
            curr = parent[curr]
        path.reverse()

    computed_minutes = int(dist[target]) if dist[target] < 1e8 else None
    is_possible = computed_minutes is not None and computed_minutes <= claimed

    steps.append(AlgoStep(
        kind="PATH" if is_possible or computed_minutes is not None else "UNREACHABLE",
        message=f"Shortest path calculated: {' -> '.join(path)} takes {computed_minutes} min (Claimed: {claimed} min).",
        payload={"dist": dict(dist), "path": path, "minutes": computed_minutes}
    ).to_dict())

    return {
        "steps": steps,
        "nodes": nodes,
        "edges": edges,
        "alibi": alibi,
        "claimed_minutes": claimed,
        "minutes": computed_minutes,
        "possible": is_possible,
    }
