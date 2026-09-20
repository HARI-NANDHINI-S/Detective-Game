"""
Recursive Backtracking Graph Coloring.

Suspects = vertices, locations = colors, restrictions = edges.
The solver records every step it takes as an AlgoEvent so the UI can replay
the REAL search (nothing here is pre-scripted or hard-coded).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Sequence

# Event kinds
CHECK = "CHECK"
ASSIGN = "ASSIGN"
CONFLICT = "CONFLICT"
BACKTRACK = "BACKTRACK"
SUCCESS = "SUCCESS"
FAIL = "FAIL"


@dataclass
class AlgoEvent:
    """One observable step of the backtracking search."""
    kind: str
    suspect: str = ""
    location: str = ""
    message: str = ""
    depth: int = 0
    assignment: Dict[str, str] = field(default_factory=dict)
    # suspect the conflict was caused by (for edge highlighting), if any
    blame: str = ""

    def label(self) -> str:
        icon = {
            CHECK: "?",
            ASSIGN: "+",
            CONFLICT: "x",
            BACKTRACK: "<",
            SUCCESS: "*",
            FAIL: "!",
        }.get(self.kind, "-")
        return f"[{icon}] {self.message}"


class GraphColoringSolver:
    """Recursive backtracking solver over (suspects, locations, edges, domains)."""

    def __init__(
        self,
        suspects: Sequence[str],
        locations: Sequence[str],
        edges: Sequence[Sequence[str]],
        allowed: Dict[str, List[str]],
    ):
        self.suspects = list(suspects)
        self.locations = list(locations)
        self.edges = [tuple(e) for e in edges]
        self.allowed = {s: list(allowed.get(s, list(locations))) for s in self.suspects}

        self.adjacency: Dict[str, List[str]] = {s: [] for s in self.suspects}
        for a, b in self.edges:
            if a in self.adjacency and b in self.adjacency:
                if b not in self.adjacency[a]:
                    self.adjacency[a].append(b)
                if a not in self.adjacency[b]:
                    self.adjacency[b].append(a)

        self.events: List[AlgoEvent] = []
        self.assignment: Dict[str, str] = {}
        self.nodes_explored = 0
        self.backtracks = 0

    # ------------------------------------------------------------------ utils
    def conflicting_neighbour(self, suspect: str, location: str,
                              assignment: Dict[str, str]) -> str:
        """Return the neighbour that already occupies `location`, or ''."""
        for other in self.adjacency[suspect]:
            if assignment.get(other) == location:
                return other
        return ""

    def is_valid(self, suspect: str, location: str,
                 assignment: Dict[str, str]) -> bool:
        if location not in self.allowed[suspect]:
            return False
        return self.conflicting_neighbour(suspect, location, assignment) == ""

    def explain(self, suspect: str, location: str,
                assignment: Dict[str, str]) -> str:
        """Human readable reason why an assignment fails ('' if it is fine)."""
        if location not in self.allowed[suspect]:
            return f"Invalid: evidence rules out {suspect} being in the {location}."
        other = self.conflicting_neighbour(suspect, location, assignment)
        if other:
            return (f"Invalid: {suspect} and {other} are connected and "
                    f"cannot both be in the {location}.")
        return ""

    def _record(self, ev: AlgoEvent):
        ev.assignment = dict(self.assignment)
        self.events.append(ev)

    # ------------------------------------------------------------------ solve
    def solve(self, record: bool = True):
        """Run the search. Returns (solved, assignment)."""
        self.events = []
        self.assignment = {}
        self.nodes_explored = 0
        self.backtracks = 0
        solved = self._backtrack(0, record)
        if record:
            if solved:
                self._record(AlgoEvent(
                    SUCCESS, message="SUCCESS - every suspect placed, all constraints satisfied.",
                    depth=len(self.suspects)))
            else:
                self._record(AlgoEvent(
                    FAIL, message="FAILURE - no assignment satisfies the evidence."))
        return solved, dict(self.assignment)

    def _backtrack(self, index: int, record: bool) -> bool:
        if index == len(self.suspects):
            return True

        suspect = self.suspects[index]
        for location in self.locations:
            self.nodes_explored += 1
            if record:
                self._record(AlgoEvent(
                    CHECK, suspect, location,
                    f"Testing {suspect} -> {location} ...", depth=index))

            reason = self.explain(suspect, location, self.assignment)
            if reason:
                if record:
                    blame = self.conflicting_neighbour(suspect, location, self.assignment)
                    self._record(AlgoEvent(
                        CONFLICT, suspect, location, reason, depth=index, blame=blame))
                continue

            self.assignment[suspect] = location
            if record:
                self._record(AlgoEvent(
                    ASSIGN, suspect, location,
                    f"{suspect} -> {location} accepted.", depth=index))

            if self._backtrack(index + 1, record):
                return True

            del self.assignment[suspect]
            self.backtracks += 1
            if record:
                self._record(AlgoEvent(
                    BACKTRACK, suspect, location,
                    f"Backtracking: undo {suspect} -> {location}.", depth=index))

        return False


def count_solutions(suspects, locations, edges, allowed, cap: int = 5) -> int:
    """Count solutions (up to `cap`) - used to verify the case is unique."""
    solver = GraphColoringSolver(suspects, locations, edges, allowed)
    found = [0]
    assignment: Dict[str, str] = {}

    def rec(i: int):
        if found[0] >= cap:
            return
        if i == len(solver.suspects):
            found[0] += 1
            return
        s = solver.suspects[i]
        for loc in solver.locations:
            if solver.is_valid(s, loc, assignment):
                assignment[s] = loc
                rec(i + 1)
                del assignment[s]

    rec(0)
    return found[0]
