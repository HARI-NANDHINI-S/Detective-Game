from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from models.case import load_case, default_case_path


# ---------------------------------------------------------------------
# App
# ---------------------------------------------------------------------

app = FastAPI(
    title="Detective Game API",
    version="1.0.0",
    description="Backend API for the Detective Evidence Board game.",
)


# ---------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://detective-game-dwcb.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------
# Case loading
# ---------------------------------------------------------------------

CASE_PATH = Path(default_case_path())
CASE = load_case(str(CASE_PATH))


# ---------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------

class SolveRequest(BaseModel):
    case_id: str = "case_001"
    found_evidence: list[str] = []
    interviewed: list[str] = []


class CountRequest(BaseModel):
    found_evidence: list[str] = []
    interviewed: list[str] = []
    cap: int = 5


class ValidateRequest(BaseModel):
    found_evidence: list[str] = []
    interviewed: list[str] = []
    suspect: str
    location: str
    assignment: dict[str, str] = {}


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_case(case_id: str = "case_001"):
    if case_id != CASE.case_id:
        raise HTTPException(
            status_code=404,
            detail=f"Case '{case_id}' not found.",
        )
    return CASE


def serialize_case(case):
    return {
        "case_id": case.case_id,
        "title": case.title,
        "subtitle": case.subtitle,
        "briefing": case.briefing,
        "theft_window": case.theft_window,
        "culprit_location": case.culprit_location,
        "locations": [
            {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
            }
            for loc in case.locations
        ],
        "suspects": [
            {
                "id": suspect.id,
                "name": suspect.name,
                "full_name": suspect.full_name,
                "role": suspect.role,
                "profile": suspect.profile,
                "statement": suspect.statement,
                "constraints": suspect.constraints,
            }
            for suspect in case.suspects
        ],
        "evidence": [
            {
                "id": evidence.id,
                "object": evidence.object,
                "name": evidence.name,
                "description": evidence.description,
                "clue": evidence.clue,
                "constraints": evidence.constraints,
            }
            for evidence in case.evidence
        ],
        "conclusion": case.conclusion,
    }


# ---------------------------------------------------------------------
# Basic routes
# ---------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "name": "Detective Game API",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/cases")
def cases():
    return [
        {
            "case_id": CASE.case_id,
            "title": CASE.title,
            "subtitle": CASE.subtitle,
        }
    ]


@app.get("/api/case")
def case(case_id: str = "case_001"):
    return serialize_case(get_case(case_id))


# ---------------------------------------------------------------------
# Graph Coloring
# ---------------------------------------------------------------------

@app.post("/api/solve/graph-coloring")
def solve_graph_coloring(request: SolveRequest):
    case = get_case(request.case_id)

    solver = case.build_solver(
        request.found_evidence,
        request.interviewed,
    )

    solved, assignment = solver.solve(record=False)

    return {
        "solved": solved,
        "assignment": assignment,
        "nodes_explored": solver.nodes_explored,
        "backtracks": solver.backtracks,
    }


# ---------------------------------------------------------------------
# Count possible solutions
# ---------------------------------------------------------------------

@app.post("/api/solve/count")
def solve_count(request: CountRequest):
    cap = max(1, min(request.cap, 100))

    count = CASE.solution_count(
        request.found_evidence,
        request.interviewed,
        cap=cap,
    )

    constraints = CASE.active_constraints(
        request.found_evidence,
        request.interviewed,
    )

    return {
        "count": count,
        "capped": count >= cap,
        "constraints": constraints,
    }


# ---------------------------------------------------------------------
# Validate one suspect -> location placement
# ---------------------------------------------------------------------

@app.post("/api/solve/validate")
def validate_assignment(request: ValidateRequest):
    case = CASE

    if request.suspect not in case.suspect_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown suspect: {request.suspect}",
        )

    if request.location not in case.location_ids:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown location: {request.location}",
        )

    allowed = case.allowed(
        request.found_evidence,
        request.interviewed,
    )

    # Direct forbidden-location check.
    if request.location not in allowed[request.suspect]:
        forbidden = case.forbidden(
            request.found_evidence,
            request.interviewed,
        )

        return {
            "valid": False,
            "reason": "forbidden_location",
            "pretty": (
                f"{case.suspect_name(request.suspect)} cannot be placed "
                f"in the {case.location_name(request.location)}."
            ),
            "blame": None,
            "forbidden": forbidden.get(request.suspect, []),
        }

    # Test the proposed assignment against all active graph constraints.
    candidate = dict(request.assignment)
    candidate[request.suspect] = request.location

    # Validate that no two connected suspects share a location.
    edges = case.edges(
        request.found_evidence,
        request.interviewed,
    )

    for a, b in edges:
        if candidate.get(a) and candidate.get(b):
            if candidate[a] == candidate[b]:
                blame = b if a == request.suspect else a

                return {
                    "valid": False,
                    "reason": "edge_conflict",
                    "pretty": (
                        f"{case.suspect_name(request.suspect)} cannot share "
                        f"the {case.location_name(request.location)} with "
                        f"{case.suspect_name(blame)}."
                    ),
                    "blame": blame,
                }

    return {
        "valid": True,
        "reason": "ok",
        "pretty": (
            f"{case.suspect_name(request.suspect)} can be placed "
            f"in the {case.location_name(request.location)}."
        ),
        "blame": None,
    }