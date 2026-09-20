"""Small reusable Pygame widgets: buttons, panels, text helpers, toasts."""

import pygame

from ui import theme as T


# ----------------------------------------------------------------- drawing
def draw_panel(surf, rect, fill=T.PANEL, edge=T.PANEL_EDGE, radius=10, width=2):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, fill, rect, border_radius=radius)
    if width:
        pygame.draw.rect(surf, edge, rect, width, border_radius=radius)


def draw_text(surf, text, pos, size=20, color=T.TEXT, bold=False,
              kind="body", center=False, right=False):
    img = T.font(size, bold, kind).render(str(text), True, color)
    r = img.get_rect()
    if center:
        r.center = pos
    elif right:
        r.midright = pos
    else:
        r.topleft = pos
    surf.blit(img, r)
    return r


def wrap_lines(text, size, max_width, bold=False, kind="body"):
    """Split `text` into lines that fit inside max_width pixels."""
    f = T.font(size, bold, kind)
    lines = []
    for paragraph in str(text).split("\n"):
        words = paragraph.split(" ")
        cur = ""
        for w in words:
            trial = w if not cur else cur + " " + w
            if f.size(trial)[0] <= max_width or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def draw_wrapped(surf, text, pos, max_width, size=18, color=T.TEXT,
                 bold=False, kind="body", line_gap=5):
    x, y = pos
    f = T.font(size, bold, kind)
    for line in wrap_lines(text, size, max_width, bold, kind):
        surf.blit(f.render(line, True, color), (x, y))
        y += f.get_height() + line_gap
    return y


def wrapped_height(text, max_width, size=18, bold=False, kind="body", line_gap=5):
    f = T.font(size, bold, kind)
    n = len(wrap_lines(text, size, max_width, bold, kind))
    return n * (f.get_height() + line_gap)


# ----------------------------------------------------------------- widgets
class Button:
    def __init__(self, rect, label, on_click=None, color=T.PANEL_LIGHT,
                 text_color=T.TEXT, size=20, bold=True, tooltip="", icon=""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.color = color
        self.text_color = text_color
        self.size = size
        self.bold = bold
        self.tooltip = tooltip
        self.icon = icon
        self.enabled = True
        self.hover = False
        self.selected = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.enabled and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surf):
        base = self.color
        if not self.enabled:
            base = (max(base[0] - 14, 16), max(base[1] - 14, 18), max(base[2] - 14, 24))
        elif self.selected:
            base = tuple(min(c + 42, 255) for c in base)
        elif self.hover:
            base = tuple(min(c + 22, 255) for c in base)
        edge = T.GOLD if (self.selected or (self.hover and self.enabled)) else T.PANEL_EDGE
        draw_panel(surf, self.rect, base, edge, radius=8, width=2)
        txt = self.label if not self.icon else f"{self.icon}  {self.label}"
        col = self.text_color if self.enabled else T.TEXT_FAINT
        draw_text(surf, txt, self.rect.center, self.size, col,
                  bold=self.bold, center=True)


class Slider:
    """Simple horizontal slider used for the animation speed."""

    def __init__(self, rect, lo, hi, value, label=""):
        self.rect = pygame.Rect(rect)
        self.lo, self.hi = lo, hi
        self.value = value
        self.label = label
        self.dragging = False

    def _set_from_x(self, x):
        t = (x - self.rect.x) / max(self.rect.width, 1)
        t = max(0.0, min(1.0, t))
        self.value = self.lo + t * (self.hi - self.lo)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(12, 18).collidepoint(event.pos):
                self.dragging = True
                self._set_from_x(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_from_x(event.pos[0])
            return True
        return False

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, T.PANEL_LIGHT, r, border_radius=5)
        t = (self.value - self.lo) / max(self.hi - self.lo, 1e-6)
        fill = pygame.Rect(r.x, r.y, int(r.width * t), r.height)
        pygame.draw.rect(surf, T.GOLD_DARK, fill, border_radius=5)
        knob = (r.x + int(r.width * t), r.centery)
        pygame.draw.circle(surf, T.GOLD, knob, 9)
        pygame.draw.circle(surf, T.BG_DEEP, knob, 9, 2)
        if self.label:
            draw_text(surf, f"{self.label}: {self.value:.1f}x",
                      (r.x, r.y - 22), 16, T.TEXT_DIM)


class Toast:
    """Short lived message at the bottom of the screen."""

    def __init__(self):
        self.text = ""
        self.timer = 0.0
        self.color = T.GOLD

    def show(self, text, color=T.GOLD, seconds=3.2):
        self.text = text
        self.color = color
        self.timer = seconds

    def update(self, dt):
        if self.timer > 0:
            self.timer = max(0.0, self.timer - dt)

    def draw(self, surf, y=None):
        if self.timer <= 0 or not self.text:
            return
        w = surf.get_width()
        y = y if y is not None else surf.get_height() - 62
        lines = wrap_lines(self.text, 19, w - 220)
        h = 18 + len(lines) * 24
        rect = pygame.Rect(0, 0, min(w - 160, 980), h)
        rect.center = (w // 2, y)
        draw_panel(surf, rect, T.PANEL_LIGHT, self.color, radius=9, width=2)
        ty = rect.y + 9
        for line in lines:
            draw_text(surf, line, (rect.centerx, ty + 11), 19, self.color,
                      bold=True, center=True)
            ty += 24


class ScrollList:
    """A clipped, scrollable surface region."""

    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.offset = 0
        self.content_height = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.rect.collidepoint(mx, my):
                self.offset -= event.y * 42
                self.clamp()
                return True
        return False

    def clamp(self):
        max_off = max(0, self.content_height - self.rect.height)
        self.offset = max(0, min(self.offset, max_off))

    def scroll_to_bottom(self):
        self.offset = max(0, self.content_height - self.rect.height)

    def draw_scrollbar(self, surf):
        if self.content_height <= self.rect.height:
            return
        track = pygame.Rect(self.rect.right - 7, self.rect.y, 5, self.rect.height)
        pygame.draw.rect(surf, T.PANEL_LIGHT, track, border_radius=3)
        frac = self.rect.height / self.content_height
        h = max(26, int(track.height * frac))
        max_off = max(1, self.content_height - self.rect.height)
        y = track.y + int((track.height - h) * (self.offset / max_off))
        pygame.draw.rect(surf, T.GOLD_DARK, pygame.Rect(track.x, y, 5, h),
                         border_radius=3)
