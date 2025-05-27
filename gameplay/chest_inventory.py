"""
Chest Inventory - handles the display and interaction with lootchest contents
"""
import pygame
import os

class ChestInventory:
    """Class to handle the lootchest inventory display"""
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

        # Dragging state
        self.dragging = False
        self.drag_item = None
        self.drag_source = -1
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Picked up item state (for right-click picking)
        self.picked_item = None
        self.picked_source = -1
        self.picked_count = 0
        self.cursor_item = None  # Item that follows the cursor

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
        """Load an image from the specified path"""
        full_path = os.path.join(os.getcwd(), path)
        try:
            image = pygame.image.load(full_path).convert_alpha()
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            # Return a placeholder image (red square)
            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
            placeholder.fill((255, 0, 0, 128))
            return placeholder

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

        # Update drag position if dragging
        if self.dragging:
            # Update the drag position to follow the mouse
            self.drag_offset_x = mouse_pos[0]
            self.drag_offset_y = mouse_pos[1]

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
            # Draw semi-transparent black background
            bg_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            surface.blit(bg_surface, (0, 0))

        # Draw each inventory slot
        for i in range(self.grid_width * self.grid_height):
            row = i // self.grid_width
            col = i % self.grid_width
            x = self.x + (self.slot_size + self.slot_padding) * col
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
                    # Get the item image
                    item_image = item["image"]

                    # Calculate position to center the item in the slot
                    item_x = x + (self.slot_size - item_image.get_width()) // 2
                    item_y = y + (self.slot_size - item_image.get_height()) // 2
                    surface.blit(item_image, (item_x, item_y))

                    # Draw item count if more than 1
                    if "count" in item and item["count"] > 1:
                        # Use a small font for the count (same as player inventory)
                        font = pygame.font.SysFont(None, 16)
                        count_text = font.render(str(item["count"]), True, (255, 255, 255))

                        # Position at bottom right of the slot
                        count_x = x + self.slot_size - count_text.get_width() - 2
                        count_y = y + self.slot_size - count_text.get_height() - 2

                        # Draw the count text directly without background (same as player inventory)
                        surface.blit(count_text, (count_x, count_y))

        # Don't draw dragged or picked items here
        # They will be drawn separately by the play_screen to ensure proper layering

    def draw_dragged_item(self, surface):
        """Draw the dragged item on the surface

        Args:
            surface: The surface to draw on
        """
        if not self.dragging or not self.drag_item:
            return

        # Get the item image
        item_image = self.drag_item["image"]

        # Calculate position to center the item on the mouse cursor
        item_x = self.drag_offset_x - item_image.get_width() // 2
        item_y = self.drag_offset_y - item_image.get_height() // 2

        # Draw the item with semi-transparency
        temp_surface = pygame.Surface((item_image.get_width(), item_image.get_height()), pygame.SRCALPHA)
        temp_surface.blit(item_image, (0, 0))
        temp_surface.set_alpha(180)  # Semi-transparent
        surface.blit(temp_surface, (item_x, item_y))

        # Draw item count if more than 1
        if "count" in self.drag_item and self.drag_item["count"] > 1:
            # Use a small font for the count
            font = pygame.font.SysFont(None, 16)
            count_text = font.render(str(self.drag_item["count"]), True, (255, 255, 255))

            # Position at bottom right of the item
            count_x = item_x + item_image.get_width() - count_text.get_width() - 2
            count_y = item_y + item_image.get_height() - count_text.get_height() - 2

            # Draw the count text directly without background
            surface.blit(count_text, (count_x, count_y))

    def draw_picked_item(self, surface):
        """Draw the picked up item on the surface

        Args:
            surface: The surface to draw on
        """
        if not self.cursor_item or self.picked_count <= 0:
            return

        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()

        # Get the item image
        item_image = self.cursor_item["image"]

        # Calculate position to center the item on the mouse cursor
        item_x = mouse_pos[0] - item_image.get_width() // 2
        item_y = mouse_pos[1] - item_image.get_height() // 2

        # Draw the item with semi-transparency
        temp_surface = pygame.Surface((item_image.get_width(), item_image.get_height()), pygame.SRCALPHA)
        temp_surface.blit(item_image, (0, 0))
        temp_surface.set_alpha(180)  # Semi-transparent
        surface.blit(temp_surface, (item_x, item_y))

        # Draw item count
        font = pygame.font.SysFont(None, 16)
        count_text = font.render(str(self.picked_count), True, (255, 255, 255))

        # Position at bottom right of the item
        count_x = item_x + item_image.get_width() - count_text.get_width() - 2
        count_y = item_y + item_image.get_height() - count_text.get_height() - 2

        # Draw the count text directly without background
        surface.blit(count_text, (count_x, count_y))

    def show(self, chest_pos, chest_contents, player_inventory=None):
        """Show the chest inventory with the given contents

        Args:
            chest_pos: Position of the chest (x, y) tuple
            chest_contents: List of items in the chest
            player_inventory: Optional player inventory to position next to
        """
        self.visible = True
        self.current_chest_pos = chest_pos

        # Clear inventory
        self.inventory_items = [None] * (self.grid_width * self.grid_height)

        # Fill inventory with chest contents
        for i, item in enumerate(chest_contents):
            if i < len(self.inventory_items):
                self.inventory_items[i] = item

        # If player inventory is visible, position this inventory next to it
        if player_inventory and player_inventory.is_visible():
            # Position to the right of the player inventory with some spacing
            spacing = 40  # Spacing between inventories
            self.x = player_inventory.x + player_inventory.total_width + spacing
            self.y = player_inventory.y  # Align vertically with player inventory

            # Update slot rects for the new position
            for i in range(len(self.slot_rects)):
                row = i // self.grid_width
                col = i % self.grid_width
                x = self.x + (self.slot_size + self.slot_padding) * col
                y = self.y + (self.slot_size + self.slot_padding) * row
                self.slot_rects[i] = pygame.Rect(x, y, self.slot_size, self.slot_size)
        else:
            # Position in center of screen
            self.x = (self.screen_width - self.total_width) // 2
            self.y = (self.screen_height - self.total_height) // 2

            # Update slot rects for the new position
            for i in range(len(self.slot_rects)):
                row = i // self.grid_width
                col = i % self.grid_width
                x = self.x + (self.slot_size + self.slot_padding) * col
                y = self.y + (self.slot_size + self.slot_padding) * row
                self.slot_rects[i] = pygame.Rect(x, y, self.slot_size, self.slot_size)

    def hide(self):
        """Hide the chest inventory"""
        self.visible = False
        self.current_chest_pos = None

    def is_visible(self):
        """Check if the chest inventory is visible"""
        return self.visible

    def get_current_chest_pos(self):
        """Get the position of the currently open chest"""
        return self.current_chest_pos

    def handle_click(self, mouse_pos, right_click=False):
        """Handle a click in the inventory

        Args:
            mouse_pos: Mouse position (x, y)
            right_click: Whether this was a right click (for picking up one item at a time)
        """
        # Debug output
        print(f"Chest inventory handle_click at {mouse_pos}, right_click={right_click}")

        # Check if a slot was clicked
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                print(f"Clicked on chest inventory slot {i}")
                # If there's an item in this slot
                if self.inventory_items[i]:
                    if right_click:
                        # Handle right-click to pick up one item at a time
                        self._handle_right_click_pickup(i)
                    else:
                        # Left-click to start dragging the whole stack
                        print(f"Starting to drag item: {self.inventory_items[i].get('name', 'Unknown')}")
                        self.dragging = True
                        self.drag_item = self.inventory_items[i].copy()  # Make a copy of the item
                        self.drag_source = i
                        self.drag_offset_x = mouse_pos[0]
                        self.drag_offset_y = mouse_pos[1]
                        # Don't remove the item yet, wait until drop
                elif right_click and self.picked_count > 0:
                    # Right-click on empty slot with picked items - place one item
                    self._place_one_picked_item(i)
                else:
                    print(f"Slot {i} is empty, nothing to drag")
                return

        print("No chest inventory slot clicked")

    def _handle_right_click_pickup(self, slot_index):
        """Handle right-click to pick up one item at a time

        Args:
            slot_index: Index of the slot that was right-clicked
        """
        # Get the item in the slot
        item = self.inventory_items[slot_index]

        # If we don't have a picked item yet, or it's a different item
        if self.picked_item is None or self.picked_item.get("name") != item.get("name"):
            # Start a new picked item
            self.picked_item = item
            self.picked_source = slot_index
            self.picked_count = 1
            self.cursor_item = item.copy()

            # Reduce the count in the source slot
            if item.get("count", 1) > 1:
                item["count"] -= 1
            else:
                # If this was the last item, remove it from the slot
                self.inventory_items[slot_index] = None
        else:
            # We already have a picked item of the same type
            # Add one more to the picked count
            self.picked_count += 1

            # Reduce the count in the source slot
            if item.get("count", 1) > 1:
                item["count"] -= 1
            else:
                # If this was the last item, remove it from the slot
                self.inventory_items[slot_index] = None

    def _place_one_picked_item(self, slot_index):
        """Place one picked item into the specified slot

        Args:
            slot_index: Index of the slot to place the item in
        """
        # Make sure we have a picked item and the target slot is empty
        if self.picked_count <= 0 or self.inventory_items[slot_index] is not None:
            return

        # Create a new item with count of 1
        new_item = self.cursor_item.copy()
        new_item["count"] = 1

        # Place it in the slot
        self.inventory_items[slot_index] = new_item

        # Reduce the picked count
        self.picked_count -= 1

        # If no more picked items, clear the cursor
        if self.picked_count <= 0:
            self.picked_item = None
            self.picked_source = -1
            self.cursor_item = None

    def handle_mouse_up(self, mouse_pos, player_inventory=None):
        """Handle mouse button up in the inventory

        Args:
            mouse_pos: Mouse position (x, y)
            player_inventory: Optional player inventory to transfer items to
        """
        # Debug output
        print(f"Chest inventory handle_mouse_up at {mouse_pos}")
        print(f"Dragging: {self.dragging}, Drag item: {self.drag_item is not None}")

        # If not dragging and no picked items, nothing to do
        if not self.dragging and self.picked_count <= 0:
            print("Not dragging and no picked items, returning")
            return

        # If we have picked items, handle placing them
        if self.picked_count > 0:
            self._handle_place_picked_items(mouse_pos, player_inventory)
            return

        # If not dragging or no drag item, nothing to do
        if not self.dragging or not self.drag_item:
            print("Not dragging or no drag item, returning")
            return

        print(f"Dragging item from slot {self.drag_source}")

        # Check if dropping on a slot in this inventory
        target_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                target_slot = i
                break

        # If dropping on a valid slot in this inventory
        if target_slot != -1:
            print(f"Dropping on chest inventory slot {target_slot}")
            # If dropping on a different slot than source
            if target_slot != self.drag_source:
                # Get source and target items
                source_item = self.inventory_items[self.drag_source]
                target_item = self.inventory_items[target_slot]

                # If target slot is empty, just move the item
                if not target_item:
                    print(f"Moving item to empty slot {target_slot}")
                    self.inventory_items[target_slot] = source_item
                    self.inventory_items[self.drag_source] = None
                else:
                    # Check if items are the same type (can be merged)
                    if target_item.get("name") == source_item.get("name"):
                        print(f"Merging items in slot {target_slot}")
                        # Same item type, merge them by adding counts
                        target_count = target_item.get("count", 1)
                        source_count = source_item.get("count", 1)

                        # Update the target item count
                        target_item["count"] = target_count + source_count

                        # Remove the source item
                        self.inventory_items[self.drag_source] = None
                    else:
                        print(f"Swapping with item in slot {target_slot}")
                        # Different items, swap them
                        self.inventory_items[target_slot] = source_item
                        self.inventory_items[self.drag_source] = target_item
        # Check if dropping on player inventory
        elif player_inventory and player_inventory.is_visible():
            print(f"Checking if dropping on player inventory")
            print(f"Player inventory visible: {player_inventory.is_visible()}")
            print(f"Player inventory position: ({player_inventory.x}, {player_inventory.y})")
            print(f"Player inventory dimensions: {player_inventory.total_width}x{player_inventory.total_height}")

            # Check if dropping on a slot in player inventory
            player_target_slot = player_inventory.get_slot_at_position(mouse_pos)
            print(f"Player target slot: {player_target_slot}")

            if player_target_slot != -1:
                print(f"Dropping on player inventory slot {player_target_slot}")
                # Get source and target items
                source_item = self.inventory_items[self.drag_source]
                target_item = player_inventory.inventory_items[player_target_slot]

                # Transfer item from chest to player inventory
                if not target_item:
                    print(f"Moving item to empty player inventory slot {player_target_slot}")
                    player_inventory.inventory_items[player_target_slot] = source_item
                    self.inventory_items[self.drag_source] = None
                else:
                    # Check if items are the same type (can be merged)
                    if target_item.get("name") == source_item.get("name"):
                        print(f"Merging items in player inventory slot {player_target_slot}")
                        # Same item type, merge them by adding counts
                        target_count = target_item.get("count", 1)
                        source_count = source_item.get("count", 1)

                        # Update the target item count
                        target_item["count"] = target_count + source_count

                        # Remove the source item
                        self.inventory_items[self.drag_source] = None
                    else:
                        print(f"Swapping with item in player inventory slot {player_target_slot}")
                        # Different items, swap them
                        player_inventory.inventory_items[player_target_slot] = source_item
                        self.inventory_items[self.drag_source] = target_item
            else:
                print(f"No player inventory slot found at {mouse_pos}")
                # Print all player inventory slot rects for debugging
                print("Player inventory slot rects:")
                for i, rect in enumerate(player_inventory.slot_rects):
                    print(f"Slot {i}: {rect}")

        # Reset dragging state
        print("Resetting dragging state")
        self.dragging = False
        self.drag_item = None
        self.drag_source = -1

    def _handle_place_picked_items(self, mouse_pos, player_inventory=None):
        """Handle placing picked items when mouse button is released

        Args:
            mouse_pos: Mouse position (x, y)
            player_inventory: Optional player inventory to transfer items to
        """
        # Check if dropping on a slot in this inventory
        target_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                target_slot = i
                break

        # If dropping on a valid slot in this inventory
        if target_slot != -1:
            # Get the target item
            target_item = self.inventory_items[target_slot]

            # If target slot is empty, place all picked items
            if not target_item:
                # Create a new item with the full count
                new_item = self.cursor_item.copy()
                new_item["count"] = self.picked_count

                # Place it in the slot
                self.inventory_items[target_slot] = new_item

                # Clear the cursor
                self.picked_count = 0
                self.picked_item = None
                self.picked_source = -1
                self.cursor_item = None
            # If target has same item type, add all to the stack
            elif target_item.get("name") == self.cursor_item.get("name"):
                # Add all picked items to the target count
                target_item["count"] = target_item.get("count", 1) + self.picked_count

                # Clear the cursor
                self.picked_count = 0
                self.picked_item = None
                self.picked_source = -1
                self.cursor_item = None
        # Check if dropping on player inventory
        elif player_inventory and player_inventory.is_visible():
            # Check if dropping on a slot in player inventory
            player_target_slot = player_inventory.get_slot_at_position(mouse_pos)
            if player_target_slot != -1:
                # Get the target item
                target_item = player_inventory.inventory_items[player_target_slot]

                # If target slot is empty, place all picked items in player inventory
                if not target_item:
                    # Create a new item with the full count
                    new_item = self.cursor_item.copy()
                    new_item["count"] = self.picked_count

                    # Place it in the player inventory slot
                    player_inventory.inventory_items[player_target_slot] = new_item

                    # Clear the cursor
                    self.picked_count = 0
                    self.picked_item = None
                    self.picked_source = -1
                    self.cursor_item = None
                # If target has same item type, add all to the stack
                elif target_item.get("name") == self.cursor_item.get("name"):
                    # Add all picked items to the target count
                    target_item["count"] = target_item.get("count", 1) + self.picked_count

                    # Clear the cursor
                    self.picked_count = 0
                    self.picked_item = None
                    self.picked_source = -1
                    self.cursor_item = None

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
