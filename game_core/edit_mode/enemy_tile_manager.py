"""
Enemy Tile Manager for Edit Mode - handles placing enemies as tiles
"""
import pygame
import os
import math
from game_core.core.font_loader import font_manager
from game_core.core.config import FONT_SIZE_SMALL

class EnemyTileManager:
    """Manages enemy tiles in edit mode"""
    def __init__(self, sidebar_width):
        self.sidebar_width = sidebar_width

        # Enemy tile data
        self.enemy_tiles = []  # List of enemy tile data
        self.selected_enemy_tile = None

        # Enemy spawn points
        self.enemy_spawn_points = []  # List of enemy spawn points (x, y, type)

        # Load enemy tiles
        self.load_enemy_tiles()

        # UI elements
        self.enemy_tile_buttons = []
        self.enemy_tile_rects = []
        self.enemy_list_rect = pygame.Rect(0, 0, 0, 0)
        self.enemy_list_items = []
        self.delete_button = pygame.Rect(0, 0, 0, 0)

        # Fonts
        self.font = font_loader.get_font('regular', FONT_SIZE_SMALL)

        # Position UI elements
        self.position_ui_elements()

    def load_enemy_tiles(self):
        """Load enemy tile images"""
        # Phantom enemy - right facing
        phantom_right_path = "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_right/tile000.png"
        if os.path.exists(phantom_right_path):
            try:
                phantom_right_image = pygame.image.load(phantom_right_path).convert_alpha()
                self.enemy_tiles.append({
                    "type": "phantom_right",
                    "image": phantom_right_image,
                    "source_path": phantom_right_path
                })
            except Exception as e:
                print(f"Error loading phantom right enemy tile: {e}")

        # Phantom enemy - left facing
        phantom_left_path = "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_left/tile000.png"
        if os.path.exists(phantom_left_path):
            try:
                phantom_left_image = pygame.image.load(phantom_left_path).convert_alpha()
                self.enemy_tiles.append({
                    "type": "phantom_left",
                    "image": phantom_left_image,
                    "source_path": phantom_left_path
                })
            except Exception as e:
                print(f"Error loading phantom left enemy tile: {e}")

        # Spinner enemy - add right after phantoms
        spinner_path = "Enemies_Sprites/Spinner_Sprites/spinner_idle_anim_all_dir/tile000.png"
        if os.path.exists(spinner_path):
            try:
                spinner_image = pygame.image.load(spinner_path).convert_alpha()
                self.enemy_tiles.append({
                    "type": "spinner",
                    "image": spinner_image,
                    "source_path": spinner_path
                })
            except Exception as e:
                print(f"Error loading spinner enemy tile: {e}")

        # Bomberplant enemy
        bomberplant_path = "Enemies_Sprites/Bomberplant_Sprites/bomberplant_idle_anim_all_dir/tile000.png"
        if os.path.exists(bomberplant_path):
            try:
                bomberplant_image = pygame.image.load(bomberplant_path).convert_alpha()
                self.enemy_tiles.append({
                    "type": "bomberplant",
                    "image": bomberplant_image,
                    "source_path": bomberplant_path
                })
            except Exception as e:
                print(f"Error loading bomberplant enemy tile: {e}")



        # If we have no enemy tiles, add a placeholder
        if not self.enemy_tiles:
            # Create a placeholder image
            placeholder = pygame.Surface((16, 16))
            placeholder.fill((255, 0, 255))  # Magenta
            pygame.draw.rect(placeholder, (0, 0, 0), pygame.Rect(0, 0, 16, 16), 1)
            pygame.draw.line(placeholder, (0, 0, 0), (0, 0), (16, 16), 1)
            pygame.draw.line(placeholder, (0, 0, 0), (0, 16), (16, 0), 1)

            self.enemy_tiles.append({
                "type": "phantom",
                "image": placeholder,
                "source_path": "placeholder"
            })

    def position_ui_elements(self):
        """Position UI elements in the sidebar"""
        self.enemy_tile_buttons = []
        self.enemy_tile_rects = []

        # Calculate grid layout
        tile_size = 32  # 2x the normal tile size for better visibility
        padding = 5
        margin = 20
        start_y = 150

        # Calculate how many tiles can fit in a row
        available_width = self.sidebar_width - 2 * margin
        tiles_per_row = max(1, available_width // (tile_size + padding))

        # Position tiles in a grid
        for i, enemy_tile in enumerate(self.enemy_tiles):
            # Calculate row and column
            row = i // tiles_per_row
            col = i % tiles_per_row

            # Calculate position
            x = margin + col * (tile_size + padding)
            y = start_y + row * (tile_size + padding)

            # Create button rect
            button_rect = pygame.Rect(x, y, tile_size, tile_size)
            self.enemy_tile_rects.append(button_rect)

            # Create button data
            self.enemy_tile_buttons.append({
                "rect": button_rect,
                "enemy_tile": enemy_tile,
                "selected": False,
                "button": {
                    "rect": button_rect,
                    "is_selected": False
                }
            })

        # Enemy list
        self.enemy_list_rect = pygame.Rect(margin, 250, self.sidebar_width - 2 * margin, 150)

        # Delete button
        self.delete_button = pygame.Rect(margin, 410, self.sidebar_width - 2 * margin, 30)

    def add_enemy_spawn_point(self, x, y):
        """Add an enemy spawn point at the given position"""
        if self.selected_enemy_tile:
            enemy_type = self.selected_enemy_tile["type"]
            self.enemy_spawn_points.append({
                "x": x,
                "y": y,
                "type": enemy_type
            })
            self.update_enemy_list_items()
            return True
        return False

    def remove_enemy_spawn_point(self, index):
        """Remove an enemy spawn point by index"""
        if 0 <= index < len(self.enemy_spawn_points):
            del self.enemy_spawn_points[index]
            self.update_enemy_list_items()
            return True
        return False

    def update_enemy_list_items(self):
        """Update the list of enemy spawn points for display"""
        self.enemy_list_items = []
        item_height = 25
        for i, spawn_point in enumerate(self.enemy_spawn_points):
            y = self.enemy_list_rect.y + i * item_height
            if y + item_height > self.enemy_list_rect.bottom:
                break  # Don't show items that would go beyond the list rect

            item_rect = pygame.Rect(self.enemy_list_rect.x, y, self.enemy_list_rect.width, item_height)
            text = f"{spawn_point['type']} at ({spawn_point['x']}, {spawn_point['y']})"
            self.enemy_list_items.append((item_rect, text, i))

    def handle_event(self, event, mouse_pos, grid_x=None, grid_y=None):
        """Handle events for enemy placement"""
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        # Check enemy tile button clicks
        for button in self.enemy_tile_buttons:
            if button["rect"].collidepoint(mouse_pos):
                # Deselect all buttons
                for other_button in self.enemy_tile_buttons:
                    other_button["selected"] = False
                    other_button["button"]["is_selected"] = False

                # Select this button
                button["selected"] = True
                button["button"]["is_selected"] = True
                self.selected_enemy_tile = button["enemy_tile"]
                return True

        # Check enemy list items for selection
        for item_rect, _, _ in self.enemy_list_items:
            if item_rect.collidepoint(mouse_pos):
                # Select this enemy
                return True

        # Check delete button
        if self.delete_button.collidepoint(mouse_pos):
            # Delete the selected enemy
            if self.enemy_list_items:
                # For simplicity, just delete the last one for now
                self.remove_enemy_spawn_point(len(self.enemy_spawn_points) - 1)
                return True

        # Check for placing enemy in the map area
        if grid_x is not None and grid_y is not None and mouse_pos[0] < self.sidebar_width:
            # Add enemy at grid position if we have a selected enemy tile
            if self.selected_enemy_tile:
                self.add_enemy_spawn_point(grid_x, grid_y)
                return True

        return False

    def draw(self, surface):
        """Draw the enemy tile selection UI"""
        # Draw title
        title_text = self.font.render("Enemy Tiles Palette", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(self.sidebar_width // 2, 130))
        surface.blit(title_text, title_rect)

        # Draw palette background
        palette_margin = 15
        palette_top = 150 - palette_margin

        # Calculate palette height based on the number of rows needed
        if self.enemy_tile_buttons:
            last_button = self.enemy_tile_buttons[-1]
            palette_height = last_button["rect"].bottom - palette_top + palette_margin * 2
        else:
            palette_height = 100  # Default height if no buttons

        palette_rect = pygame.Rect(
            palette_margin,
            palette_top,
            self.sidebar_width - palette_margin * 2,
            palette_height
        )

        # Draw palette background
        pygame.draw.rect(surface, (240, 240, 240), palette_rect)
        pygame.draw.rect(surface, (180, 180, 180), palette_rect, 1)

        # Draw enemy tile buttons
        for button in self.enemy_tile_buttons:
            # Draw button background
            color = (100, 100, 200) if button["selected"] else (220, 220, 220)
            pygame.draw.rect(surface, color, button["rect"])
            pygame.draw.rect(surface, (100, 100, 100), button["rect"], 1)

            # Draw enemy tile image
            enemy_tile = button["enemy_tile"]
            image = enemy_tile["image"]

            # Scale the image to fit the button
            scaled_image = pygame.transform.scale(image, (button["rect"].width - 4, button["rect"].height - 4))

            # Draw the image centered in the button
            image_rect = scaled_image.get_rect(center=button["rect"].center)
            surface.blit(scaled_image, image_rect)

            # Draw a small label to identify the enemy type
            debug_font = pygame.font.SysFont(None, 12)
            debug_text = debug_font.render(enemy_tile["type"][:1].upper(), True, (0, 0, 0))
            debug_rect = debug_text.get_rect(bottomright=button["rect"].bottomright)
            surface.blit(debug_text, debug_rect)

        # Draw a label for the palette
        if not self.enemy_tile_buttons:
            no_tiles_text = self.font.render("No enemy tiles available", True, (100, 100, 100))
            no_tiles_rect = no_tiles_text.get_rect(center=palette_rect.center)
            surface.blit(no_tiles_text, no_tiles_rect)

        # Draw enemy list background
        pygame.draw.rect(surface, (240, 240, 240), self.enemy_list_rect)
        pygame.draw.rect(surface, (180, 180, 180), self.enemy_list_rect, 1)

        # Draw enemy list title
        list_title = self.font.render("Placed Enemies", True, (50, 50, 50))
        list_title_rect = list_title.get_rect(topleft=(self.enemy_list_rect.x, self.enemy_list_rect.y - 25))
        surface.blit(list_title, list_title_rect)

        # Draw enemy list items
        for item_rect, item_text, _ in self.enemy_list_items:
            text = self.font.render(item_text, True, (50, 50, 50))
            text_rect = text.get_rect(midleft=(item_rect.x + 5, item_rect.centery))
            surface.blit(text, text_rect)

        # Draw delete button
        pygame.draw.rect(surface, (220, 100, 100), self.delete_button)
        pygame.draw.rect(surface, (180, 180, 180), self.delete_button, 1)
        delete_text = self.font.render("Delete Last Enemy", True, (50, 50, 50))
        delete_text_rect = delete_text.get_rect(center=self.delete_button.center)
        surface.blit(delete_text, delete_text_rect)

    def draw_enemy_spawn_points(self, surface, camera_x, camera_y, grid_cell_size):
        """Draw enemy spawn points on the map"""
        for spawn_point in self.enemy_spawn_points:
            # Calculate screen position
            screen_x = spawn_point["x"] * grid_cell_size - camera_x
            screen_y = spawn_point["y"] * grid_cell_size - camera_y

            # Draw a marker for the spawn point - ONLY MARKERS, NOT ACTUAL SPRITES
            if spawn_point["type"] == "phantom_right" or spawn_point["type"] == "phantom_left" or spawn_point["type"] == "phantom":
                color = (200, 100, 200)  # Purple for phantom

                # Draw a circle with an X for phantom
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)
                pygame.draw.line(surface, color, (screen_x, screen_y), (screen_x + grid_cell_size, screen_y + grid_cell_size), 2)
                pygame.draw.line(surface, color, (screen_x + grid_cell_size, screen_y), (screen_x, screen_y + grid_cell_size), 2)

                # Add a small "P" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("P", True, color)
                text_rect = text.get_rect(center=(screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2))
                surface.blit(text, text_rect)

            elif spawn_point["type"] == "bomberplant":
                color = (0, 200, 0)  # Green for bomberplant

                # Draw a circle with a plus sign for bomberplant
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)
                pygame.draw.line(surface, color, (screen_x + grid_cell_size // 2, screen_y), (screen_x + grid_cell_size // 2, screen_y + grid_cell_size), 2)
                pygame.draw.line(surface, color, (screen_x, screen_y + grid_cell_size // 2), (screen_x + grid_cell_size, screen_y + grid_cell_size // 2), 2)

                # Add a small "B" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("B", True, color)
                text_rect = text.get_rect(center=(screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2))
                surface.blit(text, text_rect)

            elif spawn_point["type"] == "spinner":
                color = (0, 150, 255)  # Blue for spinner

                # Draw a circle with a spiral-like pattern for spinner
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)

                # Draw a spiral-like pattern (simplified as curved lines)
                center_x = screen_x + grid_cell_size // 2
                center_y = screen_y + grid_cell_size // 2

                # Draw an X inside the circle
                pygame.draw.line(surface, color,
                                (center_x - grid_cell_size // 4, center_y - grid_cell_size // 4),
                                (center_x + grid_cell_size // 4, center_y + grid_cell_size // 4), 2)
                pygame.draw.line(surface, color,
                                (center_x + grid_cell_size // 4, center_y - grid_cell_size // 4),
                                (center_x - grid_cell_size // 4, center_y + grid_cell_size // 4), 2)

                # Add a small "S" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("S", True, color)
                text_rect = text.get_rect(center=(center_x, center_y))
                surface.blit(text, text_rect)

            elif spawn_point["type"] == "spider":
                color = (255, 100, 0)  # Orange for spider

                # Draw a circle for the spider
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)

                # Draw a spider-like pattern (simplified as 8 legs)
                center_x = screen_x + grid_cell_size // 2
                center_y = screen_y + grid_cell_size // 2

                # Draw 8 legs (simplified as lines)
                for i in range(8):
                    angle = i * 45  # 8 directions, 45 degrees apart
                    leg_x = center_x + int((grid_cell_size // 2) * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).x)
                    leg_y = center_y + int((grid_cell_size // 2) * 0.7 * pygame.math.Vector2(1, 0).rotate(angle).y)
                    pygame.draw.line(surface, color, (center_x, center_y), (leg_x, leg_y), 1)

                # Add a small "Sp" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("Sp", True, color)
                text_rect = text.get_rect(center=(center_x, center_y))
                surface.blit(text, text_rect)

            elif spawn_point["type"] == "pinkslime":
                color = (255, 105, 180)  # Hot pink for pinkslime

                # Draw a circle for the pinkslime
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)

                # Draw a slime-like pattern (simplified as a wavy bottom)
                center_x = screen_x + grid_cell_size // 2
                center_y = screen_y + grid_cell_size // 2

                # Draw wavy bottom
                wave_points = []
                for i in range(5):
                    x_offset = (i - 2) * (grid_cell_size // 4)
                    y_offset = 3 * math.sin(i * math.pi / 2)
                    wave_points.append((center_x + x_offset, center_y + y_offset))

                # Draw the wave
                if len(wave_points) >= 2:
                    pygame.draw.lines(surface, color, False, wave_points, 2)

                # Add a small "PS" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("PS", True, color)
                text_rect = text.get_rect(center=(center_x, center_y))
                surface.blit(text, text_rect)

            elif spawn_point["type"] == "pinkbat_left" or spawn_point["type"] == "pinkbat_right":
                color = (219, 112, 147)  # Pale violet red for pinkbat

                # Draw a circle for the pinkbat
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)

                # Draw a bat-like pattern (simplified as wings)
                center_x = screen_x + grid_cell_size // 2
                center_y = screen_y + grid_cell_size // 2

                # Draw wings
                wing_size = grid_cell_size // 3

                # Left wing
                pygame.draw.line(surface, color,
                                (center_x, center_y - wing_size // 2),
                                (center_x - wing_size, center_y - wing_size), 2)
                pygame.draw.line(surface, color,
                                (center_x - wing_size, center_y - wing_size),
                                (center_x - wing_size, center_y), 2)
                pygame.draw.line(surface, color,
                                (center_x - wing_size, center_y),
                                (center_x, center_y), 2)

                # Right wing
                pygame.draw.line(surface, color,
                                (center_x, center_y - wing_size // 2),
                                (center_x + wing_size, center_y - wing_size), 2)
                pygame.draw.line(surface, color,
                                (center_x + wing_size, center_y - wing_size),
                                (center_x + wing_size, center_y), 2)
                pygame.draw.line(surface, color,
                                (center_x + wing_size, center_y),
                                (center_x, center_y), 2)

                # Add a small "PB" label with direction indicator
                font = pygame.font.SysFont(None, 14)
                direction_indicator = "L" if spawn_point["type"] == "pinkbat_left" else "R"
                text = font.render(f"PB{direction_indicator}", True, color)
                text_rect = text.get_rect(center=(center_x, center_y + wing_size // 2))
                surface.blit(text, text_rect)

            else:
                color = (255, 0, 0)  # Red for unknown types

                # Draw a circle with an X for unknown types
                pygame.draw.circle(surface, color, (screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2), grid_cell_size // 2, 2)
                pygame.draw.line(surface, color, (screen_x, screen_y), (screen_x + grid_cell_size, screen_y + grid_cell_size), 2)
                pygame.draw.line(surface, color, (screen_x + grid_cell_size, screen_y), (screen_x, screen_y + grid_cell_size), 2)

                # Add a small "?" label
                font = pygame.font.SysFont(None, 14)
                text = font.render("?", True, color)
                text_rect = text.get_rect(center=(screen_x + grid_cell_size // 2, screen_y + grid_cell_size // 2))
                surface.blit(text, text_rect)

    def get_enemy_data_for_save(self):
        """Get enemy data in a format suitable for saving"""
        return self.enemy_spawn_points

    def get_selected_enemy_tile(self):
        """Get the currently selected enemy tile"""
        return self.selected_enemy_tile
