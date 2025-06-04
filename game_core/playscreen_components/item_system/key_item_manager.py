"""
Key Item Manager - handles key item collection and animation
"""
import pygame
import os
from playscreen_components.animation_system import AnimatedTile

class KeyItemManager:
    """Manages key item collection and animation"""
    def __init__(self):
        # Key item properties
        self.key_items = {}  # Dictionary of key items by position (x, y)
        self.collected_items = {}  # Dictionary of collected items with animation in progress
        self.collected_keys = []  # List of collected key positions

        # Collection animation
        self.collection_animation = None
        self.collection_duration = 30  # Duration of collection animation in frames (reduced to 0.5 seconds at 60 FPS)
        self.collection_frames = []  # Store all animation frames

        # Load collection animation
        self.load_collection_animation()

    def clear_items(self):
        """Clear key items and related animations from the previous map"""
        self.key_items = {}
        self.collected_items = {}

    def load_collection_animation(self):
        """Load the key item collection animation"""
        animation_folder = "character/Props_Items_(animated)/key_item_collected_anim"
        if os.path.exists(animation_folder):
            self.collection_animation = AnimatedTile(animation_folder, frame_duration=5)  # Reduced frame duration for faster animation

            # Store all animation frames for direct access
            if self.collection_animation.frames:
                self.collection_frames = self.collection_animation.frames
                pass  # Loaded key item collection animation
            else:
                pass  # No frames found in key item collection animation
        else:
            pass  # Key item collection animation folder not found

    def add_key_item(self, grid_x, grid_y, tile_id, layer=0):
        """Add a key item to the manager

        Args:
            grid_x: X position on the grid
            grid_y: Y position on the grid
            tile_id: ID of the key tile
            layer: Layer number the key is on (for proper layering)
        """
        position = (grid_x, grid_y)
        self.key_items[position] = {
            "tile_id": tile_id,
            "collected": False,
            "layer": layer  # Store which layer this key belongs to
        }

    def check_player_collision(self, player_rect, grid_cell_size):
        """Check if player collides with any key items"""
        # Skip if player is dead or no key items
        if not player_rect or not self.key_items:
            return

        # Convert player position to grid coordinates
        player_grid_x = player_rect.centerx // grid_cell_size
        player_grid_y = player_rect.centery // grid_cell_size
        player_grid_pos = (player_grid_x, player_grid_y)

        # Check if player is on a key item position
        if player_grid_pos in self.key_items and not self.key_items[player_grid_pos]["collected"]:
            # Mark the key item as collected IMMEDIATELY to prevent it from being drawn
            self.key_items[player_grid_pos]["collected"] = True

            # Start collection animation
            self.collected_items[player_grid_pos] = {
                "animation_frame": 0,  # Current frame index
                "timer": self.collection_duration,
                "frame_counter": 0,  # Counter for frame timing
                "layer": self.key_items[player_grid_pos]["layer"]  # Preserve layer information
            }

            # Add to collected keys list
            self.collected_keys.append(player_grid_pos)

            # Return the collected key position
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
                    item_data["animation_frame"] = (item_data["animation_frame"] + 1) % len(self.collection_frames)

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

    def is_key_collected(self, grid_x, grid_y):
        """Check if a key at the given position has been collected"""
        return (grid_x, grid_y) in self.collected_keys

    def should_draw_key_item(self, grid_x, grid_y):
        """Check if a key item at the given position should be drawn"""
        # Don't draw the key item if it has been collected
        position = (grid_x, grid_y)

        # First check if this position is in the collected keys list
        if position in self.collected_keys:
            return False

        # Then check if it's marked as collected in the key_items dictionary
        if position in self.key_items and self.key_items[position]["collected"]:
            return False

        # Also check if there's a collection animation in progress for this position
        if position in self.collected_items:
            return False

        return True

    def get_collected_keys_count(self):
        """Get the number of collected keys"""
        return len(self.collected_keys)
