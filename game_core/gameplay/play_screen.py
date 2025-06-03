"""
Play Screen - displays and allows interaction with the selected map

This module handles the main gameplay screen where the player interacts with the game world.
It manages map loading, player movement, enemy interactions, inventory management, and game state saving.
"""
import os
import json
import pygame
from debug_utils import debug_manager
from character_system import PlayerCharacter
# CollisionHandler now imported from map_system
from playscreen_components.animation_system import AnimatedTileManager
from playscreen_components.item_system import KeyItemManager, CrystalItemManager, LootchestManager
from playscreen_components.inventory_system import ChestInventory
from playscreen_components.map_system import MapSystem
from playscreen_components.player_system import PlayerSystem, PlayerInventory
from playscreen_components.game_systems_coordinator import GameSystemsCoordinator
from playscreen_components.input_system import InputSystem
from playscreen_components.rendering_system import RenderingPipeline
from enemy_system import EnemyManager
# Removed unused imports
from base_screen import BaseScreen
from playscreen_components.ui_system import HUD, GameOverScreen
from playscreen_components.state_system import SaveLoadManager
from playscreen_components.camera_system import CameraController
from playscreen_components.ui_management import UIManager
from playscreen_components.teleportation_system import TeleportationManager
# RelationHandler now imported from map_system


