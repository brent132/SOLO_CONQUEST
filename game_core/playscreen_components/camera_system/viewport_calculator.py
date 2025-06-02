"""
Viewport Calculator - Handles viewport calculations and map centering

This module manages:
- Center offset calculations for small maps
- Used area bounds detection
- Map centering logic
- Viewport size calculations
- Enemy and player tile filtering
"""


class ViewportCalculator:
    """Handles viewport calculations and map centering logic"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Map data references
        self.layers = None
        self.map_data = None
        self.map_width = 0
        self.map_height = 0
        self.expanded_mapping = None
        
    def set_map_data(self, layers, map_data, map_width: int, map_height: int, expanded_mapping):
        """Set map data for viewport calculations"""
        self.layers = layers
        self.map_data = map_data
        self.map_width = map_width
        self.map_height = map_height
        self.expanded_mapping = expanded_mapping
        
    def find_used_area_bounds(self):
        """Find the bounds of the used area in the map, excluding enemy and player tiles

        Returns:
            tuple: (min_x, max_x, min_y, max_y) - the bounds of the used area
        """
        # Initialize bounds to extreme values
        min_x = self.map_width
        max_x = 0
        min_y = self.map_height
        max_y = 0

        # Flag to track if any tiles were found
        found_tiles = False

        # Check if we have layers
        if self.layers:
            # Scan each layer for tiles
            for layer in self.layers:
                layer_data = layer["data"]

                for y in range(len(layer_data)):
                    for x in range(len(layer_data[y])):
                        # Check if this tile is not empty (-1)
                        tile_id = layer_data[y][x]
                        if tile_id != -1:
                            # Skip enemy and player tiles
                            if self.is_enemy_or_player_tile(tile_id):
                                continue

                            # Update bounds
                            min_x = min(min_x, x)
                            max_x = max(max_x, x)
                            min_y = min(min_y, y)
                            max_y = max(max_y, y)
                            found_tiles = True
        # Fallback to old format if no layers
        elif self.map_data:
            for y in range(len(self.map_data)):
                for x in range(len(self.map_data[y])):
                    # Check if this tile is not empty (-1)
                    tile_id = self.map_data[y][x]
                    if tile_id != -1:
                        # Skip enemy and player tiles
                        if self.is_enemy_or_player_tile(tile_id):
                            continue

                        # Update bounds
                        min_x = min(min_x, x)
                        max_x = max(max_x, x)
                        min_y = min(min_y, y)
                        max_y = max(max_y, y)
                        found_tiles = True

        # If no tiles were found, use the full map dimensions
        if not found_tiles:
            min_x = 0
            max_x = self.map_width - 1
            min_y = 0
            max_y = self.map_height - 1

        return min_x, max_x, min_y, max_y

    def is_enemy_or_player_tile(self, tile_id):
        """Check if a tile is an enemy or player tile

        Args:
            tile_id: The tile ID to check

        Returns:
            bool: True if the tile is an enemy or player tile, False otherwise
        """
        # Convert tile_id to string for dictionary lookup
        tile_id_str = str(tile_id)

        # Check if we have the expanded mapping
        if not self.expanded_mapping:
            return False

        # Check if this tile is in the expanded mapping
        if tile_id_str in self.expanded_mapping:
            path = self.expanded_mapping[tile_id_str].get("path", "")

            # Check if this is an enemy or player tile
            if ("Enemies_Sprites/Phantom_Sprites" in path or
                "Enemies_Sprites/Bomberplant_Sprites" in path or
                "Enemies_Sprites/Spinner_Sprites" in path or
                "character/char_idle_" in path or
                "character/char_run_" in path or
                "character/char_attack_" in path or
                "character/char_hit_" in path or
                "character/char_shield_" in path):
                return True

        return False

    def calculate_center_offset(self, effective_screen_width: float, effective_screen_height: float):
        """Calculate the offset needed to center the used area of a map on the screen

        Args:
            effective_screen_width: The effective screen width (accounting for zoom)
            effective_screen_height: The effective screen height (accounting for zoom)
            
        Returns:
            tuple: (center_offset_x, center_offset_y) - the center offsets
        """
        # Find the bounds of the used area in the map
        min_x, max_x, min_y, max_y = self.find_used_area_bounds()

        # Calculate the size of the used area in pixels (use base grid size for logical coordinates)
        used_width = (max_x - min_x + 1) * self.base_grid_cell_size if max_x >= min_x else 0
        used_height = (max_y - min_y + 1) * self.base_grid_cell_size if max_y >= min_y else 0

        # Calculate the offset to the start of the used area (use base grid size for logical coordinates)
        area_offset_x = min_x * self.base_grid_cell_size
        area_offset_y = min_y * self.base_grid_cell_size

        # Calculate center offsets
        if used_width < effective_screen_width:
            # Center horizontally
            center_offset_x = (effective_screen_width - used_width) // 2 - area_offset_x
        else:
            # Used area is wider than or equal to the screen, no horizontal centering needed
            center_offset_x = 0

        if used_height < effective_screen_height:
            # Center vertically
            center_offset_y = (effective_screen_height - used_height) // 2 - area_offset_y
        else:
            # Used area is taller than or equal to the screen, no vertical centering needed
            center_offset_y = 0

        print(f"Used area bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        print(f"Used area size: {used_width}x{used_height} pixels")
        print(f"Center offset: ({center_offset_x}, {center_offset_y})")

        return center_offset_x, center_offset_y
