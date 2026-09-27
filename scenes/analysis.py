"""Evidence Analysis: replays the REAL backtracking search, step by step."""

import pygame

from algorithms import backtracking as BT
from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.graph_view import GraphView
from ui.widgets import (Button, ScrollList, Slider, draw_panel, draw_text,
                        draw_wrapped, wrapped_height)

BASE_INTERVAL = 0.55        # seconds per event at 1.0x


class AnalysisScene(Scene):
    name = C.ANALYSIS

    def __init__(self, app):
        super().__init__(app)
        self.graph = GraphView(self.case, (36, 92, 620, 470))
        self.log = ScrollList((676, 92, 568, 470))
        self.events = []
        self.index = -1              # index of the last event applied
        self.playing = False
        self.timer = 0.0
        self.solved = False
        self.solution = {}
        self.auto_scroll = True

        self.speed = Slider((300, 600, 240, 12), 0.25, 6.0, 1.5, "Speed")

        self.btn_play = Button((36, 578, 120, 44), "PLAY", self.toggle_play,
                               color=T.GOLD_DARK, text_color=(22, 18, 10))
        self.btn_step = Button((164, 578, 120, 44), "STEP", self.step_once)
        self.btn_restart = Button((36, 634, 120, 40), "RESTART", self.restart, size=17)
        self.btn_finish = Button((164, 634, 120, 40), "RUN TO END", self.run_to_end,
                                 size=17)
        self.btn_result = Button((980, 578, 264, 44), "CASE RESULT >",
                                 lambda: self.go(C.RESULT), color=T.GOLD_DARK,
                                 text_color=(22, 18, 10))
        self.buttons = [
            self.btn_play, self.btn_step, self.btn_restart, self.btn_finish,
            self.btn_result,
            Button((600, 634, 170, 40), "BACK TO BOARD",
                   lambda: self.go(C.BOARD), size=17),
            Button((780, 634, 170, 40), "DAA EXPLANATION",
                   lambda: self.go(C.DAA), size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    # ------------------------------------------------------------ lifecycle
    def on_enter(self):
        self.restart()

    def restart(self):
        solver = self.case.build_solver(self.state.found_evidence,
                                        self.state.interviewed)
        ok, assignment = solver.solve(record=True)
        self.solver = solver
        self.events = solver.events
        self.final_ok = ok
        self.final_assignment = assignment
        self.index = -1
        self.playing = False
        self.timer = 0.0
        self.solved = False
        self.solution = {}
        self.log.offset = 0
        self.auto_scroll = True
        self.btn_play.label = "PLAY"
        self.btn_result.enabled = self.state.solved_by_algorithm

    # -------------------------------------------------------------- control
    def toggle_play(self):
        if self.index >= len(self.events) - 1:
            self.restart()
        self.playing = not self.playing
        self.btn_play.label = "PAUSE" if self.playing else "PLAY"

    def step_once(self):
        self.playing = False
        self.btn_play.label = "PLAY"
        self.advance()

    def run_to_end(self):
        self.playing = False
        self.btn_play.label = "PLAY"
        while self.index < len(self.events) - 1:
            self.advance()

    def advance(self):
        if self.index >= len(self.events) - 1:
            self.playing = False
            self.btn_play.label = "PLAY"
            return
        self.index += 1
        self.auto_scroll = True
        ev = self.events[self.index]
        if ev.kind == BT.SUCCESS:
            self.solved = True
            self.solution = dict(ev.assignment)
            self.state.solved_by_algorithm = True
            self.state.algorithm_solution = dict(ev.assignment)
            self.btn_result.enabled = True
            self.playing = False
            self.btn_play.label = "PLAY"
            self.toast("Solution found by backtracking. Open the case result.",
                       T.GREEN, 4.5)
        elif ev.kind == BT.FAIL:
            self.playing = False
            self.btn_play.label = "PLAY"
            self.toast("No valid colouring exists with the current constraints.",
                       T.RED, 4.5)

    # --------------------------------------------------------------- events
    def handle_event(self, event):
        if super().handle_event(event):
            return True
        if self.speed.handle_event(event):
            return True
        if self.log.handle_event(event):
            self.auto_scroll = False
            return True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_play()
                return True
            if event.key == pygame.K_RIGHT:
                self.step_once()
                return True
            if event.key == pygame.K_r:
                self.restart()
                return True
        return False

    def update(self, dt):
        if self.playing:
            self.timer += dt * self.speed.value
            while self.timer >= BASE_INTERVAL and self.playing:
                self.timer -= BASE_INTERVAL
                self.advance()

    # -------------------------------------------------------------- drawing
    def current(self):
        if 0 <= self.index < len(self.events):
            return self.events[self.index]
        return None

    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "EVIDENCE ANALYSIS - BACKTRACKING GRAPH COLOURING",
                         "Every line below is emitted by the real recursive solver "
                         "while it runs.")
        ev = self.current()
        assignment = dict(ev.assignment) if ev else {}
        active = ev.suspect if ev else None
        conflict_pair = None
        conflict_node = None
        if ev and ev.kind == BT.CONFLICT:
            conflict_node = ev.suspect
            if ev.blame:
                conflict_pair = (ev.suspect, ev.blame)

        edges = self.case.edges(self.state.found_evidence, self.state.interviewed)
        self.graph.draw(surf, edges, assignment, active=active,
                        conflict_pair=conflict_pair, conflict_node=conflict_node,
                        title="SEARCH STATE")
        self.draw_log(surf)
        self.draw_status(surf)
        for b in self.buttons:
            b.draw(surf)
        self.speed.draw(surf)

    def draw_log(self, surf):
        rect = self.log.rect
        draw_panel(surf, rect, T.BG_DEEP, T.PANEL_EDGE)
        draw_text(surf, "ALGORITHM LOG", (rect.x + 14, rect.y + 10), 16, T.GOLD,
                  bold=True)
        draw_text(surf, f"{max(self.index + 1, 0)} / {len(self.events)} steps",
                  (rect.right - 14, rect.y + 18), 15, T.TEXT_DIM, right=True)

        inner = pygame.Rect(rect.x + 8, rect.y + 36, rect.width - 22, rect.height - 46)
        colors = {
            BT.CHECK: T.TEXT_DIM,
            BT.ASSIGN: T.GREEN,
            BT.CONFLICT: T.RED,
            BT.BACKTRACK: T.AMBER,
            BT.SUCCESS: T.GOLD,
            BT.FAIL: T.RED,
        }
        shown = self.events[: self.index + 1]
        line_h = []
        total = 0
        for e in shown:
            h = wrapped_height(self.pretty(e), inner.width - 30 - e.depth * 14, 16) + 2
            line_h.append(h)
            total += h
        self.log.content_height = total
        if self.auto_scroll:
            self.log.scroll_to_bottom()
        self.log.clamp()

        clip = surf.get_clip()
        surf.set_clip(inner)
        y = inner.y - self.log.offset
        for e, h in zip(shown, line_h):
            if y + h > inner.y and y < inner.bottom:
                x = inner.x + 6 + e.depth * 14
                col = colors.get(e.kind, T.TEXT)
                draw_text(surf, e.kind, (x, y), 15, col, bold=True)
                draw_wrapped(surf, self.pretty(e), (x + 88, y), inner.width - 100 - e.depth * 14,
                             16, col if e.kind in (BT.SUCCESS, BT.FAIL) else T.TEXT)
            y += h
        surf.set_clip(clip)
        self.log.draw_scrollbar(surf)

    def pretty(self, e):
        """Replace internal ids with readable names."""
        msg = e.message
        for s in self.case.suspects:
            msg = msg.replace(s.id, s.name)
        for l in self.case.locations:
            msg = msg.replace(l.id, l.name)
        return msg

    def draw_status(self, surf):
        ev = self.current()
        info = pygame.Rect(300, 630, 290, 48)
        draw_panel(surf, info, T.PANEL, T.PANEL_EDGE, radius=8)
        depth = ev.depth if ev else 0
        bt_done = sum(1 for e in self.events[: self.index + 1]
                      if e.kind == BT.BACKTRACK)
        draw_text(surf, f"depth {depth}   backtracks {bt_done}",
                  (info.x + 14, info.y + 14), 17, T.TEXT_DIM)

        line = (self.pretty(ev) if ev else
                "Press PLAY (or SPACE) to watch the solver search the graph.")
        col = T.GOLD if ev and ev.kind in (BT.SUCCESS,) else (
            T.RED if ev and ev.kind in (BT.CONFLICT, BT.FAIL) else T.TEXT)
        draw_text(surf, line, (36, 690), 17, col, bold=True)
