"""Tab manager for selecting tilesets within the tiles tab."""

from __future__ import annotations

import pygame

from .show_overworld_tileset import draw_tileset as draw_overworld_tileset
from .show_overworld_anim_tileset import draw_tileset as draw_overworld_anim_tileset
from .show_dungeon_tileset import draw_tileset as draw_dungeon_tileset
from .show_dungeon_anim_tileset import draw_tileset as draw_dungeon_anim_tileset
from .show_player_spawnpoint import draw_tileset as draw_player_spawnpoint
from .show_enemy_spawnpoint import draw_tileset as draw_enemy_spawnpoint
from .tile_selection_manager import TileSelectionManager

from ..color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH


class TilesetTabManager:
    """Manage numeric tileset tabs (1-6) inside the tiles tab."""

    TAB_HEIGHT = 30
    TAB_WIDTH = 30
    PADDING = 5

    def __init__(self, sidebar_rect: pygame.Rect,
                 selection_manager: TileSelectionManager | None = None) -> None:
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.selection_manager = selection_manager or TileSelectionManager()

        self.tilesets = [str(i) for i in range(1, 7)]
        self.active = 0
        self._drawers = [
            draw_overworld_tileset,
            draw_overworld_anim_tileset,
            draw_dungeon_tileset,
            draw_dungeon_anim_tileset,
            draw_player_spawnpoint,
            draw_enemy_spawnpoint,
        ]

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update position and size when the sidebar changes."""
        self.sidebar_rect = sidebar_rect

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse clicks to switch tilesets."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for index, rect in enumerate(self._tileset_rects()):
                if rect.collidepoint(mx, my):
                    self.active = index
                    return
            # If click wasn't on tabs, delegate to selection manager
            self.selection_manager.handle_event(event, self.active)

    def _tileset_rects(self) -> list[pygame.Rect]:
        rects = []
        x = self.sidebar_rect.left + self.PADDING
        y = self.sidebar_rect.top + self.PADDING * 2 + self.TAB_HEIGHT
        for _ in self.tilesets:
            rect = pygame.Rect(x, y, self.TAB_WIDTH, self.TAB_HEIGHT)
            rects.append(rect)
            x += self.TAB_WIDTH + self.PADDING
        return rects

    def draw(self, surface: pygame.Surface) -> None:
        """Draw tileset tabs on the given surface."""
        for index, rect in enumerate(self._tileset_rects()):
            color = LIGHT_GRAY if index == self.active else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(self.tilesets[index], True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        if self.active < len(self._drawers):
            drawer = self._drawers[self.active]
            rects = drawer(surface, self.sidebar_rect)
            self.selection_manager.set_tile_rects(self.active, rects)
            self.selection_manager.draw_selection(surface, self.active)
