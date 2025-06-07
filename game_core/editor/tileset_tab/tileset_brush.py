"""UI component for choosing brush size and shape."""
from __future__ import annotations
# Provides brush button layout and logic wrapped in a bordered container.

import pygame
from typing import Iterator

from ..color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH


def iter_brush_positions(
    center_x: int, center_y: int, size: int, shape: str = "square"
) -> Iterator[tuple[int, int]]:
    """Yield grid coordinates affected by a brush of the given size and shape."""
    radius = size // 2
    if shape == "circle":
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                if dx * dx + dy * dy <= radius * radius:
                    yield center_x + dx, center_y + dy
    else:  # square
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                yield center_x + dx, center_y + dy


class TilesetBrush:
    """UI component for choosing brush size and shape when placing tiles."""

    SIZES = [1, 3, 5, 7]
    SHAPES = ["square", "circle"]
    BUTTON_SIZE = 30
    PADDING = 5

    def __init__(self, sidebar_rect: pygame.Rect) -> None:
        self.sidebar_rect = sidebar_rect
        self.selected = 1
        self.shape = "square"
        self.font = pygame.font.Font(FONT_PATH, 16)

        # Container rect defines the outer box drawn around the buttons
        width_buttons = self.BUTTON_SIZE * len(self.SIZES) + self.PADDING * (len(self.SIZES) - 1)
        width_shapes = self.BUTTON_SIZE * len(self.SHAPES) + self.PADDING * (len(self.SHAPES) - 1)
        container_width = max(width_buttons, width_shapes) + self.PADDING * 2
        container_height = self.BUTTON_SIZE * 2 + self.PADDING * 3
        self.container_rect = pygame.Rect(sidebar_rect.left + self.PADDING, sidebar_rect.top, container_width, container_height)

        # Button coordinates relative to the container
        self._left = self.container_rect.left + self.PADDING
        self._top = self.container_rect.top + self.PADDING

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect
        width_buttons = self.BUTTON_SIZE * len(self.SIZES) + self.PADDING * (len(self.SIZES) - 1)
        width_shapes = self.BUTTON_SIZE * len(self.SHAPES) + self.PADDING * (len(self.SHAPES) - 1)
        self.container_rect.width = max(width_buttons, width_shapes) + self.PADDING * 2
        self.container_rect.height = self.BUTTON_SIZE * 2 + self.PADDING * 3
        self.container_rect.left = sidebar_rect.left + self.PADDING

    def set_top(self, top: int) -> None:
        """Set the top y-coordinate for the brush buttons."""
        self.container_rect.top = top - self.PADDING
        self._top = top
        self._left = self.container_rect.left + self.PADDING

    def set_container(self, rect: pygame.Rect) -> None:
        """Define the container rectangle for the brush."""
        self.container_rect = rect
        self._left = rect.left + self.PADDING
        self._top = rect.top + self.PADDING

    def _button_rects(self) -> list[pygame.Rect]:
        rects = []
        x = self._left
        y = self._top
        for _ in self.SIZES:
            rects.append(pygame.Rect(x, y, self.BUTTON_SIZE, self.BUTTON_SIZE))
            x += self.BUTTON_SIZE + self.PADDING
        return rects

    def _shape_rects(self) -> list[pygame.Rect]:
        rects = []
        x = self._left
        y = self._top + self.BUTTON_SIZE + self.PADDING
        for _ in self.SHAPES:
            rects.append(pygame.Rect(x, y, self.BUTTON_SIZE, self.BUTTON_SIZE))
            x += self.BUTTON_SIZE + self.PADDING
        return rects

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if not self.container_rect.collidepoint(mx, my):
                return
            for size, rect in zip(self.SIZES, self._button_rects()):
                if rect.collidepoint(mx, my):
                    self.selected = size
                    return
            for shape, rect in zip(self.SHAPES, self._shape_rects()):
                if rect.collidepoint(mx, my):
                    self.shape = shape
                    return

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, DARK_GRAY, self.container_rect)
        pygame.draw.rect(surface, SIDEBAR_BORDER, self.container_rect, 1)
        for size, rect in zip(self.SIZES, self._button_rects()):
            color = LIGHT_GRAY if size == self.selected else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(f"{size}x{size}", True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        for shape, rect in zip(self.SHAPES, self._shape_rects()):
            color = LIGHT_GRAY if shape == self.shape else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            text = "O" if shape == "circle" else "[]"
            label = self.font.render(text, True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)


__all__ = ["TilesetBrush", "iter_brush_positions"]
