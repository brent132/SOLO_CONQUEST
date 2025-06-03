"""
Lootchest Manager - handles lootchest interaction and animation
"""
import pygame
import os
from playscreen_components.animation_system import AnimatedTile

class LootchestManager:
    """Manages lootchest interaction and animation"""
    def __init__(self):
        # Lootchest properties
        self.lootchests = {}  # Dictionary of lootchests by position (x, y)
        self.opened_chests = []  # List of opened chest positions
        self.opening_chests = {}  # Dictionary of chests with opening animation in progress
        self.chest_contents = {}  # Dictionary of chest contents by position (x, y)

        # Current map name - used to make chests map-specific
        self.current_map = None

        # Opening animation
        self.opening_animation = None
        self.opening_frames = []
        self.opening_duration = 30  # Duration of opening animation in frames (0.5 seconds at 60 FPS)

        # Static open frame
        self.static_open_frame = None

        # Callback for when a chest is opened
        self.on_chest_opened_callback = None

        # Load animations
        self.load_animations()

    def set_current_map(self, map_name):
        """Set the current map and clear lootchests

        Args:
            map_name: Name of the current map
        """
        # If the map is changing, clear the lootchests
        if self.current_map != map_name:
            print(f"LootchestManager: Changing map from {self.current_map} to {map_name}")
            print(f"  Previous lootchests count: {len(self.lootchests)}")
            print(f"  Previous opened chests count: {len(self.opened_chests)}")
            print(f"  Previous opening chests count: {len(self.opening_chests)}")

            self.lootchests = {}
            self.opened_chests = []
            self.opening_chests = {}
            # Don't clear chest_contents as it's persistent across maps

        # Set the current map
        self.current_map = map_name
        print(f"LootchestManager current map set to: {self.current_map}")
        print(f"  Current lootchests count: {len(self.lootchests)}")

    def load_animations(self):
        """Load the lootchest opening animation and static open frame"""
        # Load opening animation
        animation_folder = "character/Props_Items_(animated)/lootchest_item_anim_opening"
        print(f"Attempting to load lootchest opening animation from: {animation_folder}")

        if os.path.exists(animation_folder):
            print(f"Animation folder exists")
            self.opening_animation = AnimatedTile(animation_folder, frame_duration=5)  # Faster animation

            # Store all animation frames for direct access
            if self.opening_animation.frames:
                self.opening_frames = self.opening_animation.frames
                print(f"Loaded lootchest opening animation with {len(self.opening_frames)} frames")
                for i, frame in enumerate(self.opening_frames):
                    print(f"  Frame {i}: {frame.get_size()}")
            else:
                print("No frames found in lootchest opening animation")

            # Check if we have a static open frame
            if hasattr(self, 'static_open_frame') and self.static_open_frame:
                print(f"Static open frame loaded: {self.static_open_frame.get_size()}")
            else:
                print("No static open frame loaded")
        else:
            print(f"Lootchest opening animation folder not found: {animation_folder}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Directory contents: {os.listdir('.')}")
            if os.path.exists("character"):
                print(f"Character directory contents: {os.listdir('character')}")
                if os.path.exists("character/Props_Items_(animated)"):
                    print(f"Props_Items_(animated) directory contents: {os.listdir('character/Props_Items_(animated)')}")

        # Load static open frame - try multiple possible paths
        possible_paths = [
            "character/Props_Items_(animated)/lootchest_item_static_open/lootchest_item_static_open.png",
            "character/Props_Items_(animated)/lootchest_item_static_open.png"
        ]

        # Try each path until we find one that works
        self.static_open_frame = None
        for static_open_path in possible_paths:
            print(f"Attempting to load static open frame from: {static_open_path}")

            if os.path.exists(static_open_path):
                print(f"Static open frame file exists at: {static_open_path}")
                try:
                    self.static_open_frame = pygame.image.load(static_open_path).convert_alpha()
                    print(f"Loaded lootchest static open frame: {self.static_open_frame.get_size()}")
                    break  # Successfully loaded, exit the loop
                except Exception as e:
                    print(f"Error loading lootchest static open frame: {e}")
            else:
                print(f"Static open frame not found at: {static_open_path}")

        # If we couldn't load from any path, create a placeholder
        if not self.static_open_frame:
            print("Could not load static open frame from any path, creating placeholder")
            try:
                placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
                placeholder.fill((255, 0, 0, 128))  # Semi-transparent red
                self.static_open_frame = placeholder
                print(f"Created placeholder static open frame")
            except Exception as e:
                print(f"Error creating placeholder static open frame: {e}")
                self.static_open_frame = None

    def add_lootchest(self, grid_x, grid_y, tile_id, layer=0):
        """Add a lootchest to the manager

        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid
            tile_id: ID of the lootchest tile
            layer: Layer number the lootchest is on (for proper layering)
        """
        # Precaution: Validate input parameters
        if not isinstance(grid_x, (int, float)) or not isinstance(grid_y, (int, float)):
            print(f"Warning: Invalid grid coordinates - x: {grid_x} ({type(grid_x)}), y: {grid_y} ({type(grid_y)})")
            return

        if not isinstance(tile_id, (int, float)):
            print(f"Warning: Invalid tile_id: {tile_id} ({type(tile_id)})")
            return

        position = (int(grid_x), int(grid_y))
        print(f"LootchestManager: Adding lootchest at position {position} with tile_id {tile_id} on layer {layer} for map {self.current_map}")

        # Precaution: Check if lootchest already exists at this position
        if position in self.lootchests:
            print(f"Warning: Lootchest already exists at position {position}, overwriting")

        try:
            self.lootchests[position] = {
                "tile_id": tile_id,
                "opened": False,
                "layer": layer  # Store which layer this lootchest belongs to
            }
            print(f"Successfully added lootchest. Total lootchests: {len(self.lootchests)}")

            # Initialize empty chest contents if not already set
            if position not in self.chest_contents:
                # Initialize with an empty inventory
                self.initialize_chest_contents(position)
                print(f"Initialized empty chest contents for position {position}")
            else:
                print(f"Chest contents already exist for position {position}")

        except Exception as e:
            print(f"Error adding lootchest at position {position}: {e}")
            raise

    def handle_right_click(self, mouse_pos, camera_x, camera_y, grid_cell_size, player_rect=None):
        """Handle right-click on a lootchest

        Args:
            mouse_pos: Mouse position (x, y)
            camera_x: Camera X position
            camera_y: Camera Y position
            grid_cell_size: Size of grid cells
            player_rect: Optional player rectangle for distance checking

        Returns:
            True if a lootchest was clicked, False otherwise
        """
        print(f"LootchestManager.handle_right_click called for map: {self.current_map}")
        print(f"  Mouse position: {mouse_pos}")
        print(f"  Camera position: ({camera_x}, {camera_y})")
        print(f"  Grid cell size: {grid_cell_size}")
        print(f"  Player rect: {player_rect}")
        print(f"  Available lootchests: {len(self.lootchests)}")
        if self.lootchests:
            print(f"  Lootchest positions: {list(self.lootchests.keys())}")

        # Precaution: Validate input parameters
        if not mouse_pos or len(mouse_pos) != 2:
            print(f"Warning: Invalid mouse position: {mouse_pos}")
            return False

        if not isinstance(camera_x, (int, float)) or not isinstance(camera_y, (int, float)):
            print(f"Warning: Invalid camera position - x: {camera_x}, y: {camera_y}")
            return False

        if not isinstance(grid_cell_size, (int, float)) or grid_cell_size <= 0:
            print(f"Warning: Invalid grid cell size: {grid_cell_size}")
            return False

        try:
            # Calculate precise grid position from mouse position
            world_x = mouse_pos[0] + camera_x
            world_y = mouse_pos[1] + camera_y
            grid_x = int(world_x // grid_cell_size)
            grid_y = int(world_y // grid_cell_size)

            # Calculate the position within the tile (0.0 to 1.0)
            tile_offset_x = (world_x % grid_cell_size) / grid_cell_size
            tile_offset_y = (world_y % grid_cell_size) / grid_cell_size

            position = (grid_x, grid_y)
            print(f"  World position: ({world_x}, {world_y})")
            print(f"  Calculated grid position: ({grid_x}, {grid_y})")
            print(f"  Tile offset: ({tile_offset_x:.3f}, {tile_offset_y:.3f})")

        except Exception as e:
            print(f"Error in coordinate calculation: {e}")
            return False

        # Check if there's a lootchest at this exact position
        if position not in self.lootchests:
            print(f"  No lootchest found at exact position {position}")
            print(f"  Available lootchests: {list(self.lootchests.keys())}")
            return False

        # Additional precision check: ensure click is within the center area of the tile
        # This prevents accidental activation from edge clicks
        center_tolerance = 0.2  # Allow clicks within 20% margin from edges
        if (tile_offset_x < center_tolerance or tile_offset_x > (1.0 - center_tolerance) or
            tile_offset_y < center_tolerance or tile_offset_y > (1.0 - center_tolerance)):
            print(f"  Click too close to tile edge. Offset: ({tile_offset_x:.3f}, {tile_offset_y:.3f})")
            print(f"  Required center area: {center_tolerance:.1f} to {1.0 - center_tolerance:.1f}")
            return False

        print(f"  Found lootchest at position {position}")
        print(f"  Lootchest data: {self.lootchests[position]}")

        # Check if the lootchest is already opening (animation in progress)
        if position in self.opening_chests:
            print(f"  Lootchest is already in the process of opening")
            return False

        # If the chest is already opened, show its contents
        if position in self.opened_chests:
            print(f"  Chest is already opened")
            # Check if player is close enough to the chest (within 7 tiles)
            if player_rect:
                print(f"  Checking if player is close enough to opened chest")
                # Calculate distance between player and chest centers in grid units
                player_grid_x = player_rect.centerx // grid_cell_size
                player_grid_y = player_rect.centery // grid_cell_size
                chest_grid_x = position[0]
                chest_grid_y = position[1]

                # Calculate Manhattan distance in grid units
                grid_distance = abs(player_grid_x - chest_grid_x) + abs(player_grid_y - chest_grid_y)

                print(f"  Player grid position: ({player_grid_x}, {player_grid_y})")
                print(f"  Chest grid position: ({chest_grid_x}, {chest_grid_y})")
                print(f"  Grid distance: {grid_distance}")
                print(f"  Max grid distance allowed: 7")

                # Check if player is within range (7 tiles)
                if grid_distance > 7:
                    print(f"  Player is too far from chest")
                    return False
                else:
                    print(f"  Player is within range of chest")

            # Call the callback to show the chest contents
            if self.on_chest_opened_callback:
                print(f"  Calling on_chest_opened_callback")
                chest_contents = self.get_chest_contents(position)
                print(f"  Chest contents: {chest_contents}")
                try:
                    self.on_chest_opened_callback(position, chest_contents)
                    print(f"  Successfully called on_chest_opened_callback")
                except Exception as e:
                    print(f"  Error calling on_chest_opened_callback: {e}")
            else:
                print(f"  No on_chest_opened_callback set")

            return True

        # Check if player is close enough to the chest (within 7 tiles)
        if player_rect:
            print(f"  Checking if player is close enough to unopened chest")
            # We'll use grid-based distance calculation

            # Calculate distance between player and chest centers in grid units
            player_grid_x = player_rect.centerx // grid_cell_size
            player_grid_y = player_rect.centery // grid_cell_size
            chest_grid_x = position[0]
            chest_grid_y = position[1]

            # Calculate Manhattan distance in grid units
            grid_distance = abs(player_grid_x - chest_grid_x) + abs(player_grid_y - chest_grid_y)

            print(f"  Player grid position: ({player_grid_x}, {player_grid_y})")
            print(f"  Chest grid position: ({chest_grid_x}, {chest_grid_y})")
            print(f"  Grid distance: {grid_distance}")
            print(f"  Max grid distance allowed: 7")

            # Check if player is within range (7 tiles)
            if grid_distance > 7:
                print(f"  Player is too far from chest")
                return False
            else:
                print(f"  Player is within range of chest")

        # Start opening animation
        print(f"  Starting chest opening animation")
        self.opening_chests[position] = {
            "animation_frame": 0,  # Current frame index
            "timer": self.opening_duration,
            "frame_counter": 0,  # Counter for frame timing
            "layer": self.lootchests[position]["layer"]  # Preserve layer information
        }
        print(f"  Opening chests: {self.opening_chests}")

        return True

    def update(self):
        """Update opening animations"""
        # Update opening animation (still needed for global animation timing)
        if self.opening_animation:
            self.opening_animation.update()

        # Update timers and animation frames for opening chests
        for pos in list(self.opening_chests.keys()):
            chest_data = self.opening_chests[pos]

            # Decrement timer
            chest_data["timer"] -= 1

            # Check if animation is complete
            if chest_data["timer"] <= 0:
                print(f"Chest animation complete for {pos}")
                # Animation complete, remove from opening chests and add to opened chests
                del self.opening_chests[pos]
                self.opened_chests.append(pos)
                print(f"Added {pos} to opened_chests: {self.opened_chests}")

                # Mark the chest as opened in the lootchests dictionary
                if pos in self.lootchests:
                    self.lootchests[pos]["opened"] = True
                    print(f"Marked chest as opened in lootchests dictionary")

                # Call the callback if set
                if self.on_chest_opened_callback:
                    print(f"Calling on_chest_opened_callback after animation complete")
                    chest_contents = self.get_chest_contents(pos)
                    print(f"Chest contents: {chest_contents}")
                    try:
                        self.on_chest_opened_callback(pos, chest_contents)
                        print(f"Successfully called on_chest_opened_callback")
                    except Exception as e:
                        print(f"Error calling on_chest_opened_callback: {e}")
                else:
                    print(f"No on_chest_opened_callback set")

                continue

            # Update animation frame
            if self.opening_frames:
                chest_data["frame_counter"] += 1

                # Check if it's time to advance to the next frame
                if chest_data["frame_counter"] >= self.opening_animation.frame_duration:
                    chest_data["frame_counter"] = 0

                    # Advance to next frame, but don't loop back to the beginning
                    next_frame = chest_data["animation_frame"] + 1

                    # If we've reached the last frame, stay on it until the timer expires
                    if next_frame < len(self.opening_frames):
                        chest_data["animation_frame"] = next_frame

    def draw_layer(self, surface, camera_x, camera_y, grid_cell_size, layer_idx):
        """Draw lootchest animations for a specific layer

        Args:
            surface: Surface to draw on
            camera_x: Camera X position
            camera_y: Camera Y position
            grid_cell_size: Size of grid cells (already scaled for zoom)
            layer_idx: Layer index to draw
        """
        # Calculate zoom factor from grid cell size
        base_grid_size = 16
        zoom_factor = grid_cell_size / base_grid_size

        # Draw opening animations for this layer
        for pos, chest_data in self.opening_chests.items():
            # Skip if not on this layer
            if chest_data["layer"] != layer_idx:
                continue

            grid_x, grid_y = pos

            # Get the specific frame for this opening chest
            frame_index = chest_data["animation_frame"]
            if 0 <= frame_index < len(self.opening_frames):
                frame = self.opening_frames[frame_index]

                # Calculate screen position - use the same method as tiles
                # First calculate logical position
                logical_x = grid_x * base_grid_size - camera_x
                logical_y = grid_y * base_grid_size - camera_y

                # Scale for zoom
                screen_x = logical_x * zoom_factor
                screen_y = logical_y * zoom_factor

                # Scale the frame to match the grid cell size (for zoom)
                scaled_frame = pygame.transform.scale(frame, (grid_cell_size, grid_cell_size))

                # Draw the opening animation
                surface.blit(scaled_frame, (screen_x, screen_y))

        # Draw opened chests for this layer
        for pos in self.opened_chests:
            # Skip if not on this layer
            if pos in self.lootchests and self.lootchests[pos]["layer"] != layer_idx:
                continue

            grid_x, grid_y = pos

            # Calculate screen position - use the same method as tiles
            # First calculate logical position
            logical_x = grid_x * base_grid_size - camera_x
            logical_y = grid_y * base_grid_size - camera_y

            # Scale for zoom
            screen_x = logical_x * zoom_factor
            screen_y = logical_y * zoom_factor

            # Draw the static open frame if available
            if self.static_open_frame:
                # Scale the frame to match the grid cell size (for zoom)
                scaled_frame = pygame.transform.scale(self.static_open_frame, (grid_cell_size, grid_cell_size))
                surface.blit(scaled_frame, (screen_x, screen_y))

    def get_chest_frame(self, grid_x, grid_y):
        """Get the current frame for a lootchest at the given position

        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid

        Returns:
            The current frame for the lootchest, or None if no special frame is needed
        """
        position = (grid_x, grid_y)

        # Check if this chest is opening
        if position in self.opening_chests:
            chest_data = self.opening_chests[position]
            frame_index = chest_data["animation_frame"]

            if 0 <= frame_index < len(self.opening_frames):
                return self.opening_frames[frame_index]

        # Check if this chest is opened
        if position in self.opened_chests and self.static_open_frame:
            return self.static_open_frame

        # No special frame needed, use the default animation
        return None

    def get_opened_chests_data(self):
        """Get opened chests data for saving

        Returns:
            List of opened chest positions as [x, y] lists
        """
        opened_chests_data = []

        # Convert tuple positions to lists for JSON serialization
        for chest_pos in self.opened_chests:
            # Each position is a tuple (x, y), convert to a list [x, y]
            opened_chests_data.append(list(chest_pos))

        return opened_chests_data

    def get_chest_contents_data(self):
        """Get chest contents data for saving

        Returns:
            Dictionary mapping chest positions (as strings) to their contents
            in a compact format with only non-null items
        """
        chest_contents_data = {}

        # Convert tuple positions to strings for JSON serialization
        for pos, contents in self.chest_contents.items():
            # Convert tuple (x, y) to string "x,y"
            pos_str = f"{pos[0]},{pos[1]}"

            # Convert item images to references and only store non-null items with their positions
            compact_contents = {}
            for i, item in enumerate(contents):
                if item:
                    # Create a copy of the item without the image
                    serializable_item = item.copy()
                    if "image" in serializable_item:
                        del serializable_item["image"]
                    # Store the item with its slot index as the key
                    compact_contents[str(i)] = serializable_item

            # Only add this chest to the data if it has any items
            if compact_contents:
                chest_contents_data[pos_str] = compact_contents

        return chest_contents_data

    def load_chest_contents_data(self, chest_contents_data, animated_tile_manager):
        """Load chest contents data from saved game state

        Args:
            chest_contents_data: Dictionary mapping chest positions to their contents
            animated_tile_manager: AnimatedTileManager for loading item images
        """
        # Clear existing chest contents
        self.chest_contents = {}

        # Load each chest's contents
        for pos_str, contents in chest_contents_data.items():
            # Convert string "x,y" back to tuple (x, y)
            # Handle both integer and float coordinates
            x, y = map(float, pos_str.split(","))
            position = (int(x), int(y))

            # Initialize empty contents for a 10x6 grid (60 slots)
            loaded_contents = [None] * 60

            # Check if we're using the new compact format (dictionary) or old format (list)
            if isinstance(contents, dict):
                # New compact format - dictionary with slot indices as keys
                for slot_idx, item in contents.items():
                    # Convert slot index from string to integer
                    slot = int(slot_idx)

                    if slot < len(loaded_contents):
                        # Create a copy of the item
                        loaded_item = item.copy()

                        # Load the image based on item name
                        if item["name"] == "Key" and hasattr(animated_tile_manager, 'get_animated_tile_id'):
                            key_id = animated_tile_manager.get_animated_tile_id("key_item")
                            if key_id:
                                loaded_item["image"] = animated_tile_manager.get_animated_tile_frame(key_id)
                        elif item["name"] == "Crystal" and hasattr(animated_tile_manager, 'get_animated_tile_id'):
                            crystal_id = animated_tile_manager.get_animated_tile_id("crystal_item")
                            if crystal_id:
                                loaded_item["image"] = animated_tile_manager.get_animated_tile_frame(crystal_id)
                        else:
                            # Placeholder image for unknown items
                            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
                            placeholder.fill((255, 0, 0, 128))
                            loaded_item["image"] = placeholder

                        loaded_contents[slot] = loaded_item
            else:
                # Old format - list of items (possibly with nulls)
                for i, item in enumerate(contents):
                    if item and i < len(loaded_contents):
                        # Create a copy of the item
                        loaded_item = item.copy()

                        # Load the image based on item name
                        if item["name"] == "Key" and hasattr(animated_tile_manager, 'get_animated_tile_id'):
                            key_id = animated_tile_manager.get_animated_tile_id("key_item")
                            if key_id:
                                loaded_item["image"] = animated_tile_manager.get_animated_tile_frame(key_id)
                        elif item["name"] == "Crystal" and hasattr(animated_tile_manager, 'get_animated_tile_id'):
                            crystal_id = animated_tile_manager.get_animated_tile_id("crystal_item")
                            if crystal_id:
                                loaded_item["image"] = animated_tile_manager.get_animated_tile_frame(crystal_id)
                        else:
                            # Placeholder image for unknown items
                            placeholder = pygame.Surface((16, 16), pygame.SRCALPHA)
                            placeholder.fill((255, 0, 0, 128))
                            loaded_item["image"] = placeholder

                        loaded_contents[i] = loaded_item

            self.chest_contents[position] = loaded_contents

    def get_chest_contents(self, position):
        """Get the contents of a chest at the given position

        Args:
            position: Position of the chest (x, y) tuple

        Returns:
            List of items in the chest
        """
        return self.chest_contents.get(position, [None] * 60)  # Return empty 60-slot inventory if not found

    def set_chest_contents(self, position, contents):
        """Set the contents of a chest at the given position

        Args:
            position: Position of the chest (x, y) tuple
            contents: List of items to put in the chest
        """
        self.chest_contents[position] = contents

    def set_on_chest_opened_callback(self, callback):
        """Set the callback to be called when a chest is opened

        Args:
            callback: Function to call when a chest is opened
                     The function should take two arguments: position and contents
        """
        self.on_chest_opened_callback = callback

    def initialize_chest_contents(self, position):
        """Initialize chest contents with an empty inventory

        Args:
            position: Position of the chest (x, y) tuple
        """
        # Create an empty chest inventory (60 slots)
        contents = [None] * 60

        # No default items - chest starts completely empty
        print(f"Initialized empty chest at position {position}")

        # Store the contents
        self.chest_contents[position] = contents

    def update_chest_contents(self, position, new_contents):
        """Update chest contents with new inventory items

        Args:
            position: Position of the chest (x, y) tuple
            new_contents: List of items representing the new chest contents
        """
        if position in self.chest_contents:
            self.chest_contents[position] = new_contents.copy()
        else:
            # Initialize the chest if it doesn't exist
            self.chest_contents[position] = new_contents.copy()
