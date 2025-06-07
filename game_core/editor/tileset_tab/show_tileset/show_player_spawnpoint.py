"""Utilities for displaying the player spawn point tile."""
# Renders player spawn preview inside the sidebar.

from __future__ import annotations

from typing import Optional
import pygame

from ..tileset_components import PlayerSpawnpointTileset
from .common import draw_tileset as _draw_tileset

_player_tileset: Optional[PlayerSpawnpointTileset] = None


def _get_player_tileset() -> PlayerSpawnpointTileset:
    """Return the singleton player spawn point tileset, loading it if needed."""
    global _player_tileset
    if _player_tileset is None:
        _player_tileset = PlayerSpawnpointTileset()
    return _player_tileset


def draw_tileset(surface: pygame.Surface, sidebar_rect: pygame.Rect) -> list[pygame.Rect]:
    """Draw the player spawn point tile in the sidebar."""

    tileset = _get_player_tileset()
    return _draw_tileset(surface, sidebar_rect, tileset)
