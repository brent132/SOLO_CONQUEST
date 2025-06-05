"""Sidebar UI component for the map editor."""

import pygame

from ..color_palette import SIDEBAR_BACKGROUND, SIDEBAR_BORDER

# Fixed width for the sidebar
SIDEBAR_WIDTH = 500


class Sidebar:
    """Simple vertical sidebar container."""

    def __init__(self, height: int, x: int = 0) -> None:
        self.width = SIDEBAR_WIDTH
        self.height = height
        self.rect = pygame.Rect(x, 0, self.width, self.height)

    def resize(self, height: int, x: int) -> None:
        """Resize and reposition the sidebar."""
        self.height = height
        self.rect.update(x, 0, self.width, self.height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the sidebar on the given surface."""
        pygame.draw.rect(surface, SIDEBAR_BACKGROUND, self.rect)
        pygame.draw.rect(surface, SIDEBAR_BORDER, self.rect, 2)
