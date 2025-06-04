"""
Scrollable components for the Edit Mode
"""
import pygame
from game_core.other_components.config import *
from game_core.other_components.font_loader import font_manager


class ScrollableTextArea:
    """A scrollable text area for displaying large amounts of text"""
    def __init__(self, x, y, width, height, font_size=FONT_SIZE_SMALL):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_surface = pygame.Surface((width, 8000), pygame.SRCALPHA)  # Larger surface for content
        self.content_surface.fill((245, 245, 245))  # Light gray background
        self.scroll_y = 0
        self.max_scroll = 0
        self.font = font_loader.get_font('light', font_size)
        self.header_font = font_loader.get_font('regular', font_size + 2)
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
