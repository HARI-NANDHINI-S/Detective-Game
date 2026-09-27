# Detective's Evidence Board

A complete Python + Pygame mystery/puzzle game built around a real
**Backtracking Graph Colouring** algorithm, made for a college DAA demonstration.

A Chola bronze has been stolen from the Meridian Museum. Five suspects were inside.
You collect physical evidence, interview everyone, and then place every suspect in
a museum location on an Evidence Board without breaking a single constraint.

* **Suspects** are the graph's **vertices**
* **Museum locations** are the **colours**
* **"These two were never in the same room"** statements are the **edges**
* **Physical evidence** removes colours from a vertex's **domain**

The case is constructed so that the constraint graph has **exactly one valid
colouring**, and so that a fixed-order solver must perform **10 real backtracks**
(115 recorded steps) before it finds it.

---

## Running

```bash
pip install -r requirements.txt
python main.py
```

Requires Python 3.8+ and Pygame 2.x. No internet, database or external asset is
used - all graphics are drawn with Pygame primitives and system fonts.

## Controls

| Input | Action |
|---|---|
| Left click | Examine an object / select a suspect / press a button |
| Right click a suspect | Remove that suspect's placement |
| `1` – `4` | Assign the selected suspect to location 1–4 |
| `Backspace` / `Delete` | Clear the selected suspect |
| `Space` | Play / pause the algorithm animation |
| `→` | Single step the algorithm |
| `R` | Restart the animation |
| Mouse wheel | Scroll lists and logs |
| `F5` / `F9` | Save / load the case (JSON) |
| `Esc` | Back to the main menu (quits from the menu) |

## Game flow

1. **Main Menu** – new case, load case, board, DAA explanation.
2. **Crime Scene** – examine six objects (broken display case, security camera,
   fingerprints, footprints, torn note, security badge) and log them. Each one
   unlocks constraints.
3. **Case File** – every clue collected plus the constraints it produced, and a
   live count of how constrained the graph currently is.
4. **Suspect Interviews** – five suspects; recording a statement adds edges.
5. **Evidence Board** – assign locations by hand. Invalid moves are rejected with
   an explanation, e.g. *"Invalid: Daniel and Maya are connected and cannot both
   be in the Laboratory."*
6. **Evidence Analysis** – press **ANALYZE EVIDENCE** to watch the real solver run,
   with Play / Pause / Step / Run-to-end / Restart and a speed slider.
7. **Case Result** – final placements, the thief, the supporting evidence and the
   full explanation.
8. **DAA Explanation** – graph colouring, backtracking, pseudocode and complexity.

## The algorithm

`algorithms/backtracking.py` contains `GraphColoringSolver`. `solve()` calls the
recursive `_backtrack(index)`:

```
if every suspect is coloured        -> success
for each location:
    CHECK    the (suspect, location) pair
    CONFLICT if evidence forbids it, or a neighbour already holds it
    ASSIGN   otherwise, then recurse on the next suspect
    BACKTRACK undo the assignment if the recursion failed
```

The **same call** that computes the answer appends `AlgoEvent` objects
(`CHECK`, `ASSIGN`, `CONFLICT`, `BACKTRACK`, `SUCCESS`, `FAIL`) to a list, and the
Analysis screen simply replays that list against the clock. The animation therefore
cannot disagree with the algorithm, and nothing about the solution is hard-coded —
change `data/case_001.json` and the game will solve the new case instead.

`count_solutions()` is used in-game to tell you whether the evidence you have
gathered pins the answer down to a unique colouring.

**Complexity:** O(V · k^V) worst case (V suspects, k locations); O(V + E) space plus
the O(V) recursion stack. k-colouring is NP-complete for k ≥ 3, which is exactly why
pruning-based backtracking is the right tool.

## Project structure

```
detective_evidence_board/
├── main.py                  entry point
├── game/
│   ├── config.py            window size, paths, scene ids
│   ├── state.py             player progress + JSON save/load
│   └── app.py               window, main loop, scene manager
├── algorithms/
│   └── backtracking.py      graph colouring solver + event recorder
├── models/
│   └── case.py              case file model, builds the graph from constraints
├── scenes/
│   ├── base.py  menu.py  crime_scene.py  investigation.py
│   ├── interviews.py  board.py  analysis.py  result.py  daa_info.py
├── ui/
│   ├── theme.py             palette and fonts
│   ├── widgets.py           buttons, panels, sliders, scroll lists, toasts
│   └── graph_view.py        corkboard graph renderer
├── data/
│   └── case_001.json        the case (suspects, locations, evidence, constraints)
├── assets/                  (empty - everything is drawn procedurally)
├── requirements.txt
└── README.md
```

## Editing or adding a case

Everything about the mystery lives in `data/case_001.json`: locations, suspects
(with their statement and the edges it creates), evidence (with the forbidden
placements it proves), and the closing narration. `culprit_location` names the room
that identifies the thief. Add constraints, save, restart — the solver adapts.

Save files are written to `data/savegame.json`.
