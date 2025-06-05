"""
Tab Manager - handles sidebar tabs for the edit mode
"""
import pygame

class TabManager:
    """Manages tabs for the sidebar in edit mode"""
    def __init__(self, map_area_width, sidebar_width):
        self.map_area_width = map_area_width
        self.sidebar_width = sidebar_width

        # Tab settings
        self.tab_height = 30
        self.tab_spacing = 5
        self.active_tab = "Collision"  # Default active tab after tileset removal

        # Define remaining tabs (Tiles tab removed)
        self.tabs = ["Collision", "Relations", "Save", "Help"]
        self.tab_buttons = {}

        # Create tab buttons
        self.create_tabs()

        # Font for tab labels
        self.font = pygame.font.SysFont(None, 20)

        # Show tips flag
        self.show_tips = False

    def create_tabs(self):
        """Create tab buttons"""
        tab_width = (self.sidebar_width - (len(self.tabs) + 1) * self.tab_spacing) // len(self.tabs)

        for i, tab_name in enumerate(self.tabs):
            x = self.map_area_width + self.tab_spacing + i * (tab_width + self.tab_spacing)
            y = 45  # Position directly below the mode buttons

            self.tab_buttons[tab_name] = pygame.Rect(x, y, tab_width, self.tab_height)

    def is_tab_click(self, mouse_pos):
        """Check if the mouse position is over any tab button"""
        for tab_rect in self.tab_buttons.values():
            if tab_rect.collidepoint(mouse_pos):
                return True
        return False

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for tabs"""
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        # Check tab clicks
        for tab_name, tab_rect in self.tab_buttons.items():
            if tab_rect.collidepoint(mouse_pos):
                self.active_tab = tab_name

                # Toggle tips if Help tab is clicked
                if tab_name == "Help":
                    self.show_tips = not self.show_tips

                return True

        return False

    def draw(self, surface):
        """Draw the tabs"""
        # Draw tab buttons
        for tab_name, tab_rect in self.tab_buttons.items():
            # Determine tab color based on active state
            if tab_name == self.active_tab:
                bg_color = (180, 200, 255)  # Blue for active tab
                text_color = (0, 0, 0)
            else:
                bg_color = (220, 220, 220)  # Light gray for inactive tabs
                text_color = (100, 100, 100)

            # Draw tab background
            pygame.draw.rect(surface, bg_color, tab_rect)
            pygame.draw.rect(surface, (100, 100, 100), tab_rect, 1)

            # Draw tab label
            text = self.font.render(tab_name, True, text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            surface.blit(text, text_rect)
