"""
Inventory Manager - Handles inventory state and interactions

This module manages:
- Player and chest inventory visibility states
- Inventory interaction coordination
- Inventory event handling
- Inventory positioning and layout
- Cross-inventory item transfers
"""

import pygame
from typing import Optional, Tuple


class InventoryManager:
    """Manages inventory states and interactions"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Inventory references
        self.player_inventory = None
        self.chest_inventory = None
        self.hud_inventory = None  # Reference to HUD inventory for syncing
        self.lootchest_manager = None  # Reference to lootchest manager for chest syncing

        # State tracking
        self.both_inventories_visible = False
        self.current_chest_pos = None

        # Interaction state
        self.last_mouse_pos = (0, 0)

        # Save callbacks
        self.save_callback = None  # For character inventory saves
        self.game_state_save_callback = None  # For game state saves (chest contents)
        
    def initialize(self, player_inventory, chest_inventory, hud_inventory=None, lootchest_manager=None):
        """Initialize with inventory references"""
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.hud_inventory = hud_inventory
        self.lootchest_manager = lootchest_manager

    def set_save_callback(self, callback):
        """Set the callback for character inventory saves"""
        self.save_callback = callback

    def set_game_state_save_callback(self, callback):
        """Set the callback for game state saves (chest contents)"""
        self.game_state_save_callback = callback
        
    def resize(self, new_width: int, new_height: int):
        """Update inventory manager for new screen dimensions"""
        self.screen_width = new_width
        self.screen_height = new_height
        
        # Update inventory positions if both are visible
        if self.both_inventories_visible:
            self._position_side_by_side_inventories()
            
    def show_player_inventory(self):
        """Show the player inventory and sync from HUD"""
        if self.player_inventory:
            # IMPORTANT: Sync HUD inventory to player inventory bottom row before showing
            # This ensures that items collected and visible in the HUD appear in the player inventory
            self._sync_hud_to_player_inventory()

            if self.chest_inventory and self.chest_inventory.is_visible():
                # Both inventories will be visible
                self.both_inventories_visible = True
                self._position_side_by_side_inventories()
            else:
                # Only player inventory
                self.both_inventories_visible = False
                self.player_inventory.show(None)  # Use default positioning
                
    def hide_player_inventory(self):
        """Hide the player inventory and sync to HUD"""
        if self.player_inventory:
            # Pass HUD inventory to sync bottom row to HUD when hiding
            self.player_inventory.hide(self.hud_inventory)
            self.both_inventories_visible = False

            # Trigger save when player inventory is closed
            if self.save_callback:
                self.save_callback()
            
    def show_chest_inventory(self, chest_pos: Tuple[int, int], chest_contents: list):
        """Show the chest inventory with contents"""
        if self.chest_inventory:
            self.current_chest_pos = chest_pos
            self.chest_inventory.show(chest_pos, chest_contents)
            
            if self.player_inventory and self.player_inventory.is_visible():
                # Both inventories will be visible
                self.both_inventories_visible = True
                self._position_side_by_side_inventories()
            else:
                # Only chest inventory
                self.both_inventories_visible = False
                
    def hide_chest_inventory(self):
        """Hide the chest inventory and sync changes back to lootchest manager"""
        if self.chest_inventory:
            # Create sync callback to update lootchest manager
            sync_callback = None
            if self.lootchest_manager:
                sync_callback = self.lootchest_manager.update_chest_contents

            # Hide chest inventory with sync callback
            self.chest_inventory.hide(sync_callback)
            self.current_chest_pos = None
            self.both_inventories_visible = False

            # Trigger game state save when chest inventory is closed
            if self.game_state_save_callback:
                self.game_state_save_callback()
            
    def hide_all_inventories(self):
        """Hide all inventories"""
        self.hide_player_inventory()
        self.hide_chest_inventory()
        
    def toggle_player_inventory(self):
        """Toggle player inventory visibility"""
        if self.player_inventory:
            if self.player_inventory.is_visible():
                self.hide_player_inventory()
            else:
                self.show_player_inventory()
                
    def is_any_inventory_visible(self) -> bool:
        """Check if any inventory is currently visible"""
        player_visible = self.player_inventory and self.player_inventory.is_visible()
        chest_visible = self.chest_inventory and self.chest_inventory.is_visible()
        return player_visible or chest_visible
        
    def are_both_inventories_visible(self) -> bool:
        """Check if both inventories are currently visible"""
        return self.both_inventories_visible
        
    def update(self, mouse_pos: Tuple[int, int]):
        """Update inventory states and interactions"""
        self.last_mouse_pos = mouse_pos
        
        # Update individual inventories
        if self.player_inventory and self.player_inventory.is_visible():
            self.player_inventory.update(mouse_pos)
            
        if self.chest_inventory and self.chest_inventory.is_visible():
            self.chest_inventory.update(mouse_pos)
            
    def handle_click(self, mouse_pos: Tuple[int, int], right_click: bool = False, shift_held: bool = False):
        """Handle inventory clicks with proper coordination"""
        # Check chest inventory first (it's rendered on top)
        if self.chest_inventory and self.chest_inventory.is_visible():
            # Check if click is within chest inventory bounds
            if self._is_click_in_chest_inventory(mouse_pos):
                self.chest_inventory.handle_click(
                    mouse_pos, right_click, shift_held, self.player_inventory
                )
                return True

        # Only check player inventory if chest inventory didn't handle the click
        # Check player inventory
        if self.player_inventory and self.player_inventory.is_visible():
            # Check if click is within player inventory bounds
            if self._is_click_in_player_inventory(mouse_pos):
                self.player_inventory.handle_click(
                    mouse_pos, right_click, shift_held, self.chest_inventory
                )
                return True

        return False
        
    def handle_escape_key(self):
        """Handle ESC key press for inventory management"""
        if self.chest_inventory and self.chest_inventory.is_visible():
            # Close both inventories if chest is open
            self.hide_all_inventories()
            return "both_closed"
        elif self.player_inventory and self.player_inventory.is_visible():
            # Close only player inventory
            self.hide_player_inventory()
            return "player_closed"
        else:
            # Show player inventory
            self.show_player_inventory()
            return "player_opened"
            
    def get_chest_contents(self) -> Optional[list]:
        """Get current chest contents for saving"""
        if self.chest_inventory and self.chest_inventory.is_visible():
            return self.chest_inventory.inventory_items
        return None
        
    def get_current_chest_position(self) -> Optional[Tuple[int, int]]:
        """Get the position of the currently open chest"""
        return self.current_chest_pos

    def get_inventory_state(self) -> dict:
        """Get current inventory state for debugging"""
        return {
            "player_visible": self.player_inventory.is_visible() if self.player_inventory else False,
            "chest_visible": self.chest_inventory.is_visible() if self.chest_inventory else False,
            "both_visible": self.both_inventories_visible,
            "current_chest_pos": self.current_chest_pos
        }

    def _position_side_by_side_inventories(self):
        """Position inventories side by side when both are visible"""
        if not (self.player_inventory and self.chest_inventory):
            return
            
        # Calculate total width needed
        total_width = (self.player_inventory.total_width + 
                      40 +  # spacing
                      self.chest_inventory.total_width)
        
        # Center the combined inventories
        screen_center_x = self.screen_width // 2
        left_x = screen_center_x - (total_width // 2)
        
        # Position player inventory on the left
        self.player_inventory.x = left_x
        self.player_inventory.y = (self.screen_height - self.player_inventory.total_height) // 2
        
        # Update player inventory slot rects
        self._update_player_inventory_rects()
        
        # Position chest inventory on the right
        spacing = 40
        self.chest_inventory.x = (self.player_inventory.x + 
                                 self.player_inventory.total_width + spacing)
        self.chest_inventory.y = self.player_inventory.y
        
        # Update chest inventory slot rects
        self._update_chest_inventory_rects()
        
    def _update_player_inventory_rects(self):
        """Update player inventory slot rectangles"""
        if not self.player_inventory:
            return
            
        for i in range(len(self.player_inventory.slot_rects)):
            row = i // self.player_inventory.grid_width
            col = i % self.player_inventory.grid_width
            
            x = (self.player_inventory.x + 
                (self.player_inventory.slot_size + self.player_inventory.slot_padding) * col)
            
            # Handle extra padding for bottom row (quick access)
            if row == self.player_inventory.grid_height - 1:
                y = (self.player_inventory.y + 
                    (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row + 
                    self.player_inventory.extra_padding)
            else:
                y = (self.player_inventory.y + 
                    (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row)
                
            self.player_inventory.slot_rects[i] = pygame.Rect(
                x, y, self.player_inventory.slot_size, self.player_inventory.slot_size
            )
            
    def _update_chest_inventory_rects(self):
        """Update chest inventory slot rectangles"""
        if not self.chest_inventory:
            return
            
        for i in range(len(self.chest_inventory.slot_rects)):
            row = i // self.chest_inventory.grid_width
            col = i % self.chest_inventory.grid_width
            
            x = (self.chest_inventory.x + 
                (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * col)
            y = (self.chest_inventory.y + 
                (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * row)
                
            self.chest_inventory.slot_rects[i] = pygame.Rect(
                x, y, self.chest_inventory.slot_size, self.chest_inventory.slot_size
            )
            
    def _is_click_in_player_inventory(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if click is within player inventory bounds"""
        if not self.player_inventory:
            return False
            
        for rect in self.player_inventory.slot_rects:
            if rect.collidepoint(mouse_pos):
                return True
        return False

    def _sync_hud_to_player_inventory(self):
        """Sync HUD inventory items to the bottom row of player inventory

        This ensures that items in the HUD hotbar are transferred to the player inventory
        when opening the full inventory screen.
        """
        if not self.player_inventory or not self.hud_inventory:
            return

        # Calculate the starting index for the bottom row of player inventory
        bottom_row_start = self.player_inventory.grid_width * (self.player_inventory.grid_height - 1)

        # Copy items from HUD inventory to the bottom row of player inventory
        for i in range(min(self.hud_inventory.num_slots, self.player_inventory.grid_width)):
            # Copy HUD inventory item to corresponding slot in bottom row
            self.player_inventory.inventory_items[bottom_row_start + i] = self.hud_inventory.inventory_items[i]

    def _is_click_in_chest_inventory(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if click is within chest inventory bounds"""
        if not self.chest_inventory:
            return False
            
        for rect in self.chest_inventory.slot_rects:
            if rect.collidepoint(mouse_pos):
                return True
        return False
