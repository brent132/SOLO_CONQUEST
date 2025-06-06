from __future__ import annotations

import pygame
from typing import Iterator

from ..color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH


def iter_brush_positions(center_x: int, center_y: int, size: int) -> Iterator[tuple[int, int]]:
    """Yield grid coordinates affected by a brush of the given size."""
    radius = size // 2
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            yield center_x + dx, center_y + dy


class TilesetBrush:
    """UI component for choosing brush size when placing tiles."""

    SIZES = [1, 3, 5, 7]
    BUTTON_SIZE = 30
    PADDING = 5

    def __init__(self, sidebar_rect: pygame.Rect) -> None:
        self.sidebar_rect = sidebar_rect
        self.selected = 1
        self.font = pygame.font.Font(FONT_PATH, 16)
        self._top = sidebar_rect.bottom - self.BUTTON_SIZE - self.PADDING

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect
        self._top = sidebar_rect.bottom - self.BUTTON_SIZE - self.PADDING

    def set_top(self, top: int) -> None:
        """Set the top y-coordinate for the brush buttons."""
        self._top = top

    def _button_rects(self) -> list[pygame.Rect]:
        rects = []
        x = self.sidebar_rect.left + self.PADDING
        y = self._top
        for _ in self.SIZES:
            rects.append(pygame.Rect(x, y, self.BUTTON_SIZE, self.BUTTON_SIZE))
            x += self.BUTTON_SIZE + self.PADDING
        return rects

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for size, rect in zip(self.SIZES, self._button_rects()):
                if rect.collidepoint(mx, my):
                    self.selected = size
                    break

    def draw(self, surface: pygame.Surface) -> None:
        for size, rect in zip(self.SIZES, self._button_rects()):
            color = LIGHT_GRAY if size == self.selected else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(f"{size}x{size}", True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)


__all__ = ["TilesetBrush", "iter_brush_positions"]
