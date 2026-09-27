"""Case file: everything collected so far, with the constraints it unlocked."""

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import Button, ScrollList, draw_panel, draw_text, draw_wrapped, wrapped_height


class InvestigationScene(Scene):
    name = C.INVESTIGATION

    def __init__(self, app):
        super().__init__(app)
        self.list = ScrollList((40, 96, 800, 540))
        self.buttons = [
            Button((870, 560, 340, 42), "BACK TO CRIME SCENE",
                   lambda: self.go(C.CRIME_SCENE), size=17),
            Button((870, 610, 340, 42), "GO TO INTERVIEWS",
                   lambda: self.go(C.INTERVIEWS), size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    def handle_event(self, event):
        if super().handle_event(event):
            return True
        return self.list.handle_event(event)

    # -------------------------------------------------------------- drawing
    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "CASE FILE",
                         "Every clue you have logged, and the constraints it puts on the board.")
        self.draw_entries(surf)
        self.draw_summary(surf)
        for b in self.buttons:
            b.draw(surf)
        self.draw_progress_strip(surf)

    def draw_entries(self, surf):
        rect = self.list.rect
        draw_panel(surf, rect, T.PANEL, T.PANEL_EDGE)
        clip = surf.get_clip()
        surf.set_clip(rect.inflate(-6, -6))

        y = rect.y + 14 - self.list.offset
        width = rect.width - 48
        if not self.state.found_evidence:
            draw_text(surf, "The case file is empty. Go back to the crime scene.",
                      (rect.x + 24, rect.y + 24), 19, T.TEXT_DIM)
            total = 60
        else:
            total = 14
            for ev in self.case.evidence:
                if ev.id not in self.state.found_evidence:
                    continue
                h = 76 + wrapped_height(ev.clue, width - 20, 17)
                h += 26 * len(ev.constraints)
                card = pygame.Rect(rect.x + 18, y, width + 12, h)
                if card.bottom > rect.y and card.y < rect.bottom:
                    draw_panel(surf, card, T.PANEL_LIGHT, T.PANEL_EDGE, radius=8)
                    draw_text(surf, ev.object.upper(), (card.x + 16, card.y + 12),
                              18, T.GOLD, bold=True)
                    draw_text(surf, ev.name, (card.right - 16, card.y + 22), 15,
                              T.TEXT_DIM, right=True)
                    cy = draw_wrapped(surf, ev.clue, (card.x + 16, card.y + 40),
                                      width - 20, 17, T.TEXT) + 6
                    for c in ev.constraints:
                        draw_text(surf, "- " + c["text"], (card.x + 16, cy), 16,
                                  T.GREEN)
                        cy += 26
                    if not ev.constraints:
                        draw_text(surf, "- context only, no board constraint",
                                  (card.x + 16, cy), 16, T.TEXT_FAINT)
                y += h + 14
                total += h + 14

            for s in self.case.suspects:
                if s.id not in self.state.interviewed:
                    continue
                h = 62 + wrapped_height(s.statement, width - 20, 17)
                h += 26 * len(s.constraints)
                card = pygame.Rect(rect.x + 18, y, width + 12, h)
                if card.bottom > rect.y and card.y < rect.bottom:
                    draw_panel(surf, card, (36, 32, 44), T.PANEL_EDGE, radius=8)
                    draw_text(surf, f"STATEMENT - {s.full_name.upper()}",
                              (card.x + 16, card.y + 12), 18, T.PURPLE, bold=True)
                    cy = draw_wrapped(surf, '"' + s.statement + '"',
                                      (card.x + 16, card.y + 38), width - 20, 17,
                                      T.TEXT) + 6
                    for c in s.constraints:
                        draw_text(surf, "- " + c["text"], (card.x + 16, cy), 16, T.GREEN)
                        cy += 26
                y += h + 14
                total += h + 14

        self.list.content_height = total
        self.list.clamp()
        surf.set_clip(clip)
        self.list.draw_scrollbar(surf)

    def draw_summary(self, surf):
        panel = pygame.Rect(866, 96, 374, 440)
        draw_panel(surf, panel, T.PANEL, T.GOLD_DARK, radius=10, width=2)
        draw_text(surf, "BOARD STATUS", (panel.x + 18, panel.y + 14), 18,
                  T.GOLD, bold=True)
        cons = self.case.active_constraints(self.state.found_evidence,
                                            self.state.interviewed)
        edges = [c for c in cons if c["type"] == "edge"]
        forbids = [c for c in cons if c["type"] == "forbid"]
        rows = [
            ("Suspects (vertices)", len(self.case.suspects)),
            ("Locations (colours)", len(self.case.locations)),
            ("Edges unlocked", len(edges)),
            ("Forbidden placements", len(forbids)),
            ("Evidence logged", f"{len(self.state.found_evidence)}/{len(self.case.evidence)}"),
            ("Interviews done", f"{len(self.state.interviewed)}/{len(self.case.suspects)}"),
        ]
        y = panel.y + 48
        for label, val in rows:
            draw_text(surf, label, (panel.x + 18, y), 17, T.TEXT_DIM)
            draw_text(surf, str(val), (panel.right - 18, y + 9), 17, T.TEXT,
                      bold=True, right=True)
            y += 30

        y += 8
        pygame.draw.line(surf, T.PANEL_EDGE, (panel.x + 18, y), (panel.right - 18, y), 1)
        y += 14
        if not self.state.ready_for_board:
            draw_wrapped(surf, "Keep investigating. With missing constraints the "
                               "puzzle can have several answers - and a detective "
                               "needs exactly one.",
                         (panel.x + 18, y), panel.width - 36, 17, T.AMBER)
        else:
            n = self.case.solution_count(self.state.found_evidence,
                                         self.state.interviewed, cap=3)
            msg = ("All constraints gathered. The graph now has exactly one valid "
                   "colouring - open the Evidence Board." if n == 1 else
                   f"The graph currently admits {n}+ colourings.")
            draw_wrapped(surf, msg, (panel.x + 18, y), panel.width - 36, 17, T.GREEN)
