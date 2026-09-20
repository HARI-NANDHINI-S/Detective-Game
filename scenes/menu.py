"""Main menu."""

import math

import pygame

from game import config as C
from scenes.base import Scene
from ui import theme as T
from ui.widgets import Button, draw_panel, draw_text, draw_wrapped


class MenuScene(Scene):
    name = C.MENU

    def __init__(self, app):
        super().__init__(app)
        self.t = 0.0
        bw, bh, x = 360, 52, 96
        y = 250
        self.btn_new = Button((x, y, bw, bh), "NEW INVESTIGATION",
                              self.app.new_game, color=T.GOLD_DARK,
                              text_color=(24, 20, 12))
        self.btn_continue = Button((x, y + 66, bw, bh), "CONTINUE (LOAD CASE)",
                                   self.continue_game)
        self.btn_board = Button((x, y + 132, bw, bh), "EVIDENCE BOARD",
                                lambda: self.go(C.BOARD))
        self.btn_daa = Button((x, y + 198, bw, bh), "HOW IT WORKS (DAA)",
                              lambda: self.go(C.DAA))
        self.btn_quit = Button((x, y + 264, bw, bh), "QUIT", self.quit)
        self.buttons = [self.btn_new, self.btn_continue, self.btn_board,
                        self.btn_daa, self.btn_quit]

    def on_enter(self):
        from game.state import GameState
        self.btn_continue.enabled = GameState.save_exists(C.SAVE_PATH)

    def continue_game(self):
        if self.app.load_game():
            self.go(C.CRIME_SCENE)

    def quit(self):
        self.app.running = False

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        self.draw_background(surf, T.BG_DEEP)

        # moving torch light
        glow = pygame.Surface((C.WIDTH, C.HEIGHT), pygame.SRCALPHA)
        cx = int(C.WIDTH * 0.72 + 30 * math.sin(self.t * 0.6))
        for r, a in ((320, 16), (220, 18), (130, 22)):
            pygame.draw.circle(glow, (214, 172, 88, a), (cx, 320), r)
        surf.blit(glow, (0, 0))

        draw_text(surf, "DETECTIVE'S", (94, 84), 58, T.TEXT, bold=True, kind="title")
        draw_text(surf, "EVIDENCE BOARD", (94, 146), 58, T.GOLD, bold=True, kind="title")
        pygame.draw.line(surf, T.GOLD_DARK, (98, 214), (560, 214), 2)
        draw_text(surf, "A Graph Colouring + Backtracking mystery",
                  (98, 222), 19, T.TEXT_DIM)

        # right hand case card
        card = pygame.Rect(720, 150, 470, 420)
        draw_panel(surf, card, T.PANEL, T.GOLD_DARK, radius=12, width=2)
        draw_text(surf, "CASE FILE " + self.case.case_id.upper().replace("_", " "),
                  (card.x + 22, card.y + 20), 17, T.GOLD, bold=True)
        draw_text(surf, self.case.title, (card.x + 22, card.y + 48), 24,
                  T.TEXT, bold=True, kind="title")
        draw_text(surf, self.case.subtitle, (card.x + 22, card.y + 80), 15, T.TEXT_DIM)
        y = card.y + 112
        for line in self.case.briefing:
            y = draw_wrapped(surf, line, (card.x + 22, y), card.width - 44, 16,
                             T.TEXT_DIM) + 10
        draw_text(surf, f"{len(self.case.suspects)} suspects   "
                        f"{len(self.case.locations)} locations   "
                        f"{len(self.case.evidence)} pieces of evidence",
                  (card.x + 22, card.bottom - 36), 16, T.GOLD)

        for b in self.buttons:
            b.draw(surf)
        draw_text(surf, "ESC quits    F5 save    F9 load",
                  (96, C.HEIGHT - 44), 15, T.TEXT_FAINT)
