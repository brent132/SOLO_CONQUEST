"""Utilities for displaying the animated overworld tileset."""
# Displays animated overworld tiles inside the sidebar.

from __future__ import annotations

from typing import Optional
import pygame

from ..tileset_components import OverworldAnimTileset
from .common import draw_tileset as _draw_tileset

# Lazy loaded tileset instance
_overworld_anim_tileset: Optional[OverworldAnimTileset] = None


def _get_overworld_anim_tileset() -> OverworldAnimTileset:
    """Return the singleton animated overworld tileset, loading it if needed."""
    global _overworld_anim_tileset
    if _overworld_anim_tileset is None:
        _overworld_anim_tileset = OverworldAnimTileset()
    return _overworld_anim_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the animated overworld tileset in the sidebar."""
    tileset = _get_overworld_anim_tileset()
    return _draw_tileset(surface, sidebar_rect, tileset)
