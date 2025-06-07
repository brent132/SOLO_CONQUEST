"""Repository for loaded tileset objects."""
from __future__ import annotations
# Centralized access to various tileset resources.

import pygame

from ..tileset_tab.tileset_components import (
    OverworldTileset,
    OverworldAnimTileset,
    DungeonTileset,
    DungeonAnimTileset,
    PlayerSpawnpointTileset,
    EnemySpawnpointTileset,
)


class TilesetRepository:
    """Load and provide tile surfaces for placement."""

    def __init__(self) -> None:
        self._tilesets = [
            OverworldTileset(),
            OverworldAnimTileset(),
            DungeonTileset(),
            DungeonAnimTileset(),
            PlayerSpawnpointTileset(),
            EnemySpawnpointTileset(),
        ]

    def get_tile(self, tileset_index: int, tile_index: int) -> pygame.Surface | None:
        """Return a tile from the specified tileset."""
        if 0 <= tileset_index < len(self._tilesets):
            return self._tilesets[tileset_index].get_tile(tile_index)
        return None
