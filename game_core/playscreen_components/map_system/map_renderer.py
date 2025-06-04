"""
Map Renderer - Handles rendering maps and tiles

Extracted from PlayScreen to handle all map rendering operations including
layer rendering, tile scaling, and performance optimizations.

RESPONSIBILITY: Rendering maps and tiles

FEATURES:
- Renders layered maps with proper depth sorting
- Renders legacy single-layer maps
- Optimizes rendering with visible tile culling
- Handles animated tiles through the animated tile manager
- Supports different rendering modes (skip player/enemy tiles)
- Scales tiles properly for zoom levels

This component handles all rendering operations for maps and tiles. It supports
multiple map formats, optimizes performance through visible tile culling,
integrates with the animated tile manager for dynamic tiles, and properly
handles scaling for different zoom levels. It also supports different rendering
modes for various game states.
"""
import pygame
from typing import Dict, List, Optional, Tuple
from game_core.image_cache import sprite_cache


class MapRenderer:
    """Handles rendering maps, layers, and tiles with performance optimizations"""
    
    def __init__(self, grid_cell_size: int = 16):
        self.grid_cell_size = grid_cell_size
        self.base_grid_cell_size = 16
        
    def set_grid_size(self, grid_cell_size: int):
        """Set the current grid cell size (affected by zoom)"""
        self.grid_cell_size = grid_cell_size
    
    def render_layered_map(self, surface: pygame.Surface, layers: List[Dict], 
                          tiles: Dict[int, pygame.Surface], expanded_mapping: Dict[str, Dict],
                          animated_tile_manager, camera_x: int, camera_y: int, 
                          center_offset_x: int, center_offset_y: int,
                          skip_player_enemy_tiles: bool = False) -> None:
        """
        Render a layered map to the surface.
        
        Args:
            surface: Surface to render to
            layers: List of map layers
            tiles: Dictionary of loaded tiles
            expanded_mapping: Expanded tile mapping
            animated_tile_manager: Manager for animated tiles
            camera_x, camera_y: Camera position
            center_offset_x, center_offset_y: Center offsets for small maps
            skip_player_enemy_tiles: Whether to skip rendering player/enemy tiles
        """
        if skip_player_enemy_tiles:
            # Draw each layer individually to skip player/enemy tiles
            for layer_idx in range(len(layers)):
                self.render_single_layer(surface, layers, layer_idx, tiles, 
                                       expanded_mapping, animated_tile_manager,
                                       camera_x, camera_y, center_offset_x, center_offset_y)
        else:
            # Draw all layers at once
            self.render_layer_range(surface, layers, 0, len(layers) - 1, tiles,
                                  expanded_mapping, animated_tile_manager,
                                  camera_x, camera_y, center_offset_x, center_offset_y)
    
    def render_single_layer(self, surface: pygame.Surface, layers: List[Dict], 
                           layer_idx: int, tiles: Dict[int, pygame.Surface],
                           expanded_mapping: Dict[str, Dict], animated_tile_manager,
                           camera_x: int, camera_y: int, center_offset_x: int, 
                           center_offset_y: int) -> None:
        """Render a single map layer"""
        if layer_idx >= len(layers):
            return
            
        layer = layers[layer_idx]
        if not layer.get("visible", True):
            return
            
        layer_data = layer["data"]
        
        # Calculate visible tile range for performance
        visible_range = self._calculate_visible_range(surface, camera_x, camera_y, 
                                                    center_offset_x, center_offset_y)
        
        start_x, end_x, start_y, end_y = visible_range
        
        # Render tiles in the visible range
        for grid_y in range(start_y, end_y):
            if 0 <= grid_y < len(layer_data):
                row = layer_data[grid_y]
                for grid_x in range(start_x, end_x):
                    if 0 <= grid_x < len(row):
                        tile_id = row[grid_x]
                        
                        if tile_id != -1:  # -1 means empty tile
                            self._render_tile(surface, tile_id, grid_x, grid_y, tiles,
                                            expanded_mapping, animated_tile_manager,
                                            camera_x, camera_y, center_offset_x, center_offset_y)
    
    def render_layer_range(self, surface: pygame.Surface, layers: List[Dict],
                          start_layer: int, end_layer: int, tiles: Dict[int, pygame.Surface],
                          expanded_mapping: Dict[str, Dict], animated_tile_manager,
                          camera_x: int, camera_y: int, center_offset_x: int, 
                          center_offset_y: int) -> None:
        """Render a range of map layers"""
        for layer_idx in range(start_layer, min(end_layer + 1, len(layers))):
            self.render_single_layer(surface, layers, layer_idx, tiles,
                                   expanded_mapping, animated_tile_manager,
                                   camera_x, camera_y, center_offset_x, center_offset_y)
    
    def _render_tile(self, surface: pygame.Surface, tile_id: int, grid_x: int, grid_y: int,
                    tiles: Dict[int, pygame.Surface], expanded_mapping: Dict[str, Dict],
                    animated_tile_manager, camera_x: int, camera_y: int,
                    center_offset_x: int, center_offset_y: int) -> None:
        """Render a single tile at the specified grid position"""
        # Calculate screen position
        screen_x = (grid_x * self.grid_cell_size) - camera_x + center_offset_x
        screen_y = (grid_y * self.grid_cell_size) - camera_y + center_offset_y
        
        # Check if this is an animated tile
        if animated_tile_manager.is_animated_tile_id(tile_id):
            # Get the current frame of the animated tile
            frame = animated_tile_manager.get_animated_tile_frame(tile_id)
            if frame:
                # Use cached scaling for better performance
                tile_size = (self.grid_cell_size, self.grid_cell_size)
                if frame.get_size() != tile_size:
                    # Create a zoom-aware cache key for animated tiles
                    cache_key = (f"animated_tile_{tile_id}", self.grid_cell_size)

                    # Check if we have this scaled version cached
                    if cache_key in sprite_cache._scaled_cache:
                        scaled_frame = sprite_cache._scaled_cache[cache_key]
                    else:
                        # If not in cache, scale and cache it
                        scaled_frame = pygame.transform.scale(frame, tile_size)
                        # Store in cache with proper key format
                        sprite_cache._scaled_cache[cache_key] = scaled_frame
                else:
                    scaled_frame = frame
                # Draw the animated tile frame
                surface.blit(scaled_frame, (screen_x, screen_y))
        # Draw the tile if we have it loaded
        elif tile_id in tiles:
            # Use sprite cache for scaled tiles to improve performance
            tile_size = (self.grid_cell_size, self.grid_cell_size)
            if tiles[tile_id].get_size() != tile_size:
                # Get the original path for this tile from expanded mapping
                tile_path = None
                for tid, tile_info in expanded_mapping.items():
                    if int(tid) == tile_id:
                        tile_path = tile_info["path"]
                        break
                
                if tile_path and not tile_path.startswith("animated:"):
                    # Use cached scaling
                    scaled_tile = sprite_cache.get_scaled_sprite(tile_path, tile_size)
                else:
                    # Fallback to direct scaling
                    scaled_tile = pygame.transform.scale(tiles[tile_id], tile_size)
            else:
                scaled_tile = tiles[tile_id]
            
            # Draw the static tile
            surface.blit(scaled_tile, (screen_x, screen_y))
    
    def _calculate_visible_range(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                               center_offset_x: int, center_offset_y: int) -> Tuple[int, int, int, int]:
        """Calculate the range of tiles that are visible on screen"""
        # Calculate the visible area in world coordinates
        visible_left = camera_x - center_offset_x
        visible_top = camera_y - center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates with minimal padding for better performance
        # Reduce padding when zoomed to avoid rendering too many tiles
        padding = max(1, 3 - int(self.grid_cell_size / 16))  # Less padding at higher zoom
        start_x = max(0, (visible_left // self.grid_cell_size) - padding)
        end_x = (visible_right // self.grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.grid_cell_size) - padding)
        end_y = (visible_bottom // self.grid_cell_size) + padding + 1

        return int(start_x), int(end_x), int(start_y), int(end_y)
    
    def render_legacy_map(self, surface: pygame.Surface, map_data: List,
                         tiles: Dict[int, pygame.Surface], animated_tile_manager,
                         camera_x: int, camera_y: int, center_offset_x: int, 
                         center_offset_y: int, skip_player_enemy_tiles: bool = False) -> None:
        """
        Render a map in the legacy format (single layer).
        
        Args:
            surface: Surface to render to
            map_data: 2D array of tile IDs
            tiles: Dictionary of loaded tiles
            animated_tile_manager: Manager for animated tiles
            camera_x, camera_y: Camera position
            center_offset_x, center_offset_y: Center offsets
            skip_player_enemy_tiles: Whether to skip rendering player/enemy tiles
        """
        if not map_data:
            return
            
        # Calculate visible tile range for performance
        visible_range = self._calculate_visible_range(surface, camera_x, camera_y,
                                                    center_offset_x, center_offset_y)
        start_x, end_x, start_y, end_y = visible_range
        
        # Render tiles in the visible range
        for grid_y in range(start_y, min(end_y, len(map_data))):
            row = map_data[grid_y]
            for grid_x in range(start_x, min(end_x, len(row))):
                tile_id = row[grid_x]
                
                if tile_id != -1:  # -1 means empty tile
                    # Skip player/enemy tiles if requested
                    if skip_player_enemy_tiles and self._is_player_or_enemy_tile(tile_id):
                        continue
                        
                    self._render_legacy_tile(surface, tile_id, grid_x, grid_y, tiles,
                                           animated_tile_manager, camera_x, camera_y,
                                           center_offset_x, center_offset_y)
    
    def _render_legacy_tile(self, surface: pygame.Surface, tile_id: int, grid_x: int, grid_y: int,
                           tiles: Dict[int, pygame.Surface], animated_tile_manager,
                           camera_x: int, camera_y: int, center_offset_x: int, 
                           center_offset_y: int) -> None:
        """Render a single tile in legacy format"""
        # Calculate screen position
        screen_x = (grid_x * self.grid_cell_size) - camera_x + center_offset_x
        screen_y = (grid_y * self.grid_cell_size) - camera_y + center_offset_y
        
        # Check if this is an animated tile
        if animated_tile_manager.is_animated_tile_id(tile_id):
            frame = animated_tile_manager.get_animated_tile_frame(tile_id)
            if frame:
                tile_size = (self.grid_cell_size, self.grid_cell_size)
                if frame.get_size() != tile_size:
                    # Create a zoom-aware cache key for animated tiles
                    cache_key = (f"animated_tile_{tile_id}", self.grid_cell_size)

                    # Check if we have this scaled version cached
                    if cache_key in sprite_cache._scaled_cache:
                        scaled_frame = sprite_cache._scaled_cache[cache_key]
                    else:
                        # If not in cache, scale and cache it
                        scaled_frame = pygame.transform.scale(frame, tile_size)
                        # Store in cache with proper key format
                        sprite_cache._scaled_cache[cache_key] = scaled_frame
                else:
                    scaled_frame = frame
                surface.blit(scaled_frame, (screen_x, screen_y))
        elif tile_id in tiles:
            tile_size = (self.grid_cell_size, self.grid_cell_size)
            if tiles[tile_id].get_size() != tile_size:
                # Create a cache key for static tiles
                cache_key = (f"static_tile_{tile_id}", self.grid_cell_size)

                # Check if we have this scaled version cached
                if cache_key in sprite_cache._scaled_cache:
                    scaled_tile = sprite_cache._scaled_cache[cache_key]
                else:
                    # If not in cache, scale and cache it
                    scaled_tile = pygame.transform.scale(tiles[tile_id], tile_size)
                    # Store in cache with proper key format
                    sprite_cache._scaled_cache[cache_key] = scaled_tile
            else:
                scaled_tile = tiles[tile_id]
            surface.blit(scaled_tile, (screen_x, screen_y))
    
    def _is_player_or_enemy_tile(self, tile_id: int) -> bool:
        """Check if a tile ID represents a player or enemy tile"""
        # This would need to be implemented based on your tile ID ranges
        # For now, return False as a placeholder
        return False
