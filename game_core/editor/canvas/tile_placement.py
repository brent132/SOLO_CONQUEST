"""Utility classes for placing tiles on the canvas."""
# Tracks tile instances and their screen positions.

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pygame


@dataclass
class PlacedTile:
    """Data structure for a tile placed on the canvas."""

    image: pygame.Surface
    rect: pygame.Rect

    def draw(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int] = (0, 0),
        alpha: int = 255,
    ) -> None:
        """Blit the tile image onto ``surface`` taking offset and transparency into account."""

        if alpha != 255:
            image = self.image.copy()
            image.set_alpha(alpha)
        else:
            image = self.image
        surface.blit(image, self.rect.move(-offset[0], -offset[1]))


class TilePlacementManager:
    """Manage placement of tiles within a canvas grid across multiple layers."""

    def __init__(self, grid_size: int = 16) -> None:
        self.grid_size = grid_size
        # Each element in ``layers`` is a list of ``PlacedTile`` objects.
        self.layers: List[List[PlacedTile]] = [[]]

    def _grid_to_pixels(self, x: int, y: int) -> tuple[int, int]:
        """Convert grid coordinates to pixel coordinates."""
        return x * self.grid_size, y * self.grid_size

    def ensure_layer(self, index: int) -> None:
        """Ensure that the layer list is long enough for ``index``."""
        while len(self.layers) <= index:
            self.layers.append([])

    def add_tile(
        self,
        image: pygame.Surface,
        grid_x: int,
        grid_y: int,
        width: int | None = None,
        height: int | None = None,
        layer: int = 0,
    ) -> pygame.Rect:
        """Place a tile at the given grid coordinates.

        The width and height default to the image's size, allowing special tiles
        to span multiple grid cells (e.g. a 48x32 door).
        """
        self.ensure_layer(layer)
        px, py = self._grid_to_pixels(grid_x, grid_y)
        # Overwrite any tile already occupying this grid position on the same layer.
        self.remove_tile_at(grid_x, grid_y, layer)

        width = width or image.get_width()
        height = height or image.get_height()
        rect = pygame.Rect(px, py, width, height)
        self.layers[layer].append(PlacedTile(image, rect))
        return rect

    def remove_tile_at(self, grid_x: int, grid_y: int, layer: int = 0) -> None:
        """Remove the first tile found at the given grid position on a layer."""
        if layer >= len(self.layers):
            return
        px, py = self._grid_to_pixels(grid_x, grid_y)
        for tile in list(self.layers[layer]):
            if tile.rect.collidepoint(px, py):
                self.layers[layer].remove(tile)
                break

    def has_tile_at(self, grid_x: int, grid_y: int, layer: int | None = None) -> bool:
        """Return True if a tile occupies the given grid position."""
        px, py = self._grid_to_pixels(grid_x, grid_y)
        if layer is None:
            return any(
                tile.rect.collidepoint(px, py)
                for layer_tiles in self.layers
                for tile in layer_tiles
            )
        if 0 <= layer < len(self.layers):
            return any(tile.rect.collidepoint(px, py) for tile in self.layers[layer])
        return False

    def draw(
        self,
        surface: pygame.Surface,
        offset: tuple[int, int] = (0, 0),
        active_layer: int | None = None,
    ) -> None:
        """Draw all placed tiles onto the provided surface.

        ``active_layer`` controls which layer is fully opaque. Other layers are
        rendered semi-transparently.
        """

        for idx, layer_tiles in enumerate(self.layers):
            alpha = 255 if active_layer is None or idx == active_layer else 128
            for tile in layer_tiles:
                tile.draw(surface, offset, alpha)

    # Layer management -------------------------------------------------
    def add_layer(self) -> None:
        """Append a new empty layer."""
        self.layers.append([])

    def delete_layer(self, index: int) -> None:
        """Delete a layer and all its tiles if multiple layers exist."""
        if 0 <= index < len(self.layers) and len(self.layers) > 1:
            self.layers.pop(index)

    def clear(self) -> None:
        """Remove all tiles and reset to a single empty layer."""
        self.layers = [[]]

