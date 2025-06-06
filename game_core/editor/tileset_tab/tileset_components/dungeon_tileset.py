"""Loader for the dungeon tileset palette."""
# Reads dungeon tiles from disk for use in the palette.

from __future__ import annotations

import os
import pygame

from game_core.editor.image_cache import sprite_cache


class DungeonTileset:
    """Load and store dungeon tiles for the editor palette."""

    TILE_SIZE = 16
    # Dimensions of the full dungeon tileset image (in pixels)
    TILESET_WIDTH = 192
    TILESET_HEIGHT = 208

    def __init__(self, tileset_folder: str = "Tilesets/Dungeon") -> None:
        self.tileset_folder = tileset_folder
        self.tiles: list[pygame.Surface] = []
        self.load_tiles()

    def tiles_per_row(self) -> int:
        """Return the number of tiles per row in the full tileset image."""
        return self.TILESET_WIDTH // self.TILE_SIZE

    def load_tiles(self) -> None:
        """Load all tile images from the dungeon folder."""
        if not os.path.isdir(self.tileset_folder):
            return

        png_files = [f for f in os.listdir(self.tileset_folder) if f.endswith('.png')]
        png_files.sort()

        for filename in png_files:
            path = os.path.join(self.tileset_folder, filename)
            sprite = sprite_cache.get_sprite(path)
            if sprite is not None:
                self.tiles.append(sprite)

    def get_tile(self, index: int) -> pygame.Surface | None:
        """Return the tile surface at the specified index."""
        if 0 <= index < len(self.tiles):
            return self.tiles[index]
        return None

    def tile_count(self) -> int:
        """Return the number of loaded tiles."""
        return len(self.tiles)
