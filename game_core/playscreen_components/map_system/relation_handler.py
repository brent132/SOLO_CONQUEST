"""
Relation Handler - handles teleportation between maps using relation points

This module manages the relation points that allow players to teleport between maps.
It loads relation points from map files, checks for player collisions with relation points,
and handles the teleportation logic.
"""
import os
import json
import pygame

class RelationHandler:
    """Handles relation points and teleportation between maps"""
    def __init__(self, grid_cell_size=16):
        self.grid_cell_size = grid_cell_size

        # Store relation points for all maps
        # Format: {map_name: {id: {'a': (grid_x, grid_y), 'b': (grid_x, grid_y)}}}
        self.relation_points = {}

        # Current map being displayed
        self.current_map = ""

        # Current teleport point (to prevent immediate re-teleportation)
        self.current_teleport_point = None

        # Colors for drawing relation points
        self.point_colors = {
            'a': (220, 60, 60, 128),  # Red with alpha
            'b': (60, 60, 220, 128)   # Blue with alpha
        }

        # Size of relation point markers
        self.point_size = grid_cell_size

    def load_relation_points(self, map_name, relation_points=None):
        """Load relation points for a specific map

        Args:
            map_name: Name of the map
            relation_points: Optional relation points data to use instead of loading from file
        """
        if relation_points:
            # Use provided relation points
            # Make sure the relation points are in the correct format
            validated_points = self._validate_relation_points(relation_points)
            self.relation_points[map_name] = validated_points
            pass  # Loaded relation points from provided data
            return

        # Try to load relation points from map file
        try:
            # Get the map file path
            maps_dir = "Maps"

            # First check if it's a main map
            main_map_path = os.path.join(maps_dir, map_name, f"{map_name}.json")

            if os.path.exists(main_map_path):
                # It's a main map
                map_path = main_map_path
            else:
                # It might be a related map, search in all map folders
                map_path = None

                # Check if Maps directory exists
                if os.path.exists(maps_dir):
                    # List all folders in the Maps directory
                    folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]

                    for folder_name in folders:
                        folder_path = os.path.join(maps_dir, folder_name)

                        # Check if this folder contains our map
                        related_map_path = os.path.join(folder_path, f"{map_name}.json")

                        if os.path.exists(related_map_path):
                            map_path = related_map_path
                            break

            # Load relation points from the map file if found
            if map_path and os.path.exists(map_path):
                with open(map_path, 'r') as f:
                    map_data = json.load(f)

                if "relation_points" in map_data:
                    # Validate the relation points to ensure they're in the correct format
                    validated_points = self._validate_relation_points(map_data["relation_points"])
                    self.relation_points[map_name] = validated_points
                    pass  # Loaded relation points from file
                else:
                    # No relation points in this map
                    self.relation_points[map_name] = {}
                    pass  # No relation points found
            else:
                # Map file not found
                self.relation_points[map_name] = {}
                pass  # Map file not found, initializing empty relation points

        except Exception as e:
            pass  # Error loading relation points
            self.relation_points[map_name] = {}

    def _validate_relation_points(self, relation_points):
        """Validate and normalize relation points to ensure they're in the correct format

        Args:
            relation_points: Relation points to validate

        Returns:
            Validated relation points
        """
        validated = {}

        try:
            # Ensure relation_points is a dictionary
            if not isinstance(relation_points, dict):
                pass  # Warning: relation_points is not a dictionary
                return validated

            # Process each ID
            for id_key, points in relation_points.items():
                # Ensure points is a dictionary
                if not isinstance(points, dict):
                    pass  # Warning: points is not a dictionary
                    continue

                # Create a new entry for this ID
                validated[id_key] = {}

                # Process each point type (a or b)
                for point_type, position in points.items():
                    # Ensure point_type is 'a' or 'b'
                    if point_type not in ['a', 'b']:
                        pass  # Warning: Invalid point type
                        continue

                    # Ensure position is a list or tuple with 2 elements
                    if not isinstance(position, (list, tuple)) or len(position) != 2:
                        pass  # Warning: Invalid position
                        continue

                    # Ensure position elements are integers
                    try:
                        grid_x = int(position[0])
                        grid_y = int(position[1])
                        validated[id_key][point_type] = [grid_x, grid_y]
                    except (ValueError, TypeError):
                        pass  # Warning: Invalid position values
                        continue

            return validated
        except Exception as e:
            pass  # Error validating relation points
            return {}

    def load_all_relation_points(self):
        """Load relation points from all map files"""
        # Get the Maps directory
        maps_dir = "Maps"

        if not os.path.exists(maps_dir):
            pass  # Maps directory not found
            return

        # List all folders in the Maps directory (main maps)
        folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]

        for folder_name in folders:
            folder_path = os.path.join(maps_dir, folder_name)

            # Load the main map file
            main_map_path = os.path.join(folder_path, f"{folder_name}.json")

            if os.path.exists(main_map_path):
                try:
                    with open(main_map_path, 'r') as f:
                        map_data = json.load(f)

                    if "relation_points" in map_data:
                        # Validate the relation points to ensure they're in the correct format
                        validated_points = self._validate_relation_points(map_data["relation_points"])
                        self.relation_points[folder_name] = validated_points
                        pass  # Loaded relation points for main map
                except Exception as e:
                    pass  # Error loading relation points for main map

            # Load all related map files in this folder
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".json") and file_name != f"{folder_name}.json":
                    # This is a related map
                    related_map_name = file_name[:-5]  # Remove .json extension
                    related_map_path = os.path.join(folder_path, file_name)

                    try:
                        with open(related_map_path, 'r') as f:
                            map_data = json.load(f)

                        if "relation_points" in map_data:
                            # Validate the relation points to ensure they're in the correct format
                            validated_points = self._validate_relation_points(map_data["relation_points"])
                            self.relation_points[related_map_name] = validated_points
                            pass  # Loaded relation points for related map
                    except Exception as e:
                        pass  # Error loading relation points for related map

    def get_map_folder(self, map_name):
        """Get the folder that contains a map

        Args:
            map_name: Name of the map

        Returns:
            Folder name if found, None otherwise
        """
        maps_dir = "Maps"

        # First check if it's a main map (folder name matches map name)
        main_map_path = os.path.join(maps_dir, map_name, f"{map_name}.json")
        if os.path.exists(main_map_path):
            return map_name  # The map is in its own folder

        # If not a main map, search in all folders
        if os.path.exists(maps_dir):
            folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]

            for folder_name in folders:
                folder_path = os.path.join(maps_dir, folder_name)
                map_path = os.path.join(folder_path, f"{map_name}.json")

                if os.path.exists(map_path):
                    return folder_name  # Found the folder containing this map

        return None  # Map not found in any folder

    def are_maps_in_same_folder(self, map1, map2):
        """Check if two maps are in the same folder

        Args:
            map1: Name of the first map
            map2: Name of the second map

        Returns:
            True if both maps are in the same folder, False otherwise
        """
        folder1 = self.get_map_folder(map1)
        folder2 = self.get_map_folder(map2)

        # Both maps must be found and in the same folder
        return folder1 is not None and folder1 == folder2

    def check_player_collision(self, player_rect):
        """Check if player collides with any relation point

        Args:
            player_rect: Player's rectangle for collision detection

        Returns:
            Dictionary with teleport information if collision detected, None otherwise
        """
        # Skip if no current map or no relation points
        if not self.current_map or not self.relation_points:
            return None

        # Get relation points for the current map
        current_map_points = self.relation_points.get(self.current_map, {})
        if not current_map_points:
            return None

        # Check each relation point in the current map
        for id_key, points in current_map_points.items():
            # Skip if points is not a dictionary
            if not isinstance(points, dict):
                pass  # Warning: points is not a dictionary
                continue

            for point_type, position in points.items():
                # Skip if point_type is not 'a' or 'b'
                if point_type not in ['a', 'b']:
                    pass  # Warning: Invalid point type
                    continue

                # Skip if position is not a list or tuple with 2 elements
                if not isinstance(position, (list, tuple)) or len(position) != 2:
                    pass  # Warning: Invalid position
                    continue

                try:
                    # Convert grid position to pixel position
                    grid_x = int(position[0])
                    grid_y = int(position[1])
                    pixel_x = grid_x * self.grid_cell_size
                    pixel_y = grid_y * self.grid_cell_size

                    # Create a rect for the relation point
                    point_rect = pygame.Rect(
                        pixel_x,
                        pixel_y,
                        self.grid_cell_size,
                        self.grid_cell_size
                    )

                    # Check if player collides with this point
                    if player_rect.colliderect(point_rect):
                        # Skip if this is the current teleport point (to prevent immediate re-teleportation)
                        if (self.current_teleport_point and
                            self.current_teleport_point['point_type'] == point_type and
                            self.current_teleport_point['position'] == position and
                            self.current_teleport_point['id'] == id_key):
                            return None

                        # Find the corresponding point in other maps
                        for map_name, map_points in self.relation_points.items():
                            # Skip the current map
                            if map_name == self.current_map:
                                continue

                            # Skip if map_points is not a dictionary
                            if not isinstance(map_points, dict):
                                continue

                            # Check if this map has a point with the same ID
                            if id_key in map_points:
                                # Skip if map_points[id_key] is not a dictionary
                                if not isinstance(map_points[id_key], dict):
                                    continue

                                # Find the opposite point type
                                opposite_type = 'b' if point_type == 'a' else 'a'

                                # Check if the opposite point exists
                                if opposite_type in map_points[id_key]:
                                    # Skip if the opposite point position is not valid
                                    opposite_position = map_points[id_key][opposite_type]
                                    if not isinstance(opposite_position, (list, tuple)) or len(opposite_position) != 2:
                                        continue

                                    # Check if both maps are in the same folder
                                    if not self.are_maps_in_same_folder(self.current_map, map_name):
                                        pass  # Cannot teleport: Maps not in same folder
                                        continue

                                    # Found a matching point in the same folder, prepare teleport information
                                    return {
                                        'from_map': self.current_map,
                                        'from_point': point_type,
                                        'to_map': map_name,
                                        'to_point': opposite_type,
                                        'to_position': opposite_position
                                    }
                except Exception as e:
                    pass  # Error checking collision for point
                    continue

        # Reset current teleport point if player is not colliding with any point
        self.current_teleport_point = None
        return None

    def update(self):
        """Update relation handler state

        This method is called every frame to update the state of the relation handler.
        Currently, it doesn't need to do anything, but it's included for compatibility
        with the play_screen.py update cycle.
        """
        # No update logic needed at the moment
        pass

    def draw(self, surface, camera_x, camera_y, grid_cell_size):
        """Draw relation points on the screen

        Args:
            surface: Surface to draw on
            camera_x: Camera X position
            camera_y: Camera Y position
            grid_cell_size: Size of grid cells
        """
        # Points are now invisible - this method intentionally does nothing
        # The relation points still function for teleportation, but they are not visible to the player
        pass
