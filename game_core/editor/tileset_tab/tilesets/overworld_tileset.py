"""Utilities for loading the overworld tileset panel."""

import os
from typing import List, Optional
import pygame

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
