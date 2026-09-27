from typing import Dict, List, Any
from .events import AlgoStep

DEFAULT_ITEMS = [
    {"id": "lead_1", "name": "Lab Solvent Audit", "cost": 2, "value": 40},
    {"id": "lead_2", "name": "Archive Keypad Log", "cost": 3, "value": 50},
    {"id": "lead_3", "name": "Security Badge Printer", "cost": 4, "value": 70},
    {"id": "lead_4", "name": "Gallery Entrance Tape", "cost": 1, "value": 30},
]
DEFAULT_CAPACITY = 5

def solve_knapsack(case_id: str = "case_001") -> Dict[str, Any]:
    items = DEFAULT_ITEMS
    capacity = DEFAULT_CAPACITY
    n = len(items)

    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    steps: List[dict] = []

    steps.append(AlgoStep(
        kind="CHECK",
        message=f"Initializing 0/1 Knapsack with capacity {capacity} hours.",
        payload={"table": [row[:] for row in dp], "i": 0, "w": 0, "chosen": []}
    ).to_dict())

    for i in range(1, n + 1):
        item = items[i - 1]
        w_item = item["cost"]
        v_item = item["value"]

        for w in range(capacity + 1):
            if w_item <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - w_item] + v_item)
            else:
                dp[i][w] = dp[i - 1][w]

            steps.append(AlgoStep(
                kind="CELL",
                message=f"Evaluated lead '{item['name']}' for budget {w}h -> max value: {dp[i][w]}.",
                payload={"table": [row[:] for row in dp], "i": i, "w": w, "chosen": []}
            ).to_dict())

    # Backtrack chosen items
    w = capacity
    chosen = []
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            item = items[i - 1]
            chosen.append(item)
            w -= item["cost"]

    chosen.reverse()

    steps.append(AlgoStep(
        kind="DONE",
        message=f"Optimal lead selection completed! Max value: {dp[n][capacity]} with {len(chosen)} leads.",
        payload={"table": [row[:] for row in dp], "i": n, "w": capacity, "chosen": chosen}
    ).to_dict())

    return {
        "steps": steps,
        "items": items,
        "capacity": capacity,
        "table": dp,
    }
