"""
UI Components for the Edit Mode - buttons, text inputs, etc.
"""
import os
import pygame
from settings import *
from font_manager import font_manager





class Button:
    """Generic button for UI using custom PNG images"""
    def __init__(self, x, y, button_type, scale=1.0):
        # Map button type to image file
        button_images = {
            "edit_mode": "edit_mode/Buttons/Edit_Mode-Button.png",
            "browse_map": "edit_mode/Buttons/Browse_Map-Button.png",
            "save": "edit_mode/Buttons/Save-Button.png",
            "delete": "edit_mode/Buttons/Delete-Button.png",
            "cancel": "edit_mode/Buttons/Cancel-Button.png"
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

class TextInput:
    """Text input field for entering map name"""
    def __init__(self, x, y, width, height, font_size=FONT_SIZE_MEDIUM, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = "map1"  # Default text
        self.font = font_manager.get_font('regular', font_size)
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
        self.font = font_manager.get_font('regular', font_size)
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

class RelationGroup:
    """A group of A and B buttons with an ID"""
    def __init__(self, id_value, x, y, button_size=32, spacing=10):
        self.id = id_value
        self.button_size = button_size
        self.spacing = spacing
        self.y_position = y

        # Button A (Red)
        self.button_a_rect = pygame.Rect(x, y, button_size, button_size)
        self.button_a_color = (220, 60, 60)  # Red
        self.button_a_hover_color = (255, 100, 100)  # Lighter red
        self.button_a_selected = False
        self.button_a_hovered = False

        # Button B (Blue)
        self.button_b_rect = pygame.Rect(x + button_size + spacing, y, button_size, button_size)
        self.button_b_color = (60, 60, 220)  # Blue
        self.button_b_hover_color = (100, 100, 255)  # Lighter blue
        self.button_b_selected = False
        self.button_b_hovered = False

        # ID label
        self.id_font = pygame.font.SysFont(None, 20)
        self.id_label = self.id_font.render(f"ID: {self.id}", True, (50, 50, 50))
        self.id_rect = self.id_label.get_rect(topleft=(x, y + button_size + 5))

        # Track which button is active
        self.active_button = None  # 'a', 'b', or None

    def set_position(self, x, y):
        """Set the position of the group"""
        self.y_position = y
        self.button_a_rect.topleft = (x, y)
        self.button_b_rect.topleft = (x + self.button_size + self.spacing, y)
        self.id_rect = self.id_label.get_rect(topleft=(x, y + self.button_size + 5))

    def update(self, mouse_pos):
        """Update button states based on mouse position"""
        self.button_a_hovered = self.button_a_rect.collidepoint(mouse_pos)
        self.button_b_hovered = self.button_b_rect.collidepoint(mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for the group"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if button A was clicked
            if self.button_a_hovered:
                # Toggle selection state
                was_selected = self.button_a_selected
                self.button_a_selected = not was_selected

                if self.button_a_selected:
                    self.active_button = 'a'
                    # Deselect button B if A is selected
                    self.button_b_selected = False
                else:
                    # Only clear active_button if we're deselecting
                    if was_selected:
                        self.active_button = None
                return True

            # Check if button B was clicked
            elif self.button_b_hovered:
                # Toggle selection state
                was_selected = self.button_b_selected
                self.button_b_selected = not was_selected

                if self.button_b_selected:
                    self.active_button = 'b'
                    # Deselect button A if B is selected
                    self.button_a_selected = False
                else:
                    # Only clear active_button if we're deselecting
                    if was_selected:
                        self.active_button = None
                return True

        return False

    def draw(self, surface):
        """Draw the group on the surface"""
        # Draw button A
        a_color = self.button_a_hover_color if self.button_a_hovered else self.button_a_color
        pygame.draw.rect(surface, a_color, self.button_a_rect)

        # Draw button A border (thicker if selected)
        border_width_a = 3 if self.button_a_selected else 1
        pygame.draw.rect(surface, (0, 0, 0), self.button_a_rect, border_width_a)

        # Draw button B
        b_color = self.button_b_hover_color if self.button_b_hovered else self.button_b_color
        pygame.draw.rect(surface, b_color, self.button_b_rect)

        # Draw button B border (thicker if selected)
        border_width_b = 3 if self.button_b_selected else 1
        pygame.draw.rect(surface, (0, 0, 0), self.button_b_rect, border_width_b)

        # Draw labels on the buttons
        font = pygame.font.SysFont(None, 20)

        # Label for button A
        label_a = font.render("A", True, (255, 255, 255))
        label_a_rect = label_a.get_rect(center=self.button_a_rect.center)
        surface.blit(label_a, label_a_rect)

        # Label for button B
        label_b = font.render("B", True, (255, 255, 255))
        label_b_rect = label_b.get_rect(center=self.button_b_rect.center)
        surface.blit(label_b, label_b_rect)

        # Draw ID label
        surface.blit(self.id_label, self.id_rect)

    @property
    def is_active(self):
        """Check if any button is selected"""
        return self.button_a_selected or self.button_b_selected

    @property
    def height(self):
        """Get the total height of the group"""
        return self.button_size + 25  # Button height + spacing for ID label


class ScrollableTextArea:
    """A scrollable text area for displaying large amounts of text"""
    def __init__(self, x, y, width, height, font_size=FONT_SIZE_SMALL):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_surface = pygame.Surface((width, 8000), pygame.SRCALPHA)  # Larger surface for content
        self.content_surface.fill((245, 245, 245))  # Light gray background
        self.scroll_y = 0
        self.max_scroll = 0
        self.font = font_manager.get_font('light', font_size)
        self.header_font = font_manager.get_font('regular', font_size + 2)
        self.line_height = font_size
        self.scrollbar_width = 12  # Slightly wider scrollbar
        self.scrollbar_color = (180, 180, 180)
        self.scrollbar_hover_color = (150, 150, 150)
        self.scrollbar_bg_color = (220, 220, 220)
        self.background_color = (245, 245, 245)  # Light gray background
        self.border_color = (180, 180, 180)
        self.scrollbar_rect = pygame.Rect(
            self.rect.right - self.scrollbar_width,
            self.rect.y,
            self.scrollbar_width,
            self.rect.height
        )
        self.scrollbar_handle_rect = pygame.Rect(0, 0, self.scrollbar_width, 30)
        self.scrollbar_handle_rect.topleft = (self.scrollbar_rect.x, self.scrollbar_rect.y)
        self.is_scrollbar_dragging = False
        self.scrollbar_drag_start_y = 0
        self.scrollbar_drag_start_scroll = 0

        # Padding for text
        self.padding_x = 15  # Horizontal padding
        self.padding_y = 15  # Vertical padding

    def set_text(self, instructions):
        """Set the text content of the scrollable area"""
        # Clear the content surface
        self.content_surface.fill(self.background_color)

        # Calculate maximum text width to prevent overflow
        max_text_width = self.rect.width - self.padding_x * 2 - self.scrollbar_width - 10  # Extra 10px buffer

        # Draw text on the content surface
        y_pos = self.padding_y
        for instruction in instructions:
            if instruction == "":
                y_pos += 15  # Increased spacing for empty lines
                continue

            # Use header font for headers (lines without "-") and regular font for details
            if instruction.startswith("-"):
                # For bullet points, we need to handle wrapping manually
                text_color = (70, 70, 70)
                line_height = int(self.line_height * 1.3)  # Increased line height for details

                # Check if text is too long and needs wrapping
                text_surface = self.font.render(instruction, True, text_color)
                if text_surface.get_width() > max_text_width:
                    # Split the text into words
                    words = instruction.split()
                    lines = []
                    current_line = words[0]

                    # Group words into lines that fit within max_text_width
                    for word in words[1:]:
                        test_line = current_line + " " + word
                        test_surface = self.font.render(test_line, True, text_color)
                        if test_surface.get_width() <= max_text_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word

                    # Add the last line
                    lines.append(current_line)

                    # Draw each line
                    for i, line in enumerate(lines):
                        # First line keeps the bullet point, subsequent lines are indented
                        if i == 0:
                            text_surface = self.font.render(line, True, text_color)
                            self.content_surface.blit(text_surface, (self.padding_x, y_pos))
                        else:
                            # Indent wrapped lines for better readability
                            text_surface = self.font.render(line, True, text_color)
                            self.content_surface.blit(text_surface, (self.padding_x + 15, y_pos))

                        y_pos += line_height

                    # Subtract one line height since we'll add it again at the end of the loop
                    y_pos -= line_height
                else:
                    # Text fits on one line
                    self.content_surface.blit(text_surface, (self.padding_x, y_pos))

                y_pos_increment = line_height
            else:
                # For headers, we also need to handle wrapping
                text_color = (50, 50, 50)
                line_height = int(self.line_height * 1.5)  # Increased line height for headers

                # Add extra space before section headers (except the first one)
                if y_pos > self.padding_y + 10 and not instruction.startswith("-"):
                    y_pos += 15

                # Check if text is too long and needs wrapping
                text_surface = self.header_font.render(instruction, True, text_color)
                if text_surface.get_width() > max_text_width:
                    # Split the text into words
                    words = instruction.split()
                    lines = []
                    current_line = words[0]

                    # Group words into lines that fit within max_text_width
                    for word in words[1:]:
                        test_line = current_line + " " + word
                        test_surface = self.header_font.render(test_line, True, text_color)
                        if test_surface.get_width() <= max_text_width:
                            current_line = test_line
                        else:
                            lines.append(current_line)
                            current_line = word

                    # Add the last line
                    lines.append(current_line)

                    # Draw each line
                    for line in lines:
                        text_surface = self.header_font.render(line, True, text_color)
                        self.content_surface.blit(text_surface, (self.padding_x, y_pos))
                        y_pos += line_height

                    # Subtract one line height since we'll add it again at the end of the loop
                    y_pos -= line_height
                else:
                    # Text fits on one line
                    self.content_surface.blit(text_surface, (self.padding_x, y_pos))

                y_pos_increment = line_height

            y_pos += y_pos_increment

        # Update max scroll value based on content height
        self.max_scroll = max(0, y_pos - self.rect.height)

        # Update scrollbar handle size and position
        self._update_scrollbar_handle()

    def _update_scrollbar_handle(self):
        """Update the scrollbar handle size and position based on content"""
        if self.max_scroll <= 0:
            # No scrolling needed, hide scrollbar
            self.scrollbar_handle_rect.height = self.rect.height
        else:
            # Calculate handle height based on visible portion
            visible_ratio = min(1.0, self.rect.height / (self.rect.height + self.max_scroll))
            self.scrollbar_handle_rect.height = max(20, int(self.rect.height * visible_ratio))

            # Calculate handle position based on scroll position
            if self.max_scroll > 0:
                scroll_ratio = min(1.0, self.scroll_y / self.max_scroll)
                scroll_range = self.rect.height - self.scrollbar_handle_rect.height
                self.scrollbar_handle_rect.y = self.rect.y + int(scroll_ratio * scroll_range)
            else:
                self.scrollbar_handle_rect.y = self.rect.y

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for scrolling"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                # Check if clicking on scrollbar handle
                if self.scrollbar_handle_rect.collidepoint(mouse_pos):
                    self.is_scrollbar_dragging = True
                    self.scrollbar_drag_start_y = mouse_pos[1]
                    self.scrollbar_drag_start_scroll = self.scroll_y
                    return True
                # Check if clicking on scrollbar background
                elif self.scrollbar_rect.collidepoint(mouse_pos):
                    # Jump to clicked position
                    click_ratio = (mouse_pos[1] - self.rect.y) / self.rect.height
                    self.scroll_y = int(click_ratio * self.max_scroll)
                    self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
                    self._update_scrollbar_handle()
                    return True
                # Check if clicking in the text area
                elif self.rect.collidepoint(mouse_pos):
                    return True
            elif event.button == 4:  # Mouse wheel up
                if self.rect.collidepoint(mouse_pos) or self.scrollbar_rect.collidepoint(mouse_pos):
                    self.scroll_y = max(0, self.scroll_y - 20)
                    self._update_scrollbar_handle()
                    return True
            elif event.button == 5:  # Mouse wheel down
                if self.rect.collidepoint(mouse_pos) or self.scrollbar_rect.collidepoint(mouse_pos):
                    self.scroll_y = min(self.max_scroll, self.scroll_y + 20)
                    self._update_scrollbar_handle()
                    return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_scrollbar_dragging:
                self.is_scrollbar_dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.is_scrollbar_dragging:
                # Calculate scroll based on drag distance
                drag_distance = mouse_pos[1] - self.scrollbar_drag_start_y
                scroll_range = self.rect.height - self.scrollbar_handle_rect.height
                if scroll_range > 0:
                    scroll_ratio = drag_distance / scroll_range
                    self.scroll_y = self.scrollbar_drag_start_scroll + int(scroll_ratio * self.max_scroll)
                    self.scroll_y = max(0, min(self.max_scroll, self.scroll_y))
                    self._update_scrollbar_handle()
                return True
        return False

    def draw(self, surface):
        """Draw the scrollable text area with scrollbar"""
        # Draw background for the text area
        pygame.draw.rect(surface, self.background_color, self.rect)

        # Create a clipping rect to ensure content doesn't overflow
        original_clip = surface.get_clip()
        clip_rect = pygame.Rect(
            self.rect.x,
            self.rect.y,
            self.rect.width - self.scrollbar_width,
            self.rect.height
        )
        surface.set_clip(clip_rect)

        # Create a subsurface for the visible content area
        visible_rect = pygame.Rect(0, self.scroll_y, self.rect.width - self.scrollbar_width, self.rect.height)

        # Draw the visible content to the main surface
        surface.blit(self.content_surface, self.rect.topleft, visible_rect)

        # Restore original clipping rect
        surface.set_clip(original_clip)

        # Draw scrollbar background
        pygame.draw.rect(surface, self.scrollbar_bg_color, self.scrollbar_rect)

        # Draw scrollbar handle if needed
        if self.max_scroll > 0:
            # Determine scrollbar color based on hover/drag state
            scrollbar_color = self.scrollbar_hover_color if self.is_scrollbar_dragging else self.scrollbar_color
            pygame.draw.rect(surface, scrollbar_color, self.scrollbar_handle_rect)

            # Add rounded corners to scrollbar handle
            handle_radius = 3
            pygame.draw.rect(surface, scrollbar_color,
                pygame.Rect(self.scrollbar_handle_rect.x + handle_radius,
                           self.scrollbar_handle_rect.y,
                           self.scrollbar_handle_rect.width - 2 * handle_radius,
                           self.scrollbar_handle_rect.height))
            pygame.draw.rect(surface, scrollbar_color,
                pygame.Rect(self.scrollbar_handle_rect.x,
                           self.scrollbar_handle_rect.y + handle_radius,
                           self.scrollbar_handle_rect.width,
                           self.scrollbar_handle_rect.height - 2 * handle_radius))
            pygame.draw.circle(surface, scrollbar_color,
                              (self.scrollbar_handle_rect.x + handle_radius,
                               self.scrollbar_handle_rect.y + handle_radius),
                              handle_radius)
            pygame.draw.circle(surface, scrollbar_color,
                              (self.scrollbar_handle_rect.x + handle_radius,
                               self.scrollbar_handle_rect.y + self.scrollbar_handle_rect.height - handle_radius),
                              handle_radius)
            pygame.draw.circle(surface, scrollbar_color,
                              (self.scrollbar_handle_rect.x + self.scrollbar_handle_rect.width - handle_radius,
                               self.scrollbar_handle_rect.y + handle_radius),
                              handle_radius)
            pygame.draw.circle(surface, scrollbar_color,
                              (self.scrollbar_handle_rect.x + self.scrollbar_handle_rect.width - handle_radius,
                               self.scrollbar_handle_rect.y + self.scrollbar_handle_rect.height - handle_radius),
                              handle_radius)

        # Draw border around the text area
        pygame.draw.rect(surface, self.border_color, self.rect, 1)


class RelationComponent:
    """A component with multiple groups of A and B buttons for map relations"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.button_size = 32
        self.spacing = 10
        self.group_spacing = 60  # Vertical spacing between groups

        # Create the first group
        self.groups = [RelationGroup(1, x, y)]

        # Add and Delete buttons
        self.add_button = TextButton(x, y + 200, 80, 30, "Add")
        self.delete_button = TextButton(x + 90, y + 200, 80, 30, "Delete")

        # Currently selected group index
        self.selected_group_index = 0

    def update(self, mouse_pos):
        """Update all groups and buttons"""
        # Update all groups
        for group in self.groups:
            group.update(mouse_pos)

        # Update add and delete buttons
        self.add_button.update(mouse_pos)
        self.delete_button.update(mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Handle events for all groups and buttons"""
        # Check if any group was clicked
        for i, group in enumerate(self.groups):
            if group.handle_event(event, mouse_pos):
                # Deselect all other groups
                for j, other_group in enumerate(self.groups):
                    if j != i:
                        other_group.button_a_selected = False
                        other_group.button_b_selected = False
                        other_group.active_button = None

                # Set the selected group
                self.selected_group_index = i
                return True

        # Check if add button was clicked
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.add_button.is_clicked(event):
                # Add a new group with the next ID
                new_id = len(self.groups) + 1
                new_y = self.y + len(self.groups) * self.group_spacing
                self.groups.append(RelationGroup(new_id, self.x, new_y))

                # Reposition all groups
                self._reposition_groups()
                return True

            # Check if delete button was clicked
            elif self.delete_button.is_clicked(event) and len(self.groups) > 1:
                # Remove the last group
                self.groups.pop()

                # If the selected group was removed, select the last group
                if self.selected_group_index >= len(self.groups):
                    self.selected_group_index = len(self.groups) - 1

                # Reposition all groups
                self._reposition_groups()
                return True

        return False

    def _reposition_groups(self):
        """Reposition all groups based on their order"""
        for i, group in enumerate(self.groups):
            group.set_position(self.x, self.y + i * self.group_spacing)

    def set_button_positions(self, x, y, bottom_y=None):
        """Set the positions of all buttons"""
        self.x = x
        self.y = y

        # Reposition all groups
        self._reposition_groups()

        # Set add and delete button positions at the bottom if provided
        if bottom_y:
            self.add_button.topleft = (x, bottom_y - 40)
            self.delete_button.topleft = (x + 90, bottom_y - 40)

    def draw(self, surface):
        """Draw all groups and buttons"""
        # Draw all groups
        for group in self.groups:
            group.draw(surface)

        # Draw add and delete buttons
        self.add_button.draw(surface)
        self.delete_button.draw(surface)

    @property
    def is_active(self):
        """Check if any button in any group is selected"""
        return any(group.is_active for group in self.groups)

    @property
    def active_button(self):
        """Get the active button type ('a', 'b', or None)"""
        if self.selected_group_index < len(self.groups):
            return self.groups[self.selected_group_index].active_button
        return None

    @property
    def current_id(self):
        """Get the ID of the currently selected group"""
        if self.selected_group_index < len(self.groups):
            return self.groups[self.selected_group_index].id
        return 1

    def set_id(self, id_value):
        """Set the ID of the currently selected group (for backward compatibility)"""
        # This method is kept for backward compatibility
        # Find or create a group with the given ID
        for i, group in enumerate(self.groups):
            if group.id == id_value:
                self.selected_group_index = i
                return

        # If not found, create groups up to this ID
        while len(self.groups) < id_value:
            new_id = len(self.groups) + 1
            new_y = self.y + len(self.groups) * self.group_spacing
            self.groups.append(RelationGroup(new_id, self.x, new_y))

        # Reposition all groups
        self._reposition_groups()

        # Select the group with the given ID
        self.selected_group_index = id_value - 1