"""Application shell: window, main loop and scene management."""

import pygame

from game import config as C
from game.state import GameState
from models.case import load_case
from ui import theme as T
from ui.widgets import Toast


class App:
    def __init__(self, headless: bool = False):
        pygame.init()
        pygame.display.set_caption(C.TITLE)
        flags = 0
        self.screen = pygame.display.set_mode((C.WIDTH, C.HEIGHT), flags)
        self.clock = pygame.time.Clock()
        self.running = True
        self.headless = headless

        self.case = load_case(C.CASE_PATH)
        self.state = GameState(self.case)
        self.toast = Toast()

        # imported here so that pygame.init() has already run
        from scenes.menu import MenuScene
        from scenes.crime_scene import CrimeSceneScene
        from scenes.investigation import InvestigationScene
        from scenes.interviews import InterviewScene
        from scenes.board import BoardScene
        from scenes.analysis import AnalysisScene
        from scenes.result import ResultScene
        from scenes.daa_info import DaaScene

        self.scenes = {
            C.MENU: MenuScene(self),
            C.CRIME_SCENE: CrimeSceneScene(self),
            C.INVESTIGATION: InvestigationScene(self),
            C.INTERVIEWS: InterviewScene(self),
            C.BOARD: BoardScene(self),
            C.ANALYSIS: AnalysisScene(self),
            C.RESULT: ResultScene(self),
            C.DAA: DaaScene(self),
        }
        self.scene = None
        self.go(C.MENU)

    # ------------------------------------------------------------- scenes
    def go(self, name: str):
        if name not in self.scenes:
            return
        if self.scene is not None:
            self.scene.on_exit()
        self.scene = self.scenes[name]
        self.scene.on_enter()

    def new_game(self):
        self.state.reset()
        self.go(C.CRIME_SCENE)

    def save_game(self):
        ok = self.state.save(C.SAVE_PATH)
        self.toast.show("Case notes saved." if ok else "Could not write the save file.",
                        T.GREEN if ok else T.RED)

    def load_game(self):
        ok = self.state.load(C.SAVE_PATH)
        if ok:
            self.toast.show("Case notes loaded.", T.GREEN)
        else:
            self.toast.show("No save file for this case yet.", T.RED)
        return ok

    # --------------------------------------------------------------- loop
    def handle_global_key(self, event) -> bool:
        if event.key == pygame.K_ESCAPE:
            if self.scene is not None and self.scene.name == C.MENU:
                self.running = False
            else:
                self.go(C.MENU)
            return True
        if event.key == pygame.K_F5:
            self.save_game()
            return True
        if event.key == pygame.K_F9:
            if self.load_game():
                self.scene.on_enter()
            return True
        return False

    def process_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue
            if event.type == pygame.KEYDOWN and self.handle_global_key(event):
                continue
            self.scene.handle_event(event)

    def tick(self, dt):
        self.scene.update(dt)
        self.toast.update(dt)
        self.scene.draw(self.screen)
        self.toast.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(C.FPS) / 1000.0
            dt = min(dt, 0.1)
            self.process_events()
            self.tick(dt)
        pygame.quit()
