"""Utility classes for placing tiles on the canvas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pygame


@dataclass
class PlacedTile:
    """Data structure for a tile placed on the canvas."""

    image: pygame.Surface
    rect: pygame.Rect

    def draw(self, surface: pygame.Surface, offset: tuple[int, int] = (0, 0)) -> None:
        """Blit the tile image onto the destination surface respecting the offset."""
        surface.blit(self.image, self.rect.move(-offset[0], -offset[1]))


class TilePlacementManager:
    """Manage placement of tiles within a canvas grid."""

    def __init__(self, grid_size: int = 16) -> None:
        self.grid_size = grid_size
        self.tiles: List[PlacedTile] = []

    def _grid_to_pixels(self, x: int, y: int) -> tuple[int, int]:
        """Convert grid coordinates to pixel coordinates."""
        return x * self.grid_size, y * self.grid_size

    def add_tile(
        self,
        image: pygame.Surface,
        grid_x: int,
        grid_y: int,
        width: int | None = None,
        height: int | None = None,
    ) -> pygame.Rect:
        """Place a tile at the given grid coordinates.

        The width and height default to the image's size, allowing special tiles
        to span multiple grid cells (e.g. a 48x32 door).
        """
        px, py = self._grid_to_pixels(grid_x, grid_y)
        # If another tile already occupies this grid position remove it so
        # the new tile replaces the old one. This allows simple overwriting
        # behaviour both for single clicks and for click-and-drag placement.
        self.remove_tile_at(grid_x, grid_y)

        width = width or image.get_width()
        height = height or image.get_height()
        rect = pygame.Rect(px, py, width, height)
        self.tiles.append(PlacedTile(image, rect))
        return rect

    def remove_tile_at(self, grid_x: int, grid_y: int) -> None:
        """Remove the first tile found at the given grid position."""
        px, py = self._grid_to_pixels(grid_x, grid_y)
        for tile in list(self.tiles):
            if tile.rect.collidepoint(px, py):
                self.tiles.remove(tile)
                break

    def has_tile_at(self, grid_x: int, grid_y: int) -> bool:
        """Return True if a tile occupies the given grid position."""
        px, py = self._grid_to_pixels(grid_x, grid_y)
        return any(tile.rect.collidepoint(px, py) for tile in self.tiles)

    def draw(self, surface: pygame.Surface, offset: tuple[int, int] = (0, 0)) -> None:
        """Draw all placed tiles onto the provided surface."""
        for tile in self.tiles:
            tile.draw(surface, offset)
