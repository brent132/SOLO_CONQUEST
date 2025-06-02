"""
UI Management System - Comprehensive UI coordination and management

This package provides:
- Message system for status and popup messages
- Inventory state management and interactions
- UI event handling and coordination
- UI state management and visibility control
- Integration with rendering pipeline
"""

from .ui_manager import UIManager
from .message_system import MessageSystem
from .inventory_manager import InventoryManager
from .ui_state_manager import UIStateManager

__all__ = [
    'UIManager',
    'MessageSystem',
    'InventoryManager',
    'UIStateManager'
]
