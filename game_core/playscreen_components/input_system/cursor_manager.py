"""
Cursor Manager - Handles cursor states and custom cursor management

This module manages:
- Custom cursor loading and creation
- Cursor state management (default vs select cursor)
- Hover detection for UI elements
- Shared cursor system for Terraria-style inventory interactions
- Cursor updates based on game state
"""
import pygame
from typing import Optional, Tuple, Any


class CursorManager:
    """Manages cursor states and custom cursors"""
    
    def __init__(self):
        # Cursor states
        self.default_cursor = pygame.mouse.get_cursor()
        self.select_cursor = None
        self.current_cursor_state = "default"
        
        # Shared cursor item for Terraria-style inventory system
        self.shared_cursor_item = None
        
        # Load custom cursor
        self.load_custom_cursor()
        
    def load_custom_cursor(self):
        """Load the custom cursor image and rotate it"""
        try:
            # Load the select icon image
            original_image = pygame.image.load("character/Hud_Ui/select_icon_ui.png").convert_alpha()

            # Rotate the image 135 degrees counter-clockwise (to point top-left)
            cursor_image = pygame.transform.rotate(original_image, 135)

            # Create a cursor from the rotated image
            # Set hotspot to the tip of the arrow (approximately)
            # For a 135-degree rotation (pointing top-left), the tip would be in the top-left quadrant
            hotspot = (cursor_image.get_width() // 4, cursor_image.get_height() // 4)
            self.select_cursor = pygame.cursors.Cursor((hotspot), cursor_image)
        except Exception as e:
            print(f"Error loading custom cursor: {e}")
            self.select_cursor = None
            
    def update_cursor_state(self, hud_hovered_slot: int, hovered_lootchest: bool):
        """
        Update cursor based on hover state
        
        Args:
            hud_hovered_slot: The currently hovered HUD inventory slot (-1 if none)
            hovered_lootchest: Whether mouse is hovering over a lootchest
        """
        should_use_select_cursor = (hud_hovered_slot != -1 or hovered_lootchest) and self.select_cursor
        
        if should_use_select_cursor and self.current_cursor_state != "select":
            # Mouse is hovering over an inventory slot or a lootchest, use custom cursor
            pygame.mouse.set_cursor(self.select_cursor)
            self.current_cursor_state = "select"
        elif not should_use_select_cursor and self.current_cursor_state != "default":
            # Use default cursor
            pygame.mouse.set_cursor(self.default_cursor)
            self.current_cursor_state = "default"
            
    def setup_shared_cursor_system(self, player_inventory, chest_inventory):
        """
        Set up the shared cursor system for Terraria-style inventory interactions
        
        Args:
            player_inventory: The player inventory instance
            chest_inventory: The chest inventory instance
        """
        # Store original cursor_item attributes as private
        player_inventory._original_cursor_item = player_inventory.cursor_item
        chest_inventory._original_cursor_item = chest_inventory.cursor_item

        # Replace cursor_item with property that uses shared state
        def get_shared_cursor(inventory_self):
            return self.shared_cursor_item

        def set_shared_cursor(inventory_self, value):
            self.shared_cursor_item = value

        # Monkey patch both inventories to use shared cursor
        player_inventory.__class__.cursor_item = property(get_shared_cursor, set_shared_cursor)
        chest_inventory.__class__.cursor_item = property(get_shared_cursor, set_shared_cursor)
        
    def get_shared_cursor_item(self) -> Optional[Any]:
        """Get the current shared cursor item"""
        return self.shared_cursor_item
        
    def set_shared_cursor_item(self, item: Optional[Any]):
        """Set the shared cursor item"""
        self.shared_cursor_item = item
        
    def clear_shared_cursor_item(self):
        """Clear the shared cursor item"""
        self.shared_cursor_item = None
        
    def has_cursor_item(self) -> bool:
        """Check if there's currently a cursor item"""
        return self.shared_cursor_item is not None
        
    def get_cursor_state(self) -> str:
        """Get the current cursor state"""
        return self.current_cursor_state
        
    def force_cursor_state(self, state: str):
        """
        Force a specific cursor state
        
        Args:
            state: "default" or "select"
        """
        if state == "select" and self.select_cursor:
            pygame.mouse.set_cursor(self.select_cursor)
            self.current_cursor_state = "select"
        else:
            pygame.mouse.set_cursor(self.default_cursor)
            self.current_cursor_state = "default"
