"""Manage tile selection across all tileset palettes."""

from __future__ import annotations

from typing import Dict, List
import pygame

from ..color_palette import ORANGE


class TileSelectionManager:
    """Track and draw tile selections for each tileset."""

    def __init__(self) -> None:
        self.selections: Dict[int, int] = {}
        self.tile_rects: Dict[int, List[pygame.Rect]] = {}

    def set_tile_rects(self, tileset_index: int, rects: List[pygame.Rect]) -> None:
        """Store rectangles for tiles in the given tileset."""
        self.tile_rects[tileset_index] = rects

    def handle_event(self, event: pygame.event.Event, tileset_index: int) -> None:
        """Update selection for the active tileset based on mouse click."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            rects = self.tile_rects.get(tileset_index)
            if not rects:
                return
            mx, my = event.pos
            for index, rect in enumerate(rects):
                if rect.collidepoint(mx, my):
                    self.selections[tileset_index] = index
                    break

    def draw_selection(self, surface: pygame.Surface, tileset_index: int) -> None:
        """Highlight the currently selected tile for the active tileset."""
        rects = self.tile_rects.get(tileset_index)
        if not rects:
            return
        index = self.selections.get(tileset_index)
        if index is None or index >= len(rects):
            return
        pygame.draw.rect(surface, ORANGE, rects[index], 2)

    def get_selected(self, tileset_index: int) -> int | None:
        """Return the selected tile index for a tileset."""
        return self.selections.get(tileset_index)
