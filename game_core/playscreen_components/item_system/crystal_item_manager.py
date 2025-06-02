"""
Crystal Item Manager - handles crystal item collection and animation
"""
import pygame
import os
from playscreen_components.animation_system import AnimatedTile

class CrystalItemManager:
    """Manages crystal item collection and animation"""
    def __init__(self):
        # Crystal item properties
        self.crystal_items = {}  # Dictionary of crystal items by position (x, y)
        self.collected_items = {}  # Dictionary of collected items with animation in progress
        self.collected_crystals = []  # List of collected crystal positions

        # Collection animation
        self.collection_animation = None
        self.collection_duration = 30  # Duration of collection animation in frames (0.5 seconds at 60 FPS)
        self.collection_frames = []  # Store all animation frames

        # Load collection animation
        self.load_collection_animation()

    def load_collection_animation(self):
        """Load the crystal item collection animation"""
        animation_folder = "character/Props_Items_(animated)/crystal_item_anim_collected"
        if os.path.exists(animation_folder):
            # Instead of using AnimatedTile, we'll load frames manually to ensure correct order
            self.collection_frames = []

            # Define the correct frame order (explicitly list the files in the desired sequence)
            frame_files = ["tile000.png", "tile001.png", "tile002.png", "tile003.png", "tile004.png"]

            # Load each frame in the specified order
            loaded_frames = []
            for frame_file in frame_files:
                frame_path = os.path.join(animation_folder, frame_file)
                if os.path.exists(frame_path):
                    try:
                        frame = pygame.image.load(frame_path).convert_alpha()
                        loaded_frames.append(frame)
                    except Exception as e:
                        print(f"Error loading crystal animation frame {frame_path}: {e}")

            # Process frames to ensure consistent size and positioning
            if loaded_frames:
                # Find the maximum dimensions
                base_width = max(frame.get_width() for frame in loaded_frames)
                base_height = max(frame.get_height() for frame in loaded_frames)

                # Process each frame
                for frame in loaded_frames:
                    # Create a new surface with consistent size
                    new_frame = pygame.Surface((base_width, base_height), pygame.SRCALPHA)

                    # Calculate position to center the frame
                    x_offset = (base_width - frame.get_width()) // 2
                    y_offset = (base_height - frame.get_height()) // 2

                    # Blit the original frame centered on the new surface
                    new_frame.blit(frame, (x_offset, y_offset))

                    # Add to processed frames
                    self.collection_frames.append(new_frame)

                # Create a dummy AnimatedTile for timing purposes
                self.collection_animation = AnimatedTile(animation_folder, frame_duration=6)

                print(f"Loaded crystal item collection animation with {len(self.collection_frames)} frames in custom order")
            else:
                print("No frames loaded for crystal item collection animation")
                self.collection_animation = None
        else:
            print(f"Crystal item collection animation folder not found: {animation_folder}")
            self.collection_animation = None

    def add_crystal_item(self, grid_x, grid_y, tile_id, layer=0):
        """Add a crystal item to the manager

        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid
            tile_id: ID of the crystal tile
            layer: Layer number the crystal is on (for proper layering)
        """
        position = (grid_x, grid_y)
        self.crystal_items[position] = {
            "tile_id": tile_id,
            "collected": False,
            "layer": layer  # Store which layer this crystal belongs to
        }

    def check_player_collision(self, player_rect, grid_cell_size):
        """Check if player collides with any crystal items"""
        # Skip if player is dead or no crystal items
        if not player_rect or not self.crystal_items:
            return None

        # Calculate player's grid position
        player_grid_x = (player_rect.centerx) // grid_cell_size
        player_grid_y = (player_rect.centery) // grid_cell_size
        player_grid_pos = (player_grid_x, player_grid_y)

        # Check if player is on a crystal item position
        if player_grid_pos in self.crystal_items and not self.crystal_items[player_grid_pos]["collected"]:
            # Mark the crystal item as collected IMMEDIATELY to prevent it from being drawn
            self.crystal_items[player_grid_pos]["collected"] = True

            # Start collection animation
            self.collected_items[player_grid_pos] = {
                "animation_frame": 0,  # Current frame index
                "timer": self.collection_duration,
                "frame_counter": 0,  # Counter for frame timing
                "layer": self.crystal_items[player_grid_pos]["layer"]  # Preserve layer information
            }

            # Add to collected crystals list
            self.collected_crystals.append(player_grid_pos)

            # Return the collected crystal position
            return player_grid_pos

        return None

    def update(self):
        """Update collection animations"""
        # Update collection animation (still needed for global animation timing)
        if self.collection_animation:
            self.collection_animation.update()

        # Update timers and animation frames for collected items
        for pos in list(self.collected_items.keys()):
            item_data = self.collected_items[pos]

            # Decrement timer
            item_data["timer"] -= 1

            # Check if animation is complete
            if item_data["timer"] <= 0:
                # Animation complete, remove from collected items
                del self.collected_items[pos]
                continue

            # Update animation frame
            if self.collection_frames:
                item_data["frame_counter"] += 1

                # Check if it's time to advance to the next frame
                if item_data["frame_counter"] >= self.collection_animation.frame_duration:
                    item_data["frame_counter"] = 0

                    # Advance to next frame, but don't loop back to the beginning
                    next_frame = item_data["animation_frame"] + 1

                    # If we've reached the last frame, stay on it until the timer expires
                    if next_frame < len(self.collection_frames):
                        item_data["animation_frame"] = next_frame

    def draw_layer(self, surface, camera_x, camera_y, grid_cell_size, layer):
        """Draw collection animations for a specific layer

        Args:
            surface: Surface to draw on
            camera_x: Camera X position
            camera_y: Camera Y position
            grid_cell_size: Size of each grid cell
            layer: Layer number to draw
        """
        if not self.collection_frames:
            return

        # Calculate zoom factor from grid cell size
        base_grid_size = 16
        zoom_factor = grid_cell_size / base_grid_size

        # Draw collection animations for items being collected on this layer
        for pos, item_data in self.collected_items.items():
            # Skip if not on the requested layer
            if item_data.get("layer", 0) != layer:
                continue

            grid_x, grid_y = pos

            # Get the specific frame for this collected item
            frame_index = item_data["animation_frame"]
            if 0 <= frame_index < len(self.collection_frames):
                frame = self.collection_frames[frame_index]

                # Calculate screen position - use the same method as tiles
                # First calculate logical position
                logical_x = grid_x * base_grid_size - camera_x
                logical_y = grid_y * base_grid_size - camera_y

                # Scale for zoom
                screen_x = logical_x * zoom_factor
                screen_y = logical_y * zoom_factor

                # Calculate the center position of the grid cell
                center_x = screen_x + grid_cell_size // 2
                center_y = screen_y + grid_cell_size // 2

                # Scale the frame to match the zoom level
                if zoom_factor != 1.0:
                    original_size = frame.get_size()
                    new_width = int(original_size[0] * zoom_factor)
                    new_height = int(original_size[1] * zoom_factor)
                    scaled_frame = pygame.transform.scale(frame, (new_width, new_height))
                else:
                    scaled_frame = frame

                # Calculate the position to center the scaled frame on the grid cell
                frame_x = center_x - scaled_frame.get_width() // 2
                frame_y = center_y - scaled_frame.get_height() // 2

                # Draw the collection animation centered on the grid cell
                surface.blit(scaled_frame, (frame_x, frame_y))

    def draw(self, surface, camera_x, camera_y, grid_cell_size):
        """Draw all collection animations (legacy method, kept for compatibility)"""
        if not self.collection_frames:
            return

        # Draw collection animations for all items being collected
        for pos, item_data in self.collected_items.items():
            grid_x, grid_y = pos

            # Get the specific frame for this collected item
            frame_index = item_data["animation_frame"]
            if 0 <= frame_index < len(self.collection_frames):
                frame = self.collection_frames[frame_index]

                # Calculate the center position of the grid cell
                center_x = (grid_x * grid_cell_size + grid_cell_size // 2) - camera_x
                center_y = (grid_y * grid_cell_size + grid_cell_size // 2) - camera_y

                # Calculate the position to center the frame on the grid cell
                frame_x = center_x - frame.get_width() // 2
                frame_y = center_y - frame.get_height() // 2

                # Draw the collection animation centered on the grid cell
                surface.blit(frame, (frame_x, frame_y))

    def is_crystal_collected(self, grid_x, grid_y):
        """Check if a crystal at the given position has been collected"""
        return (grid_x, grid_y) in self.collected_crystals

    def should_draw_crystal_item(self, grid_x, grid_y):
        """Check if a crystal item at the given position should be drawn"""
        # Don't draw the crystal item if it has been collected
        position = (grid_x, grid_y)

        # First check if this position is in the collected crystals list
        if position in self.collected_crystals:
            return False

        # Then check if it's marked as collected in the crystal_items dictionary
        if position in self.crystal_items and self.crystal_items[position]["collected"]:
            return False

        # Also check if there's a collection animation in progress for this position
        if position in self.collected_items:
            return False

        return True
