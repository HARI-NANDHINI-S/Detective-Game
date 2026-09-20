"""Crime scene: click objects to collect evidence."""

import math

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import Button, draw_panel, draw_text, draw_wrapped


class CrimeSceneScene(Scene):
    name = C.CRIME_SCENE

    LAYOUT = {
        "display_case": (95, 190, 210, 170),
        "camera":       (335, 150, 150, 120),
        "fingerprints": (515, 170, 150, 120),
        "footprints":   (95, 400, 210, 130),
        "note":         (335, 300, 150, 120),
        "badge":        (515, 330, 150, 120),
    }

    def __init__(self, app):
        super().__init__(app)
        self.selected = None
        self.t = 0.0
        self.hover = None

        self.btn_collect = Button((720, 566, 240, 44), "COLLECT EVIDENCE",
                                  self.collect_selected, color=T.GOLD_DARK,
                                  text_color=(24, 20, 12))
        nav_y = 634
        self.buttons = [
            self.btn_collect,
            Button((720, nav_y, 180, 40), "CASE FILE",
                   lambda: self.go(C.INVESTIGATION), size=17),
            Button((912, nav_y, 180, 40), "INTERVIEWS",
                   lambda: self.go(C.INTERVIEWS), size=17),
            Button((1104, nav_y, 150, 40), "BOARD",
                   lambda: self.go(C.BOARD), size=17),
            self.make_back_button(C.MENU, "MENU", C.WIDTH - 150, 16),
        ]

    # -------------------------------------------------------------- helpers
    def hotspots(self):
        out = []
        for ev in self.case.evidence:
            rect = self.LAYOUT.get(ev.id)
            if rect:
                out.append((ev, pygame.Rect(rect)))
        return out

    def selected_evidence(self):
        for ev in self.case.evidence:
            if ev.id == self.selected:
                return ev
        return None

    def collect_selected(self):
        ev = self.selected_evidence()
        if ev is None:
            return
        if self.state.collect(ev.id):
            self.toast(f"Evidence logged: {ev.name}. {len(ev.constraints)} "
                       f"new constraint(s) added to the board.", T.GREEN, 4.0)
            if self.state.all_evidence_found:
                self.toast("All physical evidence collected. Interview the suspects next.",
                           T.GOLD, 4.5)
        else:
            self.toast("Already in the case file.", T.TEXT_DIM, 2.0)

    def on_enter(self):
        self.update_buttons()

    def update_buttons(self):
        ev = self.selected_evidence()
        self.btn_collect.enabled = ev is not None and ev.id not in self.state.found_evidence

    # --------------------------------------------------------------- events
    def handle_event(self, event):
        if super().handle_event(event):
            self.update_buttons()
            return True
        if event.type == pygame.MOUSEMOTION:
            self.hover = None
            for ev, rect in self.hotspots():
                if rect.collidepoint(event.pos):
                    self.hover = ev.id
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for ev, rect in self.hotspots():
                if rect.collidepoint(event.pos):
                    self.selected = ev.id
                    self.update_buttons()
                    return True
        return False

    def update(self, dt):
        self.t += dt

    # -------------------------------------------------------------- drawing
    def draw(self, surf):
        self.draw_background(surf)
        self.draw_header(surf, "CRIME SCENE - MERIDIAN MUSEUM, GALLERY HALL",
                         "Click an object to examine it, then log it as evidence.")
        self.draw_room(surf)
        self.draw_side_panel(surf)
        for b in self.buttons:
            b.draw(surf)
        self.draw_progress_strip(surf)

    def draw_room(self, surf):
        room = pygame.Rect(40, 96, 650, 540)
        draw_panel(surf, room, (20, 24, 33), T.PANEL_EDGE, radius=10, width=2)
        # floor line + plinth
        pygame.draw.line(surf, (40, 47, 62), (room.x + 10, 470),
                         (room.right - 10, 470), 2)
        pulse = 0.5 + 0.5 * math.sin(self.t * 2.4)

        for ev, rect in self.hotspots():
            found = ev.id in self.state.found_evidence
            hot = (self.hover == ev.id) or (self.selected == ev.id)
            edge = T.GOLD if hot else (T.GREEN if found else T.PANEL_EDGE)
            fill = (30, 36, 48) if not hot else (40, 48, 63)
            draw_panel(surf, rect, fill, edge, radius=9, width=2 if not hot else 3)
            self.draw_icon(surf, ev.id, rect)
            draw_text(surf, ev.object, (rect.centerx, rect.bottom - 16), 15,
                      T.TEXT if not found else T.GREEN, bold=True, center=True)
            if found:
                draw_text(surf, "LOGGED", (rect.right - 10, rect.y + 12), 13,
                          T.GREEN, bold=True, right=True)
            elif not hot:
                a = int(120 + 100 * pulse)
                pygame.draw.circle(surf, (a, a // 2, 60), (rect.right - 12, rect.y + 12), 5)

    def draw_icon(self, surf, eid, rect):
        cx, cy = rect.centerx, rect.centery - 8
        if eid == "display_case":
            box = pygame.Rect(0, 0, 90, 74)
            box.center = (cx, cy)
            pygame.draw.rect(surf, (52, 72, 92), box, 3, border_radius=4)
            pygame.draw.line(surf, T.RED, box.topleft, box.center, 3)
            pygame.draw.line(surf, T.RED, box.center, (box.right, box.y + 52), 3)
            pygame.draw.line(surf, T.RED, box.center, (box.x + 20, box.bottom), 3)
        elif eid == "camera":
            body = pygame.Rect(0, 0, 66, 30)
            body.center = (cx, cy)
            pygame.draw.rect(surf, (70, 80, 100), body, border_radius=5)
            pygame.draw.circle(surf, (26, 30, 40), (body.right - 6, body.centery), 9)
            pygame.draw.circle(surf, T.RED, (body.x + 8, body.y + 6), 4)
            pygame.draw.line(surf, (70, 80, 100), (cx, body.y - 14), (cx, body.y), 4)
        elif eid == "fingerprints":
            for i in range(5):
                pygame.draw.circle(surf, (150, 170, 200), (cx, cy), 10 + i * 7, 2)
        elif eid == "footprints":
            for i, dx in enumerate((-36, -6, 24, 54)):
                r = pygame.Rect(0, 0, 16, 26)
                r.center = (cx + dx, cy + (10 if i % 2 else -10))
                pygame.draw.ellipse(surf, (120, 140, 160), r)
        elif eid == "note":
            pts = [(cx - 34, cy - 30), (cx + 34, cy - 30), (cx + 34, cy + 26),
                   (cx + 6, cy + 30), (cx - 34, cy + 18)]
            pygame.draw.polygon(surf, (222, 214, 190), pts)
            for i in range(4):
                pygame.draw.line(surf, (150, 142, 122), (cx - 24, cy - 18 + i * 11),
                                 (cx + 22, cy - 18 + i * 11), 2)
        elif eid == "badge":
            r = pygame.Rect(0, 0, 60, 76)
            r.center = (cx, cy)
            pygame.draw.rect(surf, (200, 204, 214), r, border_radius=6)
            pygame.draw.rect(surf, (60, 70, 92), pygame.Rect(r.x + 8, r.y + 10, 44, 26),
                             border_radius=3)
            pygame.draw.line(surf, (90, 96, 110), (r.x + 8, r.y + 48), (r.right - 8, r.y + 48), 3)
            pygame.draw.line(surf, (90, 96, 110), (r.x + 8, r.y + 58), (r.right - 18, r.y + 58), 3)

    def draw_side_panel(self, surf):
        panel = pygame.Rect(712, 96, 528, 456)
        draw_panel(surf, panel, T.PANEL, T.PANEL_EDGE)
        ev = self.selected_evidence()
        if ev is None:
            draw_text(surf, "NO OBJECT SELECTED", (panel.x + 20, panel.y + 18),
                      18, T.GOLD, bold=True)
            draw_wrapped(surf, "The Chola Bronze was taken from the Gallery between "
                               "22:30 and 22:50. Six objects in this room can still "
                               "tell you something.\n\nExamine each one: every piece "
                               "of evidence you log adds a constraint to the Evidence "
                               "Board - and constraints are what make the puzzle "
                               "solvable.",
                         (panel.x + 20, panel.y + 52), panel.width - 40, 18, T.TEXT_DIM)
            return

        found = ev.id in self.state.found_evidence
        draw_text(surf, ev.object.upper(), (panel.x + 20, panel.y + 16), 22,
                  T.GOLD, bold=True, kind="title")
        draw_text(surf, ev.name, (panel.x + 20, panel.y + 46), 16, T.TEXT_DIM)
        y = draw_wrapped(surf, ev.description, (panel.x + 20, panel.y + 76),
                         panel.width - 40, 18, T.TEXT) + 12

        pygame.draw.line(surf, T.PANEL_EDGE, (panel.x + 20, y),
                         (panel.right - 20, y), 1)
        y += 12
        if found:
            draw_text(surf, "CLUE", (panel.x + 20, y), 16, T.GREEN, bold=True)
            y = draw_wrapped(surf, ev.clue, (panel.x + 20, y + 24),
                             panel.width - 40, 18, T.TEXT) + 10
            if ev.constraints:
                draw_text(surf, "CONSTRAINTS UNLOCKED", (panel.x + 20, y), 16,
                          T.GOLD, bold=True)
                y += 24
                for c in ev.constraints:
                    y = draw_wrapped(surf, "- " + c["text"], (panel.x + 20, y),
                                     panel.width - 40, 17, T.TEXT_DIM) + 4
            else:
                draw_text(surf, "No board constraint - context only.",
                          (panel.x + 20, y), 17, T.TEXT_FAINT)
        else:
            draw_text(surf, "Not yet logged. Collect it to reveal the clue.",
                      (panel.x + 20, y), 17, T.AMBER)
