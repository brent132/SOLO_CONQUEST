"""Utilities for displaying the animated dungeon tileset."""

from __future__ import annotations

from typing import Optional
import pygame

from .tileset_components import DungeonAnimTileset

# Lazy loaded tileset instance
_dungeon_anim_tileset: Optional[DungeonAnimTileset] = None


def _get_dungeon_anim_tileset() -> DungeonAnimTileset:
    """Return the singleton animated dungeon tileset, loading it if needed."""
    global _dungeon_anim_tileset
    if _dungeon_anim_tileset is None:
        _dungeon_anim_tileset = DungeonAnimTileset()
    return _dungeon_anim_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> None:
    """Draw the animated dungeon tileset in the sidebar."""

    # Import here to avoid circular dependency during module initialization
    from .tileset_tab_manager import TilesetTabManager

    tileset = _get_dungeon_anim_tileset()

    base_spacing = 2
    tile_width = tileset.TILE_SIZE

    tiles_per_row = tileset.tiles_per_row()
    rows = (tileset.tile_count() + tiles_per_row - 1) // tiles_per_row

    # Determine the tallest tile so scaling fits every frame
    max_height = tile_width
    for tile in tileset.tiles:
        if tile is not None and tile.get_height() > max_height:
            max_height = tile.get_height()

    offset_y = TilesetTabManager.PADDING * 3 + TilesetTabManager.TAB_HEIGHT * 2

    available_width = sidebar_rect.width
    available_height = sidebar_rect.height - offset_y

    scale_w = (available_width - base_spacing * tiles_per_row) / (tile_width * tiles_per_row)
    scale_h = (available_height - base_spacing * (rows - 1)) / (max_height * rows)

    scale = min(scale_w, scale_h, 2)
    if scale <= 0:
        scale = 1

    spacing = int(base_spacing * scale)
    scaled_width = int(tile_width * scale)
    scaled_max_height = int(max_height * scale)

    grid_width = tiles_per_row * scaled_width + spacing * (tiles_per_row - 1)
    start_x = sidebar_rect.left + max((available_width - grid_width) // 2, 0)
    start_y = sidebar_rect.top + offset_y

    for i in range(tileset.tile_count()):
        tile = tileset.get_tile(i)
        if tile is None:
            continue
        row = i // tiles_per_row
        col = i % tiles_per_row
        dest_x = start_x + col * (scaled_width + spacing)
        dest_y = start_y + row * (scaled_max_height + spacing)
        scaled_height = int(tile.get_height() * scale)
        dest_y += scaled_max_height - scaled_height
        scaled = pygame.transform.scale(tile, (scaled_width, scaled_height))
        surface.blit(scaled, (dest_x, dest_y))
