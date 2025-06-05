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
    FONT_PATH,
    FONT_COLOR,
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

        # Basic font for placeholder text
        self.font = pygame.font.Font(FONT_PATH, 36)
        self.title_surf = self.font.render("Edit Mode", True, FONT_COLOR)
        self.title_rect = self.title_surf.get_rect(center=(self.width // 2, self.height // 2))

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
                self.title_rect = self.title_surf.get_rect(center=(self.width // 2, self.height // 2))
                self.sidebar.resize(self.height, self.width - SIDEBAR_WIDTH)
                self.canvas.resize(self.width - SIDEBAR_WIDTH, self.height)

    def update(self):
        pass

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.canvas.draw(self.screen)
        self.sidebar.draw(self.screen)
        self.screen.blit(self.title_surf, self.title_rect)
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
