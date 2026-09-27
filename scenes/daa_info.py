"""Beginner friendly explanation of graph colouring + backtracking."""

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import (Button, ScrollList, draw_panel, draw_text, draw_wrapped,
                        wrapped_height)

PAGES = [
    ("GRAPH COLOURING", [
        ("What is graph colouring?",
         "A graph is a set of vertices joined by edges. Graph colouring asks: can we "
         "give every vertex one colour out of k colours, so that no edge joins two "
         "vertices of the same colour? The smallest k that works is the chromatic "
         "number of the graph. It is used for exam timetables, register allocation "
         "in compilers, radio frequency assignment - and, here, for placing suspects."),
        ("Suspects become vertices",
         "Each of the five suspects is one vertex of the graph. A vertex needs exactly "
         "one colour, which matches the fact that a person can only be in one room at "
         "22:40."),
        ("Locations become colours",
         "The four museum locations - Gallery, Laboratory, Archive and Security Room - "
         "are the four colours. Colouring a vertex means saying 'this suspect was in "
         "this room'."),
        ("Edges are the restrictions",
         "An edge between two suspects means 'these two were never in the same room'. "
         "That is exactly the graph colouring rule: the two endpoints of an edge may "
         "not receive the same colour."),
        ("Evidence shrinks the domains",
         "Physical evidence does something slightly different: it removes a colour "
         "from one vertex ('Arjun was not in the Laboratory'). In CSP language each "
         "vertex has a domain of allowed colours, and evidence deletes values from "
         "that domain. Edges + domains together make the puzzle have a single answer."),
    ]),
    ("BACKTRACKING", [
        ("The idea",
         "Backtracking is organised trial and error. Choose the next vertex, try its "
         "first colour, check whether the partial colouring is still legal, and if it "
         "is, move on to the next vertex. If nothing works, undo the last choice and "
         "try the next colour there. It explores the search tree depth first and "
         "abandons a branch as soon as it becomes impossible."),
        ("Why not brute force?",
         "Brute force would build all 4^5 = 1024 complete assignments and test each at "
         "the end. Backtracking prunes: the moment Daniel clashes with Maya, every "
         "assignment that starts that way - all of them at once - is thrown away "
         "without ever being built. On bigger graphs that saving is enormous."),
        ("The events you see",
         "CHECK  - the solver is about to test a suspect in a location.\n"
         "ASSIGN - the placement passed every constraint and was kept.\n"
         "CONFLICT - it broke an edge or an evidence rule, so the colour is skipped.\n"
         "BACKTRACK - no colour worked deeper down, so the last placement is undone.\n"
         "SUCCESS - all five vertices are coloured legally."),
        ("Why backtracking suits this case",
         "The constraints are hard (never 'mostly true'), the domains are small, and "
         "we want a complete, provably consistent assignment. Backtracking gives "
         "exactly that, and because the case has a unique colouring, the answer it "
         "returns is THE answer - not one of many."),
    ]),
    ("PSEUDOCODE", [
        ("Recursive backtracking colouring",
         "colour(index):\n"
         "    if index == number_of_suspects:\n"
         "        return True                      # all vertices coloured\n"
         "    suspect = suspects[index]\n"
         "    for location in locations:\n"
         "        emit CHECK(suspect, location)\n"
         "        if location not in allowed[suspect]:\n"
         "            emit CONFLICT(evidence rules it out); continue\n"
         "        if any neighbour already has this location:\n"
         "            emit CONFLICT(edge clash); continue\n"
         "        assignment[suspect] = location\n"
         "        emit ASSIGN(suspect, location)\n"
         "        if colour(index + 1):\n"
         "            return True\n"
         "        delete assignment[suspect]\n"
         "        emit BACKTRACK(suspect, location)\n"
         "    return False                         # triggers a backtrack above"),
        ("is_valid in one line",
         "A placement is valid when the location is inside the suspect's allowed "
         "domain AND no adjacent vertex already holds that location. That single "
         "check is what makes the whole search correct."),
        ("Where the code lives",
         "algorithms/backtracking.py - GraphColoringSolver.solve() and _backtrack(). "
         "The same function that produces the answer also records the event list the "
         "Analysis screen replays, so the animation cannot drift away from the real "
         "search."),
    ]),
    ("COMPLEXITY", [
        ("Time complexity",
         "Worst case O(k^V) where V is the number of vertices (suspects) and k the "
         "number of colours (locations) - here 4^5 = 1024 leaf assignments, and with "
         "the constraint check at each node the usual bound quoted is O(V * k^V). "
         "Deciding k-colourability is NP-complete for k >= 3, so no polynomial "
         "algorithm is known."),
        ("In practice",
         "Pruning makes the real number of explored nodes far smaller. In this case "
         "the solver examines about a hundred steps and performs ten real backtracks "
         "before it locks in the unique colouring - watch the counters on the Analysis "
         "screen."),
        ("Space complexity",
         "O(V) for the recursion stack and the partial assignment, plus O(V + E) to "
         "store the graph itself. The recorded event log is only for the animation."),
        ("Possible improvements",
         "MRV (colour the most constrained suspect first), degree heuristic, "
         "forward checking and AC-3 style constraint propagation all cut the search "
         "further. This project deliberately keeps a fixed vertex order so that the "
         "demonstration shows several clear backtracking steps."),
    ]),
]


class DaaScene(Scene):
    name = C.DAA

    def __init__(self, app):
        super().__init__(app)
        self.page = 0
        self.list = ScrollList((36, 150, 1208, 462))
        self.tabs = []
        x = 36
        for i, (title, _) in enumerate(PAGES):
            b = Button((x, 92, 250, 44), title, lambda i=i: self.select(i), size=17)
            self.tabs.append(b)
            x += 258
        self.buttons = self.tabs + [
            Button((36, 634, 220, 40), "EVIDENCE BOARD",
                   lambda: self.go(C.BOARD), size=17),
            Button((266, 634, 220, 40), "RUN THE ALGORITHM",
                   lambda: self.go(C.ANALYSIS), size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]
        self.select(0)

    def select(self, i):
        self.page = i
        self.list.offset = 0
        for j, b in enumerate(self.tabs):
            b.selected = (j == i)

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        return self.list.handle_event(event)

    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "HOW THIS GAME SOLVES THE CASE",
                         "Design and Analysis of Algorithms - Graph Colouring with "
                         "Backtracking")
        for b in self.buttons:
            b.draw(surf)

        rect = self.list.rect
        draw_panel(surf, rect, T.PANEL, T.PANEL_EDGE)
        inner = pygame.Rect(rect.x + 10, rect.y + 14, rect.width - 30, rect.height - 28)
        clip = surf.get_clip()
        surf.set_clip(inner)

        y = inner.y - self.list.offset
        start = y
        for heading, body in PAGES[self.page][1]:
            draw_text(surf, heading, (inner.x + 12, y), 21, T.GOLD, bold=True,
                      kind="title")
            y += 32
            kind = "mono" if body.strip().startswith("colour(") else "body"
            y = draw_wrapped(surf, body, (inner.x + 12, y), inner.width - 40,
                             17 if kind == "body" else 16, T.TEXT, kind=kind) + 20
        self.list.content_height = (y - start)
        self.list.clamp()
        surf.set_clip(clip)
        self.list.draw_scrollbar(surf)
