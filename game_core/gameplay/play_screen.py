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
# RelationHandler now imported from map_system
from game_core.sprite_cache import sprite_cache


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

        # Status message
        self.status_message = ""
        self.status_timer = 0

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
        self.show_game_over = False

        # Centralized save/load manager for all game data
        self.save_load_manager = SaveLoadManager()

        # Legacy components (for backward compatibility)
        self.game_state_saver = self.save_load_manager.game_state_saver
        self.character_inventory_saver = self.save_load_manager.character_inventory_saver
        self.player_location_tracker = self.save_load_manager.player_location_tracker

        # Teleportation flags and info
        self.is_teleporting = False
        self.teleport_info = None

        # Popup message for save notification
        self.popup_message = ""
        self.popup_timer = 0
        self.popup_duration = 120  # 2 seconds at 60 FPS

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
        """Get camera X position from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().camera_x
        return 0

    @camera_x.setter
    def camera_x(self, value):
        """Set camera X position in input system"""
        if hasattr(self, 'input_system'):
            self.input_system.get_zoom_controller().camera_x = value

    @property
    def camera_y(self):
        """Get camera Y position from input system"""
        if hasattr(self, 'input_system'):
            return self.input_system.get_zoom_controller().camera_y
        return 0

    @camera_y.setter
    def camera_y(self, value):
        """Set camera Y position in input system"""
        if hasattr(self, 'input_system'):
            self.input_system.get_zoom_controller().camera_y = value

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
            self.status_message = f"Error loading map: {error_msg}"
            self.status_timer = 180
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

        # Set up zoom controller callbacks
        zoom_controller = self.input_system.get_zoom_controller()
        zoom_controller.add_zoom_changed_callback(self._on_zoom_changed)

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

            # Set camera position from game state if available (for non-teleporting loads)
            if not self.is_teleporting and "game_state" in map_data and "camera" in map_data["game_state"]:
                self.camera_x = map_data["game_state"]["camera"]["x"]
                self.camera_y = map_data["game_state"]["camera"]["y"]

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

            # Calculate center offset for small maps
            self.calculate_center_offset()
            print(f"Map dimensions: {self.map_width}x{self.map_height} pixels: {self.map_width * self.grid_cell_size}x{self.map_height * self.grid_cell_size}")
            print(f"Screen dimensions: {self.width}x{self.height}")
            print(f"Center offset: ({self.center_offset_x}, {self.center_offset_y})")

            # Restore teleportation flags
            self.is_teleporting = was_teleporting
            self.teleport_info = teleport_info

            return True
        except Exception as e:
            self.status_message = f"Error loading map: {str(e)}"
            self.status_timer = 180
            return False

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

        # If game over screen is showing, handle its events
        if self.show_game_over:
            result = self.game_over_screen.handle_event(event)
            if result == "restart":
                # Reload the current map to restart
                self.reload_current_map()
                return None
            elif result == "exit":
                # Return to map selection
                return "back"
            return None

        # Handle common events (back button also saves)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Use the modularized input system to handle input events
        result = self.input_system.handle_event(event, mouse_pos)

        # Handle special return values from input system
        if result == "escape_pressed":
            return self._handle_escape_key()

        return result

    def _handle_escape_key(self):
        """Handle ESC key press for inventory toggling"""
        # If chest inventory is visible, close both inventories
        if self.chest_inventory.is_visible():
            # Save chest contents before closing
            if self.chest_inventory.current_chest_pos:
                self.lootchest_manager.set_chest_contents(
                    self.chest_inventory.current_chest_pos,
                    self.chest_inventory.inventory_items
                )
            self.chest_inventory.hide()
            self.player_inventory.hide(self.hud.inventory)
            # Save character inventory when closing the inventory screen
            self.save_character_inventory()
        # If only player inventory is visible, hide it and save inventory data
        elif self.player_inventory.is_visible():
            self.player_inventory.hide(self.hud.inventory)
            # Save character inventory when closing the inventory screen
            self.save_character_inventory()
        # Otherwise, show player inventory
        else:
            self.player_inventory.show(self.hud.inventory)
        return None

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

        # Recalculate center offset for small maps
        self.calculate_center_offset()

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

        # Reset game over state
        self.show_game_over = False

        # Restore the map name
        self.map_name = current_map

    def reload_current_map(self):
        """Reload the current map to restart the game"""
        if self.map_name:
            self.show_game_over = False
            self.load_map(self.map_name)

    # OLD CURSOR LOADING METHOD REMOVED - NOW HANDLED BY InputSystem
    # load_custom_cursor() has been replaced by the modularized input system

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
        if hasattr(self, 'layers') and self.layers:
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
        elif hasattr(self, 'map_data') and self.map_data:
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
        if not hasattr(self, 'expanded_mapping') or not self.expanded_mapping:
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

    def calculate_center_offset(self):
        """Calculate the offset needed to center the used area of a map on the screen

        This method scans the map data to find the bounds of the used area
        (where tiles exist) and centers that area on the screen.
        """
        # Find the bounds of the used area in the map
        min_x, max_x, min_y, max_y = self.find_used_area_bounds()

        # Calculate the size of the used area in pixels (use base grid size for logical coordinates)
        used_width = (max_x - min_x + 1) * self.base_grid_cell_size if max_x >= min_x else 0
        used_height = (max_y - min_y + 1) * self.base_grid_cell_size if max_y >= min_y else 0

        # Calculate the offset to the start of the used area (use base grid size for logical coordinates)
        area_offset_x = min_x * self.base_grid_cell_size
        area_offset_y = min_y * self.base_grid_cell_size

        # Use pre-calculated effective screen size for performance
        effective_screen_width = self.effective_screen_width
        effective_screen_height = self.effective_screen_height

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

        # Set the center offsets in the input system
        self.center_offset_x = center_offset_x
        self.center_offset_y = center_offset_y

        print(f"Used area bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        print(f"Used area size: {used_width}x{used_height} pixels")
        print(f"Center offset: ({center_offset_x}, {center_offset_y})")

    def update(self):
        """Update play screen logic"""
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= 1

        # Update popup message timer
        if self.popup_timer > 0:
            self.popup_timer -= 1

        # Get current mouse position for HUD updates
        mouse_pos = pygame.mouse.get_pos()

        # Update HUD (for inventory hover effects)
        self.hud.update(mouse_pos)

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

        # Update chest inventory
        if self.chest_inventory.is_visible():
            self.chest_inventory.update(mouse_pos)

        # Update player inventory
        if self.player_inventory.is_visible():
            self.player_inventory.update(mouse_pos)

        # If game over screen is showing, update it
        if self.show_game_over:
            self.game_over_screen.update()
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

            if player_died and not self.show_game_over:
                # Show game over screen
                self.show_game_over = True
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

            if game_over_triggered and not self.show_game_over:
                # Show game over screen
                self.show_game_over = True
                return

            # Check for teleportation using the coordinator
            relation = self.game_systems_coordinator.handle_teleportation_check(self.player)
            if relation:
                # Player touched a relation point, teleport to the corresponding point in the other map
                print(f"Player touched relation point: {relation['from_point']} -> {relation['to_point']} in map {relation['to_map']}")
                print(f"Teleporting to position: {relation['to_position']}")

                # Save the current player position using the player system
                self.player_system.save_player_location(self.map_name, self.player_location_tracker)
                print(f"Saved player location for map {self.map_name}: ({self.player.rect.x}, {self.player.rect.y}, {self.player.direction})")

                # Save the current game state before teleporting
                self.save_game()

                # Store the target position before loading the map
                target_position = relation['to_position']
                target_map = relation['to_map']
                print(f"Loading target map: {target_map}")
                print(f"Target position: {target_position}")

                # Set a flag to indicate we're teleporting
                self.is_teleporting = True

                # Store teleport information for after map load
                self.teleport_info = {
                    'target_position': target_position,
                    'target_map': target_map,
                    'to_point': relation['to_point']
                }

                # Make sure we have all relation points loaded before switching maps
                self.relation_handler.load_all_relation_points()

                # Print all available relation points for debugging
                print(f"Available relation points before map load: {self.relation_handler.relation_points}")

                # Clear all enemies before loading the new map
                self.enemy_manager.enemies = []

                # Load the target map
                load_success = self.load_map(target_map)
                print(f"Map load success: {load_success}")

                # Make sure the relation handler has the current map set correctly
                self.relation_handler.current_map = target_map
                print(f"Set relation handler current map to: {self.relation_handler.current_map}")

                # Set the current teleport point to the destination point
                # This prevents immediate re-teleportation until player steps off and back on
                grid_x, grid_y = target_position

                # Find the ID of the destination point
                point_id = None
                if target_map in self.relation_handler.relation_points:
                    for id_key, points in self.relation_handler.relation_points[target_map].items():
                        if relation['to_point'] in points and points[relation['to_point']] == target_position:
                            point_id = id_key
                            break

                self.relation_handler.current_teleport_point = {
                    'point_type': relation['to_point'],
                    'position': target_position,
                    'id': point_id
                }
                print(f"Set current teleport point to: {self.relation_handler.current_teleport_point}")

                # Print all available relation points after map load
                print(f"Available relation points after map load: {self.relation_handler.relation_points}")

                if load_success and self.player and self.is_teleporting:
                    # Position the player exactly at the center of the target relation point
                    # Convert grid coordinates to pixel coordinates using base grid size (logical coordinates)
                    grid_x, grid_y = target_position
                    pixel_x = grid_x * self.base_grid_cell_size
                    pixel_y = grid_y * self.base_grid_cell_size

                    # Calculate the exact center of the teleport point
                    point_center_x = pixel_x + (self.base_grid_cell_size // 2)
                    point_center_y = pixel_y + (self.base_grid_cell_size // 2)

                    # Set player position directly at the center of the teleport point
                    # Use the center of the player's rect to align with the center of the point
                    self.player.rect.centerx = point_center_x
                    self.player.rect.centery = point_center_y

                    # Save this position using the player system
                    self.player_system.save_player_location(target_map, self.player_location_tracker)
                    print(f"DEBUG: Saved teleport position for map {target_map}: ({self.player.rect.x}, {self.player.rect.y}, {self.player.direction})")

                    # Reset movement states
                    self.player.velocity = [0, 0]
                    self.player.is_knocked_back = False
                    self.player.knockback_velocity = [0, 0]

                    print(f"Positioned player exactly at center of teleport point: ({point_center_x}, {point_center_y})")

                    # Reset teleporting flag
                    self.is_teleporting = False

                    # Set map boundaries for the player using base grid size (logical coordinates)
                    self.player.set_map_boundaries(
                        0, 0,  # Min X, Min Y
                        self.map_width * self.base_grid_cell_size,  # Max X
                        self.map_height * self.base_grid_cell_size  # Max Y
                    )

                    # Update the player's position in the physics system
                    # This ensures animations and collision detection work correctly
                    self.player.update_position()

                    # Update camera to center on player using zoom-aware positioning
                    # Use pre-calculated effective screen size for performance
                    self.camera_x = self.player.rect.centerx - (self.effective_screen_width // 2)
                    self.camera_y = self.player.rect.centery - (self.effective_screen_height // 2)

                    # Clamp camera to map boundaries using base grid size (logical coordinates)
                    max_camera_x = max(0, self.map_width * self.base_grid_cell_size - self.effective_screen_width)
                    max_camera_y = max(0, self.map_height * self.base_grid_cell_size - self.effective_screen_height)
                    self.camera_x = max(0, min(self.camera_x, max_camera_x))
                    self.camera_y = max(0, min(self.camera_y, max_camera_y))
                    print(f"Camera position: ({self.camera_x}, {self.camera_y})")

                    # No teleport message

            # Collision detection is now handled by the PlayerSystem

            # Update camera to follow player smoothly
            # Center camera on player
            player_center_x = self.player.rect.centerx
            player_center_y = self.player.rect.centery

            # Calculate desired camera position (centered on player)
            # Use pre-calculated effective screen size for performance
            target_camera_x = player_center_x - (self.effective_screen_width // 2)
            target_camera_y = player_center_y - (self.effective_screen_height // 2)

            # Clamp camera to map boundaries (use base grid size for logical coordinates)
            max_camera_x = max(0, self.map_width * self.base_grid_cell_size - self.effective_screen_width)
            max_camera_y = max(0, self.map_height * self.base_grid_cell_size - self.effective_screen_height)

            # Ensure target is within map boundaries
            target_camera_x = max(0, min(target_camera_x, max_camera_x))
            target_camera_y = max(0, min(target_camera_y, max_camera_y))

            # Smooth camera movement - interpolate between current and target position
            # Use a consistent interpolation to prevent jitter
            camera_smoothing = 1.0  # Set to 1.0 to disable smoothing and eliminate black lines

            # Apply smoothing
            self.camera_x = target_camera_x * camera_smoothing + self.camera_x * (1 - camera_smoothing)
            self.camera_y = target_camera_y * camera_smoothing + self.camera_y * (1 - camera_smoothing)

            # Ensure camera position is valid after smoothing and convert to integer
            self.camera_x = int(max(0, min(self.camera_x, max_camera_x)))
            self.camera_y = int(max(0, min(self.camera_y, max_camera_y)))

    def draw(self, surface):
        """Draw the play screen using the modularized rendering pipeline"""
        # Use the rendering pipeline to render the complete frame
        if hasattr(self, 'rendering_pipeline') and self.rendering_pipeline.is_initialized:
            self.rendering_pipeline.render_frame(
                surface, self.camera_x, self.camera_y, self.center_offset_x, self.center_offset_y,
                self.zoom_factor, self.show_game_over
            )
        else:
            # Fallback to basic rendering if pipeline not initialized
            surface.fill((0, 0, 0))
            if self.show_game_over and self.game_over_screen:
                self.game_over_screen.draw(surface)

    def draw_single_map_layer(self, surface, layer_idx):
        """Draw a single map layer"""
        # Only draw if we have map data and layers
        if not hasattr(self, 'layers') or not self.layers or layer_idx >= len(self.layers):
            return

        # Get the layer
        layer = self.layers[layer_idx]
        if not layer["visible"]:
            return

        layer_data = layer["data"]

        # Calculate visible area - optimized using pre-calculated values
        start_x = int(self.camera_x // self.base_grid_cell_size)
        end_x = min(self.map_width, start_x + int(self.effective_screen_width // self.base_grid_cell_size) + 2)
        start_y = int(self.camera_y // self.base_grid_cell_size)
        end_y = min(self.map_height, start_y + int(self.effective_screen_height // self.base_grid_cell_size) + 2)

        # Draw visible tiles in this layer
        for y in range(start_y, end_y):
            if y >= len(layer_data):
                continue

            for x in range(start_x, end_x):
                if x >= len(layer_data[y]):
                    continue

                # Get tile ID at this position
                try:
                    tile_id = layer_data[y][x]

                    # Validate tile_id
                    if not isinstance(tile_id, int):
                        # Try to convert to int
                        try:
                            tile_id = int(tile_id)
                        except (ValueError, TypeError):
                            print(f"Warning: Invalid tile ID {tile_id} at position ({x}, {y}) in layer {layer_idx}")
                            continue

                    # Skip empty tiles
                    if tile_id == -1:
                        continue
                except (IndexError, TypeError) as e:
                    # Skip if the tile is out of bounds or layer_data is not properly formatted
                    print(f"Warning: Error accessing tile at ({x}, {y}) in layer {layer_idx}: {e}")
                    continue

                # Skip player and enemy tiles
                if str(tile_id) in self.expanded_mapping:
                    path = self.expanded_mapping[str(tile_id)].get("path", "")
                    # Only skip tiles that are specifically player or enemy sprites
                    if ("Enemies_Sprites/Phantom_Sprites" in path or
                        "Enemies_Sprites/Bomberplant_Sprites" in path or
                        "Enemies_Sprites/Spinner_Sprites" in path or
                        "character/char_idle_" in path or
                        "character/char_run_" in path or
                        "character/char_attack_" in path or
                        "character/char_hit_" in path or
                        "character/char_shield_" in path):
                        continue

                # Calculate screen position - proper logical to screen coordinate conversion
                # First calculate logical position using base grid size
                logical_x = x * self.base_grid_cell_size - self.camera_x + self.center_offset_x
                logical_y = y * self.base_grid_cell_size - self.camera_y + self.center_offset_y

                # Scale for zoom using pre-calculated zoom factor
                screen_x = logical_x * self.zoom_factor
                screen_y = logical_y * self.zoom_factor

                # Check if this is a key item and if it should be drawn
                if tile_id == self.key_item_id and hasattr(self, 'key_item_id'):
                    # ALWAYS skip drawing the original key if there's a collection animation in progress
                    # This is a direct check to ensure the key is never drawn during collection
                    if (x, y) in self.key_item_manager.collected_items or not self.key_item_manager.should_draw_key_item(x, y):
                        continue

                # Check if this is a crystal item and if it should be drawn
                if tile_id == self.crystal_item_id and hasattr(self, 'crystal_item_id'):
                    # ALWAYS skip drawing the original crystal if there's a collection animation in progress
                    # This is a direct check to ensure the crystal is never drawn during collection
                    if (x, y) in self.crystal_item_manager.collected_items or not self.crystal_item_manager.should_draw_crystal_item(x, y):
                        continue

                # Check if this is a lootchest item - only skip if it's currently opening or opened
                if tile_id == self.lootchest_item_id and hasattr(self, 'lootchest_item_id'):
                    # Only skip drawing if this lootchest is currently opening or already opened
                    chest_pos = (x, y)
                    if (chest_pos in self.lootchest_manager.opening_chests or
                        chest_pos in self.lootchest_manager.opened_chests):
                        continue  # Skip drawing - lootchest_manager handles opening/opened states



                # Check if this is an animated tile
                if self.animated_tile_manager.is_animated_tile_id(tile_id):
                    # Get the current frame of the animated tile
                    frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
                    if frame:
                        # For animated tiles, don't cache the scaled frames since they change every update
                        # Instead, scale them directly each time to ensure animation works
                        tile_size = (self.grid_cell_size, self.grid_cell_size)
                        if frame.get_size() != tile_size:
                            scaled_frame = pygame.transform.scale(frame, tile_size)
                        else:
                            scaled_frame = frame
                        # Draw the animated tile frame
                        surface.blit(scaled_frame, (screen_x, screen_y))
                # Draw the tile if we have it loaded
                elif tile_id in self.tiles:
                    # Use sprite cache for scaled tiles to improve performance
                    tile_size = (self.grid_cell_size, self.grid_cell_size)
                    if self.tiles[tile_id].get_size() != tile_size:
                        # Get the original path for this tile from expanded mapping
                        tile_path = None
                        for tid, tile_info in self.expanded_mapping.items():
                            if int(tid) == tile_id:
                                tile_path = tile_info["path"]
                                break

                        if tile_path and not tile_path.startswith("animated:"):
                            # Use cached scaling
                            scaled_tile = sprite_cache.get_scaled_sprite(tile_path, tile_size)
                        else:
                            # Fallback to direct scaling
                            scaled_tile = pygame.transform.scale(self.tiles[tile_id], tile_size)
                    else:
                        scaled_tile = self.tiles[tile_id]

                    # Draw the static tile
                    surface.blit(scaled_tile, (screen_x, screen_y))

    def draw_map_layers(self, surface, start_layer, end_layer):
        """Draw specific map layers using the modularized map system"""
        # Use the map system to render the specified layer range
        self.map_system.render_layer_range(
            surface, start_layer, end_layer, self.animated_tile_manager,
            self.camera_x, self.camera_y, self.center_offset_x, self.center_offset_y
        )

        # Handle special item visibility for these layers
        self._handle_special_item_visibility(surface)

    def _handle_special_item_visibility(self, surface):
        """Handle visibility of special items (keys, crystals, lootchests) that need custom logic"""
        # This method handles the special visibility logic that was previously in the old rendering methods
        # For now, this is a placeholder - the special item managers handle their own visibility
        # If needed, we can add custom rendering logic here for items that need to be hidden/shown
        # based on collection state or other conditions
        pass

    def draw_map(self, surface, skip_player_enemy_tiles=False):
        """Draw the map tiles using optimized direct rendering"""
        # Performance optimization: Use direct rendering to avoid method call overhead
        if hasattr(self.map_system.processor, 'layers') and self.map_system.processor.layers:
            # Direct layered rendering - bypass intermediate method calls
            self._draw_layered_map_optimized(surface, skip_player_enemy_tiles)
        elif hasattr(self.map_system.processor, 'map_data') and self.map_system.processor.map_data:
            # Direct legacy rendering - bypass intermediate method calls
            self._draw_legacy_map_optimized(surface, skip_player_enemy_tiles)

        # Handle special item visibility (key items, crystals, lootchests)
        # This needs to be done after rendering to override the map system's rendering
        self._handle_special_item_visibility(surface)

    def _draw_layered_map_optimized_range(self, surface, start_layer, end_layer):
        """Optimized layered map rendering for a specific range of layers with proper special item handling"""
        layers = self.map_system.processor.layers
        tiles = self.map_system.tile_manager.tiles

        # Calculate visible range once
        visible_left = self.camera_x - self.center_offset_x
        visible_top = self.camera_y - self.center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates using base grid size for logical coordinates
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1

        # Render specified layer range directly with special item handling
        for layer_idx in range(start_layer, min(end_layer + 1, len(layers))):
            layer = layers[layer_idx]
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
                        if str(tile_id) in self.expanded_mapping:
                            path = self.expanded_mapping[str(tile_id)].get("path", "")
                            if ("Enemies_Sprites/Phantom_Sprites" in path or
                                "Enemies_Sprites/Bomberplant_Sprites" in path or
                                "Enemies_Sprites/Spinner_Sprites" in path or
                                "character/char_idle_" in path or
                                "character/char_run_" in path or
                                "character/char_attack_" in path or
                                "character/char_hit_" in path or
                                "character/char_shield_" in path):
                                continue

                        # Check special items
                        if hasattr(self, 'key_item_id') and tile_id == self.key_item_id:
                            if (grid_x, grid_y) in self.key_item_manager.collected_items or not self.key_item_manager.should_draw_key_item(grid_x, grid_y):
                                continue

                        if hasattr(self, 'crystal_item_id') and tile_id == self.crystal_item_id:
                            if (grid_x, grid_y) in self.crystal_item_manager.collected_items or not self.crystal_item_manager.should_draw_crystal_item(grid_x, grid_y):
                                continue

                        if hasattr(self, 'lootchest_item_id') and tile_id == self.lootchest_item_id:
                            # Only skip drawing if this lootchest is currently opening or already opened
                            chest_pos = (grid_x, grid_y)
                            if (chest_pos in self.lootchest_manager.opening_chests or
                                chest_pos in self.lootchest_manager.opened_chests):
                                continue  # Skip drawing - lootchest_manager handles opening/opened states

                        # Calculate screen position - proper logical to screen coordinate conversion
                        logical_x = grid_x * self.base_grid_cell_size - self.camera_x + self.center_offset_x
                        logical_y = grid_y * self.base_grid_cell_size - self.camera_y + self.center_offset_y
                        screen_x = logical_x * self.zoom_factor
                        screen_y = logical_y * self.zoom_factor

                        # Render tile directly
                        self._render_tile_direct(surface, tile_id, screen_x, screen_y, tiles)

    def _draw_layered_map_optimized(self, surface, skip_player_enemy_tiles=False):
        """Optimized layered map rendering with minimal method call overhead"""
        layers = self.map_system.processor.layers
        tiles = self.map_system.tile_manager.tiles
        expanded_mapping = self.map_system.processor.expanded_mapping

        # Calculate visible range once
        visible_left = self.camera_x - self.center_offset_x
        visible_top = self.camera_y - self.center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates using base grid size for logical coordinates
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1

        # Render all layers directly
        for layer in layers:
            if not layer.get("visible", True):
                continue

            layer_data = layer["data"]

            # Direct tile rendering loop - no method calls
            for grid_y in range(int(start_y), min(int(end_y), len(layer_data))):
                row = layer_data[grid_y]
                for grid_x in range(int(start_x), min(int(end_x), len(row))):
                    tile_id = row[grid_x]

                    if tile_id != -1:  # -1 means empty tile
                        # Skip player/enemy tiles if requested
                        if skip_player_enemy_tiles and self._is_player_or_enemy_tile(tile_id):
                            continue

                        # Calculate screen position - proper logical to screen coordinate conversion
                        logical_x = grid_x * self.base_grid_cell_size - self.camera_x + self.center_offset_x
                        logical_y = grid_y * self.base_grid_cell_size - self.camera_y + self.center_offset_y
                        screen_x = logical_x * self.zoom_factor
                        screen_y = logical_y * self.zoom_factor

                        # Render tile directly
                        self._render_tile_direct(surface, tile_id, screen_x, screen_y, tiles)

    def _draw_legacy_map_optimized(self, surface, skip_player_enemy_tiles=False):
        """Optimized legacy map rendering with minimal method call overhead"""
        map_data = self.map_system.processor.map_data
        tiles = self.map_system.tile_manager.tiles

        # Calculate visible range once
        visible_left = self.camera_x - self.center_offset_x
        visible_top = self.camera_y - self.center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()

        # Convert to grid coordinates using base grid size for logical coordinates
        padding = max(1, 3 - int(self.base_grid_cell_size / 16))
        start_x = max(0, (visible_left // self.base_grid_cell_size) - padding)
        end_x = (visible_right // self.base_grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // self.base_grid_cell_size) - padding)
        end_y = (visible_bottom // self.base_grid_cell_size) + padding + 1

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
                    logical_x = grid_x * self.base_grid_cell_size - self.camera_x + self.center_offset_x
                    logical_y = grid_y * self.base_grid_cell_size - self.camera_y + self.center_offset_y
                    screen_x = logical_x * self.zoom_factor
                    screen_y = logical_y * self.zoom_factor

                    # Render tile directly
                    self._render_tile_direct(surface, tile_id, screen_x, screen_y, tiles)

    def _render_tile_direct(self, surface, tile_id, screen_x, screen_y, tiles):
        """Direct tile rendering with optimized caching"""
        # Check if this is an animated tile
        if self.animated_tile_manager.is_animated_tile_id(tile_id):
            # Get the current frame of the animated tile
            frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
            if frame:
                # For animated tiles, don't cache the scaled frames since they change every update
                # Instead, scale them directly each time to ensure animation works
                tile_size = (self.grid_cell_size, self.grid_cell_size)
                if frame.get_size() != tile_size:
                    scaled_frame = pygame.transform.scale(frame, tile_size)
                else:
                    scaled_frame = frame
                # Draw the animated tile frame
                surface.blit(scaled_frame, (screen_x, screen_y))
        # Draw the tile if we have it loaded
        elif tile_id in tiles:
            # Use sprite cache for scaled tiles to improve performance
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

    def handle_common_events(self, event, mouse_pos):
        """Override handle_common_events to add auto-save when clicking back button"""
        # Update back button
        self.back_button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button was clicked
            if self.back_button.is_clicked(event):
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

        # Save the inventory data
        return self.character_inventory_saver.save_inventory(self.player_inventory)

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

    def load_character_inventory(self):
        """Load the character's inventory using the centralized save/load manager"""
        # Skip if player inventory is not initialized
        if not self.player_inventory:
            return False, "Player inventory not initialized"

        # Use the centralized load manager
        success, message = self.save_load_manager.load_all(self)

        if success:
            # Log success using debug manager
            debug_manager.log("Character data loaded successfully", "player")
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

        # Recalculate center offset for small maps (after input system is updated)
        self.calculate_center_offset()

        # Adjust camera position to maintain the same view center
        # This prevents the view from jumping when resizing
        if self.player:
            # Update camera to center on player
            effective_screen_width = self.width / self.zoom_factor
            effective_screen_height = self.height / self.zoom_factor

            self.camera_x = self.player.rect.centerx - (effective_screen_width // 2)
            self.camera_y = self.player.rect.centery - (effective_screen_height // 2)

            # Clamp camera to map boundaries (use base grid size for logical coordinates)
            max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
            max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))
        else:
            # If no player, adjust camera based on the change in center offset
            delta_offset_x = self.center_offset_x - old_center_offset_x
            delta_offset_y = self.center_offset_y - old_center_offset_y

            # Adjust camera position to account for the change in center offset
            self.camera_x -= delta_offset_x
            self.camera_y -= delta_offset_y

            # Clamp camera to map boundaries (use base grid size for logical coordinates)
            effective_screen_width = self.width / self.zoom_factor
            effective_screen_height = self.height / self.zoom_factor
            max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
            max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))

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
