from typing import Dict, List, Any
from .events import AlgoStep

DEFAULT_TIMELINE_NOTES = [
    {"id": "n1", "time": "22:45", "source": "Security Log", "text": "Corridor motion detector triggered"},
    {"id": "n2", "time": "22:20", "source": "Lab Log", "text": "Laboratory floor mopped clean"},
    {"id": "n3", "time": "22:40", "source": "Alarm Log", "text": "Display case alarm bypassed with cloned badge"},
    {"id": "n4", "time": "22:30", "source": "Camera Log", "text": "Victor seen near entrance corridor"},
    {"id": "n5", "time": "22:35", "source": "Keypad Log", "text": "Archive keypad accessed"},
]

def solve_merge_sort(case_id: str = "case_001") -> Dict[str, Any]:
    notes = [dict(n) for n in DEFAULT_TIMELINE_NOTES]
    original = [dict(n) for n in DEFAULT_TIMELINE_NOTES]
    steps: List[dict] = []

    steps.append(AlgoStep(
        kind="CHECK",
        message="Starting Merge Sort to chronologically order case timeline notes.",
        payload={"array": [dict(n) for n in notes], "lo": 0, "hi": len(notes) - 1, "highlight": []}
    ).to_dict())

    def merge_sort_helper(arr, lo, hi):
        if lo >= hi:
            return

        mid = (lo + hi) // 2

        steps.append(AlgoStep(
            kind="SPLIT",
            message=f"Splitting timeline segment [{lo}..{hi}] into [{lo}..{mid}] and [{mid+1}..{hi}].",
            payload={"array": [dict(n) for n in arr], "lo": lo, "hi": hi, "mid": mid, "highlight": list(range(lo, hi + 1))}
        ).to_dict())

        merge_sort_helper(arr, lo, mid)
        merge_sort_helper(arr, mid + 1, hi)

        # Merge
        left = arr[lo:mid + 1]
        right = arr[mid + 1:hi + 1]

        i = 0
        j = 0
        k = lo

        while i < len(left) and j < len(right):
            steps.append(AlgoStep(
                kind="COMPARE",
                message=f"Comparing note ({left[i]['time']}) with ({right[j]['time']}).",
                payload={"array": [dict(n) for n in arr], "lo": lo, "hi": hi, "highlight": [lo + i, mid + 1 + j]}
            ).to_dict())

            if left[i]["time"] <= right[j]["time"]:
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1

        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1

        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1

        steps.append(AlgoStep(
            kind="DONE",
            message=f"Merged sorted timeline segment [{lo}..{hi}].",
            payload={"array": [dict(n) for n in arr], "lo": lo, "hi": hi, "highlight": list(range(lo, hi + 1))}
        ).to_dict())

    merge_sort_helper(notes, 0, len(notes) - 1)

    steps.append(AlgoStep(
        kind="DONE",
        message="Merge Sort complete! Timeline perfectly chronological.",
        payload={"array": [dict(n) for n in notes], "lo": 0, "hi": len(notes) - 1, "highlight": list(range(len(notes)))}
    ).to_dict())

    return {
        "steps": steps,
        "original": original,
        "sorted": notes,
    }
