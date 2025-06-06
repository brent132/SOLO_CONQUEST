"""Utilities for displaying tilesets in the editor."""

from __future__ import annotations

from typing import Optional
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

    scale = 2
    spacing = 2
    tile_size = tileset.TILE_SIZE
    scaled_size = tile_size * scale

    tiles_per_row = max(1, (sidebar_rect.width - spacing * 2) // (scaled_size + spacing))
    start_x = sidebar_rect.left + spacing
    start_y = sidebar_rect.top + TilesetTabManager.PADDING * 3 + TilesetTabManager.TAB_HEIGHT * 2

    for i in range(tileset.tile_count()):
        tile = tileset.get_tile(i)
        if tile is None:
            continue
        dest_x = start_x + (i % tiles_per_row) * (scaled_size + spacing)
        dest_y = start_y + (i // tiles_per_row) * (scaled_size + spacing)
        scaled = pygame.transform.scale(tile, (scaled_size, scaled_size))
        surface.blit(scaled, (dest_x, dest_y))
