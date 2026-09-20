"""Player progress: evidence found, interviews done, board assignments."""

import json
import os
from typing import Dict, List


class GameState:
    def __init__(self, case):
        self.case = case
        self.reset()

    # ------------------------------------------------------------ lifecycle
    def reset(self):
        self.found_evidence: List[str] = []
        self.interviewed: List[str] = []
        self.assignments: Dict[str, str] = {}      # suspect_id -> location_id
        self.solved_by_algorithm = False
        self.algorithm_solution: Dict[str, str] = {}
        self.case_closed = False
        self.notes: List[str] = []

    # ------------------------------------------------------------- progress
    def collect(self, evidence_id: str) -> bool:
        if evidence_id in self.found_evidence:
            return False
        self.found_evidence.append(evidence_id)
        return True

    def interview(self, suspect_id: str) -> bool:
        if suspect_id in self.interviewed:
            return False
        self.interviewed.append(suspect_id)
        return True

    @property
    def all_evidence_found(self) -> bool:
        return len(self.found_evidence) >= len(self.case.evidence)

    @property
    def all_interviews_done(self) -> bool:
        return len(self.interviewed) >= len(self.case.suspects)

    @property
    def ready_for_board(self) -> bool:
        return self.all_evidence_found and self.all_interviews_done

    # ----------------------------------------------------------------- board
    def assign(self, suspect_id: str, location_id):
        if location_id is None:
            self.assignments.pop(suspect_id, None)
        else:
            self.assignments[suspect_id] = location_id

    def clear_assignments(self):
        self.assignments = {}

    def manual_solution_is_complete(self) -> bool:
        return all(s in self.assignments for s in self.case.suspect_ids)

    # ------------------------------------------------------------ save/load
    def to_dict(self) -> dict:
        return {
            "case_id": self.case.case_id,
            "found_evidence": self.found_evidence,
            "interviewed": self.interviewed,
            "assignments": self.assignments,
            "solved_by_algorithm": self.solved_by_algorithm,
            "algorithm_solution": self.algorithm_solution,
            "case_closed": self.case_closed,
        }

    def load_dict(self, data: dict):
        self.found_evidence = [e for e in data.get("found_evidence", [])
                               if e in self.case.all_evidence_ids()]
        self.interviewed = [s for s in data.get("interviewed", [])
                            if s in self.case.suspect_ids]
        self.assignments = {
            k: v for k, v in (data.get("assignments") or {}).items()
            if k in self.case.suspect_ids and v in self.case.location_ids
        }
        self.solved_by_algorithm = bool(data.get("solved_by_algorithm", False))
        self.algorithm_solution = {
            k: v for k, v in (data.get("algorithm_solution") or {}).items()
            if k in self.case.suspect_ids and v in self.case.location_ids
        }
        self.case_closed = bool(data.get("case_closed", False))

    def save(self, path: str) -> bool:
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(self.to_dict(), fh, indent=2)
            return True
        except OSError:
            return False

    def load(self, path: str) -> bool:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return False
        if data.get("case_id") and data["case_id"] != self.case.case_id:
            return False
        self.load_dict(data)
        return True

    @staticmethod
    def save_exists(path: str) -> bool:
        return os.path.isfile(path)
