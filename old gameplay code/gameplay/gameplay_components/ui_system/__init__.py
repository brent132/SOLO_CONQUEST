"""
UI System - Handles all user interface functionality

This module contains the UI components extracted from PlayScreen:
- HUD display and health bars
- Inventory UI and interaction
- Game over screen display
- UI element management and coordination
"""

from .hud import HUD, Inventory
from .game_over_screen import GameOverScreen

__all__ = [
    'HUD',
    'Inventory', 
    'GameOverScreen'
]
