"""
Collision Manager - handles collision data for tiles
"""
import pygame
import json
import os

class CollisionManager:
    """Manages collision data for tiles"""
    def __init__(self):
        # Dictionary to store collision data for each tile
        # Format: {tile_path: {corner_index: is_solid}}
        # corner_index: 0=top-left, 1=top-right, 2=bottom-left, 3=bottom-right
        self.collision_data = {}

        # Global collision database file path
        self.global_collision_db_path = "SaveData/global_collision_data.json"

        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(self.global_collision_db_path), exist_ok=True)

        # Load global collision data
        self.load_global_collision_data()

        # Visual settings for collision dots
        self.dot_radius = 2  # Smaller dots (was 3)
        self.active_color = (255, 0, 0, 150)  # Red for active/solid with transparency
        self.inactive_color = (100, 100, 100, 100)  # Gray for inactive with transparency

        # Flag to toggle visibility of collision dots
        self.show_collision_dots = True

    def get_collision_state(self, tile_path, corner_index):
        """Get the collision state for a specific corner of a tile"""
        # Handle animated tiles (they have a special prefix)
        if tile_path.startswith("animated:"):
            # Use the animated tile path as is
            if tile_path not in self.collision_data:
                # Initialize with all corners inactive
                self.collision_data[tile_path] = {0: False, 1: False, 2: False, 3: False}
        elif tile_path not in self.collision_data:
            # Initialize with all corners inactive for regular tiles
            self.collision_data[tile_path] = {0: False, 1: False, 2: False, 3: False}

        return self.collision_data[tile_path].get(corner_index, False)

    def toggle_collision(self, tile_path, corner_index):
        """Toggle the collision state for a specific corner of a tile"""
        # Handle animated tiles (they have a special prefix)
        if tile_path.startswith("animated:"):
            # Use the animated tile path as is
            if tile_path not in self.collision_data:
                # Initialize with all corners inactive
                self.collision_data[tile_path] = {0: False, 1: False, 2: False, 3: False}
        elif tile_path not in self.collision_data:
            # Initialize with all corners inactive for regular tiles
            self.collision_data[tile_path] = {0: False, 1: False, 2: False, 3: False}

        # Toggle the state
        self.collision_data[tile_path][corner_index] = not self.collision_data[tile_path][corner_index]

        # Save the updated collision data to the global database
        self.save_global_collision_data()

        return self.collision_data[tile_path][corner_index]

    def draw_collision_dots(self, surface, tile_rect, tile_path):
        """Draw collision dots on a tile"""
        if not self.show_collision_dots:
            return

        # Calculate dot positions (one in each corner, moved more inward)
        # Define inset amount (how far from the edge)
        inset = 3  # Pixels from the edge (reduced from 4)

        dot_positions = [
            (tile_rect.left + inset, tile_rect.top + inset),                       # Top-left
            (tile_rect.right - inset, tile_rect.top + inset),                      # Top-right
            (tile_rect.left + inset, tile_rect.bottom - inset),                    # Bottom-left
            (tile_rect.right - inset, tile_rect.bottom - inset)                    # Bottom-right
        ]

        # Draw each dot with appropriate color based on collision state
        for i, pos in enumerate(dot_positions):
            is_solid = self.get_collision_state(tile_path, i)
            color = self.active_color if is_solid else self.inactive_color

            # Create a transparent surface for the dot
            dot_surface = pygame.Surface((self.dot_radius * 2 + 2, self.dot_radius * 2 + 2), pygame.SRCALPHA)

            # Draw the dot on the transparent surface
            pygame.draw.circle(
                dot_surface,
                color,
                (self.dot_radius + 1, self.dot_radius + 1),
                self.dot_radius
            )

            # Blit the transparent dot onto the main surface
            surface.blit(dot_surface, (pos[0] - self.dot_radius - 1, pos[1] - self.dot_radius - 1))

    def handle_collision_click(self, mouse_pos, tile_rect, tile_path):
        """Handle clicks on collision dots"""
        # Calculate dot positions and check if any was clicked
        # Define inset amount (how far from the edge) - same as in draw_collision_dots
        inset = 3  # Pixels from the edge (reduced from 4)

        dot_positions = [
            (tile_rect.left + inset, tile_rect.top + inset),                       # Top-left
            (tile_rect.right - inset, tile_rect.top + inset),                      # Top-right
            (tile_rect.left + inset, tile_rect.bottom - inset),                    # Bottom-left
            (tile_rect.right - inset, tile_rect.bottom - inset)                    # Bottom-right
        ]

        # Check if any dot was clicked
        for i, pos in enumerate(dot_positions):
            # Create a small rect around the dot for easier clicking
            dot_rect = pygame.Rect(pos[0] - self.dot_radius - 2, pos[1] - self.dot_radius - 2,
                                  (self.dot_radius + 2) * 2, (self.dot_radius + 2) * 2)

            if dot_rect.collidepoint(mouse_pos):
                # Toggle collision for this corner
                self.toggle_collision(tile_path, i)
                return True

        return False

    def toggle_dots_visibility(self):
        """Toggle visibility of collision dots"""
        self.show_collision_dots = not self.show_collision_dots
        return self.show_collision_dots

    def get_collision_data_for_save(self):
        """Get collision data in a format suitable for saving"""
        # Create a more compact format for collision data
        compact_data = {}

        for tile_path, corners in self.collision_data.items():
            # Skip tiles with no active collision dots
            active_corners = [corner for corner, is_active in corners.items() if is_active]
            if active_corners:
                # Only store active corners
                compact_data[tile_path] = active_corners

        return compact_data

    def load_global_collision_data(self):
        """Load collision data from global database file"""
        try:
            if os.path.exists(self.global_collision_db_path):
                with open(self.global_collision_db_path, 'r') as f:
                    global_data = json.load(f)

                    # Load the collision data from the global database
                    if "collision_data" in global_data:
                        self.load_collision_data(global_data["collision_data"])
                    else:
                        self.collision_data = {}
            else:
                # Create a new global database file if it doesn't exist
                self.save_global_collision_data()
        except Exception as e:
            print(f"Error loading global collision data: {e}")
            self.collision_data = {}

    def save_global_collision_data(self):
        """Save collision data to global database file"""
        try:
            # Create the global database structure
            global_data = {
                "version": 1,
                "collision_data": self.get_collision_data_for_save()
            }

            # Save to file
            with open(self.global_collision_db_path, 'w') as f:
                json.dump(global_data, f, indent=2)
        except Exception as e:
            print(f"Error saving global collision data: {e}")

    def load_collision_data(self, collision_data):
        """Load collision data from saved format"""
        if not collision_data:
            # Don't clear existing collision data, just return
            return

        # Process the provided collision data
        for tile_path, corners in collision_data.items():
            # Initialize with all corners inactive if this is a new tile
            if tile_path not in self.collision_data:
                self.collision_data[tile_path] = {0: False, 1: False, 2: False, 3: False}

            # If corners is a list, it's the compact format with only active corners
            if isinstance(corners, list):
                for corner in corners:
                    # Convert corner to int if it's a string
                    corner_idx = int(corner) if isinstance(corner, str) else corner
                    self.collision_data[tile_path][corner_idx] = True
            # If corners is a dict, it's the old verbose format
            elif isinstance(corners, dict):
                for corner, is_active in corners.items():
                    # Convert corner to int if it's a string
                    corner_idx = int(corner) if isinstance(corner, str) else corner
                    self.collision_data[tile_path][corner_idx] = is_active
