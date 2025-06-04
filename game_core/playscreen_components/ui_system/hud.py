import pygame
import os
import math
from game_core.core.image_cache import sprite_cache

class Inventory:
    """Class to handle the player's inventory"""

    def __init__(self, screen_width, screen_height):
        """Initialize the inventory"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load the item box image
        original_item_box = self.load_image("character/Hud_Ui/item_box_hud.png")

        # Scale the item box image to 1.5x its original size
        original_size = original_item_box.get_width()
        scaled_size = int(original_size * 1.5)
        self.item_box_image = pygame.transform.scale(original_item_box, (scaled_size, scaled_size))

        # Load the mouse hover selection icon
        original_select_icon = self.load_image("character/Hud_Ui/select_icon_ui.png")

        # Scale the selection icon to 1.5x its original size
        self.select_icon = pygame.transform.scale(original_select_icon,
                                                 (int(original_select_icon.get_width() * 1.5),
                                                  int(original_select_icon.get_height() * 1.5)))

        # Number of inventory slots
        self.num_slots = 10

        # Size of each slot (with padding)
        self.slot_size = self.item_box_image.get_width()
        self.slot_padding = 3  # Padding between slots (1.5x original)

        # Calculate total width of inventory bar
        self.total_width = (self.slot_size + self.slot_padding) * self.num_slots - self.slot_padding

        # Position inventory next to back button (which is at 20, 20)
        self.back_button_width = 32  # Approximate width of back button
        self.inventory_x = 20 + self.back_button_width + 15  # 15px padding after back button (1.5x original)
        self.inventory_y = 20  # Same y position as back button

        # Initialize inventory slots (empty)
        self.inventory_items = [None] * self.num_slots

        # Selected slot (highlighted)
        self.selected_slot = 0

        # Hovered slot (mouse over)
        self.hovered_slot = -1  # -1 means no slot is hovered

        # Create rects for each slot (for mouse hover detection)
        self.slot_rects = []
        for i in range(self.num_slots):
            x = self.inventory_x + (self.slot_size + self.slot_padding) * i
            y = self.inventory_y
            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def load_image(self, path):
        """Load an image from the specified path using sprite cache"""
        image = sprite_cache.get_sprite(path)
        if image is None:
            # Return a placeholder image (red square) - appropriate size for 1.5x inventory
            image = sprite_cache.create_placeholder((24, 24))
        return image

    def resize(self, new_width, new_height):
        """Update inventory for new screen dimensions"""
        self.screen_width = new_width
        self.screen_height = new_height

        # Update slot rects for the new dimensions
        self.slot_rects = []
        for i in range(self.num_slots):
            x = self.inventory_x + (self.slot_size + self.slot_padding) * i
            y = self.inventory_y
            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))

    def update(self, mouse_pos):
        """Update the inventory based on mouse position"""
        # Check if mouse is hovering over any slot
        self.hovered_slot = -1
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(mouse_pos):
                self.hovered_slot = i
                break

    def draw(self, surface):
        """Draw the inventory on the given surface"""
        # Draw each inventory slot
        for i in range(self.num_slots):
            # Calculate position for this slot
            x = self.inventory_x + (self.slot_size + self.slot_padding) * i
            y = self.inventory_y

            # Draw the item box
            surface.blit(self.item_box_image, (x, y))

            # If this is the selected slot, draw a highlight
            if i == self.selected_slot:
                # Draw a highlight rectangle around the selected slot
                highlight_rect = pygame.Rect(x - 1, y - 1, self.slot_size + 2, self.slot_size + 2)
                pygame.draw.rect(surface, (255, 255, 0), highlight_rect, 1)  # Yellow highlight

            # If there's an item in this slot, draw it
            if self.inventory_items[i]:
                item = self.inventory_items[i]
                if "image" in item:
                    # Get the original item image - no scaling
                    item_image = item["image"]

                    # Calculate position to center the original-sized item in the larger slot
                    item_x = x + (self.slot_size - item_image.get_width()) // 2
                    item_y = y + (self.slot_size - item_image.get_height()) // 2
                    surface.blit(item_image, (item_x, item_y))

                    # Draw item count if it has a count greater than 1
                    if "count" in item and item["count"] > 1:
                        try:
                            # Try to use the Poppins Light font if available - smaller size for thin font
                            # Try to load Poppins-Light for a thinner font
                            try:
                                count_font = pygame.font.Font("fonts/Poppins-Light.ttf", 9)
                            except:
                                # Fall back to regular Poppins if Light is not available
                                count_font = pygame.font.Font("fonts/Poppins-Regular.ttf", 9)
                        except:
                            # Fall back to default font if Poppins is not available
                            count_font = pygame.font.Font(None, 10)

                        # Render the count text
                        count_text = count_font.render(str(item["count"]), True, (255, 255, 255))

                        # Add a shadow effect for better visibility without background
                        count_shadow = count_font.render(str(item["count"]), True, (0, 0, 0))

                        # Divide the slot into four quadrants
                        # Calculate the bottom right quadrant position
                        quadrant_size = self.slot_size // 2

                        # Position the count in the bottom right quadrant
                        # Center it within the bottom right quadrant
                        quadrant_x = x + quadrant_size  # Start of right half
                        quadrant_y = y + quadrant_size  # Start of bottom half

                        # Calculate position to center the count in the bottom right quadrant
                        count_x = quadrant_x + (quadrant_size - count_text.get_width()) // 2
                        count_y = quadrant_y + (quadrant_size - count_text.get_height()) // 2

                        # Draw shadow with slightly more offset for better visibility without background
                        surface.blit(count_shadow, (count_x + 1, count_y + 1))
                        # Draw actual count
                        surface.blit(count_text, (count_x, count_y))

class HUD:
    """Class to handle the heads-up display (HUD) elements"""

    def __init__(self, screen_width, screen_height):
        """Initialize the HUD"""
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Load HUD assets - same as enemy health bar
        original_health_bar_bg = self.load_image("character/Hud_Ui/health_hud.png")
        self.health_indicator = self.load_image("character/Hud_Ui/health_bar_hud.png")

        # Crop the health bar from the left side (reduce width by 20%)
        original_width = original_health_bar_bg.get_width()
        crop_amount = int(original_width * 0.15)  # Reduce by 20% from left side
        new_width = original_width - crop_amount

        # Create a new surface with the reduced width for background
        self.health_bar_bg = pygame.Surface((new_width, original_health_bar_bg.get_height()), pygame.SRCALPHA)
        # Copy the right portion of the original image
        self.health_bar_bg.blit(original_health_bar_bg, (0, 0),
                               (crop_amount, 0, original_width, original_health_bar_bg.get_height()))

        # Position the health bar in the top-right corner
        # Increase right_padding to move it more to the left
        right_padding = 30  # Increased from 20 to 30 to move it more to the left
        self.health_bar_pos = (self.screen_width - self.health_bar_bg.get_width() - right_padding, 20)

        # Position the indicator separately, with a different offset
        # Keep this the same to maintain the indicator position
        indicator_right_padding = 10
        self.indicator_pos = (
            self.screen_width - self.health_indicator.get_width() - indicator_right_padding,
            self.health_bar_pos[1]  # Same vertical position
        )

        # Calculate health bar dimensions
        self.health_bar_width = self.health_bar_bg.get_width()
        self.health_bar_height = self.health_bar_bg.get_height()

        # Calculate indicator position to align its right edge with the background's right edge
        self.indicator_pos = (
            self.health_bar_pos[0] + (self.health_bar_width - self.health_indicator.get_width()),
            self.health_bar_pos[1]
        )

        # Initialize inventory
        self.inventory = Inventory(screen_width, screen_height)

    def load_image(self, path):
        """Load an image from the specified path using sprite cache"""
        image = sprite_cache.get_sprite(path)
        if image is None:
            # Return a placeholder image (red square)
            image = sprite_cache.create_placeholder((32, 32))
        return image

    def resize(self, new_width, new_height):
        """Update HUD elements for new screen dimensions"""
        self.screen_width = new_width
        self.screen_height = new_height

        # Recalculate positions for the health bar
        right_padding = 30
        self.health_bar_pos = (self.screen_width - self.health_bar_bg.get_width() - right_padding, 20)

        # Recalculate indicator position to align with the background
        self.indicator_pos = (
            self.health_bar_pos[0] + (self.health_bar_width - self.health_indicator.get_width()),
            self.health_bar_pos[1]
        )

        # Update inventory dimensions
        self.inventory.resize(new_width, new_height)

    def update(self, mouse_pos):
        """Update HUD elements based on mouse position"""
        # Update inventory hover state
        self.inventory.update(mouse_pos)

    def draw(self, surface, player):
        """Draw the HUD elements on the given surface

        Args:
            surface: Surface to draw on
            player: Player character
        """
        if not player:
            return

        # Draw inventory first (so it appears behind other UI elements if they overlap)
        self.inventory.draw(surface)

        # Calculate health percentage
        health_percent = max(0, min(1, player.current_health / player.max_health))

        # Calculate width of health_hud (background) based on current health
        health_width = int(self.health_bar_bg.get_width() * health_percent)

        if health_width > 0:
            try:
                # Create a subsurface of the background (health_hud) with the appropriate width
                health_rect = pygame.Rect(0, 0, health_width, self.health_bar_bg.get_height())
                health_bg_part = self.health_bar_bg.subsurface(health_rect)

                # Draw the health_hud (background) first
                surface.blit(health_bg_part, self.health_bar_pos)

                # Draw the health_bar_hud (foreground) on top, using the aligned position
                surface.blit(self.health_indicator, self.indicator_pos)
            except ValueError:
                # If subsurface fails, use clipping rect
                clip_rect = surface.get_clip()

                health_clip_rect = pygame.Rect(
                    self.health_bar_pos[0],
                    self.health_bar_pos[1],
                    health_width,
                    self.health_bar_bg.get_height()
                )

                # Draw the health_hud (background) with clipping
                surface.set_clip(health_clip_rect)
                surface.blit(self.health_bar_bg, self.health_bar_pos)
                surface.set_clip(clip_rect)

                # Draw the health_bar_hud (foreground) on top, using the aligned position
                surface.blit(self.health_indicator, self.indicator_pos)

        # Draw health text with a smaller font size
        try:
            # Try to use the Poppins font if available
            font = pygame.font.Font("fonts/Poppins-Regular.ttf", 12)  # Smaller font size
        except:
            # Fall back to default font if Poppins is not available
            font = pygame.font.Font(None, 16)  # Smaller font size

        # Simplified text format for smaller display
        health_text = font.render(f"{int(player.current_health)}/{player.max_health}", True, (255, 255, 255))

        # Add a shadow effect to the text for better visibility
        health_text_shadow = font.render(f"{int(player.current_health)}/{player.max_health}", True, (0, 0, 0))

        # Position the text inside the health bar (centered)
        text_pos = (
            self.health_bar_pos[0] + (self.health_bar_width - health_text.get_width()) // 2,
            self.health_bar_pos[1] + self.health_bar_height + 5  # Position below the health bar
        )

        # Draw text shadow slightly offset
        surface.blit(health_text_shadow, (text_pos[0] + 1, text_pos[1] + 1))
        # Draw actual text
        surface.blit(health_text, text_pos)

        # Draw invincibility indicator with visual effects
        if player.invincibility_timer > 0:
            # Flash the text every few frames with a pulsing effect
            flash_alpha = int(155 + 100 * abs(math.sin(pygame.time.get_ticks() * 0.01)))

            try:
                invincible_font = pygame.font.Font("fonts/Poppins-Bold.ttf", 12)  # Smaller font size
            except:
                invincible_font = pygame.font.Font(None, 14)  # Smaller font size

            invincible_text = invincible_font.render("INVINCIBLE", True, (255, 255, 0))

            # Create a surface with per-pixel alpha for the pulsing effect
            invincible_surface = pygame.Surface(invincible_text.get_size(), pygame.SRCALPHA)
            invincible_surface.fill((255, 255, 0, flash_alpha))

            # Blit with blend mode for the glow effect
            invincible_text.blit(invincible_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            # Position the invincibility text below the health text
            invincible_pos = (
                self.health_bar_pos[0] + (self.health_bar_width - invincible_text.get_width()) // 2,
                self.health_bar_pos[1] + self.health_bar_height + 25  # Position below the health text
            )
            surface.blit(invincible_text, invincible_pos)
