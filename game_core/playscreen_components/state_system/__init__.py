"""
State System - Handles all game state management functionality

This module contains the state management components extracted from PlayScreen:
- Game state saving and loading
- Map state persistence
- JSON formatting and serialization
- State data management
"""

from .game_state_saver import GameStateSaver

__all__ = [
    'GameStateSaver'
]
