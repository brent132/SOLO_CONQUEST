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
from gameplay.collision_handler import CollisionHandler
from gameplay.animated_tile_manager import AnimatedTileManager
from gameplay.key_item_manager import KeyItemManager
from gameplay.crystal_item_manager import CrystalItemManager
from gameplay.lootchest_manager import LootchestManager
from gameplay.chest_inventory import ChestInventory
from gameplay.player_inventory import PlayerInventory
from enemy_system import EnemyManager
# Removed unused imports
from base_screen import BaseScreen
from gameplay.hud import HUD
from gameplay.game_over_screen import GameOverScreen
from gameplay.game_state_saver import GameStateSaver
from gameplay.character_inventory_saver import CharacterInventorySaver
from gameplay.relation_handler import RelationHandler
from gameplay.player_location_tracker import PlayerLocationTracker


class PlayScreen(BaseScreen):
    """Screen for playing a selected map"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

        # Grid settings
        self.base_grid_cell_size = 16  # Base 16x16 grid cells
        self.grid_cell_size = 16  # Current grid cell size (affected by zoom)

        # Zoom settings - limited to 100% minimum
        self.zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0]
        self.current_zoom_index = 0  # Start at 1.0x zoom (index 0)
        self.zoom_factor = self.zoom_levels[self.current_zoom_index]

        # Camera/viewport for large maps
        self.camera_x = 0
        self.camera_y = 0
        self.camera_speed = 5

        # Offset for centering small maps
        self.center_offset_x = 0
        self.center_offset_y = 0

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

        # Collision handler
        self.collision_handler = CollisionHandler(self.grid_cell_size)

        # Animated tiles manager
        self.animated_tile_manager = AnimatedTileManager()

        # Key item manager
        self.key_item_manager = KeyItemManager()

        # Crystal item manager
        self.crystal_item_manager = CrystalItemManager()

        # Lootchest manager
        self.lootchest_manager = LootchestManager()

        # Initialize shared cursor state for Terraria-style inventory system
        self.shared_cursor_item = None

        # Chest inventory (for displaying chest contents)
        self.chest_inventory = ChestInventory(self.width, self.height)

        # Player inventory (for displaying full inventory when ESC is pressed)
        self.player_inventory = PlayerInventory(self.width, self.height)

        # Set up shared cursor system - both inventories will use shared cursor methods
        # We'll override their cursor access to use our shared state
        self._setup_shared_cursor_system()

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

        # Game state saver for saving game state
        self.game_state_saver = GameStateSaver()

        # Character inventory saver for saving inventory data
        self.character_inventory_saver = CharacterInventorySaver()

        # Relation handler for teleportation between maps
        self.relation_handler = RelationHandler(self.grid_cell_size)

        # Player location tracker for saving positions across maps
        self.player_location_tracker = PlayerLocationTracker()

        # Teleportation flags and info
        self.is_teleporting = False
        self.teleport_info = None

        # Popup message for save notification
        self.popup_message = ""
        self.popup_timer = 0
        self.popup_duration = 120  # 2 seconds at 60 FPS

        # Initialize key item collection variables
        self.key_collected = False

        # Custom cursor
        self.default_cursor = pygame.mouse.get_cursor()
        self.select_cursor = None
        self.load_custom_cursor()

    def load_map(self, map_name):
        """Load a map from file"""
        # Reset the enemy manager to clear all enemies from the previous map
        self.enemy_manager.enemies = []

        # Store whether we're teleporting before resetting flags
        was_teleporting = self.is_teleporting
        teleport_info = self.teleport_info

        self.map_name = map_name

        # Get the current working directory
        current_dir = os.getcwd()
        print(f"Current working directory when loading map: {current_dir}")

        # Try to find the Maps directory
        # First check if Maps is in the current directory
        if os.path.exists(os.path.join(current_dir, "Maps")):
            maps_dir = os.path.join(current_dir, "Maps")
        # Then check if Maps is in the parent directory (for when running from a subdirectory)
        elif os.path.exists(os.path.join(current_dir, "..", "Maps")):
            maps_dir = os.path.join(current_dir, "..", "Maps")
        # Then check if Maps is in the grandparent directory (for when running from a sub-subdirectory)
        elif os.path.exists(os.path.join(current_dir, "..", "..", "Maps")):
            maps_dir = os.path.join(current_dir, "..", "..", "Maps")
        else:
            # Default to the relative path
            maps_dir = "Maps"

        print(f"Using Maps directory when loading map: {maps_dir}")

        # Try to find the map file - it could be a main map or a related map
        # First check if it's a main map
        main_map_path = os.path.join(maps_dir, map_name, f"{map_name}.json")
        print(f"DEBUG: Requested map name: '{map_name}'")
        print(f"DEBUG: Checking for main map file at: {main_map_path}")

        if os.path.exists(main_map_path):
            # It's a main map
            map_path = main_map_path
            print(f"DEBUG: Found main map file: {map_path}")
        else:
            # It might be a related map, search in all map folders
            map_path = None
            print(f"DEBUG: '{map_name}' is not a main map, searching in folders...")

            # Check if Maps directory exists
            if os.path.exists(maps_dir):
                print(f"Maps directory exists: {maps_dir}")
                # List all folders in the Maps directory
                folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]
                print(f"Found folders in Maps directory: {folders}")

                for folder_name in folders:
                    folder_path = os.path.join(maps_dir, folder_name)
                    print(f"Checking folder: {folder_path}")

                    # List all files in this folder
                    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                    print(f"Files in folder {folder_name}: {files}")

                    # Check if this folder contains our map
                    related_map_path = os.path.join(folder_path, f"{map_name}.json")
                    print(f"Checking for related map file at: {related_map_path}")

                    if os.path.exists(related_map_path):
                        map_path = related_map_path
                        print(f"Found related map file: {map_path}")
                        break
            else:
                print(f"Maps directory does not exist: {maps_dir}")
                self.status_message = f"Error: Maps directory not found"
                self.status_timer = 180
                return False

        try:
            # Check if file exists
            if not os.path.exists(map_path):
                self.status_message = f"Error: Map file not found: {map_name}"
                self.status_timer = 180
                return False

            print(f"DEBUG: Final map path being loaded: {map_path}")
            print(f"Loading map data from: {map_path}")
            # Load map data
            with open(map_path, 'r') as f:
                map_data = json.load(f)
            print(f"DEBUG: Loaded map data - map name in file: '{map_data.get('name', 'UNKNOWN')}'")
            print(f"DEBUG: Map dimensions: {map_data.get('width', 0)}x{map_data.get('height', 0)}")

            # Store map dimensions
            self.map_width = map_data.get("width", 0)
            self.map_height = map_data.get("height", 0)

            # Load collision data if available in the map file
            # Note: This is now supplementary to the global collision data
            if "collision_data" in map_data:
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

            # Make sure the current map is set correctly in both handlers
            self.relation_handler.current_map = map_name
            self.lootchest_manager.set_current_map(map_name)
            print(f"Current map set to: {self.relation_handler.current_map}")
            print(f"All loaded relation points: {self.relation_handler.relation_points}")

            # Check which format the map is in
            if "layers" in map_data and "tile_mapping" in map_data:
                # Layered format - process tile mapping and layers
                self.process_layered_format_map(map_data)
            elif "map_data" in map_data and "tile_mapping" in map_data:
                # Single-layer array format - process tile mapping and map data
                self.process_new_format_map(map_data)
            else:
                # Old format - process tiles directly
                self.process_old_format_map(map_data)

            # First check if we're teleporting - if so, we'll set the position later
            if not self.is_teleporting:
                # Determine which folder (world) this map belongs to using the same logic as player_location_tracker
                folder_name = self.player_location_tracker._determine_folder_name(map_name)

                # Get the location for this specific world
                world_location = self.player_location_tracker.get_world_location(folder_name)

                # Check if we have a saved location for this world
                if world_location:
                    # Use the world-specific location
                    player_x = world_location["x"]
                    player_y = world_location["y"]
                    player_direction = world_location["direction"]

                    # Create the player character with saved position and direction
                    self.player = PlayerCharacter(player_x, player_y)
                    self.player.direction = player_direction
                    print(f"DEBUG: Loading map '{map_name}' in world '{folder_name}'")
                    print(f"DEBUG: Saved location was for map '{world_location.get('map_name')}' at ({player_x}, {player_y})")
                    print(f"DEBUG: Using saved position for world '{folder_name}': ({player_x}, {player_y})")

                    # Set health and shield from the world location
                    self.player.current_health = world_location.get("health", 100)
                    self.player.shield_durability = world_location.get("shield_durability", 3)

                    # Set camera position from game state if available
                    if "game_state" in map_data and "camera" in map_data["game_state"]:
                        self.camera_x = map_data["game_state"]["camera"]["x"]
                        self.camera_y = map_data["game_state"]["camera"]["y"]

                # Check if there's a saved location for this specific map (cross-world compatibility - last resort)
                elif self.player_location_tracker.has_location(map_name):
                    saved_location = self.player_location_tracker.get_location(map_name)
                    if saved_location:
                        # Use the saved location for this map
                        player_x = saved_location["x"]
                        player_y = saved_location["y"]
                        player_direction = saved_location["direction"]

                        # Create the player character with saved position and direction
                        self.player = PlayerCharacter(player_x, player_y)
                        self.player.direction = player_direction
                        print(f"Loaded saved position for map '{map_name}' from any world (fallback): ({player_x}, {player_y})")

                        # Set default health and shield (since cross-world might not have these)
                        self.player.current_health = 100
                        self.player.shield_durability = 3

                # Check if map has a defined player start position
                elif "player_start" in map_data:
                    # Use the player starting position from the map data
                    player_grid_x = map_data["player_start"].get("x", 0)
                    player_grid_y = map_data["player_start"].get("y", 0)
                    player_x = player_grid_x * self.grid_cell_size
                    player_y = player_grid_y * self.grid_cell_size
                    player_direction = map_data["player_start"].get("direction", "down")

                    # Create the player character with starting position
                    self.player = PlayerCharacter(player_x, player_y)
                    self.player.direction = player_direction
                    print(f"Using map's player_start position: ({player_x}, {player_y})")

                else:
                    # Default to the middle of the map
                    player_x = (self.map_width * self.grid_cell_size) // 2
                    player_y = (self.map_height * self.grid_cell_size) // 2

                    # Create the player character (default direction is already "down")
                    self.player = PlayerCharacter(player_x, player_y)
                    print(f"Using default center position: ({player_x}, {player_y})")


            else:
                # We're teleporting, so we'll create a default player that will be positioned later
                # at the teleport point
                player_x = 0
                player_y = 0
                self.player = PlayerCharacter(player_x, player_y)

                # Set health and shield from game state if available
                if "game_state" in map_data and "player" in map_data["game_state"]:
                    player_data = map_data["game_state"]["player"]
                    if "health" in player_data:
                        self.player.current_health = player_data["health"]
                    if "shield_durability" in player_data:
                        self.player.shield_durability = player_data["shield_durability"]

            # Set map boundaries for the player
            self.player.set_map_boundaries(
                0, 0,  # Min X, Min Y
                self.map_width * self.grid_cell_size,  # Max X
                self.map_height * self.grid_cell_size  # Max Y
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

    def process_layered_format_map(self, map_data):
        """Process a map in the layered format"""
        # Clear existing tiles
        self.tiles = {}

        # Process tile mapping
        tile_mapping = map_data["tile_mapping"]
        self.expanded_mapping = self._expand_tile_mapping(tile_mapping)

        # Load all tile images
        for tile_id, tile_info in self.expanded_mapping.items():
            path = tile_info["path"]
            try:
                # Skip animated tiles - they're handled separately
                if not path.startswith("animated:"):
                    # Skip enemy tiles - they're handled by the enemy manager
                    # Skip player character tiles - they're handled separately
                    if ("Enemies_Sprites/Phantom_Sprites" not in path and
                        "Enemies_Sprites/Bomberplant_Sprites" not in path and
                        "Enemies_Sprites/Spider_Sprites" not in path and
                        "Enemies_Sprites/Pinkslime_Sprites" not in path and
                        "Enemies_Sprites/Pinkbat_Sprites" not in path and
                        "Enemies_Sprites/Spinner_Sprites" not in path and
                        "character/char_idle_" not in path):
                        self.tiles[int(tile_id)] = pygame.image.load(path).convert_alpha()
                    elif "Enemies_Sprites/Phantom_Sprites" in path:
                        print(f"Skipping phantom enemy tile: {path}")
                    elif "Enemies_Sprites/Bomberplant_Sprites" in path:
                        print(f"Skipping bomberplant enemy tile: {path}")
                    elif "Enemies_Sprites/Spider_Sprites" in path:
                        print(f"Skipping spider enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkslime_Sprites" in path:
                        print(f"Skipping pinkslime enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkbat_Sprites" in path:
                        print(f"Skipping pinkbat enemy tile: {path}")
                    elif "Enemies_Sprites/Spinner_Sprites" in path:
                        print(f"Skipping spinner enemy tile: {path}")
                    elif "character/char_idle_" in path:
                        print(f"Skipping player character tile: {path}")
            except Exception as e:
                print(f"Error loading tile {path}: {e}")

        # Add animated tiles to the expanded_mapping
        for tile_id, tile_name in self.animated_tile_manager.animated_tile_ids.items():
            # Add the animated tile to the expanded mapping
            self.expanded_mapping[str(tile_id)] = {
                "path": f"animated:{tile_name}",
                "tileset": -1,  # Special value for animated tiles
                "animated": True
            }

            # Check if this is a key item and add it to the key item manager
            if tile_name == "key_item":
                self.key_item_id = tile_id
            # Check if this is a crystal item and add it to the crystal item manager
            elif tile_name == "crystal_item":
                self.crystal_item_id = tile_id
            # Check if this is a lootchest item and add it to the lootchest manager
            elif tile_name == "lootchest_item":
                self.lootchest_item_id = tile_id


        # Store all layers separately instead of merging them
        self.layers = []
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)

        # Process each layer
        for layer_idx, layer in enumerate(map_data.get("layers", [])):
            layer_visible = layer.get("visible", True)
            layer_data = layer.get("map_data", [])

            # Validate layer_data
            if not isinstance(layer_data, list) or not layer_data:
                print(f"Warning: Invalid layer data for layer {layer_idx}")
                continue

            # Ensure all rows have the same length
            row_length = len(layer_data[0]) if layer_data else 0
            for row_idx, row in enumerate(layer_data):
                if len(row) != row_length:
                    print(f"Warning: Row {row_idx} in layer {layer_idx} has inconsistent length")
                    # Pad or truncate the row to match the expected length
                    if len(row) < row_length:
                        layer_data[row_idx] = row + [-1] * (row_length - len(row))
                    else:
                        layer_data[row_idx] = row[:row_length]

            # Store this layer
            self.layers.append({
                "data": layer_data,
                "visible": layer_visible
            })

            # Scan for key items in this layer
            if hasattr(self, 'key_item_id'):
                for y, row in enumerate(layer_data):
                    for x, tile_id in enumerate(row):
                        if tile_id == self.key_item_id:
                            # Found a key item, add it to the key item manager with layer information
                            self.key_item_manager.add_key_item(x, y, tile_id, layer_idx)

            # Scan for crystal items in this layer
            if hasattr(self, 'crystal_item_id'):
                for y, row in enumerate(layer_data):
                    for x, tile_id in enumerate(row):
                        if tile_id == self.crystal_item_id:
                            # Found a crystal item, add it to the crystal item manager with layer information
                            self.crystal_item_manager.add_crystal_item(x, y, tile_id, layer_idx)

            # Scan for lootchest items in this layer
            if hasattr(self, 'lootchest_item_id'):
                for y, row in enumerate(layer_data):
                    for x, tile_id in enumerate(row):
                        if tile_id == self.lootchest_item_id:
                            # Found a lootchest item, add it to the lootchest manager with layer information
                            self.lootchest_manager.add_lootchest(x, y, tile_id, layer_idx)



        # Keep the merged map_data for backward compatibility
        self.map_data = [[-1 for _ in range(width)] for _ in range(height)]
        for layer in self.layers:
            if not layer["visible"]:
                continue
            layer_data = layer["data"]
            for y, row in enumerate(layer_data):
                if y >= height:
                    continue
                for x, tile_id in enumerate(row):
                    if x >= width or tile_id == -1:
                        continue
                    # Validate tile_id
                    try:
                        tile_id_int = int(tile_id)
                        # Place the tile in the merged map
                        self.map_data[y][x] = tile_id_int
                    except (ValueError, TypeError):
                        print(f"Warning: Invalid tile ID {tile_id} at position ({x}, {y}) in layer {layer}")
                        continue

    def _expand_tile_mapping(self, tile_mapping):
        """Helper method to expand tile mapping patterns"""
        expanded_mapping = {}

        # Expand any loop patterns in the tile mapping
        for key, value in tile_mapping.items():
            if isinstance(value, dict) and value.get("type") == "loop":
                # This is a loop pattern
                start_id = value["start_id"]
                count = value["count"]
                pattern = value["pattern"]

                # Generate all the paths from the pattern
                for i in range(count):
                    tile_id = start_id + i
                    number = pattern["start"] + i
                    path = f"{pattern['prefix']}{number:0{pattern['digits']}d}{pattern['suffix']}"

                    expanded_mapping[str(tile_id)] = {
                        "path": path,
                        "tileset": int(key.split('_')[1]) if key.startswith('tileset_') else 0
                    }
            else:
                # This is a regular mapping
                expanded_mapping[key] = value

        return expanded_mapping

    def process_new_format_map(self, map_data):
        """Process a map in the new array-based format"""
        # Clear existing tiles
        self.tiles = {}

        # Process tile mapping
        tile_mapping = map_data["tile_mapping"]
        self.expanded_mapping = self._expand_tile_mapping(tile_mapping)

        # Load all tile images
        for tile_id, tile_info in self.expanded_mapping.items():
            path = tile_info["path"]
            try:
                # Skip animated tiles - they're handled separately
                if not path.startswith("animated:"):
                    # Skip enemy tiles - they're handled by the enemy manager
                    # Skip player character tiles - they're handled separately
                    if ("Enemies_Sprites/Phantom_Sprites" not in path and
                        "Enemies_Sprites/Bomberplant_Sprites" not in path and
                        "Enemies_Sprites/Spider_Sprites" not in path and
                        "Enemies_Sprites/Pinkslime_Sprites" not in path and
                        "Enemies_Sprites/Pinkbat_Sprites" not in path and
                        "Enemies_Sprites/Spinner_Sprites" not in path and
                        "character/char_idle_" not in path):
                        self.tiles[int(tile_id)] = pygame.image.load(path).convert_alpha()
                    elif "Enemies_Sprites/Phantom_Sprites" in path:
                        print(f"Skipping phantom enemy tile: {path}")
                    elif "Enemies_Sprites/Bomberplant_Sprites" in path:
                        print(f"Skipping bomberplant enemy tile: {path}")
                    elif "Enemies_Sprites/Spider_Sprites" in path:
                        print(f"Skipping spider enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkslime_Sprites" in path:
                        print(f"Skipping pinkslime enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkbat_Sprites" in path:
                        print(f"Skipping pinkbat enemy tile: {path}")
                    elif "Enemies_Sprites/Spinner_Sprites" in path:
                        print(f"Skipping spinner enemy tile: {path}")
                    elif "character/char_idle_" in path:
                        print(f"Skipping player character tile: {path}")
            except Exception as e:
                print(f"Error loading tile {path}: {e}")

        # Add animated tiles to the expanded_mapping
        for tile_id, tile_name in self.animated_tile_manager.animated_tile_ids.items():
            # Add the animated tile to the expanded mapping
            self.expanded_mapping[str(tile_id)] = {
                "path": f"animated:{tile_name}",
                "tileset": -1,  # Special value for animated tiles
                "animated": True
            }
            print(f"Added animated tile to expanded mapping: {tile_name} with ID {tile_id}")

        # Store the map data
        self.map_data = map_data["map_data"]

    def process_old_format_map(self, map_data):
        """Process a map in the old format with individual tile entries"""
        # Clear existing tiles
        self.tiles = {}

        # Create a 2D array filled with -1 (empty tile)
        width = map_data.get("width", 0)
        height = map_data.get("height", 0)
        self.map_data = [[-1 for _ in range(width)] for _ in range(height)]

        # Process tiles
        for key, tile_info in map_data.get("tiles", {}).items():
            try:
                # Get position
                x, y = tile_info.get("position", [0, 0])

                # Load tile image
                path = tile_info.get("source_path", "")
                if path and os.path.exists(path):
                    # Skip player character tiles - they're handled separately
                    # Skip enemy tiles - they're handled by the enemy manager
                    if ("Enemies_Sprites/Phantom_Sprites" not in path and
                        "Enemies_Sprites/Bomberplant_Sprites" not in path and
                        "Enemies_Sprites/Spider_Sprites" not in path and
                        "Enemies_Sprites/Pinkslime_Sprites" not in path and
                        "Enemies_Sprites/Pinkbat_Sprites" not in path and
                        "Enemies_Sprites/Spinner_Sprites" not in path and
                        "character/char_idle_" not in path):
                        # Create a unique ID for this tile
                        tile_id = len(self.tiles)
                        self.tiles[tile_id] = pygame.image.load(path).convert_alpha()

                        # Add to map data
                        if 0 <= x < width and 0 <= y < height:
                            self.map_data[y][x] = tile_id
                    elif "Enemies_Sprites/Phantom_Sprites" in path:
                        print(f"Skipping phantom enemy tile: {path}")
                    elif "Enemies_Sprites/Bomberplant_Sprites" in path:
                        print(f"Skipping bomberplant enemy tile: {path}")
                    elif "Enemies_Sprites/Spider_Sprites" in path:
                        print(f"Skipping spider enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkslime_Sprites" in path:
                        print(f"Skipping pinkslime enemy tile: {path}")
                    elif "Enemies_Sprites/Pinkbat_Sprites" in path:
                        print(f"Skipping pinkbat enemy tile: {path}")
                    elif "Enemies_Sprites/Spinner_Sprites" in path:
                        print(f"Skipping spinner enemy tile: {path}")
                    elif "character/char_idle_" in path:
                        print(f"Skipping player character tile: {path}")
            except Exception as e:
                print(f"Error processing tile {key}: {e}")

    def zoom_in(self):
        """Zoom in to the next zoom level"""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            # Store the center point of the current view (player position)
            if self.player:
                center_x = self.player.rect.centerx
                center_y = self.player.rect.centery
            else:
                center_x = self.camera_x + (self.width // 2)
                center_y = self.camera_y + (self.height // 2)

            # Update zoom
            self.current_zoom_index += 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self.update_zoom()

            # Recalculate camera position to maintain the same center point
            if self.player:
                # When zoomed, the effective screen size in logical coordinates is smaller
                effective_screen_width = self.width / self.zoom_factor
                effective_screen_height = self.height / self.zoom_factor

                self.camera_x = center_x - (effective_screen_width // 2)
                self.camera_y = center_y - (effective_screen_height // 2)

                # Clamp camera to map boundaries (use base grid size for logical coordinates)
                max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
                max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
                self.camera_x = max(0, min(self.camera_x, max_camera_x))
                self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def zoom_out(self):
        """Zoom out to the previous zoom level"""
        if self.current_zoom_index > 0:
            # Store the center point of the current view (player position)
            if self.player:
                center_x = self.player.rect.centerx
                center_y = self.player.rect.centery
            else:
                center_x = self.camera_x + (self.width // 2)
                center_y = self.camera_y + (self.height // 2)

            # Update zoom
            self.current_zoom_index -= 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self.update_zoom()

            # Recalculate camera position to maintain the same center point
            if self.player:
                # When zoomed, the effective screen size in logical coordinates is smaller
                effective_screen_width = self.width / self.zoom_factor
                effective_screen_height = self.height / self.zoom_factor

                self.camera_x = center_x - (effective_screen_width // 2)
                self.camera_y = center_y - (effective_screen_height // 2)

                # Clamp camera to map boundaries (use base grid size for logical coordinates)
                max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
                max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
                self.camera_x = max(0, min(self.camera_x, max_camera_x))
                self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def reset_zoom(self):
        """Reset zoom to 1.0x (100%)"""
        # Store the center point of the current view (player position)
        if self.player:
            center_x = self.player.rect.centerx
            center_y = self.player.rect.centery
        else:
            center_x = self.camera_x + (self.width // 2)
            center_y = self.camera_y + (self.height // 2)

        # Reset zoom to 1.0x
        self.current_zoom_index = 0  # 1.0x is at index 0
        self.zoom_factor = self.zoom_levels[self.current_zoom_index]
        self.update_zoom()

        # Recalculate camera position to maintain the same center point
        if self.player:
            # When at 1.0x zoom, effective screen size equals actual screen size
            effective_screen_width = self.width / self.zoom_factor
            effective_screen_height = self.height / self.zoom_factor

            self.camera_x = center_x - (effective_screen_width // 2)
            self.camera_y = center_y - (effective_screen_height // 2)

            # Clamp camera to map boundaries (use base grid size for logical coordinates)
            max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
            max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))

    def update_zoom(self):
        """Update grid cell size and collision handler based on current zoom factor"""
        self.grid_cell_size = int(self.base_grid_cell_size * self.zoom_factor)

        # Keep collision handler with base grid size (logical coordinates)
        # Collision detection should remain in the original coordinate space
        if not hasattr(self, 'collision_handler') or self.collision_handler.grid_cell_size != self.base_grid_cell_size:
            self.collision_handler = CollisionHandler(self.base_grid_cell_size)

        # Update relation handler with base grid size for logical coordinates
        self.relation_handler.grid_cell_size = self.base_grid_cell_size

    def handle_event(self, event):
        """Handle events for the play screen"""
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

        # Mouse button up events are no longer needed in Terraria-style system
        # All interactions are handled in mouse button down events

        # Pass mouse events to player character for attack handling
        if self.player and event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse wheel for inventory selection
            if event.button == 4:  # Mouse wheel up
                self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot - 1) % self.hud.inventory.num_slots
            elif event.button == 5:  # Mouse wheel down
                self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot + 1) % self.hud.inventory.num_slots
            # Handle left-click for inventory slots, player inventory, and attacks
            elif event.button == 1:  # Left mouse button
                # Check for shift key
                keys = pygame.key.get_pressed()
                shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                # Check if chest inventory is visible and handle clicks
                if self.chest_inventory.is_visible():
                    # Handle click in chest inventory
                    self.chest_inventory.handle_click(mouse_pos, shift_held=shift_held, player_inventory=self.player_inventory)
                    # Also check player inventory if it's visible
                    if self.player_inventory.is_visible():
                        self.player_inventory.handle_click(mouse_pos, shift_held=shift_held, chest_inventory=self.chest_inventory)
                # Check if only player inventory is visible and handle clicks
                elif self.player_inventory.is_visible():
                    # Handle click in player inventory (but don't close it on click outside)
                    self.player_inventory.handle_click(mouse_pos, shift_held=shift_held)
                # Check if clicking on an inventory slot
                elif self.hud.inventory.hovered_slot != -1:
                    # Select the clicked slot
                    self.hud.inventory.selected_slot = self.hud.inventory.hovered_slot
                else:
                    # No inventory slot clicked, use left-click for attack
                    self.player.handle_mouse_event(event)
            # Handle right-click for inventory item picking or lootchest interaction
            elif event.button == 3:  # Right mouse button
                # Check for shift key
                keys = pygame.key.get_pressed()
                shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

                # Check if chest inventory is visible and handle right-clicks
                if self.chest_inventory.is_visible():
                    # Handle right-click in chest inventory
                    self.chest_inventory.handle_click(mouse_pos, right_click=True, shift_held=shift_held, player_inventory=self.player_inventory)
                    # Also check player inventory if it's visible
                    if self.player_inventory.is_visible():
                        self.player_inventory.handle_click(mouse_pos, right_click=True, shift_held=shift_held, chest_inventory=self.chest_inventory)
                # Check if only player inventory is visible and handle right-clicks
                elif self.player_inventory.is_visible():
                    # Handle right-click in player inventory
                    self.player_inventory.handle_click(mouse_pos, right_click=True, shift_held=shift_held)
                # Check if clicking on a lootchest (only when inventories are not visible)
                elif not self.chest_inventory.is_visible() and not self.player_inventory.is_visible() and self.player and not self.player.is_dead:
                    # Debug output before trying to interact with a lootchest
                    print(f"Right-click at mouse position: {mouse_pos}")
                    print(f"Camera position: ({self.camera_x}, {self.camera_y})")
                    print(f"Grid cell size: {self.grid_cell_size}")
                    print(f"Player rect: {self.player.rect}")

                    # Calculate grid position from mouse position
                    # Use base grid size for logical coordinates
                    grid_x = int((mouse_pos[0] + self.camera_x) // self.base_grid_cell_size)
                    grid_y = int((mouse_pos[1] + self.camera_y) // self.base_grid_cell_size)
                    print(f"Calculated grid position: ({grid_x}, {grid_y})")

                    # Check if there's a lootchest at this position
                    position = (grid_x, grid_y)
                    if position in self.lootchest_manager.lootchests:
                        print(f"Found lootchest at position {position}")
                    else:
                        print(f"No lootchest found at position {position}")
                        print(f"Available lootchests: {list(self.lootchest_manager.lootchests.keys())}")

                    # Try to interact with a lootchest
                    # Adjust mouse position for center offset
                    adjusted_mouse_pos = (
                        mouse_pos[0],
                        mouse_pos[1]
                    )

                    # Adjust camera position for center offset
                    adjusted_camera_x = self.camera_x - self.center_offset_x
                    adjusted_camera_y = self.camera_y - self.center_offset_y

                    print(f"Adjusted mouse position: {adjusted_mouse_pos}")
                    print(f"Adjusted camera position: ({adjusted_camera_x}, {adjusted_camera_y})")

                    result = self.lootchest_manager.handle_right_click(
                        adjusted_mouse_pos,
                        adjusted_camera_x,
                        adjusted_camera_y,
                        self.base_grid_cell_size,
                        self.player.rect
                    )
                    print(f"Lootchest interaction result: {result}")
            else:
                # Handle other mouse buttons
                pass

        # Handle keyboard events for inventory selection and zoom
        if event.type == pygame.KEYDOWN:
            # Check for Ctrl key combinations first
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    # Ctrl++ to zoom in
                    self.zoom_in()
                    return None
                elif event.key == pygame.K_MINUS:
                    # Ctrl+- to zoom out
                    self.zoom_out()
                    return None
                elif event.key == pygame.K_0:
                    # Ctrl+0 to reset zoom
                    self.reset_zoom()
                    return None

            # ESC key to toggle player inventory
            if event.key == pygame.K_ESCAPE:
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

            # Number keys 1-0 for inventory selection (0 is the 10th slot)
            elif pygame.K_1 <= event.key <= pygame.K_9:
                # Convert key to slot index (0-8)
                slot = event.key - pygame.K_1
                self.hud.inventory.selected_slot = slot
            elif event.key == pygame.K_0:
                # 0 key selects the 10th slot (index 9)
                self.hud.inventory.selected_slot = 9

            # Q and E keys for inventory selection
            elif event.key == pygame.K_q:
                # Previous slot
                self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot - 1) % self.hud.inventory.num_slots
            elif event.key == pygame.K_e:
                # Next slot
                self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot + 1) % self.hud.inventory.num_slots

        return None

    def reset(self):
        """Reset the screen state but keep the map name"""
        # Store the current map name
        current_map = self.map_name

        # Reset map data
        self.map_data = {}
        self.map_width = 0
        self.map_height = 0
        self.tiles = {}

        # Reset camera
        self.camera_x = 0
        self.camera_y = 0

        # Reset player
        self.player = None

        # Reset collision handler
        self.collision_handler = CollisionHandler(self.grid_cell_size)

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

    def load_custom_cursor(self):
        """Load the custom cursor image and rotate it"""
        try:
            # Load the select icon image
            original_image = pygame.image.load("character/Hud_Ui/select_icon_ui.png").convert_alpha()

            # Rotate the image 135 degrees counter-clockwise (to point top-left)
            cursor_image = pygame.transform.rotate(original_image, 135)

            # Create a cursor from the rotated image
            # Set hotspot to the tip of the arrow (approximately)
            # For a 135-degree rotation (pointing top-left), the tip would be in the top-left quadrant
            hotspot = (cursor_image.get_width() // 4, cursor_image.get_height() // 4)
            self.select_cursor = pygame.cursors.Cursor((hotspot), cursor_image)
        except Exception as e:
            print(f"Error loading custom cursor: {e}")
            self.select_cursor = None

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

        # Calculate the size of the used area in pixels
        used_width = (max_x - min_x + 1) * self.grid_cell_size if max_x >= min_x else 0
        used_height = (max_y - min_y + 1) * self.grid_cell_size if max_y >= min_y else 0

        # Calculate the offset to the start of the used area
        area_offset_x = min_x * self.grid_cell_size
        area_offset_y = min_y * self.grid_cell_size

        # Check if the used area is smaller than the screen
        if used_width < self.width:
            # Center horizontally
            self.center_offset_x = (self.width - used_width) // 2 - area_offset_x
        else:
            # Used area is wider than or equal to the screen, no horizontal centering needed
            self.center_offset_x = 0

        if used_height < self.height:
            # Center vertically
            self.center_offset_y = (self.height - used_height) // 2 - area_offset_y
        else:
            # Used area is taller than or equal to the screen, no vertical centering needed
            self.center_offset_y = 0

        print(f"Used area bounds: ({min_x}, {min_y}) to ({max_x}, {max_y})")
        print(f"Used area size: {used_width}x{used_height} pixels")
        print(f"Center offset: ({self.center_offset_x}, {self.center_offset_y})")

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

        # Check if mouse is hovering over a lootchest
        hovered_lootchest = self.is_hovering_lootchest(mouse_pos)

        # Update cursor based on hover state
        if (self.hud.inventory.hovered_slot != -1 or hovered_lootchest) and self.select_cursor:
            # Mouse is hovering over an inventory slot or a lootchest, use custom cursor
            pygame.mouse.set_cursor(self.select_cursor)
        else:
            # Use default cursor
            pygame.mouse.set_cursor(self.default_cursor)

        # Update animated tiles
        self.animated_tile_manager.update()

        # Update key item manager
        self.key_item_manager.update()

        # Update crystal item manager
        self.crystal_item_manager.update()

        # Update lootchest manager
        self.lootchest_manager.update()

        # Update relation handler
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

        # Update enemies if player exists
        if self.player:
            # Debug output is now controlled by a flag
            debug_mode = False  # Set to True to enable debug messages

            if debug_mode:
                from debug_utils import debug_manager
                debug_manager.log(f"Player position: ({self.player.rect.centerx}, {self.player.rect.centery})", "player")

            # Pass player position and collision data to enemy manager
            self.enemy_manager.update(
                self.player.rect.centerx,
                self.player.rect.centery,
                collision_handler=self.collision_handler,
                tile_mapping=self.expanded_mapping,
                map_data=self.map_data
            )

            # Check for enemy-player collisions and apply knockback
            # Pass collision handler and map data to prevent going through walls
            if hasattr(self, 'layers') and self.layers:
                self.enemy_manager.check_player_collisions(
                    self.player,
                    collision_handler=self.collision_handler,
                    tile_mapping=self.expanded_mapping,
                    map_data=self.map_data
                )

            # Check if player's attack hits any enemies
            self.enemy_manager.check_player_attacks(
                self.player,
                collision_handler=self.collision_handler,
                tile_mapping=self.expanded_mapping,
                map_data=self.map_data
            )

        # Update player character if it exists
        if self.player:
            # Check if player is dead and death animation is complete
            if self.player.is_dead and self.player.death_animation_complete and not self.show_game_over:
                # Show game over screen
                self.show_game_over = True
                return

            # Store original position for collision detection
            original_x = self.player.rect.x
            original_y = self.player.rect.y

            # Update player (handles input and animation)
            self.player.update()

            # Check for collisions with key items
            collected_key = self.key_item_manager.check_player_collision(self.player.rect, self.grid_cell_size)
            if collected_key:
                # Key item collected, add to inventory
                grid_x, grid_y = collected_key

                # Check if we already have a key in the inventory
                key_slot = -1
                for i in range(self.hud.inventory.num_slots):
                    if self.hud.inventory.inventory_items[i] and self.hud.inventory.inventory_items[i]["name"] == "Key":
                        # Found an existing key, increment its count
                        key_slot = i
                        if "count" in self.hud.inventory.inventory_items[i]:
                            self.hud.inventory.inventory_items[i]["count"] += 1
                        else:
                            # First time adding a count to this key
                            self.hud.inventory.inventory_items[i]["count"] = 2
                        break

                # If no key was found, add to first empty slot
                if key_slot == -1:
                    for i in range(self.hud.inventory.num_slots):
                        if not self.hud.inventory.inventory_items[i]:
                            # Add key to this slot with count of 1
                            self.hud.inventory.inventory_items[i] = {
                                "name": "Key",
                                "image": self.animated_tile_manager.get_animated_tile_frame(self.key_item_id),
                                "count": 1
                            }
                            break

                # Remove the key from all map layers
                self._remove_key_from_map_layers(grid_x, grid_y)

                # Key collection message removed

            # Check for collisions with crystal items
            collected_crystal = self.crystal_item_manager.check_player_collision(self.player.rect, self.grid_cell_size)
            if collected_crystal:
                # Crystal item collected, add to inventory
                grid_x, grid_y = collected_crystal

                # Check if we already have a crystal in the inventory
                crystal_slot = -1
                for i in range(self.hud.inventory.num_slots):
                    if self.hud.inventory.inventory_items[i] and self.hud.inventory.inventory_items[i]["name"] == "Crystal":
                        # Found an existing crystal, increment its count
                        crystal_slot = i
                        if "count" in self.hud.inventory.inventory_items[i]:
                            self.hud.inventory.inventory_items[i]["count"] += 1
                        else:
                            # First time adding a count to this crystal
                            self.hud.inventory.inventory_items[i]["count"] = 2
                        break

                # If no crystal was found, add to first empty slot
                if crystal_slot == -1:
                    for i in range(self.hud.inventory.num_slots):
                        if not self.hud.inventory.inventory_items[i]:
                            # Add crystal to this slot with count of 1
                            self.hud.inventory.inventory_items[i] = {
                                "name": "Crystal",
                                "image": self.animated_tile_manager.get_animated_tile_frame(self.crystal_item_id),
                                "count": 1
                            }
                            break

                # Remove the crystal from all map layers
                self._remove_crystal_from_map_layers(grid_x, grid_y)

            # Check for collisions with entrance points (commented out as entrance_handler is not implemented)
            # entrance = self.entrance_handler.check_player_collision(self.player.rect)
            # if entrance:
            #     # Print the name of the entrance point
            #     print(f"Player touched entrance: {entrance['name']}")

            # Check for collisions with relation points
            relation = self.relation_handler.check_player_collision(self.player.rect)
            if relation:
                # Player touched a relation point, teleport to the corresponding point in the other map
                print(f"Player touched relation point: {relation['from_point']} -> {relation['to_point']} in map {relation['to_map']}")
                print(f"Teleporting to position: {relation['to_position']}")

                # Determine which folder (world) the current map belongs to using the same logic as player_location_tracker
                current_folder_name = self.player_location_tracker._determine_folder_name(self.map_name)

                print(f"DEBUG: Saving player location for world {current_folder_name}, map {self.map_name}")

                # Save the current player position for the current map and world
                self.player_location_tracker.save_location(
                    self.map_name,
                    self.player.rect.x,
                    self.player.rect.y,
                    self.player.direction,
                    self.player.current_health,
                    self.player.shield_durability,
                    current_folder_name
                )
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

                    # Determine which folder (world) the target map belongs to using the same logic as player_location_tracker
                    target_folder_name = self.player_location_tracker._determine_folder_name(target_map)

                    print(f"DEBUG: Saving player location for world {target_folder_name}, map {target_map}")

                    # Save this position to the player_location_tracker
                    self.player_location_tracker.save_location(
                        target_map,
                        self.player.rect.x,
                        self.player.rect.y,
                        self.player.direction,
                        self.player.current_health,
                        self.player.shield_durability,
                        target_folder_name
                    )
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
                    # When zoomed, the effective screen size in logical coordinates is smaller
                    effective_screen_width = self.width / self.zoom_factor
                    effective_screen_height = self.height / self.zoom_factor

                    self.camera_x = self.player.rect.centerx - (effective_screen_width // 2)
                    self.camera_y = self.player.rect.centery - (effective_screen_height // 2)

                    # Clamp camera to map boundaries using base grid size (logical coordinates)
                    max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
                    max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
                    self.camera_x = max(0, min(self.camera_x, max_camera_x))
                    self.camera_y = max(0, min(self.camera_y, max_camera_y))
                    print(f"Camera position: ({self.camera_x}, {self.camera_y})")

                    # No teleport message

            # Check for collisions with solid tile corners
            if hasattr(self, 'layers') and self.layers:
                # Use the merged map_data for collision detection
                if self.collision_handler.check_collision(self.player.rect, self.expanded_mapping, self.map_data):
                    # Collision detected, revert to original position
                    self.player.rect.x = original_x
                    self.player.rect.y = original_y

                    # If player is being knocked back, reduce knockback velocity to prevent getting stuck
                    if self.player.is_knocked_back:
                        self.player.knockback_velocity[0] *= 0.5
                        self.player.knockback_velocity[1] *= 0.5

            # Update camera to follow player smoothly
            # Center camera on player
            player_center_x = self.player.rect.centerx
            player_center_y = self.player.rect.centery

            # Calculate desired camera position (centered on player)
            # When zoomed, the effective screen size in logical coordinates is smaller
            effective_screen_width = self.width / self.zoom_factor
            effective_screen_height = self.height / self.zoom_factor

            target_camera_x = player_center_x - (effective_screen_width // 2)
            target_camera_y = player_center_y - (effective_screen_height // 2)

            # Clamp camera to map boundaries (use base grid size for logical coordinates)
            max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
            max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)

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
        """Draw the play screen"""
        # Fill the background with black
        surface.fill((0, 0, 0))

        # Draw map tiles with depth - first two layers, then player, then remaining layers
        if hasattr(self, 'layers') and self.layers:
            # Draw first layer (layer 0)
            if len(self.layers) > 0 and self.layers[0]["visible"]:
                self.draw_single_map_layer(surface, 0)

                # Draw key item collection animations for first layer
                self.key_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 0)

                # Draw crystal item collection animations for first layer
                self.crystal_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 0)

                # Draw lootchest animations for first layer
                self.lootchest_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 0)

            # Draw second layer (layer 1)
            if len(self.layers) > 1 and self.layers[1]["visible"]:
                self.draw_single_map_layer(surface, 1)

                # Draw key item collection animations for second layer
                self.key_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 1)

                # Draw crystal item collection animations for second layer
                self.crystal_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 1)

                # Draw lootchest animations for second layer
                self.lootchest_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, 1)

            # Draw enemies
            self.enemy_manager.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.zoom_factor)

            # Draw player character after second layer but before higher layers
            if self.player:
                self.player.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.zoom_factor)

            # Draw relation points
            self.relation_handler.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size)

            # Draw remaining layers (2 to max) on top of player
            for layer_idx in range(2, len(self.layers)):
                layer = self.layers[layer_idx]
                if layer["visible"]:
                    # Draw the layer
                    self.draw_single_map_layer(surface, layer_idx)

                    # Draw key item collection animations for this layer
                    self.key_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, layer_idx)

                    # Draw crystal item collection animations for this layer
                    self.crystal_item_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, layer_idx)

                    # Draw lootchest animations for this layer
                    self.lootchest_manager.draw_layer(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size, layer_idx)
        else:
            # Fallback for maps without layers
            self.draw_map(surface, skip_player_enemy_tiles=True)

            # Draw key item collection animations (using legacy method for non-layered maps)
            self.key_item_manager.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size)

            # Draw crystal item collection animations (using legacy method for non-layered maps)
            self.crystal_item_manager.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size)

            # Draw enemies first
            self.enemy_manager.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.zoom_factor)

            # Draw player character on top of enemies if it exists
            if self.player:
                self.player.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.zoom_factor)

            # Draw relation points
            self.relation_handler.draw(surface, self.camera_x - self.center_offset_x, self.camera_y - self.center_offset_y, self.grid_cell_size)

        # Draw common elements (back button also saves)
        # First draw the back button
        self.back_button.draw(surface)

        # No tooltip for back button



        # Draw zoom indicator in the bottom-left corner
        if self.zoom_factor != 1.0:  # Only show when not at 100%
            zoom_text = f"Zoom: {int(self.zoom_factor * 100)}%"
            font = pygame.font.SysFont(None, 24)
            zoom_surface = font.render(zoom_text, True, (255, 255, 255))
            zoom_rect = zoom_surface.get_rect(bottomleft=(10, self.height - 10))
            surface.blit(zoom_surface, zoom_rect)

        # Draw game over screen if showing
        if self.show_game_over:
            self.game_over_screen.draw(surface)

        # Draw inventories FIRST to ensure proper layering
        # If both inventories are visible, draw a shared background
        if self.chest_inventory.is_visible() and self.player_inventory.is_visible():
            # Draw shared semi-transparent black background
            bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            surface.blit(bg_surface, (0, 0))

            # Draw inventories in the correct order (chest inventory first, player inventory on top)
            # First draw chest inventory without its own background
            self.chest_inventory.draw(surface, skip_background=True)

            # Then draw player inventory without its own background (on top)
            self.player_inventory.draw(surface, skip_background=True)

            # Cursor items are now drawn automatically by the inventory draw methods
        else:
            # Draw chest inventory if visible
            if self.chest_inventory.is_visible():
                self.chest_inventory.draw(surface)

            # Draw player inventory if visible
            if self.player_inventory.is_visible():
                self.player_inventory.draw(surface)

        # Draw HUD elements if player exists (on top of inventories)
        if self.player:
            # Draw HUD normally
            self.hud.draw(surface, self.player)

        # No status messages

        # Draw game over screen if active
        if self.show_game_over:
            self.game_over_screen.draw(surface)

        # No popup messages

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

        # Calculate visible area - use base grid size for logical coordinates
        start_x = int(self.camera_x // self.base_grid_cell_size)
        end_x = min(self.map_width, start_x + (self.width // self.base_grid_cell_size) + 2)
        start_y = int(self.camera_y // self.base_grid_cell_size)
        end_y = min(self.map_height, start_y + (self.height // self.base_grid_cell_size) + 2)

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

                # Calculate screen position - use logical coordinates then scale for zoom
                # First calculate logical position
                logical_x = x * self.base_grid_cell_size - self.camera_x + self.center_offset_x
                logical_y = y * self.base_grid_cell_size - self.camera_y + self.center_offset_y

                # Scale for zoom
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

                # Check if this is a lootchest item and if it should be drawn
                if tile_id == self.lootchest_item_id and hasattr(self, 'lootchest_item_id'):
                    # Get the current frame for this lootchest
                    lootchest_frame = self.lootchest_manager.get_chest_frame(x, y)
                    if lootchest_frame:
                        # Scale the lootchest frame to match the grid cell size
                        scaled_lootchest_frame = pygame.transform.scale(lootchest_frame, (self.grid_cell_size, self.grid_cell_size))
                        # Draw the lootchest frame
                        surface.blit(scaled_lootchest_frame, (screen_x, screen_y))
                        continue  # Skip the normal tile drawing



                # Check if this is an animated tile
                if self.animated_tile_manager.is_animated_tile_id(tile_id):
                    # Get the current frame of the animated tile
                    frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
                    if frame:
                        # Scale the frame to match the grid cell size
                        scaled_frame = pygame.transform.scale(frame, (self.grid_cell_size, self.grid_cell_size))
                        # Draw the animated tile frame
                        surface.blit(scaled_frame, (screen_x, screen_y))
                # Draw the tile if we have it loaded
                elif tile_id in self.tiles:
                    # Scale the tile to match the grid cell size
                    scaled_tile = pygame.transform.scale(self.tiles[tile_id], (self.grid_cell_size, self.grid_cell_size))
                    # Draw the static tile
                    surface.blit(scaled_tile, (screen_x, screen_y))

    def draw_map_layers(self, surface, start_layer, end_layer):
        """Draw specific map layers from start_layer to end_layer (inclusive)"""
        # Only draw if we have map data and layers
        if not hasattr(self, 'layers') or not self.layers:
            return

        # Layer data loaded successfully

        # Calculate visible area - convert camera positions to integers
        start_x = int(self.camera_x // self.grid_cell_size)
        end_x = min(self.map_width, start_x + (self.width // self.grid_cell_size) + 1)
        start_y = int(self.camera_y // self.grid_cell_size)
        end_y = min(self.map_height, start_y + (self.height // self.grid_cell_size) + 1)

        # Ensure layer indices are valid
        start_layer = max(0, min(start_layer, len(self.layers) - 1))
        end_layer = max(0, min(end_layer, len(self.layers) - 1))

        # Draw each layer in the specified range
        for layer_idx in range(start_layer, end_layer + 1):
            if layer_idx >= len(self.layers):
                continue

            layer = self.layers[layer_idx]
            if not layer["visible"]:
                continue

            layer_data = layer["data"]

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

                    # Calculate screen position - camera position is already an integer
                    # Add center offset for small maps
                    screen_x = x * self.grid_cell_size - self.camera_x + self.center_offset_x
                    screen_y = y * self.grid_cell_size - self.camera_y + self.center_offset_y

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

                    # Check if this is a lootchest item and if it should be drawn
                    if tile_id == self.lootchest_item_id and hasattr(self, 'lootchest_item_id'):
                        # Get the current frame for this lootchest
                        lootchest_frame = self.lootchest_manager.get_chest_frame(x, y)
                        if lootchest_frame:
                            # Scale the lootchest frame to match the grid cell size
                            scaled_lootchest_frame = pygame.transform.scale(lootchest_frame, (self.grid_cell_size, self.grid_cell_size))
                            # Draw the lootchest frame
                            surface.blit(scaled_lootchest_frame, (screen_x, screen_y))
                            continue  # Skip the normal tile drawing



                    # Check if this is an animated tile
                    if self.animated_tile_manager.is_animated_tile_id(tile_id):
                        # Get the current frame of the animated tile
                        frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
                        if frame:
                            # Scale the frame to match the grid cell size
                            scaled_frame = pygame.transform.scale(frame, (self.grid_cell_size, self.grid_cell_size))
                            # Draw the animated tile frame
                            surface.blit(scaled_frame, (screen_x, screen_y))
                    # Draw the tile if we have it loaded
                    elif tile_id in self.tiles:
                        # Scale the tile to match the grid cell size
                        scaled_tile = pygame.transform.scale(self.tiles[tile_id], (self.grid_cell_size, self.grid_cell_size))
                        # Draw the static tile
                        surface.blit(scaled_tile, (screen_x, screen_y))

    def draw_map(self, surface, skip_player_enemy_tiles=False):
        """Draw the map tiles"""
        # Only draw if we have map data
        if not hasattr(self, 'layers') or not self.layers:
            # Fall back to old method if no layers
            if not self.map_data:
                return

            # Calculate visible area - convert camera positions to integers
            start_x = int(self.camera_x // self.grid_cell_size)
            end_x = min(self.map_width, start_x + (self.width // self.grid_cell_size) + 1)
            start_y = int(self.camera_y // self.grid_cell_size)
            end_y = min(self.map_height, start_y + (self.height // self.grid_cell_size) + 1)

            # Draw visible tiles
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    # Get tile ID at this position
                    try:
                        tile_id = self.map_data[y][x]
                    except IndexError:
                        continue

                    # Skip empty tiles
                    if tile_id == -1:
                        continue

                    # Skip player and enemy tiles if requested
                    if skip_player_enemy_tiles and hasattr(self, 'expanded_mapping') and str(tile_id) in self.expanded_mapping:
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

                    # Calculate screen position - camera position is already an integer
                    # Add center offset for small maps
                    screen_x = x * self.grid_cell_size - self.camera_x + self.center_offset_x
                    screen_y = y * self.grid_cell_size - self.camera_y + self.center_offset_y

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

                    # Check if this is a lootchest item and if it should be drawn
                    if tile_id == self.lootchest_item_id and hasattr(self, 'lootchest_item_id'):
                        # Get the current frame for this lootchest
                        lootchest_frame = self.lootchest_manager.get_chest_frame(x, y)
                        if lootchest_frame:
                            # Scale the lootchest frame to match the grid cell size
                            scaled_lootchest_frame = pygame.transform.scale(lootchest_frame, (self.grid_cell_size, self.grid_cell_size))
                            # Draw the lootchest frame
                            surface.blit(scaled_lootchest_frame, (screen_x, screen_y))
                            continue  # Skip the normal tile drawing



                    # Check if this is an animated tile
                    if self.animated_tile_manager.is_animated_tile_id(tile_id):
                        # Get the current frame of the animated tile
                        frame = self.animated_tile_manager.get_animated_tile_frame(tile_id)
                        if frame:
                            # Scale the frame to match the grid cell size
                            scaled_frame = pygame.transform.scale(frame, (self.grid_cell_size, self.grid_cell_size))
                            # Draw the animated tile frame
                            surface.blit(scaled_frame, (screen_x, screen_y))
                    # Draw the tile if we have it loaded
                    elif tile_id in self.tiles:
                        # Scale the tile to match the grid cell size
                        scaled_tile = pygame.transform.scale(self.tiles[tile_id], (self.grid_cell_size, self.grid_cell_size))
                        # Draw the static tile
                        surface.blit(scaled_tile, (screen_x, screen_y))
            return

        # If we have layers, draw all of them
        if skip_player_enemy_tiles:
            # Draw each layer individually to skip player/enemy tiles
            for layer_idx in range(len(self.layers)):
                self.draw_single_map_layer(surface, layer_idx)
        else:
            # Draw all layers at once - make sure to include all layers (0 to len-1)
            self.draw_map_layers(surface, 0, len(self.layers) - 1)

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
        """Save the current game state to the map file"""
        # Save map state
        map_success, map_error_message = self.game_state_saver.save_game_state(self)

        # Save character inventory separately
        inventory_success, inventory_error_message = self.save_character_inventory()

        # Save current player location for the current map
        if self.player and self.map_name:
            # Determine which folder (world) the current map belongs to using the same logic as player_location_tracker
            current_folder_name = self.player_location_tracker._determine_folder_name(self.map_name)

            print(f"DEBUG: Saving player location for world {current_folder_name}, map {self.map_name}")

            # Save the current player position for the current map and world
            self.player_location_tracker.save_location(
                self.map_name,
                self.player.rect.x,
                self.player.rect.y,
                self.player.direction,
                self.player.current_health,
                self.player.shield_durability,
                current_folder_name
            )
            # Save to file
            self.player_location_tracker.save_to_file()

        # Return results without showing popup messages
        if map_success and inventory_success:
            return True
        elif not map_success:
            # Only log error, don't show message
            print(f"Error saving game: {map_error_message}")
            return False
        else:
            # Only log error, don't show message
            print(f"Error saving inventory: {inventory_error_message}")
            return False

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
        """Load the character's inventory from the save file"""
        # Skip if player inventory is not initialized
        if not self.player_inventory:
            return False, "Player inventory not initialized"

        # Load the inventory data
        success, message = self.character_inventory_saver.load_inventory(self.player_inventory)

        if success:
            # Update item images with proper sprites from animated tile manager
            self._update_inventory_images()

            # Update the HUD inventory from the bottom row of the player inventory
            # This ensures the quick access slots are updated
            self.player_inventory.hide(self.hud.inventory)

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

        # Make sure chest_contents is a list
        if not isinstance(chest_contents, list):
            print(f"Warning: chest_contents is not a list, it's a {type(chest_contents)}")
            chest_contents = []

        # If chest_contents is empty, initialize with empty slots
        if not chest_contents:
            print("Chest contents is empty, initializing with empty slots")
            chest_contents = [None] * 60  # 10x6 grid

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

        # Show the chest inventory with whatever contents it has (even if empty)
        # Position it side-by-side with the player inventory
        self.chest_inventory.show(chest_pos, chest_contents, self.player_inventory)



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

    def is_hovering_lootchest(self, mouse_pos):
        """Check if the mouse is hovering over a lootchest"""
        # Only check if we have map data and layers
        if not hasattr(self, 'layers') or not self.layers:
            return False

        # Get the lootchest item ID
        lootchest_id = self.animated_tile_manager.get_animated_tile_id("lootchest_item")
        if not lootchest_id:
            return False

        # Calculate grid position from mouse position
        # Adjust for camera position and center offset
        # Use base grid size for logical coordinates
        adjusted_mouse_x = mouse_pos[0] + self.camera_x - self.center_offset_x
        adjusted_mouse_y = mouse_pos[1] + self.camera_y - self.center_offset_y
        grid_x = int(adjusted_mouse_x // self.base_grid_cell_size)
        grid_y = int(adjusted_mouse_y // self.base_grid_cell_size)
        position = (grid_x, grid_y)

        # Use exact position matching for cursor changes - no search range
        # We want the cursor to change only when directly over a chest



        # First check if this position is in the lootchests dictionary
        if position in self.lootchest_manager.lootchests:
            # Found a lootchest at this position in the lootchests dictionary
            return True

        # Check if this position is in the opened chests list
        # This ensures we detect opened chests even if they've been replaced in the layer data
        if position in self.lootchest_manager.opened_chests:
            return True

        # Check each layer for a lootchest at this position
        for layer_idx, layer in enumerate(self.layers):
            layer_data = layer["data"]
            if 0 <= grid_y < len(layer_data) and 0 <= grid_x < len(layer_data[grid_y]):
                # Check if this is a lootchest and at the mouse position
                if layer_data[grid_y][grid_x] == lootchest_id:
                    # Found a lootchest at the mouse position
                    return True

        # For cursor changes, we only want exact position matches
        # No nearby chest detection for cursor changes
        # This ensures the cursor only changes when directly over a chest

        return False

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Store the old center offset for calculating camera adjustment
        old_center_offset_x = self.center_offset_x
        old_center_offset_y = self.center_offset_y

        # Call the base class resize method
        super().resize(new_width, new_height)

        # Update HUD dimensions
        self.hud.resize(new_width, new_height)

        # Recalculate center offset for small maps
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

    def _setup_shared_cursor_system(self):
        """Set up the shared cursor system for Terraria-style inventory interactions"""
        # Replace the cursor_item property in both inventories with our shared system

        # Store original cursor_item attributes as private
        self.player_inventory._original_cursor_item = self.player_inventory.cursor_item
        self.chest_inventory._original_cursor_item = self.chest_inventory.cursor_item

        # Replace cursor_item with property that uses shared state
        def get_shared_cursor(inventory_self):
            return self.shared_cursor_item

        def set_shared_cursor(inventory_self, value):
            self.shared_cursor_item = value

        # Monkey patch both inventories to use shared cursor
        self.player_inventory.__class__.cursor_item = property(get_shared_cursor, set_shared_cursor)
        self.chest_inventory.__class__.cursor_item = property(get_shared_cursor, set_shared_cursor)
