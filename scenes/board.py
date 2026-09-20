"""The Evidence Board: assign a location to every suspect by hand."""

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.graph_view import GraphView
from ui.widgets import (Button, ScrollList, draw_panel, draw_text, draw_wrapped,
                        wrapped_height)


class BoardScene(Scene):
    name = C.BOARD

    def __init__(self, app):
        super().__init__(app)
        self.graph = GraphView(self.case, (36, 92, 700, 530))
        self.selected = None
        self.message = ""
        self.message_color = T.TEXT_DIM
        self.conflict_pair = None
        self.list = ScrollList((756, 330, 488, 236))

        self.loc_buttons = []
        x, y = 770, 214
        for i, loc in enumerate(self.case.locations):
            b = Button((x + (i % 2) * 232, y + (i // 2) * 46, 222, 40),
                       f"{i + 1}. {loc.name}",
                       lambda lid=loc.id: self.assign(lid), size=17,
                       color=tuple(max(c - 90, 22) for c in T.location_color(loc.id)))
            self.loc_buttons.append((loc.id, b))

        self.btn_analyze = Button((756, 578, 300, 46), "ANALYZE EVIDENCE",
                                  self.analyze, color=T.GOLD_DARK,
                                  text_color=(22, 18, 10))
        self.btn_check = Button((1066, 578, 178, 46), "CHECK BOARD", self.check_board,
                                size=18)
        nav_y = 634
        self.buttons = [b for _, b in self.loc_buttons] + [
            self.btn_analyze, self.btn_check,
            Button((36, nav_y, 170, 40), "CRIME SCENE",
                   lambda: self.go(C.CRIME_SCENE), size=17),
            Button((216, nav_y, 170, 40), "INTERVIEWS",
                   lambda: self.go(C.INTERVIEWS), size=17),
            Button((396, nav_y, 150, 40), "CASE FILE",
                   lambda: self.go(C.INVESTIGATION), size=17),
            Button((556, nav_y, 130, 40), "CLEAR", self.clear_all, size=17),
            Button((696, nav_y, 40, 40), "?", lambda: self.go(C.DAA), size=20),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    # -------------------------------------------------------------- helpers
    def solver(self):
        return self.case.build_solver(self.state.found_evidence,
                                      self.state.interviewed)

    def edges(self):
        return self.case.edges(self.state.found_evidence, self.state.interviewed)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        enabled = self.selected is not None
        for lid, b in self.loc_buttons:
            b.enabled = enabled
            b.selected = enabled and self.state.assignments.get(self.selected) == lid
        self.btn_analyze.enabled = True

    def set_message(self, text, color):
        self.message = text
        self.message_color = color

    # ----------------------------------------------------------- assignment
    def assign(self, location_id):
        if self.selected is None:
            self.set_message("Pick a suspect on the board first.", T.AMBER)
            return
        sid = self.selected
        solver = self.solver()
        trial = {k: v for k, v in self.state.assignments.items() if k != sid}
        reason = solver.explain(sid, location_id, trial)
        if reason:
            name = self.case.suspect_name(sid)
            loc = self.case.location_name(location_id)
            pretty = (reason.replace(sid, name)
                      .replace(location_id, loc))
            for other in self.case.suspect_ids:
                pretty = pretty.replace(other, self.case.suspect_name(other))
            for l in self.case.locations:
                pretty = pretty.replace(l.id, l.name)
            self.set_message(pretty, T.RED)
            self.toast(pretty, T.RED, 3.6)
            blame = solver.conflicting_neighbour(sid, location_id, trial)
            self.conflict_pair = (sid, blame) if blame else None
            return
        self.conflict_pair = None
        self.state.assign(sid, location_id)
        self.set_message(f"Valid: {self.case.suspect_name(sid)} placed in the "
                         f"{self.case.location_name(location_id)}.", T.GREEN)
        self.refresh()

    def unassign(self, sid):
        if sid in self.state.assignments:
            self.state.assign(sid, None)
            self.set_message(f"{self.case.suspect_name(sid)} removed from the board.",
                             T.TEXT_DIM)
        self.conflict_pair = None
        self.refresh()

    def clear_all(self):
        self.state.clear_assignments()
        self.conflict_pair = None
        self.set_message("Board cleared.", T.TEXT_DIM)
        self.refresh()

    def check_board(self):
        if not self.state.ready_for_board:
            self.toast("Some evidence or statements are still missing - the board "
                       "is under-constrained.", T.AMBER, 4.0)
        if not self.state.manual_solution_is_complete():
            missing = [self.case.suspect_name(s) for s in self.case.suspect_ids
                       if s not in self.state.assignments]
            self.set_message("Still unplaced: " + ", ".join(missing), T.AMBER)
            return
        solver = self.solver()
        for sid, lid in self.state.assignments.items():
            trial = {k: v for k, v in self.state.assignments.items() if k != sid}
            reason = solver.explain(sid, lid, trial)
            if reason:
                self.set_message(reason, T.RED)
                return
        self.set_message("Every constraint is satisfied. Run ANALYZE EVIDENCE to let "
                         "the backtracking solver confirm it.", T.GREEN)
        self.toast("Consistent board! Now prove it with the algorithm.", T.GREEN, 4.0)

    def analyze(self):
        if not self.state.ready_for_board:
            self.toast("Collect all evidence and statements first - otherwise the "
                       "solver may find more than one answer.", T.AMBER, 4.2)
        self.go(C.ANALYSIS)

    # --------------------------------------------------------------- events
    def handle_event(self, event):
        if super().handle_event(event):
            self.refresh()
            return True
        if self.list.handle_event(event):
            return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            node = self.graph.node_at(event.pos)
            if event.button == 1 and node:
                self.selected = node
                self.set_message(self.describe_suspect(node), T.TEXT_DIM)
                self.refresh()
                return True
            if event.button == 3 and node:
                self.unassign(node)
                return True
        if event.type == pygame.KEYDOWN and self.selected:
            keys = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]
            if event.key in keys:
                idx = keys.index(event.key)
                if idx < len(self.case.locations):
                    self.assign(self.case.locations[idx].id)
                    return True
            if event.key in (pygame.K_BACKSPACE, pygame.K_DELETE, pygame.K_0):
                self.unassign(self.selected)
                return True
        return False

    def describe_suspect(self, sid):
        allowed = self.case.allowed(self.state.found_evidence,
                                    self.state.interviewed)[sid]
        names = ", ".join(self.case.location_name(l) for l in allowed)
        return f"{self.case.suspect_name(sid)} selected. Still possible: {names}"

    # -------------------------------------------------------------- drawing
    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "EVIDENCE BOARD",
                         "Left click a suspect, then pick a location (or press 1-4). "
                         "Right click removes a placement.")
        self.graph.draw(surf, self.edges(), self.state.assignments,
                        selected=self.selected, conflict_pair=self.conflict_pair)
        self.draw_side(surf)
        for b in self.buttons:
            b.draw(surf)
        self.draw_message(surf)

    def draw_side(self, surf):
        legend = pygame.Rect(756, 92, 488, 116)
        self.graph.draw_legend(surf, legend)
        draw_text(surf, "Colour = location assigned to that suspect",
                  (legend.right - 16, legend.y + 18), 14, T.TEXT_FAINT, right=True)

        sel_txt = ("SELECTED: " + self.case.suspect_name(self.selected).upper()
                   if self.selected else "SELECT A SUSPECT")
        draw_text(surf, sel_txt, (770, 190), 16, T.GOLD, bold=True)

        rect = self.list.rect
        draw_panel(surf, rect, T.PANEL, T.PANEL_EDGE)
        draw_text(surf, "ACTIVE CONSTRAINTS", (rect.x + 14, rect.y + 10), 16,
                  T.GOLD, bold=True)
        cons = self.case.active_constraints(self.state.found_evidence,
                                            self.state.interviewed)
        clip = surf.get_clip()
        inner = pygame.Rect(rect.x + 8, rect.y + 34, rect.width - 22, rect.height - 42)
        surf.set_clip(inner)
        y = inner.y - self.list.offset
        total = 0
        if not cons:
            draw_text(surf, "Nothing yet - investigate first.", (inner.x + 8, inner.y),
                      17, T.TEXT_DIM)
            total = 30
        for c in cons:
            colr = T.RED_SOFT if c["type"] == "edge" else T.BLUE
            h = wrapped_height(c["text"], inner.width - 30, 16) + 6
            if y + h > inner.y and y < inner.bottom:
                pygame.draw.circle(surf, colr, (inner.x + 12, y + 9), 5)
                draw_wrapped(surf, c["text"], (inner.x + 26, y), inner.width - 34,
                             16, T.TEXT_DIM)
            y += h
            total += h
        self.list.content_height = total
        self.list.clamp()
        surf.set_clip(clip)
        self.list.draw_scrollbar(surf)

    def draw_message(self, surf):
        bar = pygame.Rect(36, 578, 700, 46)
        draw_panel(surf, bar, T.PANEL, self.message_color, radius=8, width=2)
        text = self.message or "Place all five suspects so that no constraint is broken."
        draw_wrapped(surf, text, (bar.x + 14, bar.y + 8), bar.width - 28, 17,
                     self.message_color)
