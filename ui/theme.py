"""Colours and fonts for the dark detective / museum theme."""

import pygame

# ---------------------------------------------------------------- palette
BG            = (14, 17, 24)
BG_DEEP       = (9, 11, 16)
PANEL         = (24, 29, 40)
PANEL_LIGHT   = (33, 40, 54)
PANEL_EDGE    = (58, 68, 88)
CORK          = (58, 44, 32)
CORK_EDGE     = (92, 70, 50)

TEXT          = (226, 232, 240)
TEXT_DIM      = (148, 160, 180)
TEXT_FAINT    = (100, 112, 132)

GOLD          = (214, 172, 88)
GOLD_DARK     = (150, 118, 55)
RED           = (206, 76, 74)
RED_SOFT      = (168, 64, 62)
GREEN         = (86, 178, 122)
BLUE          = (86, 140, 214)
AMBER         = (222, 158, 70)
PURPLE        = (150, 116, 206)
WHITE         = (255, 255, 255)

# colour used for each location ("colour" in the graph colouring sense)
LOCATION_COLORS = {
    "gallery":    (206, 76, 74),
    "laboratory": (86, 178, 122),
    "archive":    (86, 140, 214),
    "security":   (214, 172, 88),
}
UNASSIGNED = (86, 96, 116)


def location_color(loc_id):
    if not loc_id:
        return UNASSIGNED
    return LOCATION_COLORS.get(loc_id, PURPLE)


# ------------------------------------------------------------------ fonts
_FONT_CACHE = {}
_TITLE_NAMES = "georgia,timesnewroman,dejavuserif,liberationserif,serif"
_BODY_NAMES = "dejavusans,verdana,arial,liberationsans,sans"
_MONO_NAMES = "dejavusansmono,consolas,couriernew,liberationmono,monospace"


def font(size: int, bold: bool = False, kind: str = "body") -> pygame.font.Font:
    key = (size, bold, kind)
    if key not in _FONT_CACHE:
        names = {"title": _TITLE_NAMES, "mono": _MONO_NAMES}.get(kind, _BODY_NAMES)
        try:
            f = pygame.font.SysFont(names, size, bold=bold)
        except Exception:                                  # pragma: no cover
            f = pygame.font.Font(None, size)
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]
