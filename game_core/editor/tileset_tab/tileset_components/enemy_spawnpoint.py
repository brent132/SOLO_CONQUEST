"""Tileset with preview tiles for enemy spawn points."""
# Loads first enemy animation frame as preview.

from __future__ import annotations

import os
import pygame

from game_core.editor.image_cache import sprite_cache


class EnemySpawnpointTileset:
    """Load preview tiles for enemy spawn points from various enemy folders."""

    TILE_SIZE = 16
    TILESET_WIDTH = TILE_SIZE * 6
    TILESET_HEIGHT = TILE_SIZE

    def __init__(self, enemies_root: str = "Enemies_Sprites") -> None:
        self.enemies_root = enemies_root
        # Specific animation folders used to show a preview sprite for each enemy
        # type. The first frame from these folders will be loaded as the
        # representative tile in the editor sidebar.
        self.enemy_folders = [
            "Bomberplant_Sprites/bomberplant_idle_anim_all_dir",
            "Phantom_Sprites/phantom_idle_anim_left",
            "Phantom_Sprites/phantom_idle_anim_right",
            "Pinkbat_Sprites/pinkbat_idle_left_anim",
            "Pinkbat_Sprites/pinkbat_idle_right_anim",
            "Pinkslime_Sprites/pinkslime_idle_anim_all_dir",
            "Spider_Sprites/spider_idle_anim_all_dir",
            "Spinner_Sprites/spinner_idle_anim_all_dir",
        ]
        self.tiles: list[pygame.Surface] = []
        self.load_tiles()

    def tiles_per_row(self) -> int:
        """Return the number of tiles per row in the preview tileset."""
        return self.TILESET_WIDTH // self.TILE_SIZE

    def _find_first_png(self, folder: str) -> str | None:
        for root, _dirs, files in os.walk(folder):
            png_files = [f for f in files if f.endswith(".png")]
            png_files.sort()
            if png_files:
                return os.path.join(root, png_files[0])
        return None

    def load_tiles(self) -> None:
        """Load the first frame from each enemy folder."""
        for folder in self.enemy_folders:
            base_path = os.path.join(self.enemies_root, folder)
            if not os.path.isdir(base_path):
                continue
            first_png = self._find_first_png(base_path)
            if first_png and os.path.isfile(first_png):
                sprite = sprite_cache.get_sprite(first_png)
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
