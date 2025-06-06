"""
Item System - Handles all item-related functionality

This module contains the item management components extracted from PlayScreen:
- Key item collection and animation
- Crystal item collection and animation
- Lootchest interaction and management
- Item state management and persistence
"""

from .key_item_manager import KeyItemManager
from .crystal_item_manager import CrystalItemManager
from .lootchest_manager import LootchestManager

__all__ = [
    'KeyItemManager',
    'CrystalItemManager',
    'LootchestManager'
]
