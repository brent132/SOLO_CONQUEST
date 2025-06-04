"""
Map Saver - handles saving maps to files
"""
import os
import json

class MapSaver:
    """Handles saving maps to files"""
    def __init__(self):
        # Create Maps directory if it doesn't exist
        os.makedirs("Maps", exist_ok=True)

        # Save status
        self.status_message = ""
        self.status_timer = 0

    def save_map(self, map_data, map_name, grid_cell_size, tileset_manager, layer_manager=None,
                collision_manager=None, relation_points=None, is_main=True, parent_folder=None):
        """Save the current map to a file using array format with tile IDs, layers, and collision data

        Args:
            map_data: Dictionary of map data
            map_name: Name of the map
            grid_cell_size: Size of grid cells
            tileset_manager: Tileset manager for tile information
            layer_manager: Optional layer manager for layer information
            collision_manager: Optional collision manager for collision data
            relation_points: Optional dictionary of relation points {'a': (x, y), 'b': (x, y)}
            is_main: Whether this is a main map (creates new folder) or related map (saved to existing folder)
            parent_folder: For related maps, the name of the parent folder to save to
        """
        # Check if any layer has data
        has_data = False
        for layer_data in map_data.values():
            if layer_data:
                has_data = True
                break

        if not has_data:
            self.status_message = "Error: Map is empty!"
            self.status_timer = 180  # Show for 3 seconds at 60 FPS
            return

        if not map_name:
            self.status_message = "Error: Please enter a map name!"
            self.status_timer = 180
            return

        # Calculate map dimensions across all layers
        width = 0
        height = 0
        for layer_data in map_data.values():
            if layer_data:
                layer_width = max([pos[0] for pos in layer_data.keys()], default=0) + 1
                layer_height = max([pos[1] for pos in layer_data.keys()], default=0) + 1
                width = max(width, layer_width)
                height = max(height, layer_height)

        # Create a mapping of tile paths to IDs
        tile_id_mapping = {}
        current_id = 0

        # First, create a mapping for all tiles in all tilesets
        for tileset_idx, tileset in enumerate(tileset_manager.tileset_buttons):
            for tile_data in tileset:
                source_path = tile_data["source_path"]
                if source_path not in tile_id_mapping:
                    tile_id_mapping[source_path] = {
                        "id": current_id,
                        "tileset": tileset_idx
                    }
                    current_id += 1

        # Add animated tiles to the mapping
        for button_data in tileset_manager.animated_tile_buttons:
            source_path = button_data.get("source_path", "")
            animated_tile_id = button_data.get("animated_tile_id", 0)
            if source_path and source_path not in tile_id_mapping:
                # Use the actual animated tile ID (1000+) instead of incrementing current_id
                tile_id_mapping[source_path] = {
                    "id": animated_tile_id,
                    "tileset": -1,  # Special value for animated tiles
                    "animated": True
                }
                pass  # Added animated tile to mapping

        # Process each layer
        layers_data = []

        # Determine how many layers to save
        layer_count = 1
        if layer_manager:
            layer_count = layer_manager.layer_count

        for layer_idx in range(layer_count):
            # Create a 2D array filled with -1 (empty tile)
            map_array = [[-1 for _ in range(width)] for _ in range(height)]

            # Fill the array with tile IDs for this layer
            layer_tiles = map_data.get(layer_idx, {})
            for (grid_x, grid_y), tile_data in layer_tiles.items():
                # Skip if grid_x or grid_y is out of bounds
                if grid_x < 0 or grid_x >= width or grid_y < 0 or grid_y >= height:
                    pass  # Warning: Skipping tile out of bounds
                    continue

                # Skip if tile_data is not a dictionary
                if not isinstance(tile_data, dict):
                    pass  # Warning: Skipping tile - not a dictionary
                    continue

                # Skip if source_path is not in tile_data
                if "source_path" not in tile_data:
                    pass  # Warning: Skipping tile - source_path missing
                    continue

                source_path = tile_data["source_path"]

                # Check if this is an animated tile
                if source_path.startswith("animated:"):
                    # Get the animated tile ID directly
                    animated_tile_id = tile_data.get("animated_tile_id", 0)
                    if animated_tile_id >= 1000:
                        # Use the animated tile ID directly
                        map_array[grid_y][grid_x] = animated_tile_id
                # Regular tile
                elif source_path in tile_id_mapping:
                    map_array[grid_y][grid_x] = tile_id_mapping[source_path]["id"]

            # Create layer data
            layer_data = {
                "map_data": map_array,
                "visible": True
            }

            # Add visibility info if layer manager is provided
            if layer_manager:
                layer_data["visible"] = layer_manager.layer_visibility[layer_idx]

            layers_data.append(layer_data)

        # Create a more efficient tile mapping using patterns
        # Group tiles by tileset and extract patterns
        tileset_groups = {}
        for path, info in tile_id_mapping.items():
            tileset_idx = info["tileset"]
            if tileset_idx not in tileset_groups:
                tileset_groups[tileset_idx] = []
            tileset_groups[tileset_idx].append((info["id"], path))

        # Create a compact tile mapping
        compact_mapping = {}
        for tileset_idx, tiles in tileset_groups.items():
            # Sort tiles by ID for consistency
            tiles.sort(key=lambda x: x[0])

            # Check if we can use a pattern (sequential tiles from same tileset)
            if len(tiles) > 1:
                # Get the base path and extract the pattern
                first_id, first_path = tiles[0]

                # Check if the paths follow a pattern with numbers
                import re
                pattern_match = re.search(r'(.*?)(\d+)(\.\w+)$', first_path)

                if pattern_match:
                    prefix = pattern_match.group(1)
                    number_part = pattern_match.group(2)
                    suffix = pattern_match.group(3)

                    # Check if all tiles follow the same pattern
                    all_match = True
                    expected_number = int(number_part)

                    for tile_id, path in tiles:
                        expected_path = f"{prefix}{expected_number:0{len(number_part)}d}{suffix}"
                        if path != expected_path:
                            all_match = False
                            break
                        expected_number += 1

                    if all_match:
                        # We can use a loop pattern
                        compact_mapping[f"tileset_{tileset_idx}"] = {
                            "type": "loop",
                            "start_id": first_id,
                            "count": len(tiles),
                            "pattern": {
                                "prefix": prefix,
                                "digits": len(number_part),
                                "start": int(number_part),
                                "suffix": suffix
                            }
                        }
                        continue

            # If we can't use a pattern, add individual mappings
            for tile_id, path in tiles:
                compact_mapping[str(tile_id)] = {
                    "path": path,
                    "tileset": tileset_idx
                }

        # Create map metadata with compact mapping and layers
        map_file_data = {
            "name": map_name,
            "width": width,
            "height": height,
            "tile_size": grid_cell_size,
            "tile_mapping": compact_mapping,
            "layers": layers_data
            # is_main tag will be set later based on the is_main parameter
        }

        # Collision data is now stored globally, not in individual map files
        # Save collision data to global file instead
        if collision_manager:
            collision_manager.save_global_collision_data()
            pass  # Collision data saved to global database

        # We'll set the player position from the placed player tile instead of the player_position_manager

        # Extract enemy data and player position from map tiles
        enemies = []
        player_start = None
        # Track enemy positions to avoid duplicates
        enemy_positions = set()

        for layer_idx, layer_data in enumerate(map_data.values()):
            for (grid_x, grid_y), tile_data in layer_data.items():
                if isinstance(tile_data, dict):
                    # Handle player character tile
                    if tile_data.get("is_player"):
                        # Only use the first player tile found (in case there are multiple)
                        if not player_start:
                            player_start = {
                                "x": grid_x,
                                "y": grid_y,
                                "direction": "down"  # Always use down direction for simplicity
                            }


                    # Handle enemy tile
                    elif tile_data.get("is_enemy"):
                        # Check if we already have an enemy at this position
                        position_key = (grid_x, grid_y)
                        if position_key not in enemy_positions:
                            enemy_positions.add(position_key)
                            enemies.append({
                                "x": grid_x,
                                "y": grid_y,
                                "type": tile_data.get("enemy_type", "phantom")
                            })


        # Add player start position if available
        if player_start:
            map_file_data["player_start"] = player_start

        # Add enemy data if available
        if enemies:
            map_file_data["enemies"] = enemies


        # Add relation points if available
        if relation_points:
            # Make a deep copy to avoid reference issues
            import copy
            relation_points_copy = copy.deepcopy(relation_points)

            # Ensure all positions are tuples
            for id_key, points in relation_points_copy.items():
                if 'a' in points and isinstance(points['a'], list):
                    relation_points_copy[id_key]['a'] = tuple(points['a'])
                if 'b' in points and isinstance(points['b'], list):
                    relation_points_copy[id_key]['b'] = tuple(points['b'])

            # Save the relation points
            map_file_data["relation_points"] = relation_points_copy


        # Determine the folder path based on whether this is a main map or related map
        if is_main:
            # Main map - create a new folder with the map name
            map_folder_path = os.path.join("Maps", map_name)
            map_file_data["is_main"] = True
        else:
            # Related map - save to the parent folder
            if not parent_folder:
                self.status_message = "Error: No parent folder specified for related map!"
                self.status_timer = 180
                return
            map_folder_path = os.path.join("Maps", parent_folder)
            map_file_data["is_main"] = False

        os.makedirs(map_folder_path, exist_ok=True)

        # Save to file with custom JSON formatting
        file_path = os.path.join(map_folder_path, f"{map_name}.json")
        try:
            # Create a custom JSON encoder to format map_data more compactly
            class CompactMapEncoder(json.JSONEncoder):
                def encode(self, obj):
                    if isinstance(obj, dict):
                        # Make a copy of the object to avoid modifying the original
                        result = obj.copy()

                        # Handle relation_points specially
                        relation_points = None
                        if "relation_points" in result:
                            relation_points = result["relation_points"]
                            del result["relation_points"]

                        # Handle layers specially
                        layers = None
                        if "layers" in result:
                            layers = result["layers"]
                            del result["layers"]

                        # Handle map_data specially
                        map_data = None
                        if "map_data" in result:
                            map_data = result["map_data"]
                            del result["map_data"]

                        # Encode the rest of the object normally
                        result_str = super().encode(result)

                        # Add back the special fields in the correct order
                        if result_str.endswith("}"):
                            # Remove the closing brace
                            result_str = result_str[:-1]

                            # Add relation_points if present
                            if relation_points is not None:
                                relation_points_str = self.format_relation_points(relation_points)
                                result_str += ', "relation_points": ' + relation_points_str

                            # Add layers if present
                            if layers is not None:
                                layers_str = self.format_layers(layers)
                                result_str += ', "layers": ' + layers_str

                            # Add map_data if present
                            if map_data is not None:
                                map_data_str = self.format_map_data(map_data)
                                result_str += ', "map_data": ' + map_data_str

                            # Add the closing brace
                            result_str += '}'

                        return result_str

                    # Handle tuples (for relation point coordinates)
                    # We'll keep tuples as lists in the JSON, but ensure they're properly handled
                    # when loading the map data
                    elif isinstance(obj, tuple):
                        # Convert tuple to list for JSON serialization
                        # This is fine because we convert lists back to tuples when loading
                        return list(obj)

                    return super().encode(obj)

                def format_relation_points(self, relation_points):
                    """Format relation points with proper structure"""
                    if not relation_points:
                        return "{}"

                    # Format the relation points
                    relation_str = "{\n"

                    # Sort the IDs to ensure consistent output
                    sorted_ids = sorted(relation_points.keys())

                    for idx, id_key in enumerate(sorted_ids):
                        points = relation_points[id_key]

                        # Start the entry for this ID
                        relation_str += f'    "{id_key}": {{\n'

                        # Add the points
                        point_entries = []
                        for point_type, position in points.items():
                            # Ensure position is properly formatted
                            if isinstance(position, tuple):
                                # Convert tuple to list for JSON serialization
                                position_list = list(position)
                                point_entries.append(f'      "{point_type}": {json.dumps(position_list)}')
                            elif isinstance(position, list):
                                # Use the list directly
                                point_entries.append(f'      "{point_type}": {json.dumps(position)}')
                            else:
                                # For any other type, use json.dumps
                                point_entries.append(f'      "{point_type}": {json.dumps(position)}')

                        # Join the point entries
                        relation_str += ",\n".join(point_entries)

                        # End the entry for this ID
                        if idx < len(sorted_ids) - 1:
                            relation_str += "\n    },\n"
                        else:
                            relation_str += "\n    }\n"

                    relation_str += "  }"
                    return relation_str

                def format_layers(self, layers):
                    # Format the layers array with proper structure
                    layers_str = "[\n"

                    # Format each layer
                    for layer_idx, layer in enumerate(layers):
                        layers_str += "    {\n"
                        layers_str += '      "visible": true,\n'
                        layers_str += '      "map_data": ' + self.format_map_data(layer["map_data"])

                        if layer_idx < len(layers) - 1:
                            layers_str += "\n    },\n"
                        else:
                            layers_str += "\n    }\n"

                    layers_str += "  ]"
                    return layers_str

                def format_map_data(self, map_data):
                    # Format the map data with each row on its own line
                    map_data_str = "[\n"

                    # Format each row
                    for row_idx, row in enumerate(map_data):
                        row_str = "      [" + ", ".join(str(tile) for tile in row) + "]"
                        if row_idx < len(map_data) - 1:
                            row_str += ","
                        map_data_str += row_str + "\n"

                    map_data_str += "    ]"
                    return map_data_str

            # Write the JSON file with custom formatting
            try:
                # First create a temporary file to avoid corruption
                temp_file_path = file_path + ".tmp"
                with open(temp_file_path, 'w') as f:
                    # Use the custom encoder for the main object
                    json_str = CompactMapEncoder(indent=2).encode(map_file_data)
                    f.write(json_str)

                # If the write was successful, rename the temporary file to the actual file
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(temp_file_path, file_path)
            except Exception as e:

                # If there was an error, try the direct approach as a fallback
                with open(file_path, 'w') as f:
                    # Use the custom encoder for the main object
                    json_str = CompactMapEncoder(indent=2).encode(map_file_data)
                    f.write(json_str)

            # No status messages for saving
        except Exception as e:
            self.status_message = f"Error saving map: {str(e)}"
            self.status_timer = 180

    def update(self):
        """Update status message timer"""
        if self.status_timer > 0:
            self.status_timer -= 1

    # _save_entrance_maps method removed

    def draw_status(self, surface, x, y, font):
        """Draw status message if active"""
        if self.status_timer > 0:
            status_color = (0, 150, 0) if "Error" not in self.status_message else (200, 0, 0)
            status_text = font.render(self.status_message, True, status_color)
            status_rect = status_text.get_rect(topleft=(x, y))
            surface.blit(status_text, status_rect)
