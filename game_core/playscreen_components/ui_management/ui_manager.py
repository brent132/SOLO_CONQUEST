"""
UI Manager - Main UI coordination and management system

This module coordinates:
- Message system integration
- Inventory management
- UI state coordination
- Event handling delegation
- Rendering coordination
- System integration
"""

import pygame
from typing import Optional, Tuple, Any

from .message_system import MessageSystem
from .inventory_manager import InventoryManager
from .ui_state_manager import UIStateManager


class UIManager:
    """Main UI management system that coordinates all UI functionality"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize sub-systems
        self.message_system = MessageSystem(screen_width, screen_height)
        self.inventory_manager = InventoryManager(screen_width, screen_height)
        self.ui_state_manager = UIStateManager()
        
        # System references
        self.hud = None
        self.player_inventory = None
        self.chest_inventory = None
        self.game_over_screen = None
        
        # Save/load callback
        self.save_character_inventory_callback = None
        
    def initialize(self, hud, player_inventory, chest_inventory, game_over_screen):
        """Initialize UI manager with all UI components"""
        self.hud = hud
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.game_over_screen = game_over_screen
        
        # Initialize sub-systems
        self.inventory_manager.initialize(player_inventory, chest_inventory)
        self.ui_state_manager.initialize(game_over_screen)
        
    def set_save_callback(self, callback):
        """Set callback for saving character inventory"""
        self.save_character_inventory_callback = callback
        
    def resize(self, new_width: int, new_height: int):
        """Handle screen resize for all UI systems"""
        self.screen_width = new_width
        self.screen_height = new_height
        
        # Update sub-systems
        self.message_system.resize(new_width, new_height)
        self.inventory_manager.resize(new_width, new_height)
        self.ui_state_manager.resize(new_width, new_height)
        
        # Update UI components
        if self.hud:
            self.hud.resize(new_width, new_height)
            
    def update(self, mouse_pos: Tuple[int, int]):
        """Update all UI systems"""
        # Update sub-systems
        self.message_system.update()
        self.inventory_manager.update(mouse_pos)
        self.ui_state_manager.update()
        
        # Update HUD
        if self.hud:
            self.hud.update(mouse_pos)
            
        # Update cursor item state
        cursor_active = self._check_cursor_item_active()
        self.ui_state_manager.set_cursor_item_active(cursor_active)
        
    def handle_event(self, event, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """Handle UI events and return action if needed"""
        # Handle game over screen events first
        if self.ui_state_manager.is_game_over_showing():
            if self.game_over_screen:
                result = self.game_over_screen.handle_event(event)
                return self.ui_state_manager.handle_game_over_event(result)
                
        # Handle inventory clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            shift_held = pygame.key.get_pressed()[pygame.K_LSHIFT] or pygame.key.get_pressed()[pygame.K_RSHIFT]
            right_click = event.button == 3

            if self.inventory_manager.handle_click(mouse_pos, right_click, shift_held):
                return None  # Event handled by inventory
                
        # Handle escape key for inventory management
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            result = self.inventory_manager.handle_escape_key()
            
            # Save inventory when closing
            if result in ["both_closed", "player_closed"] and self.save_character_inventory_callback:
                self.save_character_inventory_callback()
                
            return "escape_handled"
            
        return None
        
    def show_status_message(self, message: str, duration: int = 180):
        """Show a status message"""
        self.message_system.show_status_message(message, duration)
        
    def show_popup_message(self, message: str, duration: Optional[int] = None):
        """Show a popup message"""
        self.message_system.show_popup_message(message, duration)
        
    def show_player_inventory(self):
        """Show the player inventory"""
        self.inventory_manager.show_player_inventory()
        
    def show_chest_inventory(self, chest_pos: Tuple[int, int], chest_contents: list):
        """Show the chest inventory"""
        self.inventory_manager.show_chest_inventory(chest_pos, chest_contents)
        
    def hide_all_inventories(self):
        """Hide all inventories"""
        self.inventory_manager.hide_all_inventories()
        
    def set_game_over(self, show: bool):
        """Set game over screen visibility"""
        self.ui_state_manager.set_game_over(show)
        
    def is_game_over_showing(self) -> bool:
        """Check if game over screen is showing"""
        return self.ui_state_manager.is_game_over_showing()
        
    def should_block_game_input(self) -> bool:
        """Check if game input should be blocked"""
        return self.ui_state_manager.should_block_game_input()
        
    def get_chest_contents_for_saving(self) -> Optional[list]:
        """Get chest contents for saving"""
        return self.inventory_manager.get_chest_contents()
        
    def get_current_chest_position(self) -> Optional[Tuple[int, int]]:
        """Get current chest position"""
        return self.inventory_manager.get_current_chest_position()
        
    def is_any_inventory_visible(self) -> bool:
        """Check if any inventory is visible"""
        return self.inventory_manager.is_any_inventory_visible()
        
    def render_ui_elements(self, surface: pygame.Surface):
        """Render UI elements that aren't handled by the rendering pipeline"""
        # Render messages (status and popup)
        if self.message_system.has_active_messages():
            self.message_system.render_messages(surface)
            
    def get_debug_info(self) -> dict:
        """Get debug information from all UI systems"""
        return {
            "message_system": self.message_system.get_status_info(),
            "inventory_manager": self.inventory_manager.get_inventory_state(),
            "ui_state_manager": self.ui_state_manager.get_state_info()
        }
        
    def _check_cursor_item_active(self) -> bool:
        """Check if any inventory has an active cursor item"""
        player_cursor = (self.player_inventory and 
                        hasattr(self.player_inventory, 'cursor_item') and 
                        self.player_inventory.cursor_item is not None)
        
        chest_cursor = (self.chest_inventory and 
                       hasattr(self.chest_inventory, 'cursor_item') and 
                       self.chest_inventory.cursor_item is not None)
        
        return player_cursor or chest_cursor
