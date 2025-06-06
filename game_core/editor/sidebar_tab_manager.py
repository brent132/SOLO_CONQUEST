"""Simple tab manager for sidebar tabs."""

from __future__ import annotations

import pygame

from .color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from .config import FONT_PATH
from .tileset_tab.tileset_tab_manager import TilesetTabManager


class TabManager:
    """Manage a list of tabs displayed inside a sidebar."""

    TAB_HEIGHT = 30
    TAB_WIDTH = 100
    PADDING = 5

    def __init__(self, tabs: list[str], sidebar_rect: pygame.Rect) -> None:
        self.tabs = tabs
        self.active = 0
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)

        # Manager for the numeric tileset tabs
        self.tileset_manager = TilesetTabManager(sidebar_rect)

    @property
    def active_tileset(self) -> int:
        """Index of the currently selected tileset."""
        return self.tileset_manager.active

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update the sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect
        self.tileset_manager.resize(sidebar_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle mouse clicks to switch tabs."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for index, rect in enumerate(self._tab_rects()):
                if rect.collidepoint(mx, my):
                    self.active = index
                    break
            # Delegate tileset button handling when the tiles tab is active
            if self.tabs[self.active] == "tiles":
                self.tileset_manager.handle_event(event)

    def _tab_rects(self) -> list[pygame.Rect]:
        rects = []
        x = self.sidebar_rect.left + self.PADDING
        y = self.sidebar_rect.top + self.PADDING
        for _ in self.tabs:
            rect = pygame.Rect(x, y, self.TAB_WIDTH, self.TAB_HEIGHT)
            rects.append(rect)
            x += self.TAB_WIDTH + self.PADDING
        return rects


    def draw(self, surface: pygame.Surface) -> None:
        """Draw the tab bar onto the surface."""
        for index, rect in enumerate(self._tab_rects()):
            color = LIGHT_GRAY if index == self.active else DARK_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, SIDEBAR_BORDER, rect, 1)

            label = self.font.render(self.tabs[index].title(), True, WHITE)
            label_rect = label.get_rect(center=rect.center)
            surface.blit(label, label_rect)

        if self.tabs[self.active] == "tiles":
            self.tileset_manager.draw(surface)


