"""
Collision Handler - handles collision detection for gameplay
"""
import pygame
import json
import os

class CollisionHandler:
    """Handles collision detection for gameplay"""
    def __init__(self, grid_cell_size=16):
        self.grid_cell_size = grid_cell_size
        self.collision_data = {}

        # Global collision database file path
        self.global_collision_db_path = "SaveData/global_collision_data.json"

        # Load global collision data
        self.load_global_collision_data()

        # Define inset amount (how far from the edge in pixels)
        self.inset = 3  # Reduced from 4

        # Calculate inset as a normalized value (0-1)
        inset_normalized = self.inset / grid_cell_size

        # Corner positions within a tile (normalized 0-1 coordinates with inset)
        self.corner_positions = [
            (inset_normalized, inset_normalized),              # Top-left
            (1.0 - inset_normalized, inset_normalized),        # Top-right
            (inset_normalized, 1.0 - inset_normalized),        # Bottom-left
            (1.0 - inset_normalized, 1.0 - inset_normalized)   # Bottom-right
        ]

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
        except Exception as e:
            pass  # Error loading global collision data
            self.collision_data = {}

    def load_collision_data(self, collision_data):
        """Load collision data from map file"""
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

    def check_collision(self, player_rect, tile_mapping, map_data):
        """Check if player collides with any solid tile corners"""
        # Convert player position to grid coordinates using the collision handler's grid size
        # This should always use the base grid size (16) for logical coordinates
        player_grid_x = player_rect.centerx // self.grid_cell_size
        player_grid_y = player_rect.centery // self.grid_cell_size

        # Check surrounding tiles (3x3 grid around player)
        for y in range(player_grid_y - 1, player_grid_y + 2):
            for x in range(player_grid_x - 1, player_grid_x + 2):
                # Skip out of bounds tiles
                if y < 0 or x < 0 or y >= len(map_data) or x >= len(map_data[0]):
                    continue

                # Get tile ID at this position
                tile_id = map_data[y][x]

                # Skip empty tiles
                if tile_id == -1:
                    continue

                # Get tile path from mapping
                tile_path = self._get_tile_path_from_id(tile_id, tile_mapping)
                if not tile_path:
                    continue

                # Check if this tile has collision data
                if tile_path not in self.collision_data:
                    continue

                # Calculate tile rect
                tile_rect = pygame.Rect(
                    x * self.grid_cell_size,
                    y * self.grid_cell_size,
                    self.grid_cell_size,
                    self.grid_cell_size
                )

                # Check each corner of the tile
                for corner_idx, corner_state in self.collision_data[tile_path].items():
                    # Skip non-solid corners
                    if not corner_state:
                        continue

                    # Get corner position
                    corner_idx = int(corner_idx)  # Convert string key to int if needed
                    corner_x = tile_rect.left + self.corner_positions[corner_idx][0] * self.grid_cell_size
                    corner_y = tile_rect.top + self.corner_positions[corner_idx][1] * self.grid_cell_size

                    # Create a small rect for the corner
                    corner_rect = pygame.Rect(
                        corner_x - 2,
                        corner_y - 2,
                        4, 4
                    )

                    # Check if player collides with this corner
                    if player_rect.colliderect(corner_rect):
                        return True

        return False

    def find_directional_free_space(self, player_rect, tile_mapping, map_data, map_width, map_height, max_search_radius=64):
        """Find free space by moving away from walls in a straight line

        Args:
            player_rect: The player's current rect
            tile_mapping: The tile mapping
            map_data: The map data for collision detection
            map_width: Map width in tiles
            map_height: Map height in tiles
            max_search_radius: Maximum distance to search for free space (in pixels)

        Returns:
            tuple: (x, y) position of free space away from walls, or None if not found
        """
        # Calculate map boundaries in pixels
        max_x = map_width * self.grid_cell_size
        max_y = map_height * self.grid_cell_size

        # Start from the player's current center position
        center_x = player_rect.centerx
        center_y = player_rect.centery

        # Analyze collision density in each cardinal direction
        directions = {
            'up': (0, -1),
            'down': (0, 1),
            'left': (-1, 0),
            'right': (1, 0)
        }

        collision_density = {}

        # Check collision density in each direction
        for direction_name, (dx, dy) in directions.items():
            density = 0
            # Check several positions in this direction to gauge wall density
            for check_distance in range(self.grid_cell_size, min(max_search_radius, 48), self.grid_cell_size // 2):
                check_x = center_x + dx * check_distance
                check_y = center_y + dy * check_distance

                check_rect = pygame.Rect(
                    check_x - player_rect.width // 2,
                    check_y - player_rect.height // 2,
                    player_rect.width,
                    player_rect.height
                )

                # Skip if out of bounds
                if (check_rect.x < 0 or check_rect.y < 0 or
                    check_rect.right > max_x or check_rect.bottom > max_y):
                    density += 2  # Penalize out of bounds heavily
                    continue

                # Check for collision
                if self.check_collision(check_rect, tile_mapping, map_data):
                    density += 1

            collision_density[direction_name] = density

        # Sort directions by collision density (lowest first = least walls)
        sorted_directions = sorted(collision_density.items(), key=lambda x: x[1])

        # Try to move in the direction with least walls (away from walls)
        for direction_name, density in sorted_directions:
            dx, dy = directions[direction_name]

            # Try increasing distances in this direction
            for distance in range(self.grid_cell_size, max_search_radius + 1, self.grid_cell_size // 4):
                test_x = center_x + dx * distance
                test_y = center_y + dy * distance

                test_rect = pygame.Rect(
                    test_x - player_rect.width // 2,
                    test_y - player_rect.height // 2,
                    player_rect.width,
                    player_rect.height
                )

                # Check if this position is within map boundaries
                if (test_rect.x < 0 or test_rect.y < 0 or
                    test_rect.right > max_x or test_rect.bottom > max_y):
                    continue  # Skip positions outside map boundaries

                # Check if this position is free of collisions
                if not self.check_collision(test_rect, tile_mapping, map_data):
                    pass  # Found directional free space
                    return (test_rect.x, test_rect.y)

        # If directional approach failed, return None
        return None

    def find_nearest_free_space(self, player_rect, tile_mapping, map_data, map_width, map_height, max_search_radius=64):
        """Find the nearest free space around the player when stuck in collision

        Args:
            player_rect: The player's current rect
            tile_mapping: The tile mapping
            map_data: The map data for collision detection
            map_width: Map width in tiles
            map_height: Map height in tiles
            max_search_radius: Maximum distance to search for free space (in pixels)

        Returns:
            tuple: (x, y) position of nearest free space, or None if not found
        """
        # First try the directional approach (move away from walls)
        directional_position = self.find_directional_free_space(
            player_rect, tile_mapping, map_data, map_width, map_height, max_search_radius
        )
        if directional_position:
            return directional_position

        pass  # Directional unstuck failed, falling back to circular search

        # Calculate map boundaries in pixels
        max_x = map_width * self.grid_cell_size
        max_y = map_height * self.grid_cell_size

        # Start from the player's current center position
        center_x = player_rect.centerx
        center_y = player_rect.centery

        # Search in expanding circles around the player (fallback method)
        for radius in range(self.grid_cell_size, max_search_radius + 1, self.grid_cell_size // 2):
            # Check positions in a circle around the player
            for angle_step in range(0, 360, 15):  # Check every 15 degrees
                import math
                angle_rad = math.radians(angle_step)

                # Calculate test position
                test_x = center_x + int(radius * math.cos(angle_rad))
                test_y = center_y + int(radius * math.sin(angle_rad))

                # Create a test rect at this position
                test_rect = pygame.Rect(
                    test_x - player_rect.width // 2,
                    test_y - player_rect.height // 2,
                    player_rect.width,
                    player_rect.height
                )

                # Check if this position is within map boundaries
                if (test_rect.x < 0 or test_rect.y < 0 or
                    test_rect.right > max_x or test_rect.bottom > max_y):
                    continue  # Skip positions outside map boundaries

                # Check if this position is free of collisions
                if not self.check_collision(test_rect, tile_mapping, map_data):
                    # Found a free space, return the top-left position for the rect
                    return (test_rect.x, test_rect.y)

        # If no free space found, try the cardinal directions at increasing distances
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Up, Right, Down, Left
        for distance in range(self.grid_cell_size, max_search_radius + 1, self.grid_cell_size // 4):
            for dx, dy in directions:
                test_x = center_x + dx * distance
                test_y = center_y + dy * distance

                test_rect = pygame.Rect(
                    test_x - player_rect.width // 2,
                    test_y - player_rect.height // 2,
                    player_rect.width,
                    player_rect.height
                )

                # Check if this position is within map boundaries
                if (test_rect.x < 0 or test_rect.y < 0 or
                    test_rect.right > max_x or test_rect.bottom > max_y):
                    continue  # Skip positions outside map boundaries

                if not self.check_collision(test_rect, tile_mapping, map_data):
                    return (test_rect.x, test_rect.y)

        # No free space found
        return None

    def _get_tile_path_from_id(self, tile_id, tile_mapping):
        """Get the tile path from its ID using the mapping"""
        # Check if this is an animated tile (IDs 1000+)
        if tile_id >= 1000:
            # Get the animated tile manager singleton
            from ..animation_system import AnimatedTileManager
            # Get the singleton instance
            animated_tile_manager = AnimatedTileManager()

            # Check if this ID is in the animated tiles
            if tile_id in animated_tile_manager.animated_tile_ids:
                tile_name = animated_tile_manager.animated_tile_ids[tile_id]
                # Return the special path format for animated tiles
                return f"animated:{tile_name}"

        # Convert tile_id to string for dictionary lookup
        tile_id_str = str(tile_id)

        # Check if it's a direct mapping
        if tile_id_str in tile_mapping:
            tile_info = tile_mapping[tile_id_str]
            if isinstance(tile_info, dict) and "path" in tile_info:
                return tile_info["path"]

        # Check if it's in a loop pattern
        for _, value in tile_mapping.items():
            if isinstance(value, dict) and value.get("type") == "loop":
                start_id = value.get("start_id", 0)
                count = value.get("count", 0)

                # Check if tile_id is in this range
                if start_id <= tile_id < start_id + count:
                    # Calculate the pattern
                    pattern = value.get("pattern", {})
                    offset = tile_id - start_id
                    number = pattern.get("start", 0) + offset
                    path = f"{pattern['prefix']}{number:0{pattern['digits']}d}{pattern['suffix']}"
                    return path

        return None
