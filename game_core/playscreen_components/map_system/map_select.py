"""
World Selection Screen - allows the player to select a world to play
"""
import os
import json
import pygame
from screen_base import BaseScreen
from .world_manager import WorldManager

class WorldItem:
    """Button-like item for a world in the selection screen"""
    def __init__(self, x, y, width, height, world_data, font_size=28):
        self.rect = pygame.Rect(x, y, width, height)
        self.folder_name = world_data["folder_name"]
        self.display_name = world_data.get("display_name", self.folder_name)
        self.description = world_data.get("description", "")

        # For backward compatibility
        self.map_name = self.folder_name

        # Create fonts
        self.title_font = pygame.font.SysFont(None, font_size)
        self.desc_font = pygame.font.SysFont(None, font_size - 8)

        # Create text surfaces (positioned without icon space)
        self.title_surf = self.title_font.render(self.display_name, True, (0, 0, 0))
        self.title_rect = self.title_surf.get_rect(topleft=(self.rect.x + 20, self.rect.y + 15))

        # Create description text (limited to one line)
        max_desc_width = width - 40  # Leave space for margins (no icon space needed)
        desc_text = self.description
        self.desc_surf = self.desc_font.render(desc_text, True, (80, 80, 80))
        if self.desc_surf.get_width() > max_desc_width:
            # Truncate description if too long
            while self.desc_surf.get_width() > max_desc_width and len(desc_text) > 3:
                desc_text = desc_text[:-4] + "..."
                self.desc_surf = self.desc_font.render(desc_text, True, (80, 80, 80))

        self.desc_rect = self.desc_surf.get_rect(topleft=(self.rect.x + 20, self.rect.y + 40))

        # State
        self.is_hovered = False
        self.is_selected = False

        # Icon removed - no longer used

        # Count maps in this folder
        import os
        maps_dir = "Maps"
        folder_path = os.path.join(maps_dir, self.folder_name)
        self.map_count = 0

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".json"):
                    self.map_count += 1

        # Create map count text
        self.info_text = f"{self.map_count} map{'s' if self.map_count != 1 else ''}"
        self.info_surf = self.desc_font.render(self.info_text, True, (80, 80, 80))
        self.info_rect = self.info_surf.get_rect(bottomright=(self.rect.right - 20, self.rect.bottom - 10))

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the world item"""
        # Draw background
        if self.is_selected:
            color = (180, 200, 255)  # Blue when selected
        elif self.is_hovered:
            color = (220, 220, 220)  # Light gray when hovered
        else:
            color = (240, 240, 240)  # Very light gray normally
        pygame.draw.rect(surface, color, self.rect)

        # Draw border
        border_color = (100, 150, 255) if self.is_selected else (200, 200, 200)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # World icon removed - no longer displayed

        # Draw title and description
        surface.blit(self.title_surf, self.title_rect)
        surface.blit(self.desc_surf, self.desc_rect)

        # Draw map count
        surface.blit(self.info_surf, self.info_rect)

    def is_clicked(self, event):
        """Check if item was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            return self.rect.collidepoint(mouse_pos)
        return False

class CustomPlayButton:
    """Custom play button using the Play-Button.png from Menu Assets"""
    def __init__(self, x, y, scale=1.0):
        # Load the button image
        self.image_path = "Menu Assets/Play-Button.png"
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
            mouse_pos = pygame.mouse.get_pos()
            return self.rect.collidepoint(mouse_pos)
        return False

