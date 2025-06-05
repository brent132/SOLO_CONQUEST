"""
Animation System - Handles all animation-related functionality

This module contains the animation management components extracted from PlayScreen:
- Animated tile loading and management
- Animation frame processing and updates
- Tile animation coordination
- Animation state management
"""

from .animated_tile import AnimatedTile
from .animated_tile_manager import AnimatedTileManager

__all__ = [
    'AnimatedTile',
    'AnimatedTileManager'
]
