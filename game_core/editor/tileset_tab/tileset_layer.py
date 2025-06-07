"""Tile layer management component for the editor."""
# Provides simple controls for creating, deleting and selecting layers.

from __future__ import annotations

from typing import List
import pygame

from ..color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH


class TilesetLayers:
    """UI component for managing tile layers inside the sidebar."""

    LAYER_HEIGHT = 25
    LAYER_WIDTH = 100
    PADDING = 5

    def __init__(self, sidebar_rect: pygame.Rect) -> None:
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.layers: List[str] = ["Layer 1"]
        self.active = 0
        self._top = sidebar_rect.top + self.PADDING

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect

    def set_top(self, top: int) -> None:
        """Set the top y-coordinate for the layer buttons."""
        self._top = top

    def add_layer(self, name: str | None = None) -> None:
        """Create a new layer and make it active."""
        name = name or f"Layer {len(self.layers) + 1}"
        self.layers.append(name)
        self.active = len(self.layers) - 1

    def delete_layer(self, index: int | None = None) -> None:
        """Remove a layer by index or the active layer if unspecified."""
        if len(self.layers) <= 1:
            return
        if index is None:
            index = self.active
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active >= len(self.layers):
                self.active = len(self.layers) - 1

    def set_active(self, index: int) -> None:
        """Set which layer new tiles are placed on."""
        if 0 <= index < len(self.layers):
            self.active = index

    def _layer_rects(self) -> List[pygame.Rect]:
        rects = []
        x = self.sidebar_rect.left + self.PADDING
        y = self._top
        for _ in self.layers:
            rects.append(pygame.Rect(x, y, self.LAYER_WIDTH, self.LAYER_HEIGHT))
            y += self.LAYER_HEIGHT + self.PADDING
        return rects

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse clicks to change the active layer."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for index, rect in enumerate(self._layer_rects()):
                if rect.collidepoint(mx, my):
                    self.active = index
                    break

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the layer buttons."""
        for index, rect in enumerate(self._layer_rects()):
            color = LIGHT_GRAY if index == self.active else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(self.layers[index], True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)


__all__ = ["TilesetLayers"]
