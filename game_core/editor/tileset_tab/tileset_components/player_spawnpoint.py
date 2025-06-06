"""Tileset with a single tile representing the player spawn point."""

from __future__ import annotations

import os
import pygame

from game_core.gameplay.other_components.image_cache import sprite_cache


class PlayerSpawnpointTileset:
    """Load the player spawn point preview tile."""

    TILE_SIZE = 16
    TILESET_WIDTH = TILE_SIZE
    TILESET_HEIGHT = TILE_SIZE

    def __init__(self, tile_path: str = "character/char_idle_up/tile000.png") -> None:
        self.tile_path = tile_path
        self.tiles: list[pygame.Surface] = []
        self.load_tiles()

    def tiles_per_row(self) -> int:
        """Return the number of tiles per row in this tileset."""
        return 1

    def load_tiles(self) -> None:
        """Load the player spawn tile if it exists."""
        if not os.path.isfile(self.tile_path):
            return

        sprite = sprite_cache.get_sprite(self.tile_path)
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
