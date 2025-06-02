"""
UI State Manager - Manages overall UI state and coordination

This module manages:
- Game over screen state
- UI visibility coordination
- UI interaction states
- UI event coordination
- Cross-system UI communication
"""

from typing import Optional, Dict, Any


class UIStateManager:
    """Manages overall UI state and coordination"""
    
    def __init__(self):
        # Game state
        self.show_game_over = False
        self.game_paused = False
        
        # UI interaction state
        self.ui_interaction_active = False
        self.cursor_item_active = False
        
        # System references
        self.game_over_screen = None
        
        # State tracking
        self.previous_state = {}
        
    def initialize(self, game_over_screen):
        """Initialize with UI system references"""
        self.game_over_screen = game_over_screen
        
    def set_game_over(self, show: bool):
        """Set game over screen visibility"""
        self.show_game_over = show
        if show:
            self.game_paused = True
        else:
            self.game_paused = False
            
    def is_game_over_showing(self) -> bool:
        """Check if game over screen is showing"""
        return self.show_game_over
        
    def is_game_paused(self) -> bool:
        """Check if game is paused (due to UI or game over)"""
        return self.game_paused or self.ui_interaction_active
        
    def set_ui_interaction_active(self, active: bool):
        """Set whether UI interaction is currently active"""
        self.ui_interaction_active = active
        
    def set_cursor_item_active(self, active: bool):
        """Set whether cursor has an item (affects game interaction)"""
        self.cursor_item_active = active
        
    def should_block_game_input(self) -> bool:
        """Check if game input should be blocked due to UI state"""
        return (self.show_game_over or 
                self.ui_interaction_active or 
                self.cursor_item_active)
                
    def should_block_camera_movement(self) -> bool:
        """Check if camera movement should be blocked"""
        return self.show_game_over
        
    def should_block_player_movement(self) -> bool:
        """Check if player movement should be blocked"""
        return (self.show_game_over or 
                self.ui_interaction_active)
                
    def handle_game_over_event(self, event_result: str) -> Optional[str]:
        """Handle game over screen events"""
        if event_result == "restart":
            self.set_game_over(False)
            return "restart_game"
        elif event_result == "exit":
            self.set_game_over(False)
            return "exit_to_menu"
        return None
        
    def save_state(self):
        """Save current UI state"""
        self.previous_state = {
            "show_game_over": self.show_game_over,
            "game_paused": self.game_paused,
            "ui_interaction_active": self.ui_interaction_active,
            "cursor_item_active": self.cursor_item_active
        }
        
    def restore_state(self):
        """Restore previous UI state"""
        if self.previous_state:
            self.show_game_over = self.previous_state.get("show_game_over", False)
            self.game_paused = self.previous_state.get("game_paused", False)
            self.ui_interaction_active = self.previous_state.get("ui_interaction_active", False)
            self.cursor_item_active = self.previous_state.get("cursor_item_active", False)
            
    def reset_state(self):
        """Reset UI state to defaults"""
        self.show_game_over = False
        self.game_paused = False
        self.ui_interaction_active = False
        self.cursor_item_active = False
        self.previous_state = {}
        
    def get_state_info(self) -> Dict[str, Any]:
        """Get current state information for debugging"""
        return {
            "show_game_over": self.show_game_over,
            "game_paused": self.game_paused,
            "ui_interaction_active": self.ui_interaction_active,
            "cursor_item_active": self.cursor_item_active,
            "should_block_game_input": self.should_block_game_input(),
            "should_block_camera_movement": self.should_block_camera_movement(),
            "should_block_player_movement": self.should_block_player_movement()
        }
        
    def update(self):
        """Update UI state manager"""
        # Update interaction state based on cursor items
        # This could be expanded to check inventory cursor states
        pass
        
    def resize(self, new_width: int, new_height: int):
        """Handle screen resize for UI state manager"""
        # Update game over screen if it exists
        if self.game_over_screen:
            self.game_over_screen.resize(new_width, new_height)
