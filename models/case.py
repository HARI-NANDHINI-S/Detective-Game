"""Data model for a case file: suspects, locations, evidence and constraints."""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from algorithms.backtracking import GraphColoringSolver, count_solutions


@dataclass
class Location:
    id: str
    name: str
    description: str = ""


@dataclass
class Suspect:
    id: str
    name: str
    full_name: str
    role: str
    profile: str
    statement: str
    constraints: List[dict] = field(default_factory=list)


@dataclass
class Evidence:
    id: str
    object: str
    name: str
    description: str
    clue: str
    constraints: List[dict] = field(default_factory=list)


class Case:
    """Holds the static case data plus helpers to turn it into a graph."""

    def __init__(self, raw: dict):
        self.raw = raw
        self.case_id = raw.get("case_id", "case")
        self.title = raw.get("title", "Untitled Case")
        self.subtitle = raw.get("subtitle", "")
        self.briefing: List[str] = raw.get("briefing", [])
        self.theft_window = raw.get("theft_window", "")
        self.culprit_location = raw.get("culprit_location", "")
        self.conclusion = raw.get("conclusion", {})

        self.locations = [Location(**l) for l in raw["locations"]]
        self.suspects = [
            Suspect(
                id=s["id"], name=s["name"], full_name=s["full_name"], role=s["role"],
                profile=s["profile"], statement=s["statement"],
                constraints=s.get("constraints", []),
            )
            for s in raw["suspects"]
        ]
        self.evidence = [
            Evidence(
                id=e["id"], object=e["object"], name=e["name"],
                description=e["description"], clue=e["clue"],
                constraints=e.get("constraints", []),
            )
            for e in raw["evidence"]
        ]

        self.location_ids = [l.id for l in self.locations]
        self.suspect_ids = [s.id for s in self.suspects]
        self._loc_by_id = {l.id: l for l in self.locations}
        self._sus_by_id = {s.id: s for s in self.suspects}

    # --------------------------------------------------------------- lookups
    def location(self, lid: str) -> Optional[Location]:
        return self._loc_by_id.get(lid)

    def suspect(self, sid: str) -> Optional[Suspect]:
        return self._sus_by_id.get(sid)

    def location_name(self, lid: str) -> str:
        loc = self.location(lid)
        return loc.name if loc else str(lid)

    def suspect_name(self, sid: str) -> str:
        sus = self.suspect(sid)
        return sus.name if sus else str(sid)

    # ----------------------------------------------------------- constraints
    def active_constraints(self, found_evidence, interviewed) -> List[dict]:
        """All constraints unlocked so far, each tagged with its source."""
        out = []
        for ev in self.evidence:
            if ev.id in found_evidence:
                for c in ev.constraints:
                    item = dict(c)
                    item["source"] = ev.object
                    item["source_id"] = ev.id
                    out.append(item)
        for s in self.suspects:
            if s.id in interviewed:
                for c in s.constraints:
                    item = dict(c)
                    item["source"] = f"Interview: {s.full_name}"
                    item["source_id"] = s.id
                    out.append(item)
        return out

    def edges(self, found_evidence, interviewed):
        return [(c["a"], c["b"])
                for c in self.active_constraints(found_evidence, interviewed)
                if c["type"] == "edge"]

    def forbidden(self, found_evidence, interviewed) -> Dict[str, List[str]]:
        bad: Dict[str, List[str]] = {s: [] for s in self.suspect_ids}
        for c in self.active_constraints(found_evidence, interviewed):
            if c["type"] == "forbid" and c["suspect"] in bad:
                if c["location"] not in bad[c["suspect"]]:
                    bad[c["suspect"]].append(c["location"])
        return bad

    def allowed(self, found_evidence, interviewed) -> Dict[str, List[str]]:
        bad = self.forbidden(found_evidence, interviewed)
        return {s: [l for l in self.location_ids if l not in bad[s]]
                for s in self.suspect_ids}

    def build_solver(self, found_evidence, interviewed) -> GraphColoringSolver:
        return GraphColoringSolver(
            self.suspect_ids,
            self.location_ids,
            self.edges(found_evidence, interviewed),
            self.allowed(found_evidence, interviewed),
        )

    def solution_count(self, found_evidence, interviewed, cap: int = 5) -> int:
        return count_solutions(
            self.suspect_ids, self.location_ids,
            self.edges(found_evidence, interviewed),
            self.allowed(found_evidence, interviewed), cap=cap,
        )

    def all_evidence_ids(self):
        return [e.id for e in self.evidence]

    def all_suspect_ids(self):
        return list(self.suspect_ids)


def load_case(path: str) -> Case:
    with open(path, "r", encoding="utf-8") as fh:
        return Case(json.load(fh))


def default_case_path() -> str:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "data", "case_001.json")
