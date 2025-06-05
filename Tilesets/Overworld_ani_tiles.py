"""Helpers for the animated overworld water tileset."""

import os
from typing import List
import pygame

# Base directory for the animated tiles
TILESET_DIR = os.path.join("Tilesets", "Overworld_ani_tiles")

# Preview image paths for palette representation
PALETTE_TILES = [
    os.path.join(TILESET_DIR, "edge_water_tile", "tile000.png"),
    os.path.join(TILESET_DIR, "regia_waterplant_tile", "tile000.png"),
    os.path.join(TILESET_DIR, "water_tile", "tile000.png"),
    os.path.join(TILESET_DIR, "waterplant_tile", "tile000.png"),
]


def load_preview_tiles() -> List[pygame.Surface]:
    """Load preview frames for the animated tiles."""
    previews: List[pygame.Surface] = []
    for path in PALETTE_TILES:
        if os.path.exists(path):
            previews.append(pygame.image.load(path).convert_alpha())
    return previews
