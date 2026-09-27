"""Draws the suspect graph (the corkboard) for the board and analysis scenes."""

import math

import pygame

from ui import theme as T
from ui.widgets import draw_panel, draw_text

NODE_R = 46


class GraphView:
    def __init__(self, case, rect):
        self.case = case
        self.rect = pygame.Rect(rect)
        self.positions = {}
        self.layout()

    def layout(self):
        ids = self.case.suspect_ids
        cx, cy = self.rect.centerx, self.rect.centery + 8
        radius = min(self.rect.width, self.rect.height) * 0.36
        n = max(len(ids), 1)
        for i, sid in enumerate(ids):
            ang = -math.pi / 2 + i * (2 * math.pi / n)
            self.positions[sid] = (int(cx + radius * math.cos(ang)),
                                   int(cy + radius * math.sin(ang)))

    def node_at(self, pos):
        for sid, (x, y) in self.positions.items():
            if (pos[0] - x) ** 2 + (pos[1] - y) ** 2 <= NODE_R * NODE_R:
                return sid
        return None

    # ------------------------------------------------------------------ draw
    def draw(self, surf, edges, assignments, selected=None, active=None,
             conflict_pair=None, conflict_node=None, title="EVIDENCE BOARD"):
        # cork background
        draw_panel(surf, self.rect, T.CORK, T.CORK_EDGE, radius=12, width=3)
        noise = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        for i in range(0, self.rect.width, 9):
            pygame.draw.line(noise, (0, 0, 0, 16), (i, 0), (i, self.rect.height), 1)
        for j in range(0, self.rect.height, 9):
            pygame.draw.line(noise, (255, 255, 255, 6), (0, j), (self.rect.width, j), 1)
        surf.blit(noise, self.rect.topleft)
        draw_text(surf, title, (self.rect.centerx, self.rect.y + 20), 20,
                  (232, 214, 186), bold=True, center=True, kind="title")

        # edges (red string)
        for a, b in edges:
            if a not in self.positions or b not in self.positions:
                continue
            pa, pb = self.positions[a], self.positions[b]
            clash = (assignments.get(a) is not None
                     and assignments.get(a) == assignments.get(b))
            flagged = conflict_pair is not None and set(conflict_pair) == {a, b}
            color = T.RED if (clash or flagged) else (176, 96, 92)
            width = 5 if (clash or flagged) else 3
            pygame.draw.line(surf, (30, 18, 14), (pa[0] + 2, pa[1] + 3),
                             (pb[0] + 2, pb[1] + 3), width)
            pygame.draw.line(surf, color, pa, pb, width)

        # nodes (photo pins)
        for sid, (x, y) in self.positions.items():
            loc = assignments.get(sid)
            col = T.location_color(loc)
            if sid == active:
                pygame.draw.circle(surf, T.WHITE, (x, y), NODE_R + 9, 3)
            if sid == selected:
                pygame.draw.circle(surf, T.GOLD, (x, y), NODE_R + 6, 3)
            if sid == conflict_node:
                pygame.draw.circle(surf, T.RED, (x, y), NODE_R + 12, 4)

            pygame.draw.circle(surf, (18, 14, 12), (x + 3, y + 4), NODE_R)
            pygame.draw.circle(surf, col, (x, y), NODE_R)
            pygame.draw.circle(surf, (245, 238, 226), (x, y), NODE_R, 3)

            name = self.case.suspect_name(sid)
            draw_text(surf, name, (x, y - 10), 19, (18, 20, 26), bold=True, center=True)
            label = self.case.location_name(loc) if loc else "unplaced"
            draw_text(surf, label, (x, y + 13), 14,
                      (26, 28, 34) if loc else (250, 250, 250), center=True)
            pygame.draw.circle(surf, T.GOLD, (x, y - NODE_R + 8), 5)

    def draw_legend(self, surf, rect):
        draw_panel(surf, rect, T.PANEL, T.PANEL_EDGE)
        draw_text(surf, "LOCATIONS (COLOURS)", (rect.x + 14, rect.y + 10), 16,
                  T.GOLD, bold=True)
        y = rect.y + 36
        for i, loc in enumerate(self.case.locations):
            pygame.draw.rect(surf, T.location_color(loc.id),
                             pygame.Rect(rect.x + 14, y + 3, 16, 16), border_radius=4)
            draw_text(surf, f"{i + 1}. {loc.name}", (rect.x + 40, y), 17, T.TEXT)
            y += 26
