"""
Game Systems Coordinator - Handles coordination between different game systems

This module contains the game systems coordination components extracted from PlayScreen:
- Enemy-player interactions and combat
- Item collection and inventory management
- Loot chest interactions and inventory
- Teleportation coordination
- Game state management (death, game over)
- Inter-system communication and coordination
"""

from .game_systems_coordinator import GameSystemsCoordinator
from .enemy_coordinator import EnemyCoordinator
from .item_coordinator import ItemCoordinator
from .inventory_coordinator import InventoryCoordinator
from .interaction_coordinator import InteractionCoordinator

__all__ = [
    'GameSystemsCoordinator',
    'EnemyCoordinator',
    'ItemCoordinator', 
    'InventoryCoordinator',
    'InteractionCoordinator'
]
