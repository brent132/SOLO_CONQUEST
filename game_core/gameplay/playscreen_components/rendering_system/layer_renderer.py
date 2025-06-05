"""
Layer Renderer - Handles rendering of map layers and tiles

This class manages the rendering of map layers, including both layered
and legacy map formats, with performance optimizations.

RESPONSIBILITY: Map layer and tile rendering

FEATURES:
- Renders layered maps with proper layer ordering
- Renders legacy single-layer maps
- Optimizes rendering with visible tile culling
- Handles animated tiles through animated tile manager
- Supports different rendering modes
- Integrates with sprite caching for performance
"""
import pygame
from typing import Tuple


class LayerRenderer:
    """Handles rendering of map layers and tiles"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        self.grid_cell_size = base_grid_cell_size

        # System references
        self.map_system = None
        self.animated_tile_manager = None

        # Cached references for performance
        self.layers = None
        self.tiles = None
        self.expanded_mapping = None

        # Performance optimization: cache scaled tiles per zoom level
        self.zoom_tile_cache = {}  # {zoom_factor: {tile_id: scaled_surface}}
        self.current_zoom_factor = 1.0
        
    def initialize_systems(self, map_system, animated_tile_manager):
        """Initialize with game system references"""
        self.map_system = map_system
        self.animated_tile_manager = animated_tile_manager
        
        # Cache frequently accessed references
        if hasattr(map_system, 'processor'):
            self.layers = getattr(map_system.processor, 'layers', None)
            self.expanded_mapping = getattr(map_system.processor, 'expanded_mapping', {})
        
        if hasattr(map_system, 'tile_manager'):
            self.tiles = getattr(map_system.tile_manager, 'tiles', {})
    
    def set_grid_size(self, grid_cell_size: int):
        """Set the current grid cell size (affected by zoom)"""
        self.grid_cell_size = grid_cell_size

        # Update current zoom factor for cache management
        new_zoom_factor = grid_cell_size / self.base_grid_cell_size

        # Only clear cache if zoom factor actually changed
        if abs(new_zoom_factor - self.current_zoom_factor) > 0.01:
            self.current_zoom_factor = new_zoom_factor

            # Limit cache size to prevent memory issues
            if len(self.zoom_tile_cache) > 5:  # Keep only 5 zoom levels cached
                # Remove oldest zoom level (simple cleanup)
                oldest_zoom = min(self.zoom_tile_cache.keys())
                del self.zoom_tile_cache[oldest_zoom]
    
    def render_layer_range(self, surface: pygame.Surface, start_layer: int, end_layer: int,
                          camera_x: int, camera_y: int, center_offset_x: int, center_offset_y: int):
        """Render a range of map layers with optimized direct rendering"""
        if not self.layers:
            return

        # Use optimized direct rendering to avoid method call overhead
        self._render_layer_range_optimized(surface, start_layer, end_layer,
                                          camera_x, camera_y, center_offset_x, center_offset_y)

    def _render_layer_range_optimized(self, surface: pygame.Surface, start_layer: int, end_layer: int,
                                     camera_x: int, camera_y: int, center_offset_x: int, center_offset_y: int):
        """Optimized layer range rendering with minimal method call overhead (from original PlayScreen)"""
        # Calculate visible range once for all layers
        visible_left = camera_x - center_offset_x
        visible_top = camera_y - center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates using base grid size for logical coordinates
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1

        # Pre-calculate zoom factor once
        zoom_factor = self.grid_cell_size / self.base_grid_cell_size

        # Render specified layer range directly with special item handling
        for layer_idx in range(start_layer, min(end_layer + 1, len(self.layers))):
            layer = self.layers[layer_idx]
            if not layer.get("visible", True):
                continue

            layer_data = layer["data"]

            # Direct tile rendering loop with special item checks
            for grid_y in range(int(start_y), min(int(end_y), len(layer_data))):
                row = layer_data[grid_y]
                for grid_x in range(int(start_x), min(int(end_x), len(row))):
                    tile_id = row[grid_x]

                    if tile_id != -1:  # -1 means empty tile
                        # Skip player and enemy tiles
                        if self._is_player_or_enemy_tile(tile_id):
                            continue

                        # Check special items
                        if self._should_skip_special_item(tile_id, grid_x, grid_y):
                            continue

                        # Calculate screen position - proper logical to screen coordinate conversion
                        logical_x = grid_x * self.base_grid_cell_size - camera_x + center_offset_x
                        logical_y = grid_y * self.base_grid_cell_size - camera_y + center_offset_y
                        screen_x = logical_x * zoom_factor
                        screen_y = logical_y * zoom_factor

                        # Render tile directly
                        self._render_tile_direct(surface, tile_id, screen_x, screen_y)
    
    def render_single_layer(self, surface: pygame.Surface, layer_idx: int,
                           camera_x: int, camera_y: int, center_offset_x: int, center_offset_y: int):
        """Render a single map layer"""
        if not self.layers or layer_idx >= len(self.layers):
            return
        
        layer = self.layers[layer_idx]
        if not layer.get("visible", True):
            return
        
        layer_data = layer["data"]
        
        # Calculate visible area for performance optimization
        visible_range = self._calculate_visible_range(surface, camera_x, camera_y, 
                                                    center_offset_x, center_offset_y)
        start_x, end_x, start_y, end_y = visible_range
        
        # Render tiles in the visible range
        for grid_y in range(start_y, min(end_y, len(layer_data))):
            row = layer_data[grid_y]
            for grid_x in range(start_x, min(end_x, len(row))):
                tile_id = row[grid_x]
                
                if tile_id != -1:  # -1 means empty tile
                    # Skip player and enemy tiles
                    if self._is_player_or_enemy_tile(tile_id):
                        continue
                    
                    # Skip special items that have custom visibility logic
                    if self._should_skip_special_item(tile_id, grid_x, grid_y):
                        continue
                    
                    # Render the tile
                    self._render_tile(surface, tile_id, grid_x, grid_y, camera_x, camera_y, 
                                    center_offset_x, center_offset_y)
    
    def render_legacy_map(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                         center_offset_x: int, center_offset_y: int, skip_player_enemy_tiles: bool = False):
        """Render a map in legacy format (single layer) with optimized direct rendering"""
        if not hasattr(self.map_system, 'processor') or not hasattr(self.map_system.processor, 'map_data'):
            return

        map_data = self.map_system.processor.map_data
        if not map_data:
            return

        # Use optimized direct rendering to avoid method call overhead
        self._render_legacy_map_optimized(surface, map_data, camera_x, camera_y,
                                         center_offset_x, center_offset_y, skip_player_enemy_tiles)

    def _render_legacy_map_optimized(self, surface: pygame.Surface, map_data, camera_x: int, camera_y: int,
                                    center_offset_x: int, center_offset_y: int, skip_player_enemy_tiles: bool = False):
        """Optimized legacy map rendering with minimal method call overhead (from original PlayScreen)"""
        # Calculate visible range once
        visible_left = camera_x - center_offset_x
        visible_top = camera_y - center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates using base grid size for logical coordinates
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1

        # Pre-calculate zoom factor once
        zoom_factor = self.grid_cell_size / self.base_grid_cell_size

        # Direct tile rendering loop - no method calls
        for grid_y in range(int(start_y), min(int(end_y), len(map_data))):
            row = map_data[grid_y]
            for grid_x in range(int(start_x), min(int(end_x), len(row))):
                tile_id = row[grid_x]

                if tile_id != -1:  # -1 means empty tile
                    # Skip player/enemy tiles if requested
                    if skip_player_enemy_tiles and self._is_player_or_enemy_tile(tile_id):
                        continue

                    # Calculate screen position - proper logical to screen coordinate conversion
                    logical_x = grid_x * self.base_grid_cell_size - camera_x + center_offset_x
                    logical_y = grid_y * self.base_grid_cell_size - camera_y + center_offset_y
                    screen_x = logical_x * zoom_factor
                    screen_y = logical_y * zoom_factor

                    # Render tile directly
                    self._render_tile_direct(surface, tile_id, screen_x, screen_y)
    
    def _render_tile(self, surface: pygame.Surface, tile_id: int, grid_x: int, grid_y: int,
                    camera_x: int, camera_y: int, center_offset_x: int, center_offset_y: int):
        """Render a single tile at the specified grid position"""
        # Calculate screen position - proper logical to screen coordinate conversion
        logical_x = grid_x * self.base_grid_cell_size - camera_x + center_offset_x
        logical_y = grid_y * self.base_grid_cell_size - camera_y + center_offset_y

        # Scale for zoom
        zoom_factor = self.grid_cell_size / self.base_grid_cell_size
        screen_x = logical_x * zoom_factor
        screen_y = logical_y * zoom_factor

        # Use optimized direct rendering method (same as original PlayScreen)
        self._render_tile_direct(surface, tile_id, screen_x, screen_y)

    def _render_tile_direct(self, surface: pygame.Surface, tile_id: int, screen_x: float, screen_y: float):
        """Direct tile rendering with optimized zoom-level caching"""
        # Check if this is an animated tile
        if self.animated_tile_manager and self.animated_tile_manager.is_animated_tile_id(tile_id):
            # Get the current frame of the animated tile
            frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
            if frame:
                # For animated tiles, scale directly each time to ensure animation works
                tile_size = (self.grid_cell_size, self.grid_cell_size)
                if frame.get_size() != tile_size:
                    scaled_frame = pygame.transform.scale(frame, tile_size)
                else:
                    scaled_frame = frame
                # Draw the animated tile frame
                surface.blit(scaled_frame, (screen_x, screen_y))
        # Draw the tile if we have it loaded
        elif tile_id in self.tiles:
            # Use zoom-level cache for maximum performance
            if self.current_zoom_factor not in self.zoom_tile_cache:
                self.zoom_tile_cache[self.current_zoom_factor] = {}

            zoom_cache = self.zoom_tile_cache[self.current_zoom_factor]

            # Check if this tile is already cached for current zoom level
            if tile_id in zoom_cache:
                scaled_tile = zoom_cache[tile_id]
            else:
                # Need to scale and cache the tile
                tile_size = (self.grid_cell_size, self.grid_cell_size)
                original_tile = self.tiles[tile_id]

                if original_tile.get_size() != tile_size:
                    # Scale the tile
                    scaled_tile = pygame.transform.scale(original_tile, tile_size)
                else:
                    scaled_tile = original_tile

                # Cache the scaled tile for this zoom level
                zoom_cache[tile_id] = scaled_tile

                # Limit cache size per zoom level to prevent memory issues
                if len(zoom_cache) > 500:  # Limit to 500 tiles per zoom level
                    # Remove oldest entries (simple cleanup)
                    oldest_tiles = list(zoom_cache.keys())[:50]
                    for old_tile_id in oldest_tiles:
                        del zoom_cache[old_tile_id]

            surface.blit(scaled_tile, (screen_x, screen_y))

    
    def _calculate_visible_range(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                               center_offset_x: int, center_offset_y: int) -> Tuple[int, int, int, int]:
        """Calculate the range of tiles that are visible on screen"""
        # Calculate visible area
        visible_left = camera_x - center_offset_x
        visible_top = camera_y - center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()
        
        # Convert to grid coordinates with padding
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1
        
        return int(start_x), int(end_x), int(start_y), int(end_y)
    
    def _is_player_or_enemy_tile(self, tile_id: int) -> bool:
        """Check if a tile ID represents a player or enemy tile"""
        if str(tile_id) in self.expanded_mapping:
            path = self.expanded_mapping[str(tile_id)].get("path", "")
            return ("Enemies_Sprites/Phantom_Sprites" in path or
                    "Enemies_Sprites/Bomberplant_Sprites" in path or
                    "Enemies_Sprites/Spinner_Sprites" in path or
                    "character/char_idle_" in path or
                    "character/char_run_" in path or
                    "character/char_attack_" in path or
                    "character/char_hit_" in path or
                    "character/char_shield_" in path)
        return False
    
    def set_entity_renderer(self, entity_renderer):
        """Set the entity renderer for special item visibility checks"""
        self.entity_renderer = entity_renderer

    def clear_zoom_cache(self):
        """Clear the zoom tile cache to free memory"""
        self.zoom_tile_cache.clear()

    def get_cache_stats(self):
        """Get cache statistics for debugging"""
        total_cached_tiles = sum(len(cache) for cache in self.zoom_tile_cache.values())
        return {
            'zoom_levels_cached': len(self.zoom_tile_cache),
            'total_cached_tiles': total_cached_tiles,
            'current_zoom_factor': self.current_zoom_factor,
            'current_zoom_tiles': len(self.zoom_tile_cache.get(self.current_zoom_factor, {}))
        }

    def _should_skip_special_item(self, tile_id: int, grid_x: int, grid_y: int) -> bool:
        """Check if a special item should be skipped due to collection state"""
        if hasattr(self, 'entity_renderer') and self.entity_renderer:
            return self.entity_renderer.should_skip_special_item(tile_id, grid_x, grid_y)
        return False
