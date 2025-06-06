"""
Map System - Handles all map-related functionality

This module contains the map management components extracted from PlayScreen:
- Map loading and parsing
- Map processing for different formats
- Tile management and caching
- Map rendering and layers
- Collision detection and handling
- Relation points and teleportation
- World/Map selection and management
- World metadata and organization
"""

from .map_loader import MapLoader
from .map_processor import MapProcessor
from .tile_manager import TileManager
from .map_renderer import MapRenderer
from .map_system import MapSystem
from .map_select import WorldSelectScreen, MapSelectScreen  # MapSelectScreen is alias for backward compatibility
from .world_manager import WorldManager
from .collision_handler import CollisionHandler
from .relation_handler import RelationHandler

__all__ = [
    'MapLoader',
    'MapProcessor',
    'TileManager',
    'MapRenderer',
    'MapSystem',
    'WorldSelectScreen',
    'MapSelectScreen',  # Backward compatibility alias
    'WorldManager',
    'CollisionHandler',
    'RelationHandler'
]
