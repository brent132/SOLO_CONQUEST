"""
Base Screen - provides common functionality for all game screens
"""
import pygame

class BackButton:
    """Back button for returning to the main menu"""
    def __init__(self, x, y, scale=1.0):
        # Load the button image
        self.image_path = "Menu Assets/Back-Button.png"
        original_image = pygame.image.load(self.image_path).convert_alpha()

        # Scale the image if needed
        if scale != 1.0:
            new_width = int(original_image.get_width() * scale)
            new_height = int(original_image.get_height() * scale)
            self.image = pygame.transform.scale(original_image, (new_width, new_height))
        else:
            self.image = original_image

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.is_hovered = False

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

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the button on the given surface"""
        if self.is_hovered:
            surface.blit(self.hover_image, self.rect)
        else:
            surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        """Check if button was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class BaseScreen:
    """Base class for all game screens with common functionality"""
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Create back button in top left corner
        self.back_button = BackButton(20, 20, scale=0.8)

    def handle_common_events(self, event, mouse_pos):
        """Handle events common to all screens (back button)"""
        # Update back button
        self.back_button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button was clicked
            if self.back_button.is_clicked(event):
                return "back"

        return None

    def draw_common_elements(self, surface):
        """Draw elements common to all screens (back button)"""
        self.back_button.draw(surface)

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        self.width = new_width
        self.height = new_height
