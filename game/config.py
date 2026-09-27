"""Global configuration."""

import os

WIDTH = 1280
HEIGHT = 720
FPS = 60
TITLE = "Detective's Evidence Board"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
ASSETS_DIR = os.path.join(ROOT, "assets")
SAVE_PATH = os.path.join(DATA_DIR, "savegame.json")
CASE_PATH = os.path.join(DATA_DIR, "case_001.json")

# Scene identifiers
MENU = "menu"
CRIME_SCENE = "crime_scene"
INVESTIGATION = "investigation"
INTERVIEWS = "interviews"
BOARD = "board"
ANALYSIS = "analysis"
RESULT = "result"
DAA = "daa"
