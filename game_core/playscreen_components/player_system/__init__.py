"""
Player System - Handles all player-related functionality

This module contains the player management components extracted from PlayScreen:
- Player creation and initialization
- Player positioning and movement coordination
- Player state management (health, shield, direction)
- Player location tracking and persistence
- Player inventory management and UI
- Player inventory persistence and save/load
"""

from .player_manager import PlayerManager
from .player_state_manager import PlayerStateManager
from .player_position_manager import PlayerPositionManager
from .player_system import PlayerSystem
from .player_inventory import PlayerInventory
from .player_location_tracker import PlayerLocationTracker
from .character_inventory_saver import CharacterInventorySaver

__all__ = [
    'PlayerManager',
    'PlayerStateManager',
    'PlayerPositionManager',
    'PlayerSystem',
    'PlayerInventory',
    'PlayerLocationTracker',
    'CharacterInventorySaver'
]
