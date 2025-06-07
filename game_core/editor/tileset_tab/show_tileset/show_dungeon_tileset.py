"""Utilities for displaying the dungeon tileset."""
# Draws the static dungeon tiles palette.

from __future__ import annotations

from typing import Optional
import pygame

from ..tileset_components import DungeonTileset
from .common import draw_tileset as _draw_tileset

# Lazy loaded tileset instance
_dungeon_tileset: Optional[DungeonTileset] = None


def _get_dungeon_tileset() -> DungeonTileset:
    """Return the singleton dungeon tileset, loading it if needed."""
    global _dungeon_tileset
    if _dungeon_tileset is None:
        _dungeon_tileset = DungeonTileset()
    return _dungeon_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the dungeon tileset inside the sidebar."""
    tileset = _get_dungeon_tileset()
    return _draw_tileset(surface, sidebar_rect, tileset)
