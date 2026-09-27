"""Base class shared by every scene."""

import pygame

from game import config as C
from ui import theme as T
from ui.widgets import Button, draw_panel, draw_text


class Scene:
    """A screen of the game. The App owns one active scene at a time."""

    name = "scene"

    def __init__(self, app):
        self.app = app
        self.buttons = []

    # ---------------------------------------------------------- convenience
    @property
    def case(self):
        return self.app.case

    @property
    def state(self):
        return self.app.state

    def toast(self, text, color=T.GOLD, seconds=3.2):
        self.app.toast.show(text, color, seconds)

    def go(self, scene_name):
        self.app.go(scene_name)

    # ------------------------------------------------------------ lifecycle
    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        for b in self.buttons:
            if b.handle_event(event):
                return True
        return False

    def update(self, dt):
        pass

    def draw(self, surf):
        pass

    # -------------------------------------------------------------- drawing
    def draw_background(self, surf, tint=T.BG):
        surf.fill(tint)
        # faint horizontal gradient bands for depth
        band = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        for i in range(0, C.HEIGHT, 4):
            a = int(26 * (i / C.HEIGHT))
            pygame.draw.line(band, (0, 0, 0, a), (0, i), (C.WIDTH, i), 4)
        surf.blit(band, (0, 0))

    def draw_header(self, surf, title, subtitle="", back_to=None):
        pygame.draw.rect(surf, T.BG_DEEP, pygame.Rect(0, 0, C.WIDTH, 66))
        pygame.draw.line(surf, T.GOLD_DARK, (0, 66), (C.WIDTH, 66), 2)
        draw_text(surf, title, (28, 14), 27, T.GOLD, bold=True, kind="title")
        if subtitle:
            draw_text(surf, subtitle, (30, 44), 15, T.TEXT_DIM)

    def draw_progress_strip(self, surf, y=C.HEIGHT - 34):
        """Small status line: evidence found / interviews completed."""
        ev = f"Evidence {len(self.state.found_evidence)}/{len(self.case.evidence)}"
        iv = f"Interviews {len(self.state.interviewed)}/{len(self.case.suspects)}"
        pygame.draw.rect(surf, T.BG_DEEP, pygame.Rect(0, y - 6, C.WIDTH, 40))
        pygame.draw.line(surf, T.PANEL_EDGE, (0, y - 6), (C.WIDTH, y - 6), 1)
        draw_text(surf, ev, (28, y), 16, T.TEXT_DIM)
        draw_text(surf, iv, (200, y), 16, T.TEXT_DIM)
        draw_text(surf, "F5 save    F9 load    ESC menu",
                  (C.WIDTH - 28, y + 8), 15, T.TEXT_FAINT, right=True)

    def make_back_button(self, to=C.MENU, label="< Back", x=C.WIDTH - 150, y=16):
        return Button((x, y, 128, 36), label, lambda: self.go(to),
                      size=17, color=T.PANEL)
