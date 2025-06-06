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

    # ------------------------------------------------------------------
    # Dragging tiles
    # ------------------------------------------------------------------
    def _tile_at_pos(self, pos: tuple[int, int]) -> PlacedTile | None:
        for tile in reversed(self.canvas.placement_manager.tiles):
            if tile.rect.collidepoint(pos):
                return tile
        return None

    def _start_drag(self, pos: tuple[int, int]) -> None:
        tile = self._tile_at_pos(pos)
        if tile:
            self.dragging = tile
            self.drag_offset = (pos[0] - tile.rect.x, pos[1] - tile.rect.y)

    def _update_drag(self, pos: tuple[int, int]) -> None:
        if self.dragging:
            new_x = pos[0] - self.drag_offset[0]
            new_y = pos[1] - self.drag_offset[1]
            self.dragging.rect.topleft = (new_x, new_y)

    def _end_drag(self) -> None:
        if self.dragging:
            x = self.dragging.rect.x - self.canvas.rect.left
            y = self.dragging.rect.y - self.canvas.rect.top
            grid = self.canvas.grid_size
            snapped_x = (x // grid) * grid + self.canvas.rect.left
            snapped_y = (y // grid) * grid + self.canvas.rect.top
            self.dragging.rect.topleft = (snapped_x, snapped_y)
        self.dragging = None

    # ------------------------------------------------------------------
    # Canvas navigation
    # ------------------------------------------------------------------
    def _pan(self, dx: int, dy: int) -> None:
        self.canvas.rect.move_ip(dx, dy)
        for tile in self.canvas.placement_manager.tiles:
            tile.rect.move_ip(dx, dy)

    # ------------------------------------------------------------------
    # Zoom handling
    # ------------------------------------------------------------------
    def _zoom(self, factor: float) -> None:
        old_size = self.canvas.grid_size
        new_size = max(1, int(old_size * factor))
        if new_size == old_size:
            return
        scale = new_size / old_size
        self.canvas.grid_size = new_size

        for tile in self.canvas.placement_manager.tiles:
            rel_x = tile.rect.x - self.canvas.rect.left
            rel_y = tile.rect.y - self.canvas.rect.top
            tile.rect.x = int(rel_x * scale + self.canvas.rect.left)
            tile.rect.y = int(rel_y * scale + self.canvas.rect.top)
            tile.rect.width = int(tile.rect.width * scale)
            tile.rect.height = int(tile.rect.height * scale)
            tile.image = pygame.transform.scale(tile.image, tile.rect.size)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process Pygame events for canvas controls."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging and event.buttons[0]:
                self._update_drag(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._end_drag()
        elif event.type == pygame.KEYDOWN:
            # WASD panning
            if event.key == pygame.K_w:
                self._pan(0, -self.PAN_SPEED)
            elif event.key == pygame.K_s:
                self._pan(0, self.PAN_SPEED)
            elif event.key == pygame.K_a:
                self._pan(-self.PAN_SPEED, 0)
            elif event.key == pygame.K_d:
                self._pan(self.PAN_SPEED, 0)

            # Ctrl + / - zooming
            if event.mod & pygame.KMOD_CTRL:
                if event.key in (pygame.K_EQUALS, pygame.K_KP_PLUS):
                    self._zoom(2.0)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    self._zoom(0.5)
