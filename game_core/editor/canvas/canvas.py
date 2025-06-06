"""Canvas component for the map editor."""
# Implements drawing and tile placement on the map canvas.

from __future__ import annotations

import pygame

from ..color_palette import LIGHT_GRAY, DARK_GRAY, WHITE
from .tile_placement import TilePlacementManager
from .tileset_repository import TilesetRepository
from ..sidebar.sidebar_tab_manager import TabManager
from ..tileset_tab.tileset_brush import iter_brush_positions


class Canvas:
    """Editable canvas with a fixed-size grid."""

    def __init__(self, width: int, height: int, grid_size: int = 16, x: int = 0, y: int = 0) -> None:
        self.grid_size = grid_size
        self.rect = pygame.Rect(x, y, width, height)
        self.offset = [0, 0]
        self.placement_manager = TilePlacementManager(grid_size)
        self.tilesets = TilesetRepository()

    def resize(self, width: int, height: int, x: int = 0, y: int = 0) -> None:
        """Resize and reposition the canvas."""
        self.rect.update(x, y, width, height)

    def handle_event(self, event: pygame.event.Event, tab_manager: TabManager) -> None:
        """Handle mouse events for placing and removing tiles."""

        def _grid_pos(mouse_pos: tuple[int, int]) -> tuple[int, int]:
            mx = mouse_pos[0] - self.rect.left + self.offset[0]
            my = mouse_pos[1] - self.rect.top + self.offset[1]
            return mx // self.grid_size, my // self.grid_size

        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            grid_x, grid_y = _grid_pos(event.pos)
            brush = tab_manager.brush_size
            shape = tab_manager.brush_shape
            layer = tab_manager.active_layer

            if event.button == 1:
                tile_index = tab_manager.selected_tile
                tileset_index = tab_manager.active_tileset
                if tile_index is not None:
                    tile = self.tilesets.get_tile(tileset_index, tile_index)
                    if tile is not None:
                        if self.grid_size != 16:
                            factor = self.grid_size / 16
                            tile = pygame.transform.scale(
                                tile,
                                (
                                    int(tile.get_width() * factor),
                                    int(tile.get_height() * factor),
                                ),
                            )

                        for bx, by in iter_brush_positions(grid_x, grid_y, brush, shape):
                            self.placement_manager.add_tile(
                                tile,
                                bx,
                                by,
                                tile.get_width(),
                                tile.get_height(),
                                layer,
                            )
            elif event.button == 3:
                for bx, by in iter_brush_positions(grid_x, grid_y, brush, shape):
                    self.placement_manager.remove_tile_at(bx, by, layer)

        elif event.type == pygame.MOUSEMOTION and self.rect.collidepoint(event.pos):
            grid_x, grid_y = _grid_pos(event.pos)
            brush = tab_manager.brush_size
            shape = tab_manager.brush_shape
            layer = tab_manager.active_layer
            if event.buttons[0]:  # Left button drag places tiles
                tile_index = tab_manager.selected_tile
                tileset_index = tab_manager.active_tileset
                if tile_index is not None:
                    tile = self.tilesets.get_tile(tileset_index, tile_index)
                    if tile is not None:
                        if self.grid_size != 16:
                            factor = self.grid_size / 16
                            tile = pygame.transform.scale(
                                tile,
                                (
                                    int(tile.get_width() * factor),
                                    int(tile.get_height() * factor),
                                ),
                            )
                        for bx, by in iter_brush_positions(grid_x, grid_y, brush, shape):
                            self.placement_manager.add_tile(
                                tile,
                                bx,
                                by,
                                tile.get_width(),
                                tile.get_height(),
                                layer,
                            )
            elif event.buttons[2]:  # Right button drag removes tiles
                for bx, by in iter_brush_positions(grid_x, grid_y, brush, shape):
                    self.placement_manager.remove_tile_at(bx, by, layer)

        elif event.type == pygame.MOUSEBUTTONUP:
            pass

    def draw(self, surface: pygame.Surface, tab_manager: TabManager) -> None:
        """Draw the canvas background, grid and tile preview."""
        pygame.draw.rect(surface, WHITE, self.rect)

        start_x = -self.offset[0] % self.grid_size
        for gx in range(self.rect.left + start_x, self.rect.right, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (gx, self.rect.top), (gx, self.rect.bottom))

        start_y = -self.offset[1] % self.grid_size
        for gy in range(self.rect.top + start_y, self.rect.bottom, self.grid_size):
            pygame.draw.line(surface, LIGHT_GRAY, (self.rect.left, gy), (self.rect.right, gy))

        self.placement_manager.draw(
            surface,
            tuple(self.offset),
            active_layer=tab_manager.active_layer,
        )

        # --------------------------------------------------------------
        # Draw preview of the currently selected tile under the cursor
        # --------------------------------------------------------------
        mx, my = pygame.mouse.get_pos()
        if self.rect.collidepoint(mx, my):
            grid_x = (mx - self.rect.left + self.offset[0]) // self.grid_size
            grid_y = (my - self.rect.top + self.offset[1]) // self.grid_size

            tile_index = tab_manager.selected_tile
            tileset_index = tab_manager.active_tileset
            brush = tab_manager.brush_size
            shape = tab_manager.brush_shape

            if tile_index is not None:
                tile = self.tilesets.get_tile(tileset_index, tile_index)
                if tile is not None:
                    if self.grid_size != 16:
                        factor = self.grid_size / 16
                        tile = pygame.transform.scale(
                            tile,
                            (
                                int(tile.get_width() * factor),
                                int(tile.get_height() * factor),
                            ),
                        )
                    preview = tile.copy()
                    preview.set_alpha(150)
                    for bx, by in iter_brush_positions(grid_x, grid_y, brush, shape):
                        px = bx * self.grid_size - self.offset[0] + self.rect.left
                        py = by * self.grid_size - self.offset[1] + self.rect.top
                        surface.blit(preview, (px, py))
