"""Simple scrollable text area widget for displaying instructions."""
import pygame
from game_core.other_components.config import WHITE, GRAY

class ScrollableTextArea:
    """Display scrollable lines of text within a rect."""

    def __init__(self, x, y, width, height, font_size=20, line_height=24):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.SysFont(None, font_size)
        self.line_height = line_height
        self.text_lines = []
        self.scroll_offset = 0

    def set_text(self, lines):
        """Set the text lines to display."""
        self.text_lines = list(lines)
        self.scroll_offset = 0

    def handle_event(self, event, mouse_pos):
        """Handle scrolling events."""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_offset -= event.y * self.line_height
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.scroll_offset += self.line_height
            elif event.key == pygame.K_DOWN:
                self.scroll_offset -= self.line_height
        max_offset = max(0, len(self.text_lines) * self.line_height - self.rect.height)
        if self.scroll_offset > 0:
            self.scroll_offset = 0
        elif -self.scroll_offset > max_offset:
            self.scroll_offset = -max_offset
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the text area with clipping."""
        previous_clip = surface.get_clip()
        surface.set_clip(self.rect)
        surface.fill(GRAY, self.rect)
        y = self.rect.y + self.scroll_offset
        for line in self.text_lines:
            text_surface = self.font.render(line, True, WHITE)
            surface.blit(text_surface, (self.rect.x + 5, y))
            y += self.line_height
        surface.set_clip(previous_clip)
        pygame.draw.rect(surface, WHITE, self.rect, 1)
