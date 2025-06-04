"""
Settings screen module - contains the settings screen UI and logic
"""
import pygame
from game_core.other_components.config import *
from game_core.other_components.screen_base import BaseScreen
from edit_mode.ui_components import ScrollableTextArea

class SettingsScreen(BaseScreen):
    """Settings screen with back button"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

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

        # Settings screen title
        self.title_font = pygame.font.SysFont(None, 72)
        self.title_text = "Settings"
        self.title_surf = self.title_font.render(self.title_text, True, WHITE)
        self.title_rect = self.title_surf.get_rect(center=(self.width // 2, 100))

        # Create scrollable text area for how to play section
        self.how_to_play_area = ScrollableTextArea(
            self.width // 2 - 400,  # x position (centered)
            180,                    # y position (below title)
            800,                    # width
            450                     # height
        )

        # Set the how to play content
        self.how_to_play_area.set_text(self.get_how_to_play_instructions())

    def handle_event(self, event):
        """Handle events for the settings screen"""
        mouse_pos = pygame.mouse.get_pos()

        # Handle common events (back and reload buttons)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Handle scrollable text area events
        if self.how_to_play_area.handle_event(event, mouse_pos):
            return None

        # Handle settings-specific events here

        return None

    def update(self):
        """Update settings screen logic and animations"""
        # Update background position for scrolling effect
        self.bg_x -= self.bg_scroll_speed
        # Reset position when the first image is completely off-screen
        if self.bg_x <= -self.width:
            self.bg_x = 0

    def draw(self, surface):
        """Draw the settings screen"""
        # Draw scrolling background
        surface.blit(self.background, (int(self.bg_x), 0))
        surface.blit(self.background, (int(self.bg_x) + self.bg_width, 0))

        # Draw title
        surface.blit(self.title_surf, self.title_rect)

        # Draw "How to Play" section title
        font = pygame.font.SysFont(None, 48)
        how_to_play_title = font.render("How to Play", True, WHITE)
        how_to_play_title_rect = how_to_play_title.get_rect(
            center=(self.width//2, 150)
        )
        surface.blit(how_to_play_title, how_to_play_title_rect)

        # Draw scrollable text area with game instructions
        self.how_to_play_area.draw(surface)

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

        # Update title position
        self.title_rect = self.title_surf.get_rect(center=(self.width // 2, 100))

        # Update how to play area position and size
        self.how_to_play_area = ScrollableTextArea(
            self.width // 2 - 400,  # x position (centered)
            180,                    # y position (below title)
            800,                    # width
            450                     # height
        )
        self.how_to_play_area.set_text(self.get_how_to_play_instructions())

    def get_how_to_play_instructions(self):
        """Get the how to play instructions for the scrollable text area"""
        return [
            "Basic Controls",
            "- WASD or Arrow Keys: Move your character",
            "- E: Interact with objects and chests",
            "- I: Open inventory",
            "- ESC: Close menus or exit inventory",
            "",
            "Inventory Management",
            "- Left-click items to pick them up",
            "- Right-click on a stack to pick up one item at a time",
            "- Left-click to place all picked up items at once",
            "- Items of the same type will automatically stack",
            "- Press ESC to exit the inventory",
            "",
            "Chest Interaction",
            "- Press E near a chest to open it",
            "- Transfer items between your inventory and the chest",
            "- Right-click to pick up one item at a time from a stack",
            "- Left-click to place all picked up items at once",
            "- Press ESC to close the chest",
            "",
            "World Exploration",
            "- Explore different maps by finding teleportation points",
            "- Look for chests to find items",
            "- Maps are connected through teleportation points",
            "",
            "Edit Mode",
            "- Create your own maps with the Edit Mode",
            "- Place tiles to build your world",
            "- Use layers to organize your map elements",
            "- Set collision areas to define where players can walk",
            "- Connect maps with relation points",
            "- Save your maps as Main Maps or Related Maps",
            "- Main Maps appear in the selection screen",
            "- Related Maps are accessed through teleportation",
            "",
            "Edit Mode Controls",
            "- Left click/drag: Place tiles",
            "- Right click/drag: Remove tiles",
            "- Mouse wheel: Cycle through tiles",
            "- Arrow keys or WASD: Move view",
            "- Use tileset buttons to switch between tilesets",
            "",
            "Edit Mode Tips",
            "- Use layers to organize your map elements",
            "- Layer 0 is typically used for ground/floor tiles",
            "- Higher layers are for objects, walls, decorations",
            "- Use the onion skin feature to see how layers interact",
            "- Save frequently to avoid losing work",
            "- Create a main map first before creating related maps",
            "- Use descriptive names for your maps"
        ]
