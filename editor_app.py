"""Basic editor window for SOLO CONQUEST"""
import pygame
import sys
import os

# Add game_core to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'game_core'))

from game_core.editor.config import (
    WIDTH,
    HEIGHT,
    FPS,
    BACKGROUND_COLOR,
    maintain_aspect_ratio,
)
from game_core.editor.sidebar import Sidebar, SIDEBAR_WIDTH
from game_core.editor.canvas import Canvas


class EditorApp:
    """Minimal application for the map editor."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("SOLO CONQUEST - Editor")
        self.clock = pygame.time.Clock()
        self.running = True
        self.width = WIDTH
        self.height = HEIGHT



        # Editor UI components
        self.sidebar = Sidebar(self.height, self.width - SIDEBAR_WIDTH)
        self.canvas = Canvas(self.width - SIDEBAR_WIDTH, self.height)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                self.width, self.height = maintain_aspect_ratio(*event.size)
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                self.sidebar.resize(self.height, self.width - SIDEBAR_WIDTH)
                self.canvas.resize(self.width - SIDEBAR_WIDTH, self.height)

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.canvas.draw(self.screen)
        self.sidebar.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = EditorApp()
    app.run()