class WorldSelectScreen(BaseScreen):
    """Screen for selecting a world to play"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

        # Background settings
        self.bg_image = pygame.image.load("Menu Assets/menu-background.png").convert()
        self.bg_image = pygame.transform.scale(self.bg_image, (width, height))

        # Create custom play button using the Play-Button.png from Menu Assets
        # Load the image first to get its dimensions for proper centering
        play_button_image = pygame.image.load("Menu Assets/Play-Button.png")
        button_width = play_button_image.get_width()
        # Center the button horizontally
        self.play_button = self.create_custom_play_button(width // 2 - button_width // 2, height - 80)

        # Initialize world manager
        self.world_manager = WorldManager()

        # World items
        self.world_items = []
        self.selected_world = None

        # Debug flag to track if we've tried to select the first world
        self.auto_selected_first_world = False

        # Status message
        self.status_message = ""
        self.status_timer = 0

        # Load world list
        self.refresh_world_list()

    def create_custom_play_button(self, x, y, scale=1.0):
        """Create a custom play button using the Play-Button.png"""
        return CustomPlayButton(x, y, scale)

    def refresh_world_list(self):
        """Refresh the list of available worlds"""
        self.world_items = []

        # Force the world manager to reload worlds from disk
        # This will detect any deleted map folders and remove them from the world list
        self.world_manager.load_worlds()

        # Get all worlds from the world manager
        worlds = self.world_manager.get_all_worlds()

        # Sort worlds alphabetically by display name
        worlds.sort(key=lambda w: w.get("display_name", w.get("folder_name", "")))

        # Create world items
        item_height = 80
        spacing = 15
        start_x = self.width // 6
        start_y = 100
        item_width = self.width * 2 // 3

        for i, world_data in enumerate(worlds):
            y = start_y + i * (item_height + spacing)
            # Create a world item
            world_item = WorldItem(start_x, y, item_width, item_height, world_data)
            self.world_items.append(world_item)

        # Auto-select the first world if there's only one available
        if len(self.world_items) == 1 and not self.auto_selected_first_world:
            self.world_items[0].is_selected = True
            self.selected_world = self.world_items[0].folder_name
            self.auto_selected_first_world = True

    def handle_event(self, event):
        """Handle events for the world selection screen"""
        mouse_pos = pygame.mouse.get_pos()

        # Handle common events (back and reload buttons)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Update play button
        self.play_button.update(mouse_pos)

        # Update world items
        for item in self.world_items:
            item.update(mouse_pos)

        # Check for play button click
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.play_button.is_clicked(event):
                if self.selected_world:
                    # The selected_world is a folder name
                    folder_name = self.selected_world

                    # Check if there's a player_location.json file in SaveData folder
                    player_location_path = "SaveData/player_location.json"
                    if os.path.exists(player_location_path):
                        try:
                            with open(player_location_path, 'r') as f:
                                player_location_data = json.load(f)

                            # Check if this is the new format with multiple worlds
                            if isinstance(player_location_data, dict) and "worlds" in player_location_data:
                                # Check if we have location data for this world
                                if folder_name in player_location_data["worlds"]:
                                    # Use the specific map from the world's location data
                                    world_location = player_location_data["worlds"][folder_name]
                                    map_name = world_location.get("map_name", folder_name)

                                    # Update current_world in player_location
                                    player_location_data["current_world"] = folder_name

                                    # Save the updated player_location
                                    with open(player_location_path, 'w') as f:
                                        json.dump(player_location_data, f, indent=2)

                                    return {"action": "play", "map": map_name}
                            # Handle old format (backward compatibility)
                            else:
                                # Check if the player was last in this folder
                                if player_location_data.get("folder_name") == folder_name:
                                    # Use the specific map from player_location
                                    map_name = player_location_data.get("map_name", folder_name)

                                    # Update player_location with the selected folder
                                    player_location_data["folder_name"] = folder_name

                                    # Save the updated player_location
                                    with open(player_location_path, 'w') as f:
                                        json.dump(player_location_data, f, indent=2)

                                    return {"action": "play", "map": map_name}
                        except Exception as e:
                            self.status_message = f"Error reading player location data: {str(e)}"
                            self.status_timer = 180

                    # If no player_location or player wasn't in this folder,
                    # use the default map (same name as folder)
                    return {"action": "play", "map": folder_name}

            # Check world item clicks
            for item in self.world_items:
                if item.is_clicked(event):
                    # Deselect all items
                    for other_item in self.world_items:
                        other_item.is_selected = False

                    # Select this item
                    item.is_selected = True
                    self.selected_world = item.folder_name

        return None

    def update(self):
        """Update world selection screen logic"""
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= 1

    def draw(self, surface):
        """Draw the world selection screen"""
        # Draw background
        surface.blit(self.bg_image, (0, 0))

        # Draw title
        font = pygame.font.SysFont(None, 48)
        title = font.render("Choose Your World", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width // 2, 50))
        surface.blit(title, title_rect)

        # Check if there are any worlds available
        if not self.world_items:
            # No worlds available - show helpful message
            message_font = pygame.font.SysFont(None, 36)
            instruction_font = pygame.font.SysFont(None, 28)

            # Main message
            no_worlds_text = message_font.render("No maps found!", True, (255, 255, 255))
            no_worlds_rect = no_worlds_text.get_rect(center=(self.width // 2, self.height // 2 - 60))
            surface.blit(no_worlds_text, no_worlds_rect)

            # Instructions
            instruction1 = instruction_font.render("Create your first map using the Map Editor:", True, (200, 200, 200))
            instruction1_rect = instruction1.get_rect(center=(self.width // 2, self.height // 2 - 10))
            surface.blit(instruction1, instruction1_rect)

            instruction2 = instruction_font.render("Run: python editor_app.py", True, (150, 200, 255))
            instruction2_rect = instruction2.get_rect(center=(self.width // 2, self.height // 2 + 20))
            surface.blit(instruction2, instruction2_rect)

            instruction3 = instruction_font.render("Then return here to play your maps!", True, (200, 200, 200))
            instruction3_rect = instruction3.get_rect(center=(self.width // 2, self.height // 2 + 50))
            surface.blit(instruction3, instruction3_rect)
        else:
            # Draw world items
            for item in self.world_items:
                item.draw(surface)

            # Draw play button (only visible if worlds are available)
            self.play_button.draw(surface)

        # Draw common elements (back and reload buttons)
        self.draw_common_elements(surface)

        # Draw status message if active
        if self.status_timer > 0:
            status_font = pygame.font.SysFont(None, 24)
            status_color = (255, 100, 100) if "Error" in self.status_message else (100, 255, 100)
            status_text = status_font.render(self.status_message, True, status_color)
            status_rect = status_text.get_rect(center=(self.width // 2, self.height - 30))
            surface.blit(status_text, status_rect)

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Call the base class resize method
        super().resize(new_width, new_height)

        # Resize background
        self.bg_image = pygame.transform.scale(self.bg_image, (new_width, new_height))

        # Reposition play button - center it horizontally
        button_width = self.play_button.rect.width
        self.play_button.rect.topleft = (new_width // 2 - button_width // 2, new_height - 80)

        # Refresh world list to reposition items
        self.refresh_world_list()

# For backward compatibility
MapSelectScreen = WorldSelectScreen
