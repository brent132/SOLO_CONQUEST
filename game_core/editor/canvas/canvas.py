"""Canvas component for the map editor."""

from __future__ import annotations

import pygame

from ..color_palette import LIGHT_GRAY, DARK_GRAY


class Canvas:
    """Editable canvas with a fixed-size grid."""

    def __init__(self, width: int, height: int, grid_size: int = 16, x: int = 0, y: int = 0) -> None:
        self.grid_size = grid_size
        self.rect = pygame.Rect(x, y, width, height)

    def resize(self, width: int, height: int, x: int = 0, y: int = 0) -> None:
        """Resize and reposition the canvas."""
        self.rect.update(x, y, width, height)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the canvas background and grid."""
        pygame.draw.rect(surface, DARK_GRAY, self.rect)

        # Draw vertical grid lines
        for gx in range(self.rect.left, self.rect.right, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (gx, self.rect.top), (gx, self.rect.bottom))

        # Draw horizontal grid lines
        for gy in range(self.rect.top, self.rect.bottom, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (self.rect.left, gy), (self.rect.right, gy))
