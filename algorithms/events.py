"""Shared step/event payload used by every solver for JSON animation."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class AlgoStep:
    kind: str
    message: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "message": self.message,
            "payload": self.payload,
        }


def snapshot_steps(steps: List[AlgoStep]) -> List[dict]:
    return [s.to_dict() for s in steps]
