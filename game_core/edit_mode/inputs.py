"""
Input components for the Edit Mode
"""
import pygame
from game_core.core.config import *
from game_core.core.font_loader import font_manager


class TextInput:
    """Text input field for entering map name"""
    def __init__(self, x, y, width, height, font_size=FONT_SIZE_MEDIUM, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = "map1"  # Default text
        self.font = font_loader.get_font('regular', font_size)
        self.text_surf = self.font.render(self.text, True, (0, 0, 0))
        self.text_rect = self.text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        self.active = False
        self.max_length = max_length
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_speed = 500  # milliseconds

    def update(self, events):
        """Update text input based on events"""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle active state based on click
                self.active = self.rect.collidepoint(event.pos)

            if event.type == pygame.KEYDOWN and self.active:
                if event.key == pygame.K_BACKSPACE:
                    # Remove last character
                    self.text = self.text[:-1]
                elif event.key == pygame.K_RETURN:
                    # Deactivate on enter
                    self.active = False
                elif len(self.text) < self.max_length:
                    # Add character if not at max length
                    # Only allow alphanumeric characters and underscore
                    if event.unicode.isalnum() or event.unicode == '_':
                        self.text += event.unicode

                # Update text surface
                self.text_surf = self.font.render(self.text, True, (0, 0, 0))
                self.text_rect = self.text_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))

        # Update cursor blink
        self.cursor_timer += pygame.time.get_ticks() % 1000
        if self.cursor_timer >= self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        """Draw the text input on the given surface"""
        # Draw input background
        color = (220, 220, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(surface, color, self.rect)

        # Draw border
        border_color = (0, 120, 215) if self.active else (100, 100, 100)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw text
        surface.blit(self.text_surf, self.text_rect)

        # Draw cursor if active
        if self.active and self.cursor_visible:
            cursor_x = self.text_rect.right + 2
            cursor_y = self.text_rect.y
            cursor_height = self.text_rect.height
            pygame.draw.line(surface, (0, 0, 0), (cursor_x, cursor_y),
                            (cursor_x, cursor_y + cursor_height), 2)


class DropdownMenu:
    """Dropdown menu for selecting from a list of options"""
    def __init__(self, x, y, width, height, options=None, font_size=FONT_SIZE_MEDIUM):
        self.rect = pygame.Rect(x, y, width, height)
        self.options = options or []
        self.selected_option = None if not self.options else self.options[0]
        self.font = font_loader.get_font('regular', font_size)
        self.is_open = False
        self.is_hovered = False

        # Create text surfaces for options
        self.option_surfs = []
        self.option_rects = []
        self.update_option_surfaces()

        # Dropdown appearance
        self.bg_color = (200, 200, 200)
        self.hover_color = (220, 220, 255)
        self.border_color = (100, 100, 100)
        self.text_color = (0, 0, 0)
        self.option_height = 30

    @property
    def topleft(self):
        return self.rect.topleft

    @topleft.setter
    def topleft(self, value):
        """Update the dropdown position and recalculate option positions"""
        self.rect.topleft = value
        self.update_option_surfaces()

    def update_option_surfaces(self):
        """Update text surfaces for all options"""
        self.option_surfs = []
        self.option_rects = []

        for i, option in enumerate(self.options):
            text_surf = self.font.render(option, True, self.text_color)
            text_rect = text_surf.get_rect(
                midleft=(self.rect.x + 10, self.rect.y + self.option_height * (i + 1) + self.option_height // 2)
            )
            self.option_surfs.append(text_surf)
            self.option_rects.append(text_rect)

    def set_options(self, options):
        """Set the list of options"""
        self.options = options
        if self.options:
            self.selected_option = self.options[0]
        else:
            self.selected_option = None
        self.update_option_surfaces()

    def update(self, mouse_pos):
        """Update dropdown state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        # Update option positions to ensure they're aligned with the dropdown
        if self.is_open:
            self.update_option_surfaces()

        # Check if mouse is over an option when dropdown is open
        if self.is_open:
            for i in range(len(self.options)):
                option_rect_full = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.option_height * (i + 1),
                    self.rect.width,
                    self.option_height
                )
                if option_rect_full.collidepoint(mouse_pos):
                    return i  # Return the index of the hovered option

        return -1  # No option hovered

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for the dropdown"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if dropdown header is clicked
            if self.rect.collidepoint(mouse_pos):
                self.is_open = not self.is_open
                # Update option positions when opening the dropdown
                if self.is_open:
                    self.update_option_surfaces()
                return True

            # Check if an option is clicked when dropdown is open
            if self.is_open:
                for i, option in enumerate(self.options):
                    option_rect = pygame.Rect(
                        self.rect.x,
                        self.rect.y + self.option_height * (i + 1),
                        self.rect.width,
                        self.option_height
                    )
                    if option_rect.collidepoint(mouse_pos):
                        self.selected_option = option
                        self.is_open = False
                        return True

                # Close dropdown if clicked outside
                self.is_open = False

        return False

    def draw(self, surface):
        """Draw the dropdown menu"""
        # Draw dropdown header
        header_color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(surface, header_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Draw selected option text
        if self.selected_option:
            text_surf = self.font.render(self.selected_option, True, self.text_color)
            text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, self.rect.centery))
            surface.blit(text_surf, text_rect)

        # Draw dropdown arrow
        arrow_points = [
            (self.rect.right - 20, self.rect.centery - 5),
            (self.rect.right - 10, self.rect.centery - 5),
            (self.rect.right - 15, self.rect.centery + 5)
        ]
        pygame.draw.polygon(surface, self.text_color, arrow_points)

        # Draw dropdown options if open
        if self.is_open:
            # Update option positions to ensure they're aligned with the dropdown
            self.update_option_surfaces()

            for i in range(len(self.options)):
                # Draw option background
                option_rect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + self.option_height * (i + 1),
                    self.rect.width,
                    self.option_height
                )
                pygame.draw.rect(surface, self.bg_color, option_rect)
                pygame.draw.rect(surface, self.border_color, option_rect, 1)

                # Draw option text - center it in the option rect
                text_surf = self.option_surfs[i]
                text_rect = text_surf.get_rect(midleft=(self.rect.x + 10, option_rect.centery))
                surface.blit(text_surf, text_rect)
