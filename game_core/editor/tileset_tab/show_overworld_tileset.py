"""Utilities for displaying the overworld tileset in the editor."""

from __future__ import annotations

from typing import Optional
import math
import pygame

from .tileset_components import OverworldTileset
from .tileset_tab_manager import TilesetTabManager

# Lazy loaded tileset instances
_overworld_tileset: Optional[OverworldTileset] = None


def _get_overworld_tileset() -> OverworldTileset:
    """Return the singleton overworld tileset, loading it if needed."""
    global _overworld_tileset
    if _overworld_tileset is None:
        _overworld_tileset = OverworldTileset()
    return _overworld_tileset


def draw_tileset(surface: pygame.Surface, index: int, sidebar_rect: pygame.Rect) -> None:
    """Draw the tileset corresponding to ``index`` inside the sidebar."""
    if index != 0:
        # Only overworld tileset is currently implemented
        return

    tileset = _get_overworld_tileset()

    # Automatically scale the overworld tileset to fit inside the sidebar.
    spacing = 2
    tile_size = tileset.TILE_SIZE

    tiles_per_row = tileset.tiles_per_row()
    rows = math.ceil(tileset.tile_count() / tiles_per_row)

    start_x = sidebar_rect.left + spacing
    start_y = (
        sidebar_rect.top
        + TilesetTabManager.PADDING * 3
        + TilesetTabManager.TAB_HEIGHT * 2
    )

    avail_width = sidebar_rect.width - spacing * 2
    avail_height = sidebar_rect.bottom - start_y - spacing

    total_width = tile_size * tiles_per_row + spacing * (tiles_per_row - 1)
    total_height = tile_size * rows + spacing * (rows - 1)

    scale_x = avail_width / total_width
    scale_y = avail_height / total_height
    scale = min(scale_x, scale_y)

    scaled_size = max(1, int(tile_size * scale))

    # Arrange tiles in the original grid layout
    for i in range(tileset.tile_count()):
        tile = tileset.get_tile(i)
        if tile is None:
            continue
        dest_x = start_x + (i % tiles_per_row) * (scaled_size + spacing)
        dest_y = start_y + (i // tiles_per_row) * (scaled_size + spacing)
        scaled = pygame.transform.scale(tile, (scaled_size, scaled_size))
        surface.blit(scaled, (dest_x, dest_y))
