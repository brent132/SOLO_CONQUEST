"""Utilities for displaying tilesets in the editor."""

from __future__ import annotations

from typing import Optional
import pygame

from ..tileset_components import OverworldTileset
from .common import draw_tileset as _draw_tileset

# Lazy loaded tileset instances
_overworld_tileset: Optional[OverworldTileset] = None


def _get_overworld_tileset() -> OverworldTileset:
    """Return the singleton overworld tileset, loading it if needed."""
    global _overworld_tileset
    if _overworld_tileset is None:
        _overworld_tileset = OverworldTileset()
    return _overworld_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the overworld tileset inside the sidebar."""

    tileset = _get_overworld_tileset()
    return _draw_tileset(surface, sidebar_rect, tileset)
