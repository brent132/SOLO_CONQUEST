"""
Inventory System - Handles all inventory-related functionality

This module contains the inventory management components extracted from PlayScreen:
- Chest inventory display and interaction
- Terraria-style inventory mechanics
- Item transfer and stacking logic
- Inventory UI management
"""

from .chest_inventory import ChestInventory

__all__ = [
    'ChestInventory'
]
