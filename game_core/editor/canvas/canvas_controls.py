"""Utilities for interacting with the editor canvas."""

from __future__ import annotations

import pygame

from .canvas import Canvas
from .tile_placement import PlacedTile


class CanvasControls:
    """Handle panning, zooming and dragging of canvas tiles."""

    PAN_SPEED = 10  # pixels moved per key press

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.dragging: PlacedTile | None = None
        self.drag_offset = (0, 0)

        # Zoom limits based on the initial grid size
        self._base_grid = canvas.grid_size
        self._min_grid = self._base_grid  # 100%
        self._max_grid = self._base_grid * 3  # 300%

    # ------------------------------------------------------------------
    # Dragging tiles
    # ------------------------------------------------------------------
    def _tile_at_pos(self, pos: tuple[int, int]) -> PlacedTile | None:
        world_pos = (
            pos[0] - self.canvas.rect.left + self.canvas.offset[0],
            pos[1] - self.canvas.rect.top + self.canvas.offset[1],
        )
        for tile in reversed(self.canvas.placement_manager.tiles):
            if tile.rect.collidepoint(world_pos):
                return tile
        return None

    def _start_drag(self, pos: tuple[int, int]) -> None:
        tile = self._tile_at_pos(pos)
        if tile:
            world_pos = (
                pos[0] - self.canvas.rect.left + self.canvas.offset[0],
                pos[1] - self.canvas.rect.top + self.canvas.offset[1],
            )
            self.dragging = tile
            self.drag_offset = (world_pos[0] - tile.rect.x, world_pos[1] - tile.rect.y)

    def _update_drag(self, pos: tuple[int, int]) -> None:
        if self.dragging:
            world_pos = (
                pos[0] - self.canvas.rect.left + self.canvas.offset[0],
                pos[1] - self.canvas.rect.top + self.canvas.offset[1],
            )
            new_x = world_pos[0] - self.drag_offset[0]
            new_y = world_pos[1] - self.drag_offset[1]
            self.dragging.rect.topleft = (new_x, new_y)

    def _end_drag(self) -> None:
        if self.dragging:
            grid = self.canvas.grid_size
            snapped_x = (self.dragging.rect.x // grid) * grid
            snapped_y = (self.dragging.rect.y // grid) * grid
            self.dragging.rect.topleft = (snapped_x, snapped_y)
        self.dragging = None

    # ------------------------------------------------------------------
    # Canvas navigation
    # ------------------------------------------------------------------
    def _pan(self, dx: int, dy: int) -> None:
        self.canvas.offset[0] += dx
        self.canvas.offset[1] += dy

    def update(self) -> None:
        """Handle continuous panning when navigation keys are held."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self._pan(0, -self.PAN_SPEED)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self._pan(0, self.PAN_SPEED)
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self._pan(-self.PAN_SPEED, 0)
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self._pan(self.PAN_SPEED, 0)

    # ------------------------------------------------------------------
    # Zoom handling
    # ------------------------------------------------------------------
    def _zoom(self, numerator: int, denominator: int) -> None:
        """Zoom the canvas by a fraction defined by numerator/denominator."""

        old_size = self.canvas.grid_size
        new_size = old_size * numerator // denominator

        # Enforce zoom limits of 100% to 300%
        new_size = min(max(new_size, self._min_grid), self._max_grid)

        if new_size == old_size:
            return

        scale_num = new_size
        scale_den = old_size
        self.canvas.grid_size = new_size

        self.canvas.offset[0] = self.canvas.offset[0] * scale_num // scale_den
        self.canvas.offset[1] = self.canvas.offset[1] * scale_num // scale_den

        for tile in self.canvas.placement_manager.tiles:
            tile.rect.x = tile.rect.x * scale_num // scale_den
            tile.rect.y = tile.rect.y * scale_num // scale_den
            tile.rect.width = tile.rect.width * scale_num // scale_den
            tile.rect.height = tile.rect.height * scale_num // scale_den
            tile.image = pygame.transform.scale(tile.image, tile.rect.size)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process Pygame events for canvas controls.

        Returns True if the event was handled and should not propagate to other
        handlers.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos)
            return self.dragging is not None
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and event.buttons[0]:
                self._update_drag(event.pos)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self._end_drag()
                return True
        elif event.type == pygame.KEYDOWN:
            # WASD/Arrow panning
            if event.key in (pygame.K_w, pygame.K_UP):
                self._pan(0, -self.PAN_SPEED)
            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self._pan(0, self.PAN_SPEED)
            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self._pan(-self.PAN_SPEED, 0)
            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self._pan(self.PAN_SPEED, 0)

            # Ctrl + / - zooming
            if event.mod & pygame.KMOD_CTRL:
                if event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self._zoom(2, 1)
                    return True
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self._zoom(1, 2)
                    return True
            return True
