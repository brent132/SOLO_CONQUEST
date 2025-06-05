"""
Entity Renderer - Handles rendering of game entities

This class manages the rendering of all game entities including player,
enemies, special items, and relation points.

RESPONSIBILITY: Entity rendering

FEATURES:
- Renders player character with proper animations
- Renders enemies with zoom-aware scaling
- Renders special items (keys, crystals, lootchests) with collection states
- Renders relation points for teleportation
- Handles entity visibility and collection logic
- Supports both layered and legacy rendering modes
"""
import pygame


class EntityRenderer:
    """Handles rendering of all game entities"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        self.zoom_factor = 1.0

        # System references
        self.player = None
        self.enemy_manager = None
        self.key_item_manager = None
        self.crystal_item_manager = None
        self.lootchest_manager = None
        self.relation_handler = None
        self.animated_tile_manager = None

        # Special item IDs (cached for performance)
        self.key_item_id = None
        self.crystal_item_id = None
        self.lootchest_item_id = None

        # Performance optimization: cache grid cell size calculation
        self.cached_grid_cell_size = base_grid_cell_size
        self.last_zoom_factor = 1.0
        
    def initialize_systems(self, player, enemy_manager, key_item_manager, 
                          crystal_item_manager, lootchest_manager, relation_handler,
                          animated_tile_manager):
        """Initialize with game system references"""
        self.player = player
        self.enemy_manager = enemy_manager
        self.key_item_manager = key_item_manager
        self.crystal_item_manager = crystal_item_manager
        self.lootchest_manager = lootchest_manager
        self.relation_handler = relation_handler
        self.animated_tile_manager = animated_tile_manager
        
        # Cache special item IDs
        self._cache_special_item_ids()
    
    def update_player(self, player):
        """Update player reference"""
        self.player = player
    
    def set_zoom_factor(self, zoom_factor: float):
        """Set the current zoom factor with caching optimization"""
        # Only update cached values if zoom factor actually changed
        if abs(zoom_factor - self.last_zoom_factor) > 0.01:
            self.zoom_factor = zoom_factor
            self.last_zoom_factor = zoom_factor
            # Pre-calculate grid cell size to avoid repeated calculations
            self.cached_grid_cell_size = int(self.base_grid_cell_size * zoom_factor)
    
    def render_entities(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                       center_offset_x: int, center_offset_y: int, zoom_factor: float):
        """Render all entities in the correct order"""
        # Update zoom factor
        self.zoom_factor = zoom_factor
        
        # Calculate camera offset for entity rendering
        camera_offset_x = camera_x - center_offset_x
        camera_offset_y = camera_y - center_offset_y
        
        # Render enemies first (behind player)
        if self.enemy_manager:
            self.enemy_manager.draw(surface, camera_offset_x, camera_offset_y, zoom_factor)
        
        # Render player character
        if self.player:
            self.player.draw(surface, camera_offset_x, camera_offset_y, zoom_factor)
        
        # Render relation points
        if self.relation_handler:
            # Convert zoom factor back to grid cell size for relation handler
            grid_cell_size = int(self.base_grid_cell_size * zoom_factor)
            self.relation_handler.draw(surface, camera_offset_x, camera_offset_y, grid_cell_size)
    
    def render_special_items_for_layers(self, surface: pygame.Surface, layer_range,
                                       camera_x: int, camera_y: int, center_offset_x: int,
                                       center_offset_y: int):
        """Render special items for specific layers with optimized calculations"""
        # Pre-calculate values once to avoid repeated calculations
        camera_offset_x = camera_x - center_offset_x
        camera_offset_y = camera_y - center_offset_y
        # Use cached grid cell size to avoid repeated calculations
        grid_cell_size = self.cached_grid_cell_size

        # Render special items for each layer in the range
        for layer_idx in layer_range:
            # Use direct method calls to avoid overhead
            if self.key_item_manager:
                self.key_item_manager.draw_layer(surface, camera_offset_x, camera_offset_y,
                                                grid_cell_size, layer_idx)

            if self.crystal_item_manager:
                self.crystal_item_manager.draw_layer(surface, camera_offset_x, camera_offset_y,
                                                   grid_cell_size, layer_idx)

            if self.lootchest_manager:
                self.lootchest_manager.draw_layer(surface, camera_offset_x, camera_offset_y,
                                                grid_cell_size, layer_idx)
    
    def render_special_items_legacy(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                                   center_offset_x: int, center_offset_y: int):
        """Render special items using legacy method (for non-layered maps)"""
        # Calculate camera offset and use cached grid cell size
        camera_offset_x = camera_x - center_offset_x
        camera_offset_y = camera_y - center_offset_y
        # Use cached grid cell size to avoid repeated calculations
        grid_cell_size = self.cached_grid_cell_size

        # Render special items using legacy draw methods
        if self.key_item_manager:
            self.key_item_manager.draw(surface, camera_offset_x, camera_offset_y, grid_cell_size)

        if self.crystal_item_manager:
            self.crystal_item_manager.draw(surface, camera_offset_x, camera_offset_y, grid_cell_size)

        if self.lootchest_manager:
            self.lootchest_manager.draw(surface, camera_offset_x, camera_offset_y, grid_cell_size)
    
    def should_skip_special_item(self, tile_id: int, grid_x: int, grid_y: int) -> bool:
        """Check if a special item should be skipped due to collection state"""
        # Check key items
        if self.key_item_id and tile_id == self.key_item_id:
            if self.key_item_manager:
                return ((grid_x, grid_y) in self.key_item_manager.collected_items or 
                       not self.key_item_manager.should_draw_key_item(grid_x, grid_y))
        
        # Check crystal items
        if self.crystal_item_id and tile_id == self.crystal_item_id:
            if self.crystal_item_manager:
                return ((grid_x, grid_y) in self.crystal_item_manager.collected_items or 
                       not self.crystal_item_manager.should_draw_crystal_item(grid_x, grid_y))
        
        # Check lootchest items
        if self.lootchest_item_id and tile_id == self.lootchest_item_id:
            if self.lootchest_manager:
                chest_pos = (grid_x, grid_y)
                return (chest_pos in self.lootchest_manager.opening_chests or
                       chest_pos in self.lootchest_manager.opened_chests)
        
        return False
    
    def _cache_special_item_ids(self):
        """Cache special item IDs for performance"""
        if self.animated_tile_manager:
            for tile_id, tile_name in self.animated_tile_manager.animated_tile_ids.items():
                if tile_name == "key_item":
                    self.key_item_id = tile_id
                elif tile_name == "crystal_item":
                    self.crystal_item_id = tile_id
                elif tile_name == "lootchest_item":
                    self.lootchest_item_id = tile_id
