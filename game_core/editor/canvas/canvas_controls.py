"""Utilities for interacting with the editor canvas."""

from __future__ import annotations

import pygame

from .canvas import Canvas


class CanvasControls:
    """Handle panning and zooming of the canvas."""

    PAN_SPEED = 10  # pixels moved per key press

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas

        # Zoom limits based on the initial grid size
        self._base_grid = canvas.grid_size
        self._min_grid = self._base_grid  # 100%
        self._max_grid = self._base_grid * 3  # 300%

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

        old_grid = self.canvas.grid_size
        new_grid = old_grid * numerator // denominator

        # Enforce zoom limits of 100% to 300%
        new_grid = min(max(new_grid, self._min_grid), self._max_grid)

        if new_grid == old_grid:
            return

        scale = new_grid / old_grid
        self.canvas.grid_size = new_grid
        # Keep the placement manager in sync so new tiles use the
        # current zoom level for pixel calculations
        self.canvas.placement_manager.grid_size = new_grid

        self.canvas.offset[0] = int(self.canvas.offset[0] * scale)
        self.canvas.offset[1] = int(self.canvas.offset[1] * scale)

        for tile in self.canvas.placement_manager.tiles:
            tile.rect.x = int(tile.rect.x * scale)
            tile.rect.y = int(tile.rect.y * scale)
            tile.rect.width = int(tile.rect.width * scale)
            tile.rect.height = int(tile.rect.height * scale)
            tile.image = pygame.transform.scale(tile.image, tile.rect.size)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Process Pygame events for canvas controls.

        Returns True if the event was handled and should not propagate to other
        handlers.
        """
        if event.type == pygame.KEYDOWN:
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
        return False
