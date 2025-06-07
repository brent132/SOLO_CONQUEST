"""Button component for creating a new map in the editor."""
from __future__ import annotations

import pygame

from ..color_palette import DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH
from .tile_placement import TilePlacementManager


class NewMapButton:
    """Simple button positioned at the bottom left of the sidebar."""

    WIDTH = 100
    HEIGHT = 30
    PADDING = 5

    def __init__(self, sidebar_rect: pygame.Rect, placement_manager: TilePlacementManager) -> None:
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.placement_manager = placement_manager

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update sidebar reference when the sidebar is resized."""
        self.sidebar_rect = sidebar_rect

    def _rect(self) -> pygame.Rect:
        x = self.sidebar_rect.left + self.PADDING
        y = self.sidebar_rect.bottom - self.HEIGHT - self.PADDING
        return pygame.Rect(x, y, self.WIDTH, self.HEIGHT)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse clicks on the button."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._rect().collidepoint(event.pos):
                self.placement_manager.clear()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        rect = self._rect()
        pygame.draw.rect(surface, DARK_GRAY, rect)
        pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)
        label = self.font.render("New Map", True, WHITE)
        label_rect = label.get_rect(center=rect.center)
        surface.blit(label, label_rect)


__all__ = ["NewMapButton"]