class PlayScreen(BaseScreen):
    """Screen for playing a selected map"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

        # Grid settings
        self.base_grid_cell_size = 16  # Base 16x16 grid cells
        self.grid_cell_size = 16  # Current grid cell size (affected by zoom)

        # Camera speed for manual movement (if needed)
        self.camera_speed = 5

        # Map data
        self.map_name = ""
        self.map_data = {}
        self.map_width = 0
        self.map_height = 0
        self.tiles = {}  # Will store loaded tile images

        # Player character
        self.player = None

        # Initialize default handlers (will be replaced when map loads successfully)
        self.collision_handler = None
        self.relation_handler = None

        # Animated tiles manager
        self.animated_tile_manager = AnimatedTileManager()

        # Initialize the modularized map system
        self.map_system = MapSystem(self.grid_cell_size)

        # Initialize the modularized player system
        self.player_system = PlayerSystem(self.grid_cell_size)

        # Initialize the game systems coordinator
        self.game_systems_coordinator = GameSystemsCoordinator(self.base_grid_cell_size)

        # Initialize the modularized input system
        self.input_system = InputSystem(self.width, self.height, self.base_grid_cell_size)

        # Initialize the modularized rendering system
        self.rendering_pipeline = RenderingPipeline(self.width, self.height, self.base_grid_cell_size)

        # Initialize the modularized camera system
        self.camera_controller = CameraController(self.base_grid_cell_size)

        # Initialize the modularized UI management system
        self.ui_manager = UIManager(self.width, self.height)

        # Initialize the modularized teleportation system
        self.teleportation_manager = TeleportationManager(self.base_grid_cell_size)

        # Key item manager
        self.key_item_manager = KeyItemManager()

        # Crystal item manager
        self.crystal_item_manager = CrystalItemManager()

        # Lootchest manager
        self.lootchest_manager = LootchestManager()

        # Chest inventory (for displaying chest contents)
        self.chest_inventory = ChestInventory(self.width, self.height)

        # Player inventory (for displaying full inventory when ESC is pressed)
        self.player_inventory = PlayerInventory(self.width, self.height)

        # Set the callback for when a chest is opened
        print("Setting lootchest_manager callback to self.on_chest_opened")
        self.lootchest_manager.set_on_chest_opened_callback(self.on_chest_opened)
        print(f"Callback set: {self.lootchest_manager.on_chest_opened_callback is not None}")

        # Enemy manager
        self.enemy_manager = EnemyManager()

        # HUD for displaying player health
        self.hud = HUD(width, height)

        # Game over screen
        self.game_over_screen = GameOverScreen(width, height)

        # Centralized save/load manager for all game data
        self.save_load_manager = SaveLoadManager()

        # Legacy components (for backward compatibility)
        self.game_state_saver = self.save_load_manager.game_state_saver
        # character_inventory_saver removed - now handled by PlayerInventory directly
        self.player_location_tracker = self.save_load_manager.player_location_tracker

        # Initialize key item collection variables
        self.key_collected = False

        # Custom cursor - now handled by input system
        self.default_cursor = pygame.mouse.get_cursor()
        self.select_cursor = None

    # Properties to access zoom-related values from input system
    @property
    def zoom_factor(self):
        """Get current zoom factor from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().zoom_factor
        return 1.0

    @property
    def zoom_factor_inv(self):
        """Get inverse zoom factor from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().zoom_factor_inv
        return 1.0

    @property
    def effective_screen_width(self):
        """Get effective screen width from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().effective_screen_width
        return self.width

    @property
    def effective_screen_height(self):
        """Get effective screen height from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().effective_screen_height
        return self.height

    @property
    def camera_x(self):
        """Get camera X position from camera controller"""
        if hasattr(self, 'camera_controller'):
            return self.camera_controller.get_camera_position()[0]
        return 0

    @camera_x.setter
    def camera_x(self, value):
        """Set camera X position in camera controller"""
        if hasattr(self, 'camera_controller'):
            current_y = self.camera_controller.get_camera_position()[1]
            self.camera_controller.set_camera_position(value, current_y)

    @property
    def camera_y(self):
        """Get camera Y position from camera controller"""
        if hasattr(self, 'camera_controller'):
            return self.camera_controller.get_camera_position()[1]
        return 0

    @camera_y.setter
    def camera_y(self, value):
        """Set camera Y position in camera controller"""
        if hasattr(self, 'camera_controller'):
            current_x = self.camera_controller.get_camera_position()[0]
            self.camera_controller.set_camera_position(current_x, value)

    @property
    def center_offset_x(self):
        """Get center offset X from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().center_offset_x
        return 0

    @center_offset_x.setter
    def center_offset_x(self, value):
        """Set center offset X in input system"""
        if hasattr(self, 'input_system'):
            self.input_system.get_zoom_controller().center_offset_x = value

    @property
    def center_offset_y(self):
        """Get center offset Y from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().center_offset_y
        return 0

    @center_offset_y.setter
    def center_offset_y(self, value):
        """Set center offset Y in input system"""
        if hasattr(self, 'input_system'):
            self.input_system.get_zoom_controller().center_offset_y = value

    @property
    def is_teleporting(self):
        """Get teleportation state from teleportation manager"""
        if hasattr(self, 'teleportation_manager'):
            return self.teleportation_manager.is_teleporting
        return False

    @is_teleporting.setter
    def is_teleporting(self, value):
        """Set teleportation state in teleportation manager"""
        if hasattr(self, 'teleportation_manager'):
            self.teleportation_manager.is_teleporting = value

    @property
    def teleport_info(self):
        """Get teleport info from teleportation manager"""
        if hasattr(self, 'teleportation_manager'):
            return self.teleportation_manager.teleport_info
        return None

    @teleport_info.setter
    def teleport_info(self, value):
        """Set teleport info in teleportation manager"""
        if hasattr(self, 'teleportation_manager'):
            self.teleportation_manager.teleport_info = value

    def load_map(self, map_name):
        """Load a map from file using the modularized map system"""
        # Reset the enemy manager to clear all enemies from the previous map
        self.enemy_manager.enemies = []

        # Store whether we're teleporting before resetting flags
        was_teleporting = self.is_teleporting
        teleport_info = self.teleport_info

        self.map_name = map_name

        # Use the modularized map system to load the map
        success, error_msg = self.map_system.load_map(map_name, self.animated_tile_manager)

        if not success:
            self.ui_manager.show_status_message(f"Error loading map: {error_msg}", 180)
            return False

        # Get map information from the map system
        map_info = self.map_system.get_map_info()
        self.map_width, self.map_height = self.map_system.get_map_dimensions()

        # Get the raw map data for compatibility with existing systems
        map_data = self.map_system.get_current_map_data()

        # Update grid size in map system if it has changed
        self.map_system.set_grid_size(self.grid_cell_size)

        # For backward compatibility, set up the old attributes that other systems expect
        self.expanded_mapping = self.map_system.get_expanded_mapping()
        self.layers = self.map_system.get_layers()
        self.map_data = self.map_system.get_map_data()

        # Get handlers from map system
        self.collision_handler = self.map_system.get_collision_handler()
        self.relation_handler = self.map_system.get_relation_handler()

        # Initialize game systems coordinator with relation handler now available
        self.game_systems_coordinator.initialize_systems(
            self.enemy_manager, self.key_item_manager, self.crystal_item_manager,
            self.lootchest_manager, self.hud, self.animated_tile_manager,
            self.player_system, self.relation_handler
        )

        # Set up save callback for item collection
        self.game_systems_coordinator.inventory_coordinator.set_save_callback(self.save_character_inventory)

        # Initialize input system with game references
        self.input_system.initialize_systems(
            self.hud, self.player_inventory, self.chest_inventory, self.player,
            self.game_systems_coordinator, self.animated_tile_manager
        )

        # Set map data in input system
        self.input_system.set_map_data(self.layers, self.map_width, self.map_height)

        # Initialize rendering pipeline with all game systems
        self.rendering_pipeline.initialize_systems(
            self.map_system, self.player, self.enemy_manager, self.key_item_manager,
            self.crystal_item_manager, self.lootchest_manager, self.relation_handler,
            self.animated_tile_manager, self.hud, self.player_inventory, self.chest_inventory,
            self.game_over_screen
        )

        # Set the back button reference in the UI renderer
        self.rendering_pipeline.ui_renderer.set_back_button(self.back_button)

        # Initialize UI manager with all UI components
        self.ui_manager.initialize(self.hud, self.player_inventory, self.chest_inventory, self.game_over_screen, self.lootchest_manager)
        self.ui_manager.set_save_callback(self.save_character_inventory)

        # Set up save callbacks for inventory exit saves
        self.ui_manager.inventory_manager.set_save_callback(self.save_character_inventory)
        self.ui_manager.inventory_manager.set_game_state_save_callback(self._save_game_state_for_chest_exit)

        # Set UI manager reference in the UI renderer
        self.rendering_pipeline.ui_renderer.set_ui_manager(self.ui_manager)

        # Set cursor manager reference in the UI renderer
        cursor_manager = self.input_system.get_cursor_manager()
        self.rendering_pipeline.ui_renderer.set_cursor_manager(cursor_manager)

        # Set up zoom controller callbacks
        zoom_controller = self.input_system.get_zoom_controller()
        zoom_controller.add_zoom_changed_callback(self._on_zoom_changed)

        # Initialize camera controller with zoom controller and map data
        self.camera_controller.initialize(zoom_controller, self.player)
        self.camera_controller.set_map_data(
            self.layers, self.map_data, self.map_width, self.map_height, self.expanded_mapping
        )

        # Initialize teleportation manager with required systems
        self.teleportation_manager.initialize(
            self.player_system, self.camera_controller, self.relation_handler,
            self.player_location_tracker, self.save_game, self.load_map
        )



        # Set up tiles dictionary for backward compatibility
        self.tiles = {}
        for tile_id in range(1000):  # Reasonable range for tile IDs
            tile_surface = self.map_system.get_tile(tile_id)
            if tile_surface:
                self.tiles[tile_id] = tile_surface

        # Set current map BEFORE scanning for items to avoid clearing lootchests
        self.lootchest_manager.set_current_map(map_name)

        # Scan for special items (key items, crystals, lootchests) in the map layers using coordinator
        self._scan_for_special_items()

        try:

            # Load collision data if available in the map file
            # Note: This is now supplementary to the global collision data
            if "collision_data" in map_data and self.collision_handler:
                self.collision_handler.load_collision_data(map_data["collision_data"])

            # First, load all relation points from all maps to ensure we have a complete set
            print(f"Loading all relation points for teleportation")
            self.relation_handler.load_all_relation_points()

            # Then load relation points for the current map if available
            if "relation_points" in map_data:
                print(f"Found relation points in map data: {map_data['relation_points']}")
                self.relation_handler.load_relation_points(map_name, map_data["relation_points"])
            else:
                # Load relation points from file (will search for other maps with relation points)
                print(f"No relation points in map data, loading from file")
                self.relation_handler.load_relation_points(map_name)

            # Make sure the current map is set correctly in relation handler
            self.relation_handler.current_map = map_name
            print(f"Current map set to: {self.relation_handler.current_map}")
            print(f"All loaded relation points: {self.relation_handler.relation_points}")

            # Map processing is now handled by the MapSystem during load_map call above
            # No need to process the map format here anymore

            # Create player using the modularized player system
            teleport_position = None
            if self.is_teleporting and self.teleport_info:
                teleport_position = self.teleport_info.get('target_position')

            self.player = self.player_system.create_player(
                map_data, map_name, self.map_width, self.map_height,
                self.player_location_tracker, self.is_teleporting, teleport_position
            )

            # Update camera controller with player reference
            self.camera_controller.set_player(self.player)

            # Set camera position from game state if available (for non-teleporting loads)
            if not self.is_teleporting and "game_state" in map_data and "camera" in map_data["game_state"]:
                self.camera_controller.set_camera_from_save_data(
                    map_data["game_state"]["camera"]["x"],
                    map_data["game_state"]["camera"]["y"]
                )

            # Load enemies from saved game state if available
            enemies_loaded = False
            if "game_state" in map_data:
                game_state = map_data["game_state"]
                if "enemies" in game_state:
                    # Standard format with descriptive keys
                    self._load_enemies_from_game_state(game_state["enemies"])
                    enemies_loaded = True
                elif "e" in game_state:
                    # Legacy compact format
                    self._load_enemies_from_game_state(game_state["e"])
                    enemies_loaded = True

                # Load inventory data if available (HUD inventory only)
                if "inventory" in game_state:
                    self._load_inventory_from_game_state(game_state["inventory"])

                # NOTE: Player inventory is now loaded separately from SaveData/character_inventory.json
                # Ignore any old "player_inventory" data that might exist in map files
                if "player_inventory" in game_state:
                    print("INFO: Ignoring old player_inventory data in map file - now loaded from separate file")

                # Load collected keys data if available
                if "collected_keys" in game_state:
                    self._load_collected_keys_from_game_state(game_state["collected_keys"])

                # Load collected crystals data if available
                if "collected_crystals" in game_state:
                    self._load_collected_crystals_from_game_state(game_state["collected_crystals"])

                # Load opened lootchests data if available
                if "opened_lootchests" in game_state:
                    self._load_opened_lootchests_from_game_state(game_state["opened_lootchests"])

                # Load chest contents data if available
                if "chest_contents" in game_state:
                    self._load_chest_contents_from_game_state(game_state["chest_contents"])



            # Only load enemies from map data if they weren't loaded from game state
            if not enemies_loaded and "enemies" in map_data:
                self.enemy_manager.load_enemies_from_map(map_data)

            # Load character inventory data from separate save file
            # This happens after map loading so we have the player and inventory initialized
            self.load_character_inventory()

            # Set up collision system for unstuck functionality after all systems are initialized
            self._setup_collision_system_for_unstuck()

            # Calculate center offset for small maps using camera controller
            center_offset_x, center_offset_y = self.camera_controller.calculate_center_offset()
            print(f"Map dimensions: {self.map_width}x{self.map_height} pixels: {self.map_width * self.grid_cell_size}x{self.map_height * self.grid_cell_size}")
            print(f"Screen dimensions: {self.width}x{self.height}")
            print(f"Center offset: ({center_offset_x}, {center_offset_y})")

            # Restore teleportation flags
            self.is_teleporting = was_teleporting
            self.teleport_info = teleport_info

            return True
        except Exception as e:
            self.ui_manager.show_status_message(f"Error loading map: {str(e)}", 180)
            return False

    def _setup_collision_system_for_unstuck(self):
        """Set up collision system references for unstuck functionality"""
        try:
            # Get the current collision map data
            collision_map_data = self.map_system.get_collision_map_data()

            # Get map dimensions
            map_width, map_height = self.map_system.get_map_dimensions()

            # Set up collision system for teleportation unstuck logic
            self.teleportation_manager.set_collision_system(
                self.collision_handler, self.expanded_mapping, collision_map_data, map_width, map_height
            )

            # Set up collision system for input system unstuck functionality
            self.input_system.set_collision_system(
                self.player_system, self.collision_handler, self.expanded_mapping, collision_map_data, map_width, map_height
            )

            print("✅ Collision system set up for unstuck functionality")
        except Exception as e:
            print(f"⚠️ Warning: Could not set up collision system for unstuck: {e}")

    # OLD MAP PROCESSING METHOD REMOVED - NOW HANDLED BY MapSystem
    # process_layered_format_map() has been replaced by the modularized map system

    # OLD TILE MAPPING METHOD REMOVED - NOW HANDLED BY MapProcessor

    # OLD MAP PROCESSING METHOD REMOVED - NOW HANDLED BY MapSystem

    # OLD MAP PROCESSING METHOD REMOVED - NOW HANDLED BY MapSystem

    def _scan_for_special_items(self):
        """Scan the map layers for special items (keys, crystals, lootchests)"""
        # Set up item IDs from animated tile manager
        key_item_id = None
        crystal_item_id = None
        lootchest_item_id = None

        for tile_id, tile_name in self.animated_tile_manager.animated_tile_ids.items():
            if tile_name == "key_item":
                key_item_id = tile_id
                self.key_item_id = tile_id  # Keep for backward compatibility
            elif tile_name == "crystal_item":
                crystal_item_id = tile_id
                self.crystal_item_id = tile_id  # Keep for backward compatibility
            elif tile_name == "lootchest_item":
                lootchest_item_id = tile_id
                self.lootchest_item_id = tile_id  # Keep for backward compatibility

        # Use game systems coordinator to scan and setup items
        self.game_systems_coordinator.scan_and_setup_items(
            self.layers, key_item_id, crystal_item_id, lootchest_item_id
        )

        # Handle lootchest setup separately since it's more complex
        for layer_idx, layer in enumerate(self.layers):
            if not layer.get("visible", True):
                continue

            layer_data = layer.get("data", [])

            for y, row in enumerate(layer_data):
                for x, tile_id in enumerate(row):
                    # Check for lootchest items
                    if lootchest_item_id and tile_id == lootchest_item_id:
                        self.lootchest_manager.add_lootchest(x, y, tile_id, layer_idx)

    # OLD ZOOM METHODS REMOVED - NOW HANDLED BY InputSystem
    # zoom_in(), zoom_out(), reset_zoom(), update_zoom() have been replaced by the modularized input system

    def handle_event(self, event):
        """Handle events for the play screen using the modularized input system"""
        mouse_pos = pygame.mouse.get_pos()

        # Handle UI events first (game over, inventories, messages)
        ui_result = self.ui_manager.handle_event(event, mouse_pos)
        if ui_result == "restart_game":
            # Reload the current map to restart
            self.reload_current_map()
            return None
        elif ui_result == "exit_to_menu":
            # Return to map selection
            return "back"
        elif ui_result == "escape_handled":
            return None  # Event was handled by UI
        elif ui_result == "inventory_handled":
            # UI Manager handled the inventory click, don't pass to input system
            return None

        # Handle common events (back button also saves)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Use the modularized input system to handle input events
        result = self.input_system.handle_event(event, mouse_pos)

        # Handle special return values from input system
        if result == "escape_pressed":
            # Escape key handling is now managed by UI Manager
            # This should not happen as UI Manager handles escape first
            return None

        return result

    def _on_zoom_changed(self, grid_cell_size: int, zoom_factor: float, zoom_factor_inv: float):
        """Callback when zoom changes - update systems that depend on zoom"""
        self.grid_cell_size = grid_cell_size

        # Update the map system's grid size for rendering
        if hasattr(self, 'map_system'):
            self.map_system.set_grid_size(grid_cell_size)

        # Update the player system's grid size
        if hasattr(self, 'player_system'):
            self.player_system.set_grid_cell_size(grid_cell_size)

        # Update relation handler with base grid size for logical coordinates
        if hasattr(self, 'relation_handler'):
            self.relation_handler.grid_cell_size = self.base_grid_cell_size

        # Update rendering pipeline zoom settings
        if hasattr(self, 'rendering_pipeline'):
            self.rendering_pipeline.update_zoom(grid_cell_size, zoom_factor)

        # Recalculate center offset for small maps using camera controller
        if hasattr(self, 'camera_controller'):
            self.camera_controller.calculate_center_offset()

    def reset(self):
        """Reset the screen state but keep the map name"""
        # Store the current map name
        current_map = self.map_name

        # Reset map data
        self.map_data = {}
        self.map_width = 0
        self.map_height = 0
        self.tiles = {}

        # Clear the map system
        if hasattr(self, 'map_system'):
            self.map_system.clear_map()

        # Clear the player system
        if hasattr(self, 'player_system'):
            self.player_system.clear_player()

        # Reset camera
        self.camera_x = 0
        self.camera_y = 0

        # Reset player
        self.player = None

        # Reset collision handler - will be obtained from map_system

        # Reset enemy manager
        self.enemy_manager = EnemyManager()

        # Reset animated tile manager
        self.animated_tile_manager = AnimatedTileManager()

        # Reset game over state using UI manager
        if hasattr(self, 'ui_manager'):
            self.ui_manager.set_game_over(False)

        # Restore the map name
        self.map_name = current_map

    def reload_current_map(self):
        """Reload the current map to restart the game"""
        if self.map_name:
            self.ui_manager.set_game_over(False)
            self.load_map(self.map_name)

    # OLD CURSOR LOADING METHOD REMOVED - NOW HANDLED BY InputSystem
    # load_custom_cursor() has been replaced by the modularized input system

    # OLD CAMERA METHODS REMOVED - NOW HANDLED BY CameraController
    # find_used_area_bounds(), is_enemy_or_player_tile(), calculate_center_offset()
    # have been replaced by the modularized camera system

    def update(self):
        """Update play screen logic"""
        # Get current mouse position for UI updates
        mouse_pos = pygame.mouse.get_pos()

        # Update UI manager (handles messages, inventories, HUD, etc.)
        self.ui_manager.update(mouse_pos)

        # Update input system (handles cursor management)
        self.input_system.update(mouse_pos)

        # Update animated tiles
        self.animated_tile_manager.update()

        # Update key item manager
        self.key_item_manager.update()

        # Update crystal item manager
        self.crystal_item_manager.update()

        # Update lootchest manager
        self.lootchest_manager.update()

        # Update relation handler (if available)
        if self.relation_handler:
            self.relation_handler.update()

        # Game over screen and inventory updates are now handled by UI Manager
        if self.ui_manager.is_game_over_showing():
            return

        # Animated tiles are ready for use

        # Get collision map data once per frame for performance from Map System
        collision_map_data = self.map_system.get_collision_map_data()

        # Update player character using the modularized player system
        if self.player_system.get_player() and self.collision_handler:
            # Check if player died this frame (reuse collision_map_data)
            player_died = self.player_system.update_player(
                self.collision_handler, self.expanded_mapping, collision_map_data
            )

            if player_died and not self.ui_manager.is_game_over_showing():
                # Show game over screen
                self.ui_manager.set_game_over(True)
                return

            # Get the updated player reference
            self.player = self.player_system.get_player()

            # Update the player reference in the input system
            self.input_system.update_player(self.player)

            # Update the player reference in the rendering pipeline
            if hasattr(self, 'rendering_pipeline'):
                self.rendering_pipeline.update_player(self.player)

            # Update all game systems using the coordinator
            game_over_triggered = self.game_systems_coordinator.update_game_systems(
                self.player, self.collision_handler, self.expanded_mapping,
                collision_map_data, self.layers
            )

            if game_over_triggered and not self.ui_manager.is_game_over_showing():
                # Show game over screen
                self.ui_manager.set_game_over(True)
                return

            # Check for teleportation using the coordinator and teleportation manager
            relation = self.game_systems_coordinator.handle_teleportation_check(self.player)
            if relation:
                # Clear all enemies before teleporting
                self.enemy_manager.enemies = []

                # Handle teleportation using the teleportation manager
                teleport_success = self.teleportation_manager.handle_teleportation(relation, self.map_name)

                if teleport_success and self.player:
                    # Set map boundaries for the player using base grid size (logical coordinates)
                    self.player.set_map_boundaries(
                        0, 0,  # Min X, Min Y
                        self.map_width * self.base_grid_cell_size,  # Max X
                        self.map_height * self.base_grid_cell_size  # Max Y
                    )

            # Collision detection is now handled by the PlayerSystem

            # Update camera to follow player smoothly using camera controller
            self.camera_controller.update_camera_following()

    def draw(self, surface):
        """Draw the play screen using the modularized rendering pipeline"""
        # Use the rendering pipeline to render the complete frame
        if hasattr(self, 'rendering_pipeline') and self.rendering_pipeline.is_initialized:
            self.rendering_pipeline.render_frame(
                surface, self.camera_x, self.camera_y, self.center_offset_x, self.center_offset_y,
                self.zoom_factor, self.ui_manager.is_game_over_showing()
            )
        else:
            # Fallback to basic rendering if pipeline not initialized
            surface.fill((0, 0, 0))
            if self.ui_manager.is_game_over_showing() and self.game_over_screen:
                self.game_over_screen.draw(surface)

    # Legacy rendering methods removed - now handled by RenderingPipeline
    # draw_single_map_layer() has been replaced by the modularized rendering system

    # Legacy rendering methods removed - now handled by RenderingPipeline
    # draw_map_layers(), draw_map(), _handle_special_item_visibility() have been replaced by the modularized rendering system

    # Legacy rendering methods removed - now handled by RenderingPipeline
    # _draw_layered_map_optimized_range() has been replaced by the modularized rendering system

    # Legacy rendering methods removed - now handled by RenderingPipeline
    # _draw_layered_map_optimized() and _draw_legacy_map_optimized() have been replaced by the modularized rendering system

    # Legacy rendering methods removed - now handled by RenderingPipeline
    # _render_tile_direct() and _is_player_or_enemy_tile() have been replaced by the modularized rendering system

    def handle_common_events(self, event, mouse_pos):
        """Override handle_common_events to add auto-save when clicking back button"""
        # Update back button
        self.back_button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button was clicked
            if self.back_button.is_clicked(event):
                # Close any open inventories and save character inventory
                if hasattr(self, 'ui_manager') and self.ui_manager:
                    # Close all inventories
                    self.ui_manager.hide_all_inventories()
                    # Save character inventory
                    self.save_character_inventory()

                # Auto-save the game before returning to map selection
                if self.player and not self.player.is_dead and self.map_name:
                    # Make sure relation points are saved
                    if hasattr(self, 'relation_handler'):
                        print(f"Saving relation points for map: {self.map_name}")
                        print(f"Current map in relation handler: {self.relation_handler.current_map}")
                        print(f"All relation points: {self.relation_handler.relation_points}")

                        # Determine the correct map path - could be a main map or a related map
                        map_path = None

                        # First check if it's a main map
                        main_map_path = os.path.join("Maps", self.map_name, f"{self.map_name}.json")
                        if os.path.exists(main_map_path):
                            map_path = main_map_path
                            print(f"Found main map file for saving: {map_path}")
                        else:
                            # It might be a related map, search in all map folders
                            maps_dir = os.path.join("Maps")
                            if os.path.exists(maps_dir):
                                folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]
                                for folder_name in folders:
                                    folder_path = os.path.join(maps_dir, folder_name)
                                    related_map_path = os.path.join(folder_path, f"{self.map_name}.json")
                                    if os.path.exists(related_map_path):
                                        map_path = related_map_path
                                        print(f"Found related map file for saving: {map_path}")
                                        break

                        # If we found a map path, save the relation points
                        if map_path:
                            try:
                                with open(map_path, 'r') as f:
                                    map_data = json.load(f)

                                # Update relation points in the map data
                                # First check if the current map name is in the relation points
                                if self.map_name in self.relation_handler.relation_points:
                                    # Use the map name as the key
                                    relation_points = self.relation_handler.relation_points[self.map_name]
                                    print(f"Found relation points using map_name: {self.map_name}")
                                # Then check if the current map in the relation handler is in the relation points
                                elif self.relation_handler.current_map in self.relation_handler.relation_points:
                                    # Use the current map in the relation handler as the key
                                    relation_points = self.relation_handler.relation_points[self.relation_handler.current_map]
                                    print(f"Found relation points using current_map: {self.relation_handler.current_map}")
                                else:
                                    # No relation points found for this map
                                    print(f"No relation points found for map: {self.map_name}")
                                    relation_points = {}

                                # Always save relation points, even if empty
                                # This ensures the relation_points field is always present in the map data
                                map_data["relation_points"] = relation_points
                                print(f"Saving relation points: {relation_points}")

                                # Save the updated map data, preserving the is_main property
                                with open(map_path, 'w') as f:
                                    json.dump(map_data, f, indent=2)

                                print(f"Saved relation points for map {self.map_name}")
                            except Exception as e:
                                print(f"Error saving relation points: {e}")
                        else:
                            print(f"Could not find map file for {self.map_name}")

                    # Save the game state without showing messages
                    self.save_game()

                    # Reset teleportation flags when exiting a map
                    # This ensures that when re-entering the map, the player will spawn at the saved position
                    self.is_teleporting = False
                    self.teleport_info = None
                    if hasattr(self, 'relation_handler'):
                        self.relation_handler.current_teleport_point = None

                return "back"

        return None

    def _load_enemies_from_game_state(self, enemies_data):
        """Load enemies from saved game state"""
        # Clear existing enemies
        print(f"Clearing {len(self.enemy_manager.enemies)} existing enemies before loading from game state")
        self.enemy_manager.enemies = []

        # Create new enemies from saved data
        print(f"Loading {len(enemies_data)} enemies from game state")
        for enemy_data in enemies_data:
            # Check which format we're using
            if isinstance(enemy_data, dict):
                # Standard format with descriptive keys
                enemy_type = enemy_data.get("type", "phantom")

                # Get position
                position = enemy_data.get("position", {"x": 0, "y": 0})
                x = position.get("x", 0)
                y = position.get("y", 0)

                # Convert to grid coordinates for the enemy manager
                grid_x = x // 16
                grid_y = y // 16

                # Create the enemy
                enemy = self.enemy_manager.add_enemy(enemy_type, grid_x, grid_y)

                if enemy:
                    # Set exact position
                    enemy.rect.x = x
                    enemy.rect.y = y

                    # Set direction and state
                    enemy.direction = enemy_data.get("direction", "right")
                    enemy.state = enemy_data.get("state", "idle")

                    # Set health if available
                    if "health" in enemy_data and hasattr(enemy, 'current_health'):
                        enemy.current_health = enemy_data["health"]

                    # Set float position if available
                    if "float_position" in enemy_data and hasattr(enemy, 'float_x') and hasattr(enemy, 'float_y'):
                        enemy.float_x = enemy_data["float_position"].get("x", enemy.rect.x)
                        enemy.float_y = enemy_data["float_position"].get("y", enemy.rect.y)

            # Support for legacy compact format
            elif isinstance(enemy_data, list):
                # Legacy compact format: [type, x, y, direction, health, state, float_x?, float_y?]
                enemy_type = enemy_data[0]
                x = enemy_data[1]
                y = enemy_data[2]

                # Convert to grid coordinates for the enemy manager
                grid_x = x // 16
                grid_y = y // 16

                # Create the enemy
                enemy = self.enemy_manager.add_enemy(enemy_type, grid_x, grid_y)

                if enemy:
                    # Set exact position
                    enemy.rect.x = x
                    enemy.rect.y = y

                    # Set direction (expand from first letter)
                    direction_letter = enemy_data[3]
                    if direction_letter == 'r':
                        enemy.direction = "right"
                    elif direction_letter == 'l':
                        enemy.direction = "left"
                    elif direction_letter == 'u':
                        enemy.direction = "up"
                    elif direction_letter == 'd':
                        enemy.direction = "down"

                    # Set health if available
                    if len(enemy_data) > 4 and hasattr(enemy, 'current_health'):
                        enemy.current_health = enemy_data[4]

                    # Set state if available (expand from first letter)
                    if len(enemy_data) > 5:
                        state_letter = enemy_data[5]
                        if state_letter == 'i':
                            enemy.state = "idle"
                        elif state_letter == 'r':
                            enemy.state = "run"
                        elif state_letter == 'h':
                            enemy.state = "hit"

                    # Set float position if available
                    if len(enemy_data) > 7 and hasattr(enemy, 'float_x') and hasattr(enemy, 'float_y'):
                        enemy.float_x = enemy_data[6]
                        enemy.float_y = enemy_data[7]

    def save_game(self):
        """Save the current game state using the centralized save/load manager"""
        # Use the centralized save manager
        success, message = self.save_load_manager.save_all(self)

        if not success:
            print(f"Error saving game: {message}")

        return success



    def save_character_inventory(self):
        """Save the character's inventory to a separate file"""
        # Skip if player inventory is not initialized
        if not self.player_inventory:
            return False, "Player inventory not initialized"

        # IMPORTANT: Sync HUD inventory to player inventory before saving
        # This ensures that items in the HUD hotbar are saved even if the player
        # never opened the full inventory screen
        self._sync_hud_to_player_inventory()

        # Save the inventory data using the consolidated PlayerInventory
        return self.player_inventory.save_to_file()

    def _save_game_state_for_chest_exit(self):
        """Save game state when chest inventory is closed"""
        try:
            success, message = self.save_load_manager.save_quick(self)
            if not success:
                print(f"Warning: Failed to save game state on chest exit: {message}")
        except Exception as e:
            print(f"Error during chest exit game state save: {e}")

    def _sync_hud_to_player_inventory(self):
        """Sync HUD inventory items to the bottom row of player inventory

        This ensures that items in the HUD hotbar are transferred to the player inventory
        before saving, even if the player never opened the full inventory screen.
        """
        if not self.player_inventory or not self.hud or not self.hud.inventory:
            return

        # Calculate the starting index for the bottom row of player inventory
        bottom_row_start = self.player_inventory.grid_width * (self.player_inventory.grid_height - 1)

        # Copy items from HUD inventory to the bottom row of player inventory
        for i in range(min(self.hud.inventory.num_slots, self.player_inventory.grid_width)):
            # Copy HUD inventory item to corresponding slot in bottom row
            self.player_inventory.inventory_items[bottom_row_start + i] = self.hud.inventory.inventory_items[i]

    def _sync_player_to_hud_inventory(self):
        """Sync player inventory bottom row to HUD inventory

        This ensures that items in the player inventory bottom row are transferred to the HUD
        after loading, so they appear in the hotbar.
        """
        if not self.player_inventory or not self.hud or not self.hud.inventory:
            return

        # Calculate the starting index for the bottom row of player inventory
        bottom_row_start = self.player_inventory.grid_width * (self.player_inventory.grid_height - 1)

        # Copy items from player inventory bottom row to HUD inventory
        for i in range(min(self.hud.inventory.num_slots, self.player_inventory.grid_width)):
            # Copy player inventory bottom row item to corresponding HUD slot
            self.hud.inventory.inventory_items[i] = self.player_inventory.inventory_items[bottom_row_start + i]

    def load_character_inventory(self):
        """Load the character's inventory using the consolidated PlayerInventory"""
        # Skip if player inventory is not initialized
        if not self.player_inventory:
            return False, "Player inventory not initialized"

        # Load inventory using the consolidated PlayerInventory
        success, message = self.player_inventory.load_from_file()

        if success:
            # Update inventory images with proper sprites
            self._update_inventory_images()

            # Sync player inventory to HUD after loading
            self._sync_player_to_hud_inventory()

            # Log success using debug manager
            debug_manager.log("Character inventory loaded successfully", "player")
        else:
            # Log message using debug manager
            # This is expected when starting a new game
            debug_manager.log(f"Note: {message}", "player")

        return success, message

    def _update_inventory_images(self):
        """Update inventory item images with proper sprites from animated tile manager"""
        # Skip if player inventory is not initialized
        if not self.player_inventory:
            return

        # Go through each inventory slot
        for i in range(self.player_inventory.num_slots):
            item = self.player_inventory.inventory_items[i]
            if item:
                # Update image based on item name
                if item["name"] == "Key" and hasattr(self, 'key_item_id'):
                    # Get key image from animated tile manager
                    item["image"] = self.animated_tile_manager.get_animated_tile_frame(self.key_item_id)
                elif item["name"] == "Crystal" and hasattr(self, 'crystal_item_id'):
                    # Get crystal image from animated tile manager
                    item["image"] = self.animated_tile_manager.get_animated_tile_frame(self.crystal_item_id)
                # Other item types can be added here

    def _load_inventory_from_game_state(self, inventory_data):
        """Load inventory items from saved game state"""
        # Clear existing inventory
        for i in range(self.hud.inventory.num_slots):
            self.hud.inventory.inventory_items[i] = None

        # Load each inventory item
        for item_data in inventory_data:
            slot = item_data.get("slot", 0)
            if 0 <= slot < self.hud.inventory.num_slots:
                # Create the item
                item_name = item_data.get("name", "Unknown")
                item_count = item_data.get("count", 1)

                # For keys, we need to get the image from the animated tile manager
                if item_name == "Key" and hasattr(self, 'key_item_id'):
                    self.hud.inventory.inventory_items[slot] = {
                        "name": item_name,
                        "count": item_count,
                        "image": self.animated_tile_manager.get_animated_tile_frame(self.key_item_id)
                    }
                # For crystals, we need to get the image from the animated tile manager
                elif item_name == "Crystal" and hasattr(self, 'crystal_item_id'):
                    self.hud.inventory.inventory_items[slot] = {
                        "name": item_name,
                        "count": item_count,
                        "image": self.animated_tile_manager.get_animated_tile_frame(self.crystal_item_id)
                    }
                else:
                    # For other items, we would need to handle them appropriately
                    # For now, just create a placeholder
                    self.hud.inventory.inventory_items[slot] = {
                        "name": item_name,
                        "count": item_count,
                        "image": pygame.Surface((16, 16), pygame.SRCALPHA)  # Placeholder image
                    }
                    # Fill with a color based on the item name (for debugging)
                    self.hud.inventory.inventory_items[slot]["image"].fill((255, 0, 0, 128))

    def _load_collected_keys_from_game_state(self, collected_keys_data):
        """Load collected keys data from saved game state"""
        # Clear existing collected keys
        self.key_item_manager.collected_keys = []

        # Load each collected key position
        for key_pos in collected_keys_data:
            # Convert list [x, y] back to tuple (x, y)
            position = tuple(key_pos)

            # Add to collected keys list
            self.key_item_manager.collected_keys.append(position)

            # Also mark as collected in the key_items dictionary
            if position in self.key_item_manager.key_items:
                self.key_item_manager.key_items[position]["collected"] = True

            # Remove the key from all map layers
            self._remove_key_from_map_layers(position[0], position[1])

    def _load_collected_crystals_from_game_state(self, collected_crystals_data):
        """Load collected crystals data from saved game state"""
        # Clear existing collected crystals
        self.crystal_item_manager.collected_crystals = []

        # Load each collected crystal position
        for crystal_pos in collected_crystals_data:
            # Convert list [x, y] back to tuple (x, y)
            position = tuple(crystal_pos)

            # Add to collected crystals list
            self.crystal_item_manager.collected_crystals.append(position)

            # Also mark as collected in the crystal_items dictionary
            if position in self.crystal_item_manager.crystal_items:
                self.crystal_item_manager.crystal_items[position]["collected"] = True

            # Remove the crystal from all map layers
            self._remove_crystal_from_map_layers(position[0], position[1])

    def _load_opened_lootchests_from_game_state(self, opened_lootchests_data):
        """Load opened lootchests data from saved game state"""
        # Clear existing opened lootchests
        self.lootchest_manager.opened_chests = []

        # Load each opened lootchest position
        for chest_pos in opened_lootchests_data:
            # Convert list [x, y] back to tuple (x, y)
            position = tuple(chest_pos)

            # Add to opened lootchests list
            self.lootchest_manager.opened_chests.append(position)

            # Also mark as opened in the lootchests dictionary
            if position in self.lootchest_manager.lootchests:
                self.lootchest_manager.lootchests[position]["opened"] = True

    def _load_chest_contents_from_game_state(self, chest_contents_data):
        """Load chest contents data from saved game state"""
        # Load chest contents
        self.lootchest_manager.load_chest_contents_data(chest_contents_data, self.animated_tile_manager)

    def on_chest_opened(self, chest_pos, chest_contents):
        """Callback for when a chest is opened

        Args:
            chest_pos: Position of the chest (x, y) tuple
            chest_contents: List of items in the chest
        """
        print(f"PlayScreen.on_chest_opened called with chest_pos={chest_pos}")

        # Use game systems coordinator to handle chest opening
        chest_contents = self.game_systems_coordinator.handle_chest_opened_callback(
            chest_pos, chest_contents
        )

        print(f"Chest contents has {len(chest_contents)} items")

        # Show the player inventory
        self.player_inventory.show(self.hud.inventory)
        print("Player inventory shown")

        # Show the chest inventory with the chest contents
        self.chest_inventory.show(chest_pos, chest_contents)
        print("Chest inventory shown")

        # Position inventories side by side in the center of the screen
        screen_center_x = self.width // 2
        total_width = self.player_inventory.total_width + 40 + self.chest_inventory.total_width
        left_x = screen_center_x - (total_width // 2)

        # Update player inventory position
        self.player_inventory.x = left_x
        self.player_inventory.y = (self.height - self.player_inventory.total_height) // 2

        # Update player inventory slot rects
        for i in range(len(self.player_inventory.slot_rects)):
            row = i // self.player_inventory.grid_width
            col = i % self.player_inventory.grid_width

            # Calculate x position (same for all rows)
            x = self.player_inventory.x + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.player_inventory.grid_height - 1:  # Bottom row (quick access)
                y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row + self.player_inventory.extra_padding
            else:
                y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row

            self.player_inventory.slot_rects[i] = pygame.Rect(x, y, self.player_inventory.slot_size, self.player_inventory.slot_size)

        # Position chest inventory to the right of player inventory
        spacing = 40  # Spacing between inventories
        self.chest_inventory.x = self.player_inventory.x + self.player_inventory.total_width + spacing
        self.chest_inventory.y = self.player_inventory.y

        # Update chest inventory slot rects
        for i in range(len(self.chest_inventory.slot_rects)):
            row = i // self.chest_inventory.grid_width
            col = i % self.chest_inventory.grid_width
            x = self.chest_inventory.x + (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * col
            y = self.chest_inventory.y + (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * row
            self.chest_inventory.slot_rects[i] = pygame.Rect(x, y, self.chest_inventory.slot_size, self.chest_inventory.slot_size)

        print(f"Positioned inventories: Player at ({self.player_inventory.x}, {self.player_inventory.y}), Chest at ({self.chest_inventory.x}, {self.chest_inventory.y})")

        # Print debug information
        print(f"Opened chest at position {chest_pos} with {len(chest_contents)} items")

        # Position player inventory on the left side of the screen
        screen_center_x = self.width // 2
        total_width = self.player_inventory.total_width + 40 + self.chest_inventory.total_width
        left_x = screen_center_x - (total_width // 2)

        # Update player inventory position
        self.player_inventory.x = left_x
        self.player_inventory.y = (self.height - self.player_inventory.total_height) // 2

        # Update player inventory slot rects
        for i in range(len(self.player_inventory.slot_rects)):
            row = i // self.player_inventory.grid_width
            col = i % self.player_inventory.grid_width

            # Calculate x position (same for all rows)
            x = self.player_inventory.x + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * col

            # Calculate y position with extra padding before the bottom row
            if row == self.player_inventory.grid_height - 1:  # Bottom row (quick access)
                y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row + self.player_inventory.extra_padding
            else:
                y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row

            self.player_inventory.slot_rects[i] = pygame.Rect(x, y, self.player_inventory.slot_size, self.player_inventory.slot_size)

        # Chest inventory is already shown above - no need to show it again



    def _remove_key_from_map_layers(self, grid_x, grid_y):
        """Remove a key from all map layers at the given position"""
        # Skip if no layers or no key_item_id
        if not hasattr(self, 'layers') or not hasattr(self, 'key_item_id'):
            return

        # Remove the key from all map layers
        for layer_idx, layer in enumerate(self.layers):
            layer_data = layer["data"]
            if 0 <= grid_y < len(layer_data) and 0 <= grid_x < len(layer_data[grid_y]):
                if layer_data[grid_y][grid_x] == self.key_item_id:
                    # Remove the key item from this layer
                    layer_data[grid_y][grid_x] = -1

        # Also update the merged map data
        if hasattr(self, 'map_data') and self.map_data:
            if 0 <= grid_y < len(self.map_data) and 0 <= grid_x < len(self.map_data[grid_y]):
                self.map_data[grid_y][grid_x] = -1

    def _remove_crystal_from_map_layers(self, grid_x, grid_y):
        """Remove a crystal from all map layers at the given position"""
        # Skip if no layers or no crystal_item_id
        if not hasattr(self, 'layers') or not hasattr(self, 'crystal_item_id'):
            return

        # Remove the crystal from all map layers
        for layer_idx, layer in enumerate(self.layers):
            layer_data = layer["data"]
            if 0 <= grid_y < len(layer_data) and 0 <= grid_x < len(layer_data[grid_y]):
                if layer_data[grid_y][grid_x] == self.crystal_item_id:
                    # Remove the crystal item from this layer
                    layer_data[grid_y][grid_x] = -1

        # Also update the merged map data
        if hasattr(self, 'map_data') and self.map_data:
            if 0 <= grid_y < len(self.map_data) and 0 <= grid_x < len(self.map_data[grid_y]):
                self.map_data[grid_y][grid_x] = -1

    # OLD CURSOR AND HOVER METHODS REMOVED - NOW HANDLED BY InputSystem
    # is_hovering_lootchest() has been replaced by the modularized input system

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Store the old center offset for calculating camera adjustment
        old_center_offset_x = self.center_offset_x
        old_center_offset_y = self.center_offset_y

        # Call the base class resize method
        super().resize(new_width, new_height)

        # Update input system dimensions (this updates zoom controller)
        self.input_system.resize(new_width, new_height)

        # Update HUD dimensions
        self.hud.resize(new_width, new_height)

        # Handle camera resize using camera controller
        if hasattr(self, 'camera_controller'):
            self.camera_controller.handle_resize(old_center_offset_x, old_center_offset_y)

        # Update UI manager dimensions (handles inventory positioning)
        if hasattr(self, 'ui_manager'):
            self.ui_manager.resize(new_width, new_height)

        # Update rendering pipeline dimensions (handles UI renderer background overlay)
        if hasattr(self, 'rendering_pipeline'):
            self.rendering_pipeline.resize(new_width, new_height)

        # Legacy inventory resize handling (will be removed when fully migrated to UI Manager)
        # If both inventories are visible, maintain their side-by-side positioning
        if self.chest_inventory.is_visible() and self.player_inventory.is_visible():
            # Calculate the new positions based on the new screen dimensions
            screen_center_x = new_width // 2
            total_width = self.player_inventory.total_width + 40 + self.chest_inventory.total_width
            left_x = screen_center_x - (total_width // 2)

            # Update player inventory position
            self.player_inventory.x = left_x
            self.player_inventory.y = (new_height - self.player_inventory.total_height) // 2

            # Update player inventory slot rects
            for i in range(len(self.player_inventory.slot_rects)):
                row = i // self.player_inventory.grid_width
                col = i % self.player_inventory.grid_width

                # Calculate x position (same for all rows)
                x = self.player_inventory.x + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * col

                # Calculate y position with extra padding before the bottom row
                if row == self.player_inventory.grid_height - 1:  # Bottom row (quick access)
                    y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row + self.player_inventory.extra_padding
                else:
                    y = self.player_inventory.y + (self.player_inventory.slot_size + self.player_inventory.slot_padding) * row

                self.player_inventory.slot_rects[i] = pygame.Rect(x, y, self.player_inventory.slot_size, self.player_inventory.slot_size)

            # Position chest inventory to the right of player inventory
            spacing = 40  # Spacing between inventories
            self.chest_inventory.x = self.player_inventory.x + self.player_inventory.total_width + spacing
            self.chest_inventory.y = self.player_inventory.y

            # Update chest inventory slot rects
            for i in range(len(self.chest_inventory.slot_rects)):
                row = i // self.chest_inventory.grid_width
                col = i % self.chest_inventory.grid_width
                x = self.chest_inventory.x + (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * col
                y = self.chest_inventory.y + (self.chest_inventory.slot_size + self.chest_inventory.slot_padding) * row
                self.chest_inventory.slot_rects[i] = pygame.Rect(x, y, self.chest_inventory.slot_size, self.chest_inventory.slot_size)
        else:
            # Update chest inventory dimensions normally
            self.chest_inventory.resize(new_width, new_height)

            # Update player inventory dimensions normally
            self.player_inventory.resize(new_width, new_height)

        # Update game over screen dimensions
        self.game_over_screen.resize(new_width, new_height)

        # No need to update popup message position as it's calculated in the draw method

    # OLD SHARED CURSOR SYSTEM SETUP REMOVED - NOW HANDLED BY InputSystem
    # _setup_shared_cursor_system() has been replaced by the modularized input system
