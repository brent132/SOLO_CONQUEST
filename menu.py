"""
Menu module - contains menu-related classes including splash screen
"""
import pygame
import math
from settings import *
from font_manager import font_manager
from base_screen import BaseScreen

class Button:
    """Interactive button class for menus using custom PNG images"""
    def __init__(self, x, y, image_path, scale=1.0):
        # Load the button image
        original_image = pygame.image.load(image_path).convert_alpha()

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

class SplashScreen(BaseScreen):
    """Splash screen with Menu Assets"""
    def __init__(self, screen_width, screen_height):
        # Initialize the base screen
        super().__init__(screen_width, screen_height)
        self.active = True

        # ===== BACKGROUND ANIMATION SETTINGS - EDIT THESE VALUES TO CUSTOMIZE =====
        # Load background image
        self.background_path = "Menu Assets/Menu-Background.png"
        self.background = pygame.image.load(self.background_path).convert_alpha()
        # Make background wider for scrolling effect (2x width)
        self.bg_width = self.width * 2
        self.bg_height = self.height
        self.background = pygame.transform.scale(self.background, (self.bg_width, self.bg_height))
        # Background animation variables
        self.bg_x = 0  # Starting x position
        self.bg_scroll_speed = 0.2  # Pixels per frame - lower = slower, smoother scrolling
        # ===== END BACKGROUND ANIMATION SETTINGS ====

        # Button configuration
        self.button_paths = {
            'start': "Menu Assets/Start-Button.png",
            'settings': "Menu Assets/Settings-Button.png",
            'edit': "Menu Assets/Edit-Button.png",
            'exit': "Menu Assets/Exit-Button.png"
        }

        # Button scaling factor (adjust this to change button size)
        button_scale = 1.0  # 0.5 = half size, 1.0 = original size, 2.0 = double size

        # Load button dimensions from the first image to calculate spacing
        temp_img = pygame.image.load(self.button_paths['start'])
        original_width = temp_img.get_width()
        original_height = temp_img.get_height()
        button_width = int(original_width * button_scale)
        button_height = int(original_height * button_scale)
        button_spacing = 20

        # ===== TITLE ANIMATION SETTINGS - EDIT THESE VALUES TO CUSTOMIZE =====
        # Load game title image
        self.title_path = "Menu Assets/Game-Title.png"
        self.title_image = pygame.image.load(self.title_path).convert_alpha()

        # Title size
        title_scale = 1.0  # Adjust this to change title size
        title_width = int(self.title_image.get_width() * title_scale)
        title_height = int(self.title_image.get_height() * title_scale)
        self.title_image = pygame.transform.scale(self.title_image, (title_width, title_height))

        # Title "floating" animation (up and down movement)
        # ===== EDIT THESE VALUES TO CHANGE THE TITLE MOVEMENT =====
        self.title_float_speed = 5.0  # Speed of floating - VERY low for ultra-smooth movement
        self.title_float_range = 5.0  # Pixels to move up and down - smaller for smoother transitions
        self.title_float_offset = 0  # Current offset
        # ===== END TITLE ANIMATION SETTINGS =====

        self.title_rect = self.title_image.get_rect()
        # ===== END TITLE ANIMATION SETTINGS =====

        # Position buttons and title
        title_y = self.height // 4 - self.title_rect.height // 2
        start_y = self.height // 2 - 50  # Adjust this to position the first button

        # Center title
        self.title_rect.centerx = self.width // 2
        self.title_rect.y = title_y

        # Create buttons
        center_x = self.width // 2 - button_width // 2
        self.buttons = {
            'start': Button(center_x, start_y, self.button_paths['start'], button_scale),
            'settings': Button(center_x, start_y + button_height + button_spacing,
                              self.button_paths['settings'], button_scale),
            'edit': Button(center_x, start_y + (button_height + button_spacing) * 2,
                          self.button_paths['edit'], button_scale),
            'exit': Button(center_x, start_y + (button_height + button_spacing) * 3,
                          self.button_paths['exit'], button_scale)
        }

    def handle_event(self, event):
        """Handle events for the splash screen"""
        mouse_pos = pygame.mouse.get_pos()

        # Handle common events (back and reload buttons)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Update all buttons
        for button in self.buttons.values():
            button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.buttons['start'].is_clicked(event):
                from debug_utils import debug_manager
                debug_manager.log("Start Game clicked", "menu")
                self.active = False  # Exit splash screen
                return "start"

            elif self.buttons['settings'].is_clicked(event):
                from debug_utils import debug_manager
                debug_manager.log("Settings clicked", "menu")
                return "settings"

            elif self.buttons['edit'].is_clicked(event):
                from debug_utils import debug_manager
                debug_manager.log("Edit Mode clicked", "menu")
                return "edit"

            elif self.buttons['exit'].is_clicked(event):
                from debug_utils import debug_manager
                debug_manager.log("Exit clicked", "menu")
                return "exit"

        return None

    def update(self):
        """Update splash screen logic and animations"""
        # ===== BACKGROUND SCROLLING ANIMATION =====
        # Update background position for scrolling effect
        self.bg_x -= self.bg_scroll_speed
        # Reset position when the first image is completely off-screen
        if self.bg_x <= -self.width:
            self.bg_x = 0

        # ===== TITLE FLOATING ANIMATION =====
        # Update title position for up and down floating effect - using precise floating point values
        # This creates a much smoother animation by allowing for sub-pixel movements
        self.title_float_offset = math.sin(pygame.time.get_ticks() * 0.001 * self.title_float_speed) * self.title_float_range

    def draw(self, surface):
        """Draw the splash screen with animations"""
        # ===== DRAW SCROLLING BACKGROUND =====
        # Draw background image twice side by side for seamless scrolling
        surface.blit(self.background, (int(self.bg_x), 0))
        surface.blit(self.background, (int(self.bg_x) + self.bg_width, 0))

        # ===== DRAW ANIMATED TITLE =====
        # Apply floating animation to title position - using exact floating point values
        # This allows for smoother sub-pixel rendering
        title_pos = self.title_rect.copy()
        # Store the exact position with floating point precision
        exact_y = title_pos.y + self.title_float_offset
        # Only convert to int at the last moment for actual drawing
        title_pos.y = int(exact_y)
        surface.blit(self.title_image, title_pos)

        # ===== DRAW BUTTONS =====
        # Draw all buttons
        for button in self.buttons.values():
            button.draw(surface)

        # Draw common elements (back and reload buttons)
        self.draw_common_elements(surface)

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Call the base class resize method
        super().resize(new_width, new_height)

        # Resize background image for scrolling
        self.bg_width = self.width * 2
        self.bg_height = self.height
        self.background = pygame.image.load(self.background_path).convert_alpha()
        self.background = pygame.transform.scale(self.background, (self.bg_width, self.bg_height))

        # Get button dimensions from the first button
        button_width = self.buttons['start'].rect.width
        button_height = self.buttons['start'].rect.height
        button_spacing = 20

        # Recalculate positions
        title_y = self.height // 4 - self.title_rect.height // 2
        start_y = self.height // 2 - 50

        # Center buttons horizontally
        center_x = self.width // 2 - button_width // 2

        # Update button positions
        self.buttons['start'].rect.topleft = (center_x, start_y)
        self.buttons['settings'].rect.topleft = (center_x, start_y + button_height + button_spacing)
        self.buttons['edit'].rect.topleft = (center_x, start_y + (button_height + button_spacing) * 2)
        self.buttons['exit'].rect.topleft = (center_x, start_y + (button_height + button_spacing) * 3)

        # Update title position
        self.title_rect.centerx = self.width // 2
        self.title_rect.y = title_y
