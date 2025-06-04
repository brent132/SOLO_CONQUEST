"""
Game Over Screen - displays when the player dies
"""
import pygame
from base_screen import BaseScreen
from menu import Button
from settings import *

class GameOverScreen(BaseScreen):
    """Game over screen with restart and exit buttons"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

        # Set up semi-transparent overlay
        self.overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Black with 70% opacity

        # Set up game over text
        try:
            self.title_font = pygame.font.Font("fonts/Poppins-Bold.ttf", 48)
        except:
            self.title_font = pygame.font.Font(None, 64)

        self.title_text = self.title_font.render("GAME OVER", True, (255, 50, 50))
        self.title_rect = self.title_text.get_rect(center=(width // 2, height // 3))

        # Button scaling factor
        button_scale = 1.0

        # Button positions
        button_spacing = 30
        restart_y = height // 2
        exit_y = restart_y + button_spacing + 50
        center_x = width // 2 - 60  # Default center position

        # Try to use image buttons if available
        try:
            # Button paths
            self.button_paths = {
                'restart': "Menu Assets/Restart-Button.png",
                'exit': "Menu Assets/Exit-Button.png"
            }

            # Load button dimensions from the first image to calculate spacing
            temp_img = pygame.image.load(self.button_paths['restart'])
            button_width = int(temp_img.get_width() * button_scale)
            center_x = width // 2 - button_width // 2

            # Create image buttons
            self.buttons = {
                'restart': Button(center_x, restart_y, self.button_paths['restart'], button_scale),
                'exit': Button(center_x, exit_y, self.button_paths['exit'], button_scale)
            }
            self.using_image_buttons = True
        except:
            # Fallback to text buttons if images can't be loaded
            self.using_image_buttons = False

            # Create text buttons
            try:
                button_font = pygame.font.Font("fonts/Poppins-Bold.ttf", 24)
            except:
                button_font = pygame.font.Font(None, 32)

            # Create text surfaces for buttons
            restart_text = button_font.render("RESTART", True, (255, 255, 255))
            exit_text = button_font.render("EXIT", True, (255, 255, 255))

            # Button dimensions
            button_width = 200
            button_height = 50

            # Create button rectangles
            restart_rect = pygame.Rect(width // 2 - button_width // 2, restart_y, button_width, button_height)
            exit_rect = pygame.Rect(width // 2 - button_width // 2, exit_y, button_width, button_height)

            # Store button data
            self.text_buttons = {
                'restart': {
                    'rect': restart_rect,
                    'text': restart_text,
                    'text_rect': restart_text.get_rect(center=restart_rect.center),
                    'hovered': False
                },
                'exit': {
                    'rect': exit_rect,
                    'text': exit_text,
                    'text_rect': exit_text.get_rect(center=exit_rect.center),
                    'hovered': False
                }
            }

        # No pulsing effect for game over text

    def handle_event(self, event):
        """Handle events for the game over screen"""
        mouse_pos = pygame.mouse.get_pos()

        if self.using_image_buttons:
            # Update all image buttons
            for button in self.buttons.values():
                button.update(mouse_pos)

            # Check for button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons['restart'].is_clicked(event):
                    return "restart"
                elif self.buttons['exit'].is_clicked(event):
                    return "exit"
        else:
            # Update text button hover states
            for button_name, button_data in self.text_buttons.items():
                button_data['hovered'] = button_data['rect'].collidepoint(mouse_pos)

            # Check for text button clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.text_buttons['restart']['rect'].collidepoint(mouse_pos):
                    return "restart"
                elif self.text_buttons['exit']['rect'].collidepoint(mouse_pos):
                    return "exit"

        return None

    def update(self):
        """Update game over screen animations"""
        # No animations to update

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Call the base class resize method
        super().resize(new_width, new_height)

        # Resize overlay
        self.overlay = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Black with 70% opacity

        # Update title position
        self.title_rect = self.title_text.get_rect(center=(new_width // 2, new_height // 3))

        # Update button positions
        if self.using_image_buttons:
            # Button positions
            button_spacing = 30
            restart_y = new_height // 2
            exit_y = restart_y + button_spacing + 50

            # Get button width
            button_width = self.buttons['restart'].rect.width
            center_x = new_width // 2 - button_width // 2

            # Update button positions
            self.buttons['restart'].rect.topleft = (center_x, restart_y)
            self.buttons['exit'].rect.topleft = (center_x, exit_y)
        else:
            # Update text button positions
            button_width = 200
            button_height = 50
            button_spacing = 30
            restart_y = new_height // 2
            exit_y = restart_y + button_spacing + 50

            # Create button rectangles
            self.text_buttons['restart']['rect'] = pygame.Rect(new_width // 2 - button_width // 2, restart_y, button_width, button_height)
            self.text_buttons['exit']['rect'] = pygame.Rect(new_width // 2 - button_width // 2, exit_y, button_width, button_height)

            # Update text positions
            self.text_buttons['restart']['text_rect'] = self.text_buttons['restart']['text'].get_rect(center=self.text_buttons['restart']['rect'].center)
            self.text_buttons['exit']['text_rect'] = self.text_buttons['exit']['text'].get_rect(center=self.text_buttons['exit']['rect'].center)

    def draw(self, surface):
        """Draw the game over screen"""
        # Draw semi-transparent overlay
        surface.blit(self.overlay, (0, 0))

        # Draw game over text (no pulsing)
        surface.blit(self.title_text, self.title_rect)

        # Draw buttons
        if self.using_image_buttons:
            # Draw image buttons
            for button in self.buttons.values():
                button.draw(surface)
        else:
            # Draw text buttons
            for button_name, button_data in self.text_buttons.items():
                # Draw button background
                button_color = (100, 100, 200) if button_data['hovered'] else (50, 50, 150)
                # Use try-except to handle different pygame versions
                try:
                    # For newer pygame versions
                    pygame.draw.rect(surface, button_color, button_data['rect'], border_radius=10)
                    pygame.draw.rect(surface, (200, 200, 255), button_data['rect'], width=2, border_radius=10)
                except TypeError:
                    # For older pygame versions
                    pygame.draw.rect(surface, button_color, button_data['rect'])
                    pygame.draw.rect(surface, (200, 200, 255), button_data['rect'], 2)

                # Draw button text
                surface.blit(button_data['text'], button_data['text_rect'])
