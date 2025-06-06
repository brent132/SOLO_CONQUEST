"""
Teleportation System - Handles player teleportation between maps

This package provides:
- Teleportation logic and coordination
- Map switching during teleportation
- Player positioning at teleport points
- Relation point management
- Teleportation state tracking
"""

from .teleportation_manager import TeleportationManager

__all__ = [
    'TeleportationManager'
]
