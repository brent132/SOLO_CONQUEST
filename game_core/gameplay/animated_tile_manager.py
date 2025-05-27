"""
Animated Tile Manager - handles loading and managing animated tiles
"""
import os
import pygame
from gameplay.animated_tile import AnimatedTile

class AnimatedTileManager:
    """Manages loading and updating animated tiles"""
    # Singleton instance
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnimatedTileManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not AnimatedTileManager._initialized:
            self.animated_tiles = {}  # Dictionary of animated tiles by name
            self.animated_tile_ids = {}  # Dictionary mapping tile IDs to animated tiles
            self.next_tile_id = 1000  # Start animated tile IDs at 1000 to avoid conflicts

            # Load animated tiles
            self.load_animated_tiles()

            # AnimatedTileManager initialized successfully

            AnimatedTileManager._initialized = True

    def load_animated_tiles(self):
        """Load all animated tiles from the animated tiles folder"""
        animated_tiles_folder = "Tilesets/Overworld_ani_tiles"

        # Check if directory exists
        if not os.path.exists(animated_tiles_folder):
            print(f"Animated tiles folder not found: {animated_tiles_folder}")
            return

        # Get all subdirectories (each subdirectory is an animated tile)
        try:
            tile_folders = [f for f in os.listdir(animated_tiles_folder)
                           if os.path.isdir(os.path.join(animated_tiles_folder, f))]

            for folder in tile_folders:
                folder_path = os.path.join(animated_tiles_folder, folder)

                # Create an animated tile for this folder
                animated_tile = AnimatedTile(folder_path)

                # Skip if no frames were loaded
                if not animated_tile.frames:
                    continue

                # Store the animated tile
                self.animated_tiles[folder] = animated_tile

                # Assign a unique ID to this animated tile
                self.animated_tile_ids[self.next_tile_id] = folder
                self.next_tile_id += 1

            # Load key item animation
            key_item_folder = "character/Props_Items_(animated)/key_item_anim"
            if os.path.exists(key_item_folder):
                try:
                    # Create an animated tile for the key item
                    key_item_tile = AnimatedTile(key_item_folder, frame_duration=10)

                    # Skip if no frames were loaded
                    if key_item_tile.frames:
                        # Store the animated tile with a special name
                        tile_name = "key_item"
                        self.animated_tiles[tile_name] = key_item_tile

                        # Assign a unique ID to this animated tile
                        self.animated_tile_ids[self.next_tile_id] = tile_name
                        self.next_tile_id += 1
                        print(f"Added key item animation with ID: {self.next_tile_id - 1}")
                    else:
                        print("No frames loaded for key item animation")
                except Exception as e:
                    print(f"Error loading key item animation: {e}")
            else:
                print(f"Key item animation folder not found: {key_item_folder}")

            # Load crystal item animation
            crystal_item_folder = "character/Props_Items_(animated)/crystal_item_anim"
            if os.path.exists(crystal_item_folder):
                try:
                    # Create an animated tile for the crystal item
                    crystal_item_tile = AnimatedTile(crystal_item_folder, frame_duration=10)

                    # Skip if no frames were loaded
                    if crystal_item_tile.frames:
                        # Store the animated tile with a special name
                        tile_name = "crystal_item"
                        self.animated_tiles[tile_name] = crystal_item_tile

                        # Assign a unique ID to this animated tile
                        self.animated_tile_ids[self.next_tile_id] = tile_name
                        self.next_tile_id += 1
                        print(f"Added crystal item animation with ID: {self.next_tile_id - 1}")
                    else:
                        print("No frames loaded for crystal item animation")
                except Exception as e:
                    print(f"Error loading crystal item animation: {e}")
            else:
                print(f"Crystal item animation folder not found: {crystal_item_folder}")

            # Load lootchest item with animation for gameplay
            lootchest_preview_path = "character/Props_Items_(animated)/lootchest_item_anim_opening/tile000.png"
            lootchest_anim_folder = "character/Props_Items_(animated)/lootchest_item_anim_strip_8"

            if os.path.exists(lootchest_preview_path) and os.path.exists(lootchest_anim_folder):
                try:
                    # Load the preview frame for the editor
                    preview_frame = pygame.image.load(lootchest_preview_path).convert_alpha()

                    # Create an AnimatedTile with the animation folder for gameplay
                    lootchest_tile = AnimatedTile(lootchest_anim_folder, frame_duration=12)  # Slower animation for chest

                    # Skip if no frames were loaded
                    if lootchest_tile.frames:
                        # Store the animated tile with a special name
                        tile_name = "lootchest_item"
                        self.animated_tiles[tile_name] = lootchest_tile

                        # Assign a unique ID to this animated tile
                        self.animated_tile_ids[self.next_tile_id] = tile_name
                        self.next_tile_id += 1
                        print(f"Added lootchest item animation with ID: {self.next_tile_id - 1}")

                        # Store the preview frame for editor use
                        self.editor_preview_frames = getattr(self, 'editor_preview_frames', {})
                        self.editor_preview_frames[tile_name] = preview_frame
                    else:
                        print("No frames loaded for lootchest item animation")
                except Exception as e:
                    print(f"Error loading lootchest item animation: {e}")
            else:
                print(f"Lootchest item files not found: {lootchest_preview_path} or {lootchest_anim_folder}")

            # Animated tiles loaded successfully
        except Exception as e:
            print(f"Error loading animated tiles: {e}")

    def update(self):
        """Update all animated tiles"""
        for animated_tile in self.animated_tiles.values():
            animated_tile.update()

    def get_animated_tile_id(self, name):
        """Get the ID for an animated tile by name"""
        for tile_id, tile_name in self.animated_tile_ids.items():
            if tile_name == name:
                return tile_id
        return None

    def get_animated_tile_by_id(self, tile_id):
        """Get an animated tile by its ID"""
        if tile_id in self.animated_tile_ids:
            tile_name = self.animated_tile_ids[tile_id]
            return self.animated_tiles.get(tile_name)
        return None

    def get_animated_tile_frame(self, tile_id):
        """Get the current frame of an animated tile by its ID"""
        animated_tile = self.get_animated_tile_by_id(tile_id)
        if animated_tile:
            return animated_tile.get_current_frame()
        return None

    def is_lootchest_tile_id(self, tile_id):
        """Check if a tile ID is a lootchest"""
        if tile_id in self.animated_tile_ids:
            tile_name = self.animated_tile_ids[tile_id]
            return tile_name == "lootchest_item"
        return False

    def get_lootchest_rect(self, grid_x, grid_y, camera_x, camera_y, grid_cell_size):
        """Get the rectangle for a lootchest at the given grid position"""
        # Calculate screen position
        screen_x = grid_x * grid_cell_size - camera_x
        screen_y = grid_y * grid_cell_size - camera_y

        # Return a rect for the lootchest
        return pygame.Rect(screen_x, screen_y, grid_cell_size, grid_cell_size)

    def is_animated_tile_id(self, tile_id):
        """Check if a tile ID belongs to an animated tile"""
        return tile_id in self.animated_tile_ids
