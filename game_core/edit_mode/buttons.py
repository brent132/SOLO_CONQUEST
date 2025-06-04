"""
Button components for the Edit Mode
"""
import os
import pygame
from game_settings import *
from font_manager import font_manager


class Button:
    """Generic button for UI using custom PNG images"""
    def __init__(self, x, y, button_type, scale=1.0):
        # Map button type to image file
        button_images = {
            "edit_mode": "game_core/edit_mode/Buttons/Edit_Mode-Button.png",
            "browse_map": "game_core/edit_mode/Buttons/Browse_Map-Button.png",
            "save": "game_core/edit_mode/Buttons/Save-Button.png",
            "delete": "game_core/edit_mode/Buttons/Delete-Button.png",
            "cancel": "game_core/edit_mode/Buttons/Cancel-Button.png"
        }

        # Default to a generic button if type not found
        image_path = button_images.get(button_type.lower(), None)

        if image_path and os.path.exists(image_path):
            # Load the button image
            original_image = pygame.image.load(image_path).convert_alpha()

            # Scale the image if needed
            if scale != 1.0:
                # Get original dimensions
                original_width = original_image.get_width()
                original_height = original_image.get_height()

                # Maintain aspect ratio when scaling
                new_width = int(original_width * scale)
                new_height = int(original_height * scale)

                # Use smooth scaling for better quality
                self.image = pygame.transform.smoothscale(original_image, (new_width, new_height))
            else:
                self.image = original_image

            self.rect = self.image.get_rect()
            self.rect.topleft = (x, y)

            # Create a slightly brighter version for hover effect
            self.hover_image = self.image.copy()
            # Apply a brightness effect to the hover image
            brightness = 30  # Brightness increase value
            for i in range(self.hover_image.get_width()):
                for j in range(self.hover_image.get_height()):
                    color = self.hover_image.get_at((i, j))
                    # Only brighten if not transparent
                    if color.a > 0:
                        r = min(color.r + brightness, 255)
                        g = min(color.g + brightness, 255)
                        b = min(color.b + brightness, 255)
                        self.hover_image.set_at((i, j), pygame.Color(r, g, b, color.a))
        else:
            # Fallback to a basic button if image not found
            self.rect = pygame.Rect(x, y, 120, 40)
            self.text = button_type
            self.font = font_manager.get_font('medium', FONT_SIZE_MEDIUM)
            self.text_surf = self.font.render(self.text, True, (255, 255, 255))
            self.text_rect = self.text_surf.get_rect(center=self.rect.center)
            self.bg_color = (100, 100, 100)
            self.hover_color = (120, 120, 120)
            self.image = None
            self.hover_image = None

        self.is_hovered = False

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the button on the given surface"""
        if self.image and self.hover_image:
            # Draw image-based button
            if self.is_hovered:
                surface.blit(self.hover_image, self.rect)
            else:
                surface.blit(self.image, self.rect)
        else:
            # Draw fallback button
            color = self.hover_color if self.is_hovered else self.bg_color
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
            surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class SaveButton(Button):
    """Button for saving the map"""
    def __init__(self, x, y):
        super().__init__(x, y, "save", scale=0.8)


class TextButton:
    """Simple text button with a rectangular background"""
    def __init__(self, x, y, width, height, text, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font_manager.get_font('regular', font_size)
        self.text_surf = self.font.render(text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)
        self.is_hovered = False
        self.is_selected = False
        self.bg_color = (200, 200, 200)
        self.hover_color = (220, 220, 255)
        self.selected_color = (180, 200, 255)
        self.border_color = (100, 100, 100)
        self.selected_border_color = (0, 120, 215)

    @property
    def topleft(self):
        return self.rect.topleft

    @topleft.setter
    def topleft(self, value):
        """Update the button position and recenter the text"""
        self.rect.topleft = value
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        # Update text position to ensure it stays centered
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

    def draw(self, surface):
        """Draw the button on the given surface"""
        # Determine background color
        if self.is_selected:
            bg_color = self.selected_color
            border_color = self.selected_border_color
        elif self.is_hovered:
            bg_color = self.hover_color
            border_color = self.selected_border_color
        else:
            bg_color = self.bg_color
            border_color = self.border_color

        # Draw button background
        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw text
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class TileButton:
    """Button for selecting a tile from the tileset"""
    def __init__(self, x, y, width, height, tile_image):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = tile_image
        self.is_hovered = False
        self.is_selected = False

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the tile button"""
        # Draw tile image
        surface.blit(self.image, self.rect)

        # Draw border (thicker if selected)
        border_color = (255, 255, 0) if self.is_selected else (200, 200, 200)
        border_width = 3 if self.is_selected else 1
        if self.is_hovered:
            border_color = (255, 150, 0)  # Orange when hovered

        pygame.draw.rect(surface, border_color, self.rect, border_width)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False
