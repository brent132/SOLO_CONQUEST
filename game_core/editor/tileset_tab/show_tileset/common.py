"""Common helper for drawing tilesets in the sidebar."""
from __future__ import annotations
# Calculates layout for tile grids.

from typing import Protocol, List
import pygame

class TilesetProtocol(Protocol):
    TILE_SIZE: int

    def tiles_per_row(self) -> int:
        ...

    def tile_count(self) -> int:
        ...

    def get_tile(self, index: int) -> pygame.Surface | None:
        ...


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect, tileset: TilesetProtocol) -> List[pygame.Rect]:
    """Render a tileset inside the sidebar and return rectangles for each tile."""
    from ..tileset_palettes import TilesetPalettes

    spacing = 2
    tile_size = tileset.TILE_SIZE

    tiles_per_row = tileset.tiles_per_row()
    rows = (tileset.tile_count() + tiles_per_row - 1) // tiles_per_row

    offset_y = TilesetPalettes.PADDING * 3 + TilesetPalettes.TAB_HEIGHT * 2

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

    rects: List[pygame.Rect] = []
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
