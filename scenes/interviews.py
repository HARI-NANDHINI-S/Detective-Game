"""Suspect interviews: record statements to unlock edge constraints."""

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import Button, draw_panel, draw_text, draw_wrapped


class InterviewScene(Scene):
    name = C.INTERVIEWS

    def __init__(self, app):
        super().__init__(app)
        self.selected = self.case.suspect_ids[0] if self.case.suspect_ids else None
        self.suspect_buttons = []
        y = 110
        for s in self.case.suspects:
            b = Button((40, y, 300, 74), s.full_name,
                       lambda sid=s.id: self.select(sid), size=19)
            self.suspect_buttons.append((s.id, b))
            y += 84

        self.btn_record = Button((380, 566, 300, 46), "RECORD STATEMENT",
                                 self.record, color=T.GOLD_DARK,
                                 text_color=(24, 20, 12))
        nav_y = 634
        self.buttons = [b for _, b in self.suspect_buttons] + [
            self.btn_record,
            Button((700, nav_y, 190, 40), "CRIME SCENE",
                   lambda: self.go(C.CRIME_SCENE), size=17),
            Button((902, nav_y, 170, 40), "CASE FILE",
                   lambda: self.go(C.INVESTIGATION), size=17),
            Button((1084, nav_y, 156, 40), "BOARD",
                   lambda: self.go(C.BOARD), size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    def on_enter(self):
        self.refresh()

    def select(self, sid):
        self.selected = sid
        self.refresh()

    def selected_suspect(self):
        return self.case.suspect(self.selected)

    def refresh(self):
        for sid, b in self.suspect_buttons:
            b.selected = (sid == self.selected)
        s = self.selected_suspect()
        self.btn_record.enabled = s is not None and s.id not in self.state.interviewed

    def record(self):
        s = self.selected_suspect()
        if s is None:
            return
        if self.state.interview(s.id):
            self.toast(f"{s.full_name}'s statement recorded - "
                       f"{len(s.constraints)} new edge(s) on the board.", T.GREEN, 4.0)
            if self.state.ready_for_board:
                self.toast("Every constraint is in. Open the Evidence Board.",
                           T.GOLD, 4.5)
        self.refresh()

    def handle_event(self, event):
        if super().handle_event(event):
            self.refresh()
            return True
        return False

    # -------------------------------------------------------------- drawing
    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "SUSPECT INTERVIEWS",
                         "Statements create edges: two suspects who were never "
                         "together cannot share a location.")
        for _, b in self.suspect_buttons:
            b.draw(surf)
        self.draw_marks(surf)
        self.draw_detail(surf)
        for b in self.buttons:
            if b not in [x for _, x in self.suspect_buttons]:
                b.draw(surf)
        self.draw_progress_strip(surf)

    def draw_marks(self, surf):
        for sid, b in self.suspect_buttons:
            s = self.case.suspect(sid)
            draw_text(surf, s.role, (b.rect.x + 14, b.rect.y + 44), 15, T.TEXT_DIM)
            if sid in self.state.interviewed:
                draw_text(surf, "DONE", (b.rect.right - 14, b.rect.y + 22), 14,
                          T.GREEN, bold=True, right=True)

    def draw_detail(self, surf):
        panel = pygame.Rect(372, 100, 868, 446)
        draw_panel(surf, panel, T.PANEL, T.PANEL_EDGE)
        s = self.selected_suspect()
        if s is None:
            return
        pygame.draw.circle(surf, T.location_color(self.state.assignments.get(s.id)),
                           (panel.x + 66, panel.y + 70), 44)
        pygame.draw.circle(surf, (240, 236, 228), (panel.x + 66, panel.y + 70), 44, 3)
        draw_text(surf, s.name, (panel.x + 66, panel.y + 70), 22, (20, 22, 28),
                  bold=True, center=True)

        draw_text(surf, s.full_name.upper(), (panel.x + 130, panel.y + 34), 26,
                  T.GOLD, bold=True, kind="title")
        draw_text(surf, s.role, (panel.x + 132, panel.y + 68), 17, T.TEXT_DIM)
        y = draw_wrapped(surf, s.profile, (panel.x + 130, panel.y + 94),
                         panel.width - 160, 17, T.TEXT_DIM) + 18

        quote = pygame.Rect(panel.x + 24, y, panel.width - 48, 108)
        draw_panel(surf, quote, (32, 30, 42), T.PURPLE, radius=8, width=2)
        if s.id in self.state.interviewed:
            draw_wrapped(surf, '"' + s.statement + '"', (quote.x + 18, quote.y + 16),
                         quote.width - 36, 19, T.TEXT)
        else:
            draw_text(surf, "Statement not taken yet.", (quote.x + 18, quote.y + 18),
                      19, T.TEXT_FAINT)
        y = quote.bottom + 18

        draw_text(surf, "CONSTRAINTS FROM THIS STATEMENT", (panel.x + 24, y), 17,
                  T.GOLD, bold=True)
        y += 28
        for c in s.constraints:
            if s.id in self.state.interviewed:
                draw_text(surf, "- " + c["text"], (panel.x + 24, y), 17, T.GREEN)
            else:
                draw_text(surf, "- locked", (panel.x + 24, y), 17, T.TEXT_FAINT)
            y += 26
