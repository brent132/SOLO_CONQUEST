"""Editor package containing editor-specific modules."""
# Groups editor widgets like Sidebar and Canvas.

__all__ = [
    "Sidebar",
    "Canvas",
    "TabManager",
    "TilesetPalettes",
    "TileSelectionManager",
    "sprite_cache",
]

from .sidebar import Sidebar
from .canvas import Canvas
from .sidebar.sidebar_tab_manager import TabManager
from .tileset_tab.tileset_palettes import TilesetPalettes
from .tileset_tab.tile_selection_manager import TileSelectionManager
from .image_cache import sprite_cache
