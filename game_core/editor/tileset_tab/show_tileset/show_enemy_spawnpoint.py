"""Utilities for displaying enemy spawn point tiles."""
# Draws enemy spawn previews inside the sidebar.

from __future__ import annotations

from typing import Optional
import pygame

from ..tileset_components import EnemySpawnpointTileset

_enemy_tileset: Optional[EnemySpawnpointTileset] = None


def _get_enemy_tileset() -> EnemySpawnpointTileset:
    """Return the singleton enemy spawn point tileset, loading it if needed."""
    global _enemy_tileset
    if _enemy_tileset is None:
        _enemy_tileset = EnemySpawnpointTileset()
    return _enemy_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the enemy spawn point tiles in the sidebar and return tile rectangles."""
    from ..tileset_palettes import TilesetPalettes

    tileset = _get_enemy_tileset()

    base_spacing = 2

    tiles_per_row = tileset.tiles_per_row()
    rows = (tileset.tile_count() + tiles_per_row - 1) // tiles_per_row

    tile_sizes: list[tuple[int, int]] = []
    max_height = 0
    for tile in tileset.tiles:
        if tile is None:
            continue
        tile_sizes.append((tile.get_width(), tile.get_height()))
        if tile.get_height() > max_height:
            max_height = tile.get_height()

    if max_height == 0:
        return []

    offset_y = TilesetPalettes.PADDING * 3 + TilesetPalettes.TAB_HEIGHT * 2

    available_width = sidebar_rect.width
    available_height = sidebar_rect.height - offset_y

    row_widths: list[int] = []
    for r in range(rows):
        start = r * tiles_per_row
        end = start + tiles_per_row
        row_tiles = tile_sizes[start:end]
        width_sum = sum(w for w, _ in row_tiles)
        row_widths.append(width_sum)
    max_row_width = max(row_widths)

    scale_w = (available_width - base_spacing * tiles_per_row) / max_row_width
    scale_h = (available_height - base_spacing * (rows - 1)) / (max_height * rows)

    scale = min(scale_w, scale_h, 2)
    if scale <= 0:
        scale = 1

    spacing = int(base_spacing * scale)
    scaled_max_height = int(max_height * scale)

    scaled_row_widths = [
        int(w * scale) + spacing * (min(tiles_per_row, tileset.tile_count() - r * tiles_per_row) - 1)
        for r, w in enumerate(row_widths)
    ]
    grid_width = max(scaled_row_widths)

    start_x = sidebar_rect.left + max((available_width - grid_width) // 2, 0)
    start_y = sidebar_rect.top + offset_y

    rects: list[pygame.Rect] = []
    for row in range(rows):
        row_start = row * tiles_per_row
        row_end = row_start + tiles_per_row
        row_tiles = tileset.tiles[row_start:row_end]
        dest_x = start_x + max((grid_width - scaled_row_widths[row]) // 2, 0)
        dest_y_base = start_y + row * (scaled_max_height + spacing)
        for tile in row_tiles:
            if tile is None:
                continue
            scaled_w = int(tile.get_width() * scale)
            scaled_h = int(tile.get_height() * scale)
            dest_y = dest_y_base + scaled_max_height - scaled_h
            scaled = pygame.transform.scale(tile, (scaled_w, scaled_h))
            surface.blit(scaled, (dest_x, dest_y))
            rects.append(pygame.Rect(dest_x, dest_y, scaled_w, scaled_h))
            dest_x += scaled_w + spacing

    return rects
