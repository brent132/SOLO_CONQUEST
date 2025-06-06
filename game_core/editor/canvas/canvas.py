"""Canvas component for the map editor."""

from __future__ import annotations

import pygame

from ..color_palette import LIGHT_GRAY, DARK_GRAY, WHITE
from .tile_placement import TilePlacementManager
from .tileset_repository import TilesetRepository
from ..sidebar.sidebar_tab_manager import TabManager


class Canvas:
    """Editable canvas with a fixed-size grid."""

    def __init__(self, width: int, height: int, grid_size: int = 16, x: int = 0, y: int = 0) -> None:
        self.grid_size = grid_size
        self.rect = pygame.Rect(x, y, width, height)
        self.placement_manager = TilePlacementManager(grid_size)
        self.tilesets = TilesetRepository()

    def resize(self, width: int, height: int, x: int = 0, y: int = 0) -> None:
        """Resize and reposition the canvas."""
        self.rect.update(x, y, width, height)

    def handle_event(self, event: pygame.event.Event, tab_manager: TabManager) -> None:
        """Handle mouse events for placing and removing tiles."""
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            mx, my = event.pos
            grid_x = (mx - self.rect.left) // self.grid_size
            grid_y = (my - self.rect.top) // self.grid_size
            if event.button == 1:
                tile_index = tab_manager.selected_tile
                tileset_index = tab_manager.active_tileset
                if tile_index is not None:
                    tile = self.tilesets.get_tile(tileset_index, tile_index)
                    if tile is not None:
                        self.placement_manager.add_tile(tile, grid_x, grid_y)
            elif event.button == 3:
                self.placement_manager.remove_tile_at(grid_x, grid_y)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the canvas background and grid."""
        pygame.draw.rect(surface, WHITE, self.rect)

        # Draw vertical grid lines
        for gx in range(self.rect.left, self.rect.right, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (gx, self.rect.top), (gx, self.rect.bottom))

        # Draw horizontal grid lines
        for gy in range(self.rect.top, self.rect.bottom, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (self.rect.left, gy), (self.rect.right, gy))

        # Draw any placed tiles on top of the grid
        self.placement_manager.draw(surface)
