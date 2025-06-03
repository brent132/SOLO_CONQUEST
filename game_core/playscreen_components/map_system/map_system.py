"""
Map System - Main coordinator for all map-related functionality

This is the main interface for the map system that coordinates all the
individual components (loader, processor, tile manager, renderer).

RESPONSIBILITY: Main coordinator that brings everything together

FEATURES:
- Provides a single interface for all map operations
- Coordinates loading, processing, and rendering
- Manages map state and dimensions
- Provides memory usage information
- Handles cleanup and resource management

This is the main entry point for all map-related operations. It coordinates
the individual components (MapLoader, MapProcessor, TileManager, MapRenderer)
to provide a unified interface for loading, processing, and rendering maps.
It manages the overall state of the map system and provides high-level
operations that the rest of the game can use.
"""
import pygame
from typing import Dict, Any, Optional, Tuple, List

from .map_loader import MapLoader
from .map_processor import MapProcessor
from .tile_manager import TileManager
from .map_renderer import MapRenderer
from .collision_handler import CollisionHandler
from .relation_handler import RelationHandler


class MapSystem:
    """Main coordinator for all map-related functionality"""
    
    def __init__(self, grid_cell_size: int = 16):
        # Initialize all components
        self.loader = MapLoader()
        self.processor = MapProcessor()
        self.tile_manager = TileManager()
        self.renderer = MapRenderer(grid_cell_size)
        self.collision_handler = CollisionHandler(16)  # Always use base grid size
        self.relation_handler = RelationHandler(16)  # Always use base grid size
        
        # Current map state
        self.current_map_name = ""
        self.current_map_data = {}
        self.map_info = {}
        self.is_loaded = False
        
        # Map dimensions
        self.map_width = 0
        self.map_height = 0

        # Collision data caching for performance
        self._cached_collision_map_data = None
        self._collision_cache_valid = False
        
    def load_map(self, map_name: str, animated_tile_manager) -> Tuple[bool, str]:
        """
        Load a complete map including all processing and tile loading.
        
        Args:
            map_name (str): Name of the map to load
            animated_tile_manager: The animated tile manager instance
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            print(f"MapSystem: Loading map '{map_name}'")

            # Step 1: Load map data from file
            success, map_data, error_msg = self.loader.load_map_data(map_name)
            if not success:
                print(f"  Failed to load map data: {error_msg}")
                return False, error_msg

            print(f"  Successfully loaded map data")

            # Step 2: Get map information
            self.map_info = self.loader.get_map_info(map_data)
            self.map_width = self.map_info['width']
            self.map_height = self.map_info['height']
            print(f"  Map info: {self.map_width}x{self.map_height}")

            # Step 3: Process map based on format
            print(f"  Processing map format...")
            processed_info = self.processor.process_map(map_data)
            print(f"  Map processing complete. Format: {processed_info.get('format', 'unknown')}")

            # Step 4: Add animated tiles to the processor
            if hasattr(animated_tile_manager, 'animated_tile_ids'):
                print(f"  Adding {len(animated_tile_manager.animated_tile_ids)} animated tiles")
                for tile_id, tile_name in animated_tile_manager.animated_tile_ids.items():
                    self.processor.add_animated_tile(tile_id, tile_name)

            # Step 5: Load tiles from the expanded mapping
            if 'expanded_mapping' in processed_info:
                print(f"  Loading tiles from expanded mapping...")
                tile_errors = self.tile_manager.load_tiles_from_mapping(
                    processed_info['expanded_mapping']
                )
                if tile_errors:
                    print(f"  Some tiles failed to load: {tile_errors}")

            # Store current state
            self.current_map_name = map_name
            self.current_map_data = map_data
            self.is_loaded = True

            # Invalidate collision cache when map changes
            self._collision_cache_valid = False

            # Debug: Check layers
            layers = self.get_layers()
            print(f"  Available layers after processing: {len(layers)}")
            for i, layer in enumerate(layers):
                layer_data = layer.get("data", [])
                visible = layer.get("visible", True)
                name = layer.get("name", f"Layer {i}")
                print(f"    Layer {i} ({name}): visible={visible}, data_rows={len(layer_data) if isinstance(layer_data, list) else 'not_list'}")

            print(f"Map system successfully loaded map: {map_name}")
            print(f"Map format: {processed_info.get('format', 'unknown')}")
            print(f"Map dimensions: {self.map_width}x{self.map_height}")
            print(f"Loaded tiles: {self.tile_manager.get_tile_count()}")

            return True, ""

        except Exception as e:
            error_msg = f"Error in map system loading {map_name}: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def render_map(self, surface: pygame.Surface, animated_tile_manager,
                   camera_x: int, camera_y: int, center_offset_x: int, 
                   center_offset_y: int, skip_player_enemy_tiles: bool = False) -> None:
        """
        Render the current map to the surface.
        
        Args:
            surface: Surface to render to
            animated_tile_manager: The animated tile manager instance
            camera_x, camera_y: Camera position
            center_offset_x, center_offset_y: Center offsets for small maps
            skip_player_enemy_tiles: Whether to skip rendering player/enemy tiles
        """
        if not self.is_loaded:
            return
        
        # Render based on map format
        if hasattr(self.processor, 'layers') and self.processor.layers:
            # Layered format
            self.renderer.render_layered_map(
                surface, self.processor.layers, self.tile_manager.tiles,
                self.processor.expanded_mapping, animated_tile_manager,
                camera_x, camera_y, center_offset_x, center_offset_y,
                skip_player_enemy_tiles
            )
        elif hasattr(self.processor, 'map_data') and self.processor.map_data:
            # Legacy format
            self.renderer.render_legacy_map(
                surface, self.processor.map_data, self.tile_manager.tiles,
                animated_tile_manager, camera_x, camera_y, center_offset_x,
                center_offset_y, skip_player_enemy_tiles
            )
    
    def render_single_layer(self, surface: pygame.Surface, layer_idx: int,
                           animated_tile_manager, camera_x: int, camera_y: int,
                           center_offset_x: int, center_offset_y: int) -> None:
        """Render a single layer of the map"""
        if not self.is_loaded or not hasattr(self.processor, 'layers'):
            return
            
        self.renderer.render_single_layer(
            surface, self.processor.layers, layer_idx, self.tile_manager.tiles,
            self.processor.expanded_mapping, animated_tile_manager,
            camera_x, camera_y, center_offset_x, center_offset_y
        )
    
    def render_layer_range(self, surface: pygame.Surface, start_layer: int, end_layer: int,
                          animated_tile_manager, camera_x: int, camera_y: int,
                          center_offset_x: int, center_offset_y: int) -> None:
        """Render a range of map layers"""
        if not self.is_loaded or not hasattr(self.processor, 'layers'):
            return
            
        self.renderer.render_layer_range(
            surface, self.processor.layers, start_layer, end_layer,
            self.tile_manager.tiles, self.processor.expanded_mapping,
            animated_tile_manager, camera_x, camera_y, center_offset_x, center_offset_y
        )
    
    def set_grid_size(self, grid_cell_size: int):
        """Update the grid cell size (for zoom changes)"""
        self.renderer.set_grid_size(grid_cell_size)
    
    def get_map_info(self) -> Dict[str, Any]:
        """Get information about the current map"""
        return self.map_info.copy() if self.map_info else {}
    
    def get_map_dimensions(self) -> Tuple[int, int]:
        """Get the current map dimensions"""
        return self.map_width, self.map_height
    
    def get_tile(self, tile_id: int) -> Optional[pygame.Surface]:
        """Get a loaded tile by ID"""
        return self.tile_manager.get_tile(tile_id)
    
    def has_layers(self) -> bool:
        """Check if the current map has layers"""
        return hasattr(self.processor, 'layers') and bool(self.processor.layers)
    
    def get_layer_count(self) -> int:
        """Get the number of layers in the current map"""
        if self.has_layers():
            return len(self.processor.layers)
        return 0
    
    def get_expanded_mapping(self) -> Dict[str, Dict]:
        """Get the expanded tile mapping"""
        return getattr(self.processor, 'expanded_mapping', {})
    
    def get_layers(self) -> List[Dict]:
        """Get the map layers"""
        return getattr(self.processor, 'layers', [])
    
    def get_map_data(self) -> Any:
        """Get the raw map data"""
        return getattr(self.processor, 'map_data', {})
    
    def get_current_map_data(self) -> Dict[str, Any]:
        """Get the current loaded map data"""
        return self.current_map_data.copy() if self.current_map_data else {}
    
    def get_collision_map_data(self):
        """Get the appropriate map data for collision detection with caching for performance"""
        # Check if we have a valid cached version
        if self._collision_cache_valid and self._cached_collision_map_data is not None:
            return self._cached_collision_map_data

        # For layered maps, we need to merge all layers into a single 2D array for collision detection
        if hasattr(self.processor, 'layers') and self.processor.layers:
            # Create a merged map from all layers
            if not self.processor.layers:
                self._cached_collision_map_data = []
                self._collision_cache_valid = True
                return self._cached_collision_map_data

            # Get dimensions from the first layer
            first_layer = self.processor.layers[0]["data"]
            if not first_layer:
                self._cached_collision_map_data = []
                self._collision_cache_valid = True
                return self._cached_collision_map_data

            height = len(first_layer)
            width = len(first_layer[0]) if height > 0 else 0

            # Create merged map data
            merged_map = []
            for y in range(height):
                row = []
                for x in range(width):
                    # Start with empty tile
                    tile_id = -1

                    # Check each layer from bottom to top
                    for layer in self.processor.layers:
                        if not layer.get("visible", True):
                            continue

                        layer_data = layer["data"]
                        if y < len(layer_data) and x < len(layer_data[y]):
                            layer_tile_id = layer_data[y][x]
                            if layer_tile_id != -1:  # Not empty
                                tile_id = layer_tile_id  # Use the topmost non-empty tile

                    row.append(tile_id)
                merged_map.append(row)

            # Cache the result
            self._cached_collision_map_data = merged_map
            self._collision_cache_valid = True
            return merged_map
        else:
            # For legacy maps, use the existing map_data
            map_data = getattr(self.processor, 'map_data', {})
            self._cached_collision_map_data = map_data
            self._collision_cache_valid = True
            return map_data

    def clear_map(self):
        """Clear the current map and free resources"""
        self.tile_manager.clear_tiles()
        self.processor.expanded_mapping = {}
        self.processor.layers = []
        self.processor.map_data = {}
        self.current_map_name = ""
        self.current_map_data = {}
        self.map_info = {}
        self.is_loaded = False
        self.map_width = 0
        self.map_height = 0

        # Clear collision cache
        self._collision_cache_valid = False
        self._cached_collision_map_data = None

        # Clear handlers
        self.collision_handler = CollisionHandler(16)
        self.relation_handler = RelationHandler(16)

    def get_collision_handler(self):
        """Get the collision handler"""
        return self.collision_handler

    def get_relation_handler(self):
        """Get the relation handler"""
        return self.relation_handler
    
    def get_memory_usage_info(self) -> Dict[str, Any]:
        """Get memory usage information for the map system"""
        tile_info = self.tile_manager.get_memory_usage_info()
        
        return {
            "map_name": self.current_map_name,
            "is_loaded": self.is_loaded,
            "map_dimensions": f"{self.map_width}x{self.map_height}",
            "layer_count": self.get_layer_count(),
            "tile_memory": tile_info
        }
