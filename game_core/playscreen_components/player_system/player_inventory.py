"""
Player Inventory - handles the display, interaction, and persistence of the player's full inventory

This module consolidates both UI display and data persistence functionality
to provide a single, coherent inventory system.
"""
import pygame
import os
import json
from game_core.sprite_cache import sprite_cache

class PlayerInventory:
    """Class to handle the player's full inventory display"""
    def __init__(self, screen_width, screen_height):
        """Initialize the player inventory"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Initialize save system
        self.save_dir = "SaveData"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        self.inventory_save_path = os.path.join(self.save_dir, "character_inventory.json")

        # Load the item box image
        original_item_box = self.load_image("character/Hud_Ui/item_box_hud.png")

        # Scale the item box image to 1.5x its original size
        original_size = original_item_box.get_width()
        scaled_size = int(original_size * 1.5)
        self.item_box_image = pygame.transform.scale(original_item_box, (scaled_size, scaled_size))

        # Grid dimensions
        self.grid_width = 10  # 10 columns
        self.grid_height = 7  # 7 rows
        self.slot_size = self.item_box_image.get_width()
        self.slot_padding = 3  # Padding between slots

        # Calculate total dimensions
        self.total_width = (self.slot_size + self.slot_padding) * self.grid_width - self.slot_padding
        self.total_height = (self.slot_size + self.slot_padding) * self.grid_height - self.slot_padding

        # Position in center of screen
        self.x = (self.screen_width - self.total_width) // 2
        self.y = (self.screen_height - self.total_height) // 2

        # Total number of slots
        self.num_slots = self.grid_width * self.grid_height

        # Initialize inventory slots (empty)
        self.inventory_items = [None] * self.num_slots

        # Hovered slot
        self.hovered_slot = -1

        # Cursor item state (Terraria-style)
        self.cursor_item = None  # Item currently held by cursor (None or item dict)

        # Create slot rects for collision detection
        self.slot_rects = []
        # Extra padding between main inventory and quick access row
        self.extra_padding = 10

        for i in range(self.num_slots):
            row = i // self.grid_width
            col = i % self.grid_width

            # Calculate x position (same for all rows)
            x = self.x + (self.slot_size + self.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.grid_height - 1:  # Bottom row (quick access)
                y = self.y + (self.slot_size + self.slot_padding) * row + self.extra_padding
            else:
                y = self.y + (self.slot_size + self.slot_padding) * row

            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

        # Visibility flag
        self.visible = False

    def load_image(self, path):
        """Load an image from the specified path using sprite cache"""
        image = sprite_cache.get_sprite(path)
        if image is None:
            # Return a placeholder image (red square)
            image = sprite_cache.create_placeholder((16, 16))
        return image

    def resize(self, new_width, new_height):
        """Update inventory for new screen dimensions"""
        self.screen_width = new_width
        self.screen_height = new_height

        # Recalculate position to center on screen
        self.x = (self.screen_width - self.total_width) // 2
        self.y = (self.screen_height - self.total_height) // 2

        # Update slot rects for the new dimensions
        self.slot_rects = []
        for i in range(self.num_slots):
            row = i // self.grid_width
            col = i % self.grid_width

            # Calculate x position (same for all rows)
            x = self.x + (self.slot_size + self.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.grid_height - 1:  # Bottom row (quick access)
                y = self.y + (self.slot_size + self.slot_padding) * row + self.extra_padding
            else:
                y = self.y + (self.slot_size + self.slot_padding) * row

            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def update(self, mouse_pos):
        """Update the inventory based on mouse position"""
        if not self.visible:
            return

        # Check if mouse is hovering over any slot
        self.hovered_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                self.hovered_slot = i
                break



    def draw(self, surface, skip_background=False):
        """Draw the inventory on the given surface

        Args:
            surface: Surface to draw on
            skip_background: If True, skip drawing the background
        """
        if not self.visible:
            return

        # Draw background if not skipped
        if not skip_background:
            # Draw semi-transparent black background using current surface dimensions
            surface_width = surface.get_width()
            surface_height = surface.get_height()
            bg_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            surface.blit(bg_surface, (0, 0))

        # Draw each inventory slot
        for i in range(self.num_slots):
            row = i // self.grid_width
            col = i % self.grid_width

            # Calculate x position (same for all rows)
            x = self.x + (self.slot_size + self.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.grid_height - 1:  # Bottom row (quick access)
                y = self.y + (self.slot_size + self.slot_padding) * row + self.extra_padding
            else:
                y = self.y + (self.slot_size + self.slot_padding) * row

            # Draw the item box
            surface.blit(self.item_box_image, (x, y))

            # If this is the hovered slot, draw a highlight
            if i == self.hovered_slot:
                # Draw a highlight rectangle around the hovered slot
                highlight_rect = pygame.Rect(x - 1, y - 1, self.slot_size + 2, self.slot_size + 2)
                pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 1)  # Yellow highlight

            # If there's an item in this slot, draw it
            if self.inventory_items[i]:
                item = self.inventory_items[i]
                if "image" in item:
                    # Get the item image (no scaling - display at original size)
                    item_image = item["image"]

                    # Calculate position to center the item in the slot
                    item_x = x + (self.slot_size - item_image.get_width()) // 2
                    item_y = y + (self.slot_size - item_image.get_height()) // 2
                    surface.blit(item_image, (item_x, item_y))

                    # Draw item count if more than 1
                    if "count" in item and item["count"] > 1:
                        # Use a small font for the count
                        font = pygame.font.SysFont(None, 16)
                        count_text = font.render(str(item["count"]), True, (255, 255, 255))

                        # Position at bottom right of the slot
                        count_x = x + self.slot_size - count_text.get_width() - 2
                        count_y = y + self.slot_size - count_text.get_height() - 2

                        # Draw the count text directly without background
                        surface.blit(count_text, (count_x, count_y))

        # Cursor item rendering is now handled centrally by the UI renderer

    def draw_cursor_item(self, surface):
        """Draw the cursor item (for compatibility with play_screen)"""
        _ = surface  # Unused parameter
        # This method is called by play_screen, but we already draw cursor item in main draw method
        pass

    def show(self, hud_inventory=None):
        """Show the player inventory

        Args:
            hud_inventory: Optional HUD inventory to copy items from
        """
        self.visible = True

        # Ensure inventory is centered on screen
        self.x = (self.screen_width - self.total_width) // 2
        self.y = (self.screen_height - self.total_height) // 2

        # Update slot rects for the new position
        for i in range(self.num_slots):
            row = i // self.grid_width
            col = i % self.grid_width

            # Calculate x position (same for all rows)
            x = self.x + (self.slot_size + self.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.grid_height - 1:  # Bottom row (quick access)
                y = self.y + (self.slot_size + self.slot_padding) * row + self.extra_padding
            else:
                y = self.y + (self.slot_size + self.slot_padding) * row

            self.slot_rects[i] = pygame.Rect(x, y, self.slot_size, self.slot_size)

        # If HUD inventory is provided, copy its items to the bottom row
        if hud_inventory and hasattr(hud_inventory, 'inventory_items'):
            # Calculate the starting index for the bottom row
            bottom_row_start = self.grid_width * (self.grid_height - 1)

            for i, item in enumerate(hud_inventory.inventory_items):
                if i < self.grid_width:  # Only copy to the bottom row
                    # Place item in the bottom row
                    self.inventory_items[bottom_row_start + i] = item

    def hide(self, hud_inventory=None):
        """Hide the player inventory and update the HUD inventory

        Args:
            hud_inventory: Optional HUD inventory to update from the bottom row
        """
        self.visible = False

        # If HUD inventory is provided, update it from the bottom row
        if hud_inventory and hasattr(hud_inventory, 'inventory_items'):
            # Calculate the starting index for the bottom row
            bottom_row_start = self.grid_width * (self.grid_height - 1)

            for i in range(self.grid_width):
                # Copy items from the bottom row to the HUD inventory
                hud_inventory.inventory_items[i] = self.inventory_items[bottom_row_start + i]

    def is_visible(self):
        """Check if the player inventory is visible"""
        return self.visible

    def handle_click(self, mouse_pos, right_click=False, shift_held=False, chest_inventory=None):
        """Handle a click in the inventory (Terraria-style)

        Args:
            mouse_pos: Mouse position (x, y)
            right_click: Whether this was a right click
            shift_held: Whether shift key is held (for quick transfer)
            chest_inventory: Optional chest inventory for quick transfer
        """
        # Find which slot was clicked
        clicked_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                clicked_slot = i
                break

        if clicked_slot == -1:
            return  # No slot clicked

        # Handle the click based on the current state
        if shift_held and chest_inventory and chest_inventory.is_visible():
            # Shift+click: Quick transfer to chest
            self._quick_transfer_to_chest(clicked_slot, chest_inventory)
        elif right_click:
            # Right-click: Pick up/place half stack
            self._handle_right_click(clicked_slot)
        else:
            # Left-click: Pick up/place entire stack
            self._handle_left_click(clicked_slot)

    def _handle_left_click(self, slot_index):
        """Handle left-click: pick up/place entire stack"""
        slot_item = self.inventory_items[slot_index]

        if self.cursor_item is None:
            # No item in cursor, pick up the entire stack from slot
            if slot_item:
                self.cursor_item = slot_item.copy()
                self.inventory_items[slot_index] = None
        else:
            # Have item in cursor
            if slot_item is None:
                # Empty slot, place entire cursor stack
                self.inventory_items[slot_index] = self.cursor_item.copy()
                self.cursor_item = None
            elif slot_item.get("name") == self.cursor_item.get("name"):
                # Same item type, try to merge
                slot_count = slot_item.get("count", 1)
                cursor_count = self.cursor_item.get("count", 1)

                # Add cursor items to slot
                slot_item["count"] = slot_count + cursor_count
                self.cursor_item = None
            else:
                # Different items, swap them
                temp_item = slot_item.copy()
                self.inventory_items[slot_index] = self.cursor_item.copy()
                self.cursor_item = temp_item

    def _handle_right_click(self, slot_index):
        """Handle right-click: pick up/place half stack"""
        slot_item = self.inventory_items[slot_index]

        if self.cursor_item is None:
            # No item in cursor, pick up half the stack from slot
            if slot_item:
                slot_count = slot_item.get("count", 1)
                if slot_count == 1:
                    # Only 1 item, take it all
                    self.cursor_item = slot_item.copy()
                    self.inventory_items[slot_index] = None
                else:
                    # Take half (rounded up)
                    take_count = (slot_count + 1) // 2
                    self.cursor_item = slot_item.copy()
                    self.cursor_item["count"] = take_count
                    slot_item["count"] = slot_count - take_count
        else:
            # Have item in cursor
            if slot_item is None:
                # Empty slot, place one item from cursor
                cursor_count = self.cursor_item.get("count", 1)
                if cursor_count == 1:
                    # Only 1 item in cursor, place it all
                    self.inventory_items[slot_index] = self.cursor_item.copy()
                    self.cursor_item = None
                else:
                    # Place 1 item
                    new_item = self.cursor_item.copy()
                    new_item["count"] = 1
                    self.inventory_items[slot_index] = new_item
                    self.cursor_item["count"] = cursor_count - 1
            elif slot_item.get("name") == self.cursor_item.get("name"):
                # Same item type, add one from cursor to slot
                cursor_count = self.cursor_item.get("count", 1)
                slot_item["count"] = slot_item.get("count", 1) + 1
                if cursor_count == 1:
                    self.cursor_item = None
                else:
                    self.cursor_item["count"] = cursor_count - 1
            else:
                # Different items, swap them
                temp_item = slot_item.copy()
                self.inventory_items[slot_index] = self.cursor_item.copy()
                self.cursor_item = temp_item

    def _quick_transfer_to_chest(self, slot_index, chest_inventory):
        """Quick transfer item from player to chest (Shift+click)"""
        if not self.inventory_items[slot_index]:
            return  # No item to transfer

        item_to_transfer = self.inventory_items[slot_index]

        # Try to find a slot with the same item type first
        for i, chest_item in enumerate(chest_inventory.inventory_items):
            if chest_item and chest_item.get("name") == item_to_transfer.get("name"):
                # Found matching item, merge them
                chest_item["count"] = chest_item.get("count", 1) + item_to_transfer.get("count", 1)
                self.inventory_items[slot_index] = None
                return

        # No matching item found, try to find an empty slot
        for i, chest_item in enumerate(chest_inventory.inventory_items):
            if chest_item is None:
                # Found empty slot, move item there
                chest_inventory.inventory_items[i] = item_to_transfer.copy()
                self.inventory_items[slot_index] = None
                return

    def handle_mouse_up(self, mouse_pos):
        """Handle mouse button up - not needed in Terraria-style system"""
        _ = mouse_pos  # Unused parameter
        pass  # All interactions are handled in handle_click

    def get_slot_at_position(self, mouse_pos):
        """Get the slot index at the given position

        Args:
            mouse_pos: Mouse position (x, y)

        Returns:
            The slot index at the position, or -1 if no slot is at the position
        """
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return -1

    # ===== PERSISTENCE METHODS =====

    def save_to_file(self):
        """Save the inventory to a file

        Returns:
            tuple: (success, message)
        """
        try:
            # Extract inventory data
            inventory_data = self._get_inventory_data()

            # Create the save data structure
            save_data = {
                "version": 1,
                "inventory": inventory_data
            }

            # Save to file
            with open(self.inventory_save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True, "Character inventory saved successfully"
        except Exception as e:
            return False, f"Error saving character inventory: {str(e)}"

    def load_from_file(self):
        """Load the inventory from the save file

        Returns:
            tuple: (success, message)
        """
        try:
            # Check if save file exists
            if not os.path.exists(self.inventory_save_path):
                return False, "No saved inventory found"

            # Load the save data
            with open(self.inventory_save_path, 'r') as f:
                save_data = json.load(f)

            # Check version
            if "version" not in save_data or save_data["version"] != 1:
                return False, "Incompatible save version"

            # Check if inventory data exists
            if "inventory" not in save_data:
                return False, "No inventory data in save file"

            # Update the inventory
            self._load_inventory_data(save_data["inventory"])

            return True, "Character inventory loaded successfully"
        except Exception as e:
            return False, f"Error loading character inventory: {str(e)}"

    def _get_inventory_data(self):
        """Extract inventory data for saving

        Returns:
            list: List of item data dictionaries
        """
        inventory_data = []

        # Go through each inventory slot
        for i in range(self.num_slots):
            item = self.inventory_items[i]
            if item:
                # Create a simplified item data structure
                item_data = {
                    "slot": i,
                    "name": item.get("name", "Unknown"),
                    "count": item.get("count", 1)
                }
                inventory_data.append(item_data)

        return inventory_data

    def _load_inventory_data(self, inventory_data):
        """Update the inventory with loaded data

        Args:
            inventory_data: List of item data dictionaries
        """
        # Clear existing inventory
        self.inventory_items = [None] * self.num_slots

        # Load each inventory item
        for item_data in inventory_data:
            slot = item_data.get("slot", 0)
            if 0 <= slot < self.num_slots:
                # Create the item
                item_name = item_data.get("name", "Unknown")
                item_count = item_data.get("count", 1)

                # Create a placeholder image if needed
                placeholder_image = pygame.Surface((16, 16), pygame.SRCALPHA)

                # Set different colors based on item type for placeholder
                if item_name == "Key":
                    placeholder_image.fill((255, 215, 0, 200))  # Gold for keys
                elif item_name == "Crystal":
                    placeholder_image.fill((0, 191, 255, 200))  # Blue for crystals
                else:
                    placeholder_image.fill((255, 0, 0, 200))  # Red for unknown items

                # Add to inventory with placeholder image
                self.inventory_items[slot] = {
                    "name": item_name,
                    "count": item_count,
                    "image": placeholder_image
                }

