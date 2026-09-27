from typing import Dict, List, Any
from .events import AlgoStep

DEFAULT_CAMERA_LOG = [
    {"id": "evt_1", "time": "22:30", "camera": "Cam 1 - Gallery North"},
    {"id": "evt_2", "time": "22:32", "camera": "Cam 2 - Lab West"},
    {"id": "evt_3", "time": "22:35", "camera": "Cam 3 - Archive Keypad"},
    {"id": "evt_4", "time": "22:38", "camera": "Cam 1 - Gallery South"},
    {"id": "evt_5", "time": "22:40", "camera": "Cam 4 - Alarm Panel Bypass"},
    {"id": "evt_6", "time": "22:42", "camera": "Cam 2 - Lab East"},
    {"id": "evt_7", "time": "22:45", "camera": "Cam 3 - Archive Door"},
    {"id": "evt_8", "time": "22:48", "camera": "Cam 5 - Exit Corridor"},
]

def solve_binary_search(case_id: str = "case_001") -> Dict[str, Any]:
    log = DEFAULT_CAMERA_LOG
    target_time = "22:40"
    steps: List[dict] = []

    lo = 0
    hi = len(log) - 1
    found_idx = -1

    steps.append(AlgoStep(
        kind="CHECK",
        message=f"Starting Binary Search for bypass event at timestamp {target_time}.",
        payload={"lo": lo, "hi": hi, "mid": None}
    ).to_dict())

    while lo <= hi:
        mid = (lo + hi) // 2
        curr_time = log[mid]["time"]

        steps.append(AlgoStep(
            kind="MID",
            message=f"Checking index {mid} (timestamp: {curr_time}). Range [{lo}..{hi}].",
            payload={"lo": lo, "hi": hi, "mid": mid}
        ).to_dict())

        if curr_time == target_time:
            found_idx = mid
            steps.append(AlgoStep(
                kind="FOUND",
                message=f"Bypass event FOUND at index {mid} ({curr_time}) on {log[mid]['camera']}.",
                payload={"lo": lo, "hi": hi, "mid": mid, "found_index": mid}
            ).to_dict())
            break
        elif curr_time < target_time:
            steps.append(AlgoStep(
                kind="GO_RIGHT",
                message=f"Target {target_time} > {curr_time}. Narrowing search to right half.",
                payload={"lo": mid + 1, "hi": hi, "mid": mid}
            ).to_dict())
            lo = mid + 1
        else:
            steps.append(AlgoStep(
                kind="GO_LEFT",
                message=f"Target {target_time} < {curr_time}. Narrowing search to left half.",
                payload={"lo": lo, "hi": mid - 1, "mid": mid}
            ).to_dict())
            hi = mid - 1

    if found_idx == -1:
        steps.append(AlgoStep(
            kind="NOT_FOUND",
            message=f"Target {target_time} not found in timestamp log.",
            payload={"lo": lo, "hi": hi}
        ).to_dict())

    return {
        "steps": steps,
        "log": log,
        "target": target_time
    }
