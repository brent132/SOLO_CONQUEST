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
    BUTTON_SIZE = 25

    def __init__(self, sidebar_rect: pygame.Rect) -> None:
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.layers: List[str] = ["Layer 1"]
        self.active = 0
        # Container the component is drawn within
        self.container_rect = sidebar_rect.copy()
        self.scroll_offset = 0
        self._left = self.container_rect.left + self.PADDING
        self._top = self.container_rect.top + self.PADDING

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect
        self.container_rect = sidebar_rect.copy()
        self._left = self.container_rect.left + self.PADDING

    def set_top(self, top: int) -> None:
        """Set the top y-coordinate for the layer buttons."""
        self.container_rect.top = top
        self._top = self.container_rect.top + self.PADDING

    def set_position(self, left: int, top: int) -> None:
        """Set the x/y position for the component."""
        self.container_rect.topleft = (left, top)
        self._left = self.container_rect.left + self.PADDING
        self._top = self.container_rect.top + self.PADDING

    def set_container(self, rect: pygame.Rect) -> None:
        """Define the container rectangle for the layer list."""
        self.container_rect = rect
        self._left = self.container_rect.left + self.PADDING
        self._top = self.container_rect.top + self.PADDING

    def scroll(self, amount: int) -> None:
        """Scroll the layer list vertically by ``amount`` pixels."""
        max_scroll = max(
            0,
            (self.LAYER_HEIGHT + self.PADDING) * (len(self.layers) + 1)
            - self.container_rect.height,
        )
        self.scroll_offset = max(0, min(self.scroll_offset + amount, max_scroll))

    def add_layer(self, name: str | None = None) -> None:
        """Create a new layer and make it active."""
        name = name or f"Layer {len(self.layers) + 1}"
        self.layers.append(name)
        self.active = len(self.layers) - 1

    def delete_layer(self, index: int | None = None) -> int | None:
        """Remove a layer by index or the active layer if unspecified."""
        if len(self.layers) <= 1:
            return None
        if index is None:
            index = self.active
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            if self.active >= len(self.layers):
                self.active = len(self.layers) - 1
            return index
        return None

    def set_active(self, index: int) -> None:
        """Set which layer new tiles are placed on."""
        if 0 <= index < len(self.layers):
            self.active = index

    def _layer_rects(self) -> List[pygame.Rect]:
        rects = []
        x = self._left
        y = self._top - self.scroll_offset
        for _ in self.layers:
            rects.append(pygame.Rect(x, y, self.LAYER_WIDTH, self.LAYER_HEIGHT))
            y += self.LAYER_HEIGHT + self.PADDING
        return rects

    def _add_rect(self) -> pygame.Rect:
        y = self._top + (self.LAYER_HEIGHT + self.PADDING) * len(self.layers) - self.scroll_offset
        return pygame.Rect(self._left, y, self.BUTTON_SIZE, self.BUTTON_SIZE)

    def _delete_rect(self) -> pygame.Rect:
        y = self._top + (self.LAYER_HEIGHT + self.PADDING) * len(self.layers) - self.scroll_offset
        return pygame.Rect(
            self._left + self.BUTTON_SIZE + self.PADDING,
            y,
            self.BUTTON_SIZE,
            self.BUTTON_SIZE,
        )

    def handle_event(self, event: pygame.event.Event) -> str | tuple[str, int] | None:
        """Handle mouse clicks to change the active layer.

        Returns "add" or "delete" when a layer is created or removed.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if not self.container_rect.collidepoint(mx, my):
                return None
            if self._add_rect().collidepoint(mx, my):
                self.add_layer()
                return "add"
            if self._delete_rect().collidepoint(mx, my):
                removed = self.delete_layer()
                if removed is not None:
                    return "delete", removed
                return None
            for index, rect in enumerate(self._layer_rects()):
                if rect.collidepoint(mx, my):
                    self.active = index
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
            mx, my = pygame.mouse.get_pos()
            if self.container_rect.collidepoint(mx, my):
                direction = -1 if event.button == 4 else 1
                self.scroll(direction * (self.LAYER_HEIGHT + self.PADDING))
        elif event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.container_rect.collidepoint(mx, my):
                self.scroll(-event.y * (self.LAYER_HEIGHT + self.PADDING))
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the layer buttons."""
        old_clip = surface.get_clip()
        surface.set_clip(self.container_rect)
        for index, rect in enumerate(self._layer_rects()):
            color = LIGHT_GRAY if index == self.active else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(self.layers[index], True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        add_rect = self._add_rect()
        del_rect = self._delete_rect()
        pygame.draw.rect(surface, DARK_GRAY, add_rect)
        pygame.draw.rect(surface, SIDEBAR_BORDER, add_rect, 1)
        pygame.draw.rect(surface, DARK_GRAY, del_rect)
        pygame.draw.rect(surface, SIDEBAR_BORDER, del_rect, 1)

        plus = self.font.render("+", True, WHITE)
        minus = self.font.render("-", True, WHITE)
        surface.blit(plus, plus.get_rect(center=add_rect.center))
        surface.blit(minus, minus.get_rect(center=del_rect.center))
        surface.set_clip(old_clip)


__all__ = ["TilesetLayers"]
