"""Simple tab manager for sidebar tabs."""
# Switches between tiles, browse, and save views.

from __future__ import annotations

import pygame

from ..color_palette import LIGHT_GRAY, DARK_GRAY, SIDEBAR_BORDER, WHITE
from ..config import FONT_PATH
from ..tileset_tab.tileset_palettes import TilesetPalettes
from ..tileset_tab.tileset_brush import TilesetBrush
from ..tileset_tab.tileset_layer import TilesetLayers
from ..canvas.tile_placement import TilePlacementManager
from ..tileset_tab.tile_selection_manager import TileSelectionManager


class TabManager:
    """Manage a list of tabs displayed inside a sidebar."""

    TAB_HEIGHT = 30
    TAB_WIDTH = 100
    PADDING = 5

    def __init__(self, tabs: list[str], sidebar_rect: pygame.Rect,
                 placement_manager: TilePlacementManager | None = None) -> None:
        self.tabs = tabs
        self.active = 0
        self.sidebar_rect = sidebar_rect
        self.font = pygame.font.Font(FONT_PATH, 16)
        self.placement_manager = placement_manager

        # Tile selection manager used by the tileset palettes
        self.selection_manager = TileSelectionManager()
        # Component for selecting among the numeric tilesets
        self.tileset_palettes = TilesetPalettes(sidebar_rect, self.selection_manager)
        # Separate brush selection component
        self.tileset_brush = TilesetBrush(sidebar_rect)
        # Layer management component
        self.tileset_layers = TilesetLayers(sidebar_rect)

    @property
    def active_tileset(self) -> int:
        """Index of the currently selected tileset."""
        return self.tileset_palettes.active

    @property
    def selected_tile(self) -> int | None:
        """Currently selected tile index for the active tileset."""
        return self.selection_manager.get_selected(self.tileset_palettes.active)

    @property
    def brush_size(self) -> int:
        """Current brush size selected in the tiles tab."""
        return self.tileset_brush.selected

    @property
    def brush_shape(self) -> str:
        """Current brush shape selected in the tiles tab."""
        return self.tileset_brush.shape

    @property
    def active_layer(self) -> int:
        """Currently active tile layer index."""
        return self.tileset_layers.active

    def resize(self, sidebar_rect: pygame.Rect) -> None:
        """Update the sidebar reference when resized."""
        self.sidebar_rect = sidebar_rect
        self.tileset_palettes.resize(sidebar_rect)
        self.tileset_brush.resize(sidebar_rect)
        self.tileset_layers.resize(sidebar_rect)

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
                self.tileset_palettes.handle_event(event)
                self.tileset_brush.handle_event(event)
                action = self.tileset_layers.handle_event(event)
                if self.placement_manager:
                    if action == "add":
                        self.placement_manager.add_layer()
                    elif isinstance(action, tuple) and action[0] == "delete":
                        self.placement_manager.delete_layer(action[1])

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
            bottom = self.tileset_palettes.draw(surface)
            brush_rect = pygame.Rect(
                self.sidebar_rect.left + self.tileset_brush.PADDING,
                bottom + self.tileset_brush.PADDING,
                self.tileset_brush.container_rect.width,
                self.tileset_brush.container_rect.height,
            )
            self.tileset_brush.set_container(brush_rect)
            self.tileset_brush.draw(surface)

            layer_left = brush_rect.right + self.tileset_brush.PADDING
            container_height = self.sidebar_rect.bottom - brush_rect.top - self.PADDING
            self.tileset_layers.set_container(
                pygame.Rect(
                    layer_left,
                    brush_rect.top,
                    self.tileset_layers.LAYER_WIDTH,
                    container_height,
                )
            )
            self.tileset_layers.draw(surface)


