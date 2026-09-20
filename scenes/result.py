"""Case Result: who was where, who did it, and why the evidence says so."""

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import (Button, ScrollList, draw_panel, draw_text, draw_wrapped,
                        wrapped_height)


class ResultScene(Scene):
    name = C.RESULT

    def __init__(self, app):
        super().__init__(app)
        self.list = ScrollList((656, 92, 588, 520))
        self.buttons = [
            Button((36, 634, 210, 40), "BACK TO BOARD",
                   lambda: self.go(C.BOARD), size=17),
            Button((256, 634, 240, 40), "DAA EXPLANATION",
                   lambda: self.go(C.DAA), size=17),
            Button((506, 634, 210, 40), "RE-RUN ANALYSIS",
                   lambda: self.go(C.ANALYSIS), size=17),
            Button((726, 634, 180, 40), "SAVE CASE",
                   self.app.save_game, size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    def on_enter(self):
        if self.state.solved_by_algorithm:
            self.state.case_closed = True
        self.list.offset = 0

    def solution(self):
        return self.state.algorithm_solution

    def culprit(self):
        for sid, lid in self.solution().items():
            if lid == self.case.culprit_location:
                return sid
        return None

    def supporting(self, sid):
        """Constraints that mention this suspect."""
        out = []
        for c in self.case.active_constraints(self.state.found_evidence,
                                              self.state.interviewed):
            if c["type"] == "forbid" and c["suspect"] == sid:
                out.append(f"{c['source']}: {c['text']}")
            elif c["type"] == "edge" and sid in (c["a"], c["b"]):
                out.append(f"{c['source']}: {c['text']}")
        return out

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        return self.list.handle_event(event)

    # -------------------------------------------------------------- drawing
    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "CASE RESULT", self.case.title)
        if not self.solution():
            draw_panel(surf, pygame.Rect(300, 260, 680, 200), T.PANEL, T.AMBER)
            draw_wrapped(surf, "No solution has been computed yet. Open the Evidence "
                               "Board, press ANALYZE EVIDENCE and let the backtracking "
                               "solver finish - the result is always produced by the "
                               "algorithm, never hard-coded.",
                         (330, 300), 620, 20, T.TEXT)
            for b in self.buttons:
                b.draw(surf)
            return

        self.draw_placements(surf)
        self.draw_story(surf)
        for b in self.buttons:
            b.draw(surf)

    def draw_placements(self, surf):
        panel = pygame.Rect(36, 92, 600, 520)
        draw_panel(surf, panel, T.PANEL, T.PANEL_EDGE)
        draw_text(surf, "FINAL PLACEMENTS (from the solver)",
                  (panel.x + 18, panel.y + 14), 18, T.GOLD, bold=True)
        culprit = self.culprit()
        y = panel.y + 48
        for s in self.case.suspects:
            lid = self.solution().get(s.id)
            row = pygame.Rect(panel.x + 16, y, panel.width - 32, 74)
            is_culprit = s.id == culprit
            draw_panel(surf, row, (44, 28, 30) if is_culprit else T.PANEL_LIGHT,
                       T.RED if is_culprit else T.PANEL_EDGE, radius=8,
                       width=3 if is_culprit else 1)
            pygame.draw.circle(surf, T.location_color(lid),
                               (row.x + 38, row.centery), 26)
            pygame.draw.circle(surf, (240, 236, 228), (row.x + 38, row.centery), 26, 2)
            draw_text(surf, s.name[:2], (row.x + 38, row.centery), 17, (20, 22, 28),
                      bold=True, center=True)
            draw_text(surf, s.full_name, (row.x + 76, row.y + 12), 20, T.TEXT, bold=True)
            draw_text(surf, s.role, (row.x + 76, row.y + 38), 15, T.TEXT_DIM)
            draw_text(surf, self.case.location_name(lid).upper(),
                      (row.right - 16, row.y + 24), 18,
                      T.RED if is_culprit else T.GOLD, bold=True, right=True)
            if is_culprit:
                draw_text(surf, "IN THE GALLERY AT 22:40",
                          (row.right - 16, row.y + 50), 14, T.RED, right=True)
            y += 82

        n = self.case.solution_count(self.state.found_evidence,
                                     self.state.interviewed, cap=3)
        msg = ("This colouring is the only one the constraints allow."
               if n == 1 else f"Warning: {n}+ colourings fit the evidence you have.")
        draw_text(surf, msg, (panel.x + 18, panel.bottom - 30), 16,
                  T.GREEN if n == 1 else T.AMBER)

    def draw_story(self, surf):
        rect = self.list.rect
        draw_panel(surf, rect, T.PANEL, T.GOLD_DARK, radius=10, width=2)
        culprit = self.culprit()
        cname = self.case.suspect(culprit).full_name if culprit else "nobody"
        crole = self.case.suspect(culprit).role if culprit else ""

        clip = surf.get_clip()
        inner = pygame.Rect(rect.x + 8, rect.y + 12, rect.width - 24, rect.height - 24)
        surf.set_clip(inner)
        x = inner.x + 12
        w = inner.width - 30
        y = inner.y - self.list.offset
        start = y

        draw_text(surf, "CASE CLOSED", (x, y), 24, T.GOLD, bold=True, kind="title")
        y += 40
        draw_text(surf, f"THE THIEF: {cname.upper()} ({crole})", (x, y), 19, T.RED,
                  bold=True)
        y += 34
        y = draw_wrapped(surf, f"The board places exactly one person inside the "
                               f"{self.case.location_name(self.case.culprit_location)} "
                               f"during the theft window ({self.case.theft_window}): "
                               f"{cname}. Everyone else is pinned somewhere else by "
                               f"the evidence.", (x, y), w, 18, T.TEXT) + 14

        draw_text(surf, "HOW IT WAS DONE", (x, y), 17, T.GOLD, bold=True)
        y += 26
        y = draw_wrapped(surf, self.case.conclusion.get("how", ""), (x, y), w, 18,
                         T.TEXT_DIM) + 12
        y = draw_wrapped(surf, self.case.conclusion.get("why", ""), (x, y), w, 18,
                         T.TEXT_DIM) + 16

        draw_text(surf, "WHY EACH PLACEMENT HOLDS", (x, y), 17, T.GOLD, bold=True)
        y += 26
        for s in self.case.suspects:
            lid = self.solution().get(s.id)
            draw_text(surf, f"{s.name} - {self.case.location_name(lid)}", (x, y), 17,
                      T.location_color(lid), bold=True)
            y += 24
            for line in self.supporting(s.id)[:4]:
                y = draw_wrapped(surf, "- " + line, (x + 14, y), w - 20, 15,
                                 T.TEXT_DIM, line_gap=3) + 2
            y += 8

        draw_text(surf, "KEY CLUES", (x, y), 17, T.GOLD, bold=True)
        y += 26
        for ev in self.case.evidence:
            if ev.id in self.state.found_evidence:
                y = draw_wrapped(surf, f"- {ev.object}: {ev.clue}", (x, y), w, 15,
                                 T.TEXT_DIM, line_gap=3) + 8

        self.list.content_height = (y - start) + 20
        self.list.clamp()
        surf.set_clip(clip)
        self.list.draw_scrollbar(surf)
