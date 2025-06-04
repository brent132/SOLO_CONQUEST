"""UI button components for the Edit Mode."""

import pygame

from game_core.other_components.config import *
from game_core.other_components.font_loader import font_loader


class Button:
    """Generic button rendered purely with code."""

    def __init__(self, x, y, button_type, scale=1.0):
        text_lookup = {
            "add": "+",
            "browse_map": "Browse",
            "cancel": "Cancel",
            "delete": "Delete",
            "edit_mode": "Edit",
            "save": "Save",
        }

        self.text = text_lookup.get(button_type.lower(), button_type.title())

        font_size = int(FONT_SIZE_MEDIUM * scale)
        self.font = font_loader.get_font("medium", font_size)
        self.text_surf = self.font.render(self.text, True, (255, 255, 255))

        width = self.text_surf.get_width() + 20
        height = self.text_surf.get_height() + 10
        self.rect = pygame.Rect(x, y, width, height)
        self.text_rect = self.text_surf.get_rect(center=self.rect.center)

        self.bg_color = (80, 80, 80)
        self.hover_color = (110, 110, 110)
        self.border_color = (200, 200, 200)
        self.is_hovered = False
        self.image = None
        self.hover_image = None

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the button on the given surface"""
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
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
        self.font = font_loader.get_font('regular', font_size)
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
