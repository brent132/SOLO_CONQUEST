"""
Rendering Pipeline - Main coordinator for all rendering operations

This class coordinates the entire rendering pipeline for the PlayScreen,
managing the order and execution of different rendering phases.

RESPONSIBILITY: Main rendering coordinator

FEATURES:
- Coordinates layer, entity, UI, and effects rendering
- Manages rendering order and depth sorting
- Handles background and overlay rendering
- Integrates with all rendering subsystems
- Maintains performance optimizations
"""
import pygame

from .layer_renderer import LayerRenderer
from .entity_renderer import EntityRenderer
from .ui_renderer import UIRenderer
from .effects_renderer import EffectsRenderer


class RenderingPipeline:
    """Main coordinator for all rendering operations in PlayScreen"""
    
    def __init__(self, width: int, height: int, base_grid_cell_size: int = 16):
        self.width = width
        self.height = height
        self.base_grid_cell_size = base_grid_cell_size
        
        # Initialize rendering components
        self.layer_renderer = LayerRenderer(base_grid_cell_size)
        self.entity_renderer = EntityRenderer(base_grid_cell_size)
        self.ui_renderer = UIRenderer(width, height)
        self.effects_renderer = EffectsRenderer()
        
        # Rendering state
        self.is_initialized = False
        
        # Game system references (set during initialization)
        self.map_system = None
        self.player = None
        self.enemy_manager = None
        self.key_item_manager = None
        self.crystal_item_manager = None
        self.lootchest_manager = None
        self.relation_handler = None
        self.animated_tile_manager = None
        self.hud = None
        self.player_inventory = None
        self.chest_inventory = None
        self.game_over_screen = None
        
    def initialize_systems(self, map_system, player, enemy_manager, key_item_manager,
                          crystal_item_manager, lootchest_manager, relation_handler,
                          animated_tile_manager, hud, player_inventory, chest_inventory,
                          game_over_screen):
        """Initialize the rendering pipeline with game system references"""
        self.map_system = map_system
        self.player = player
        self.enemy_manager = enemy_manager
        self.key_item_manager = key_item_manager
        self.crystal_item_manager = crystal_item_manager
        self.lootchest_manager = lootchest_manager
        self.relation_handler = relation_handler
        self.animated_tile_manager = animated_tile_manager
        self.hud = hud
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.game_over_screen = game_over_screen
        
        # Initialize sub-renderers
        self.layer_renderer.initialize_systems(map_system, animated_tile_manager)
        self.entity_renderer.initialize_systems(
            player, enemy_manager, key_item_manager, crystal_item_manager,
            lootchest_manager, relation_handler, animated_tile_manager
        )
        self.ui_renderer.initialize_systems(
            hud, player_inventory, chest_inventory, game_over_screen
        )
        self.effects_renderer.initialize_systems(animated_tile_manager)

        # Connect layer renderer with entity renderer for special item visibility
        self.layer_renderer.set_entity_renderer(self.entity_renderer)
        
        self.is_initialized = True

    def resize(self, new_width: int, new_height: int):
        """Handle screen resize by updating all renderer dimensions"""
        self.width = new_width
        self.height = new_height

        # Update UI renderer dimensions
        self.ui_renderer.resize(new_width, new_height)

    def update_zoom(self, grid_cell_size: int, zoom_factor: float):
        """Update zoom settings for all renderers"""
        self.layer_renderer.set_grid_size(grid_cell_size)
        self.entity_renderer.set_zoom_factor(zoom_factor)
        self.effects_renderer.set_zoom_factor(zoom_factor)
    
    def update_player(self, player):
        """Update player reference"""
        self.player = player
        self.entity_renderer.update_player(player)
    
    def render_frame(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                    center_offset_x: int, center_offset_y: int, zoom_factor: float,
                    show_game_over: bool = False) -> None:
        """
        Render a complete frame with all game elements
        
        Args:
            surface: Surface to render to
            camera_x, camera_y: Camera position
            center_offset_x, center_offset_y: Center offsets for small maps
            zoom_factor: Current zoom factor
            show_game_over: Whether to show game over screen
        """
        if not self.is_initialized:
            return
        
        # Fill background
        surface.fill((0, 0, 0))
        
        # Skip game world rendering if game over screen is showing
        if show_game_over:
            self.ui_renderer.render_game_over_screen(surface)
            return
        
        # Render the game world in proper order
        self._render_game_world(surface, camera_x, camera_y, center_offset_x, 
                               center_offset_y, zoom_factor)
        
        # Render UI elements on top
        self._render_ui_elements(surface, zoom_factor)
    
    def _render_game_world(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                          center_offset_x: int, center_offset_y: int, zoom_factor: float):
        """Render the game world with proper depth sorting"""
        # Check if we have layered or legacy map format
        if hasattr(self.map_system, 'processor') and hasattr(self.map_system.processor, 'layers') and self.map_system.processor.layers:
            self._render_layered_world(surface, camera_x, camera_y, center_offset_x, 
                                     center_offset_y, zoom_factor)
        else:
            self._render_legacy_world(surface, camera_x, camera_y, center_offset_x, 
                                    center_offset_y, zoom_factor)
    
    def _render_layered_world(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                             center_offset_x: int, center_offset_y: int, zoom_factor: float):
        """Render layered map format with proper depth sorting and optimized calculations"""
        layers = self.map_system.processor.layers
        num_layers = len(layers)

        # Render first two layers (background) - optimized direct rendering
        self.layer_renderer.render_layer_range(surface, 0, 1, camera_x, camera_y,
                                              center_offset_x, center_offset_y)

        # Render special items for first two layers with pre-calculated offsets
        if num_layers > 0:
            self.entity_renderer.render_special_items_for_layers(
                surface, range(min(2, num_layers)), camera_x, camera_y,
                center_offset_x, center_offset_y
            )

        # Render entities (enemies, player, relation points) with pre-calculated values
        self.entity_renderer.render_entities(surface, camera_x, camera_y,
                                            center_offset_x, center_offset_y, zoom_factor)

        # Render remaining layers (foreground) if they exist
        if num_layers > 2:
            self.layer_renderer.render_layer_range(surface, 2, num_layers - 1,
                                                  camera_x, camera_y, center_offset_x, center_offset_y)

            # Render special items for remaining layers
            self.entity_renderer.render_special_items_for_layers(
                surface, range(2, num_layers), camera_x, camera_y,
                center_offset_x, center_offset_y
            )
    
    def _render_legacy_world(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                            center_offset_x: int, center_offset_y: int, zoom_factor: float):
        """Render legacy map format"""
        # Render map tiles (skip player/enemy tiles)
        self.layer_renderer.render_legacy_map(surface, camera_x, camera_y, 
                                             center_offset_x, center_offset_y, 
                                             skip_player_enemy_tiles=True)
        
        # Render special items (legacy method)
        self.entity_renderer.render_special_items_legacy(surface, camera_x, camera_y, 
                                                        center_offset_x, center_offset_y)
        
        # Render entities
        self.entity_renderer.render_entities(surface, camera_x, camera_y, 
                                            center_offset_x, center_offset_y, zoom_factor)
    
    def _render_ui_elements(self, surface: pygame.Surface, zoom_factor: float):
        """Render all UI elements"""
        # Render back button and zoom indicator
        self.ui_renderer.render_common_ui(surface, zoom_factor)
        
        # Render inventories
        self.ui_renderer.render_inventories(surface)
        
        # Render HUD if player exists
        if self.player:
            self.ui_renderer.render_hud(surface, self.player)
