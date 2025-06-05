"""
Map Processor - Handles processing different map formats

Extracted from PlayScreen to handle map format processing and tile mapping expansion.

RESPONSIBILITY: Processing different map formats and tile mapping

FEATURES:
- Handles layered format maps (with multiple layers)
- Handles single-layer format maps
- Handles old format maps (legacy)
- Expands complex tile mappings including loop patterns
- Processes direct path mappings
- Converts flat arrays to 2D arrays when needed

This component takes raw map data and processes it into a standardized format
that the rest of the system can work with. It handles the complexity of different
map formats, expands tile mappings (including complex loop patterns), and ensures
that all map data is in the correct 2D array format for rendering.
"""
import os
from typing import Dict, Any, List, Optional


class MapProcessor:
    """Handles processing different map formats and tile mapping"""
    
    def __init__(self):
        self.expanded_mapping = {}
        self.layers = []
        self.map_data = {}
    
    def process_map(self, map_data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Process map data based on its format.
        
        Args:
            map_data (Dict): The loaded map data
            
        Returns:
            Dict[str, Any]: Processed map information
        """
        # Check which format the map is in and process accordingly
        if "layers" in map_data and "tile_mapping" in map_data:
            # Layered format - process tile mapping and layers
            return self.process_layered_format(map_data)
        elif "map_data" in map_data and "tile_mapping" in map_data:
            # Single-layer array format - process tile mapping and map data
            return self.process_new_format(map_data)
        else:
            # Old format - process tiles directly
            return self.process_old_format(map_data)
    
    def process_layered_format(self, map_data: Dict[Any, Any]) -> Dict[str, Any]:
        """Process a map in the layered format"""
        pass  # MapProcessor: Processing layered format map

        # Process tile mapping
        tile_mapping = map_data["tile_mapping"]
        self.expanded_mapping = self._expand_tile_mapping(tile_mapping)
        pass  # Expanded mapping has tiles

        # Store all layers separately instead of merging them
        self.layers = []
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        pass  # Map dimensions

        # Process each layer
        layers_data = map_data.get("layers", [])
        pass  # Found layers to process

        for layer_idx, layer in enumerate(layers_data):
            layer_visible = layer.get("visible", True)
            layer_data = layer.get("data", layer.get("map_data", []))  # Handle both "data" and "map_data"

            pass  # Processing layer
            if isinstance(layer_data, list):
                pass  # Layer data length
                if layer_data and isinstance(layer_data[0], list):
                    pass  # Already 2D array
                elif layer_data and isinstance(layer_data[0], int):
                    pass  # Flat array, will convert to 2D

            # Convert flat array to 2D array if needed
            if isinstance(layer_data, list) and len(layer_data) > 0:
                if isinstance(layer_data[0], int):
                    # Flat array - convert to 2D
                    pass  # Converting flat array to 2D
                    layer_2d = []
                    for y in range(height):
                        row = []
                        for x in range(width):
                            index = y * width + x
                            if index < len(layer_data):
                                row.append(layer_data[index])
                            else:
                                row.append(-1)  # Empty tile
                        layer_2d.append(row)
                    layer_data = layer_2d
                    pass  # Converted to 2D array

            # Store the layer
            processed_layer = {
                "data": layer_data,
                "visible": layer_visible,
                "name": layer.get("name", f"Layer {layer_idx}")
            }
            self.layers.append(processed_layer)
            pass  # Added layer to processed layers

        pass  # Total processed layers
        
        return {
            "format": "layered",
            "expanded_mapping": self.expanded_mapping,
            "layers": self.layers,
            "width": width,
            "height": height
        }
    
    def process_new_format(self, map_data: Dict[Any, Any]) -> Dict[str, Any]:
        """Process a map in the new single-layer format"""
        # Process tile mapping
        tile_mapping = map_data["tile_mapping"]
        self.expanded_mapping = self._expand_tile_mapping(tile_mapping)
        
        # Store the single layer as map_data
        self.map_data = map_data.get("map_data", [])
        
        return {
            "format": "new_single_layer",
            "expanded_mapping": self.expanded_mapping,
            "map_data": self.map_data,
            "width": map_data.get("width", 0),
            "height": map_data.get("height", 0)
        }
    
    def process_old_format(self, map_data: Dict[Any, Any]) -> Dict[str, Any]:
        """Process a map in the old format"""
        # In old format, tiles are stored directly
        self.map_data = map_data.get("tiles", [])
        
        return {
            "format": "old",
            "map_data": self.map_data,
            "width": map_data.get("width", 0),
            "height": map_data.get("height", 0)
        }
    
    def _expand_tile_mapping(self, tile_mapping: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Expand tile mapping to include all tile IDs.

        Args:
            tile_mapping (Dict): The tile mapping from the map file

        Returns:
            Dict[str, Dict]: Expanded mapping with all tile IDs
        """
        expanded = {}

        for tileset_id, tileset_info in tile_mapping.items():
            # Handle different tile mapping formats
            if "type" in tileset_info and tileset_info["type"] == "loop":
                # Handle loop pattern format
                self._expand_loop_pattern(tileset_id, tileset_info, expanded)
            elif "path" in tileset_info:
                # Handle direct path format
                self._expand_direct_path(tileset_id, tileset_info, expanded)
            else:
                pass  # Unknown tile mapping format

        return expanded

    def _expand_loop_pattern(self, tileset_id: str, tileset_info: Dict[str, Any], expanded: Dict[str, Dict[str, Any]]):
        """Expand a loop pattern tile mapping"""
        try:
            start_id = tileset_info["start_id"]
            count = tileset_info["count"]
            pattern = tileset_info["pattern"]

            prefix = pattern["prefix"]
            digits = pattern["digits"]
            start = pattern["start"]
            suffix = pattern["suffix"]

            for i in range(count):
                tile_id = start_id + i
                tile_number = start + i

                # Format the tile number with leading zeros
                tile_number_str = str(tile_number).zfill(digits)
                tile_path = f"{prefix}{tile_number_str}{suffix}"

                expanded[str(tile_id)] = {
                    "path": tile_path,
                    "tileset": tileset_id,
                    "animated": False
                }

        except Exception as e:
            pass  # Error expanding loop pattern

    def _expand_direct_path(self, tileset_id: str, tileset_info: Dict[str, Any], expanded: Dict[str, Dict[str, Any]]):
        """Expand a direct path tile mapping"""
        try:
            if "start_id" in tileset_info:
                # Has start_id, might be a directory or single file
                tileset_path = tileset_info["path"]
                start_id = tileset_info["start_id"]

                # Check if this is a directory (tileset) or a single file
                if os.path.isdir(tileset_path):
                    # It's a directory - enumerate all PNG files
                    png_files = [f for f in os.listdir(tileset_path) if f.endswith('.png')]
                    png_files.sort()  # Ensure consistent ordering

                    for i, png_file in enumerate(png_files):
                        tile_id = start_id + i
                        tile_path = os.path.join(tileset_path, png_file)

                        expanded[str(tile_id)] = {
                            "path": tile_path,
                            "tileset": tileset_id,
                            "animated": False
                        }
                else:
                    # It's a single file
                    expanded[str(start_id)] = {
                        "path": tileset_path,
                        "tileset": tileset_id,
                        "animated": False
                    }
            else:
                # Direct tile ID mapping (like "390": {"path": "...", "tileset": 2})
                tile_path = tileset_info["path"]
                tileset_num = tileset_info.get("tileset", -1)

                expanded[tileset_id] = {
                    "path": tile_path,
                    "tileset": tileset_num,
                    "animated": tile_path.startswith("animated:")
                }

        except Exception as e:
            pass  # Error expanding direct path
    
    def get_tile_path(self, tile_id: int) -> Optional[str]:
        """
        Get the file path for a specific tile ID.
        
        Args:
            tile_id (int): The tile ID to look up
            
        Returns:
            Optional[str]: Path to the tile file, or None if not found
        """
        tile_info = self.expanded_mapping.get(str(tile_id))
        if tile_info:
            return tile_info["path"]
        return None
    
    def is_animated_tile(self, tile_id: int) -> bool:
        """
        Check if a tile ID represents an animated tile.
        
        Args:
            tile_id (int): The tile ID to check
            
        Returns:
            bool: True if the tile is animated
        """
        tile_info = self.expanded_mapping.get(str(tile_id))
        if tile_info:
            return tile_info.get("animated", False)
        return False
    
    def add_animated_tile(self, tile_id: int, tile_name: str):
        """
        Add an animated tile to the expanded mapping.
        
        Args:
            tile_id (int): The tile ID for the animated tile
            tile_name (str): The name of the animated tile
        """
        self.expanded_mapping[str(tile_id)] = {
            "path": f"animated:{tile_name}",
            "tileset": -1,  # Special value for animated tiles
            "animated": True
        }
