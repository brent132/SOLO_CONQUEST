"""
Chest Inventory - handles the display and interaction with lootchest contents (Terraria-style)
"""
import pygame
import os
from game_core.gameplay.other_components.image_cache import sprite_cache

class ChestInventory:
    """Class to handle the lootchest inventory display with Terraria-style interactions"""
    def __init__(self, screen_width, screen_height):
        """Initialize the chest inventory"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the item box image
        original_item_box = self.load_image("character/Hud_Ui/item_box_hud.png")

        # Scale the item box image to 1.5x its original size (same as player inventory)
        original_size = original_item_box.get_width()
        scaled_size = int(original_size * 1.5)
        self.item_box_image = pygame.transform.scale(original_item_box, (scaled_size, scaled_size))

        # Grid dimensions (10x6 grid like player inventory without quick access row)
        self.grid_width = 10
        self.grid_height = 6
        self.slot_size = self.item_box_image.get_width()
        self.slot_padding = 3  # Padding between slots

        # Calculate total dimensions
        self.total_width = (self.slot_size + self.slot_padding) * self.grid_width - self.slot_padding
        self.total_height = (self.slot_size + self.slot_padding) * self.grid_height - self.slot_padding

        # Position in center of screen
        self.x = (self.screen_width - self.total_width) // 2
        self.y = (self.screen_height - self.total_height) // 2

        # Initialize inventory slots (empty)
        self.inventory_items = [None] * (self.grid_width * self.grid_height)

        # Hovered slot
        self.hovered_slot = -1

        # Cursor item state (Terraria-style)
        self.cursor_item = None  # Item currently held by cursor (None or item dict)

        # Create slot rects for collision detection
        self.slot_rects = []
        for i in range(self.grid_width * self.grid_height):
            row = i // self.grid_width
            col = i % self.grid_width
            x = self.x + (self.slot_size + self.slot_padding) * col
            y = self.y + (self.slot_size + self.slot_padding) * row
            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

        # Visibility flag
        self.visible = False

        # Current chest position (for identifying which chest is open)
        self.current_chest_pos = None

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
        for i in range(self.grid_width * self.grid_height):
            row = i // self.grid_width
            col = i % self.grid_width
            x = self.x + (self.slot_size + self.slot_padding) * col
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
        """Draw the chest inventory

        Args:
            surface: Surface to draw on
            skip_background: If True, skip drawing the background
        """
        if not self.visible:
            return

        # Draw background if not skipped
        if not skip_background:
            background_color = (50, 50, 50, 200)
            background_surface = pygame.Surface((self.total_width + 20, self.total_height + 20), pygame.SRCALPHA)
            background_surface.fill(background_color)
            surface.blit(background_surface, (self.x - 10, self.y - 10))

        # Draw title
        font = pygame.font.SysFont(None, 24)
        title_text = font.render("Chest", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.x + self.total_width // 2, y=self.y - 30)
        surface.blit(title_text, title_rect)

        # Draw inventory slots
        for i in range(len(self.inventory_items)):
            rect = self.slot_rects[i]

            # Draw slot background
            surface.blit(self.item_box_image, rect.topleft)

            # Highlight hovered slot
            if i == self.hovered_slot:
                highlight_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
                highlight_surface.fill((255, 255, 255, 50))
                surface.blit(highlight_surface, rect.topleft)

            # Draw item if present
            item = self.inventory_items[i]
            if item:
                # Draw item image
                if "image" in item:
                    item_image = item["image"]
                    # Scale item image to fit in slot (with some padding)
                    item_size = self.slot_size - 8
                    scaled_item = pygame.transform.scale(item_image, (item_size, item_size))
                    item_x = rect.x + (self.slot_size - item_size) // 2
                    item_y = rect.y + (self.slot_size - item_size) // 2
                    surface.blit(scaled_item, (item_x, item_y))

                # Draw item count if > 1
                count = item.get("count", 1)
                if count > 1:
                    font = pygame.font.SysFont(None, 16)
                    count_text = font.render(str(count), True, (255, 255, 255))
                    count_rect = count_text.get_rect(bottomright=(rect.right - 2, rect.bottom - 2))
                    surface.blit(count_text, count_rect)

        # Cursor item rendering is now handled centrally by the UI renderer

    def show(self, chest_pos, chest_contents):
        """Show the chest inventory with the given contents"""
        self.visible = True
        self.current_chest_pos = chest_pos

        # Clear inventory
        self.inventory_items = [None] * (self.grid_width * self.grid_height)

        # Fill inventory with chest contents
        for i, item in enumerate(chest_contents):
            if i < len(self.inventory_items):
                self.inventory_items[i] = item

    def hide(self, sync_callback=None):
        """Hide the chest inventory and optionally sync changes

        Args:
            sync_callback: Optional callback function to sync chest contents back to manager
                          Should accept (chest_pos, inventory_items) as parameters
        """
        # Sync changes back to lootchest manager before hiding
        if sync_callback and self.current_chest_pos is not None:
            sync_callback(self.current_chest_pos, self.inventory_items.copy())

        self.visible = False
        self.current_chest_pos = None
        # Clear cursor item when closing
        self.cursor_item = None

    def is_visible(self):
        """Check if the chest inventory is visible"""
        return self.visible

    def get_current_chest_pos(self):
        """Get the position of the currently open chest"""
        return self.current_chest_pos

    def handle_click(self, mouse_pos, right_click=False, shift_held=False, player_inventory=None):
        """Handle a click in the inventory (Terraria-style)"""
        # Find which slot was clicked
        clicked_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                clicked_slot = i
                break

        if clicked_slot == -1:
            return  # No slot clicked

        # Handle the click based on the current state
        if shift_held and player_inventory and player_inventory.is_visible():
            # Shift+click: Quick transfer to player inventory
            self._quick_transfer_to_player(clicked_slot, player_inventory)
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

    def _quick_transfer_to_player(self, slot_index, player_inventory):
        """Quick transfer item from chest to player (Shift+click)"""
        if not self.inventory_items[slot_index]:
            return  # No item to transfer

        item_to_transfer = self.inventory_items[slot_index]

        # Try to find a slot with the same item type first
        for i, player_item in enumerate(player_inventory.inventory_items):
            if player_item and player_item.get("name") == item_to_transfer.get("name"):
                # Found matching item, merge them
                player_item["count"] = player_item.get("count", 1) + item_to_transfer.get("count", 1)
                self.inventory_items[slot_index] = None
                return

        # No matching item found, try to find an empty slot
        for i, player_item in enumerate(player_inventory.inventory_items):
            if player_item is None:
                # Found empty slot, move item there
                player_inventory.inventory_items[i] = item_to_transfer.copy()
                self.inventory_items[slot_index] = None
                return

    def handle_mouse_up(self, mouse_pos):
        """Handle mouse button up - not needed in Terraria-style system"""
        _ = mouse_pos  # Unused parameter
        pass  # All interactions are handled in handle_click

    def get_slot_at_position(self, mouse_pos):
        """Get the slot index at the given position"""
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                return i
        return -1
