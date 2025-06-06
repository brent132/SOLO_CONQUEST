"""Utilities for displaying the player spawn point tile."""

from __future__ import annotations

from typing import Optional
import pygame

from .tileset_components import PlayerSpawnpointTileset

_player_tileset: Optional[PlayerSpawnpointTileset] = None


def _get_player_tileset() -> PlayerSpawnpointTileset:
    """Return the singleton player spawn point tileset, loading it if needed."""
    global _player_tileset
    if _player_tileset is None:
        _player_tileset = PlayerSpawnpointTileset()
    return _player_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the player spawn point tile in the sidebar and return tile rectangles."""
    from .tileset_tab_manager import TilesetTabManager

    tileset = _get_player_tileset()

    spacing = 2
    tile_size = tileset.TILE_SIZE

    tiles_per_row = tileset.tiles_per_row()
    rows = (tileset.tile_count() + tiles_per_row - 1) // tiles_per_row

    offset_y = TilesetTabManager.PADDING * 3 + TilesetTabManager.TAB_HEIGHT * 2

    available_width = sidebar_rect.width
    available_height = sidebar_rect.height - offset_y

    scale_w = (available_width - spacing * tiles_per_row) / (tile_size * tiles_per_row)
    scale_h = (available_height - spacing * (rows - 1)) / (tile_size * rows)

    scale = min(scale_w, scale_h, 2)
    if scale <= 0:
        scale = 1

    scaled_size = int(tile_size * scale)

    grid_width = tiles_per_row * scaled_size + spacing * (tiles_per_row - 1)
    start_x = sidebar_rect.left + max((available_width - grid_width) // 2, 0)
    start_y = sidebar_rect.top + offset_y

    rects: list[pygame.Rect] = []
    for i in range(tileset.tile_count()):
        tile = tileset.get_tile(i)
        if tile is None:
            continue
        dest_x = start_x + (i % tiles_per_row) * (scaled_size + spacing)
        dest_y = start_y + (i // tiles_per_row) * (scaled_size + spacing)
        scaled = pygame.transform.scale(tile, (scaled_size, scaled_size))
        surface.blit(scaled, (dest_x, dest_y))
        rects.append(pygame.Rect(dest_x, dest_y, scaled_size, scaled_size))

    return rects
