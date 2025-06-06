"""Loader for the animated overworld tileset palette."""

from __future__ import annotations

import os
import pygame

from game_core.editor.image_cache import sprite_cache


class OverworldAnimTileset:
    """Load and store preview frames of animated overworld tiles."""

    TILE_SIZE = 16
    # There are currently four animated tiles arranged in a single row
    TILESET_WIDTH = TILE_SIZE * 4
    TILESET_HEIGHT = TILE_SIZE

    def __init__(self, tileset_folder: str = "Tilesets/Overworld_ani_tiles") -> None:
        self.tileset_folder = tileset_folder
        self.tiles: list[pygame.Surface] = []
        self.load_tiles()

    def tiles_per_row(self) -> int:
        """Return the number of tiles per row in the preview tileset."""
        return self.TILESET_WIDTH // self.TILE_SIZE

    def load_tiles(self) -> None:
        """Load the first frame from each animated tile folder."""
        if not os.path.isdir(self.tileset_folder):
            return

        tile_folders = [f for f in os.listdir(self.tileset_folder)
                        if os.path.isdir(os.path.join(self.tileset_folder, f))]
        tile_folders.sort()

        for folder in tile_folders:
            folder_path = os.path.join(self.tileset_folder, folder)
            first_frame = os.path.join(folder_path, "tile000.png")

            # Fallback: pick the first .png file if tile000.png doesn't exist
            if not os.path.isfile(first_frame):
                frame_files = [f for f in os.listdir(folder_path) if f.endswith(".png")]
                frame_files.sort()
                if not frame_files:
                    continue
                first_frame = os.path.join(folder_path, frame_files[0])

            sprite = sprite_cache.get_sprite(first_frame)
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
