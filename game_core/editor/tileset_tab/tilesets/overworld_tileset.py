"""Utilities for loading the overworld tileset panel."""

import os
from typing import List, Optional
import pygame

from ..tileset_tab_manager import TilesetTabManager

# Directory containing the overworld tiles
TILESET_DIR = os.path.join("Tilesets", "Overworld")

# Dimensions of the overworld palette image
PALETTE_SIZE = (288, 208)

# Path to the preview palette image
PALETTE_IMAGE = os.path.join("Tilesets", "Overworld_Tileset.png")


def load_palette() -> Optional[pygame.Surface]:
    """Load the overworld palette image if available."""
    if os.path.exists(PALETTE_IMAGE):
        return pygame.image.load(PALETTE_IMAGE).convert_alpha()
    return None


def tile_paths() -> List[str]:
    """Return sorted file paths for individual overworld tile images."""
    files = [f for f in os.listdir(TILESET_DIR) if f.endswith(".png")]
    files.sort()
    return [os.path.join(TILESET_DIR, f) for f in files]


class OverworldTileset:
    """Panel displaying the overworld tileset palette."""

    def __init__(self) -> None:
        self.palette = load_palette()
        self.rect = pygame.Rect(0, 0, *PALETTE_SIZE)

    def draw(self, surface: pygame.Surface, sidebar_rect: pygame.Rect) -> None:
        """Blit the palette image inside the sidebar when available."""
        if not self.palette:
            return

        padding = TilesetTabManager.PADDING
        y_offset = (
            padding * 3
            + TilesetTabManager.TAB_HEIGHT
            + TilesetTabManager.TAB_HEIGHT
        )
        self.rect.topleft = (
            sidebar_rect.left + padding,
            sidebar_rect.top + y_offset,
        )
        surface.blit(self.palette, self.rect.topleft)
