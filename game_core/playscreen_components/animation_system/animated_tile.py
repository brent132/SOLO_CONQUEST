"""
Animated Tile - handles animated tiles for the game
"""
import os
import pygame
from game_core.core.image_cache import sprite_cache

class AnimatedTile:
    """Class for handling animated tiles"""
    def __init__(self, folder_path, frame_duration=8):
        """
        Initialize an animated tile

        Args:
            folder_path: Path to the folder containing animation frames
            frame_duration: Number of game frames to show each animation frame
        """
        self.folder_path = folder_path
        self.frame_duration = frame_duration
        self.frames = []
        self.current_frame = 0
        self.frame_counter = 0
        self.name = os.path.basename(folder_path)

        # Load all frames from the folder
        self.load_frames()

    def load_frames(self):
        """Load all animation frames from the folder using sprite cache"""
        # Use the sprite cache to load animation frames efficiently
        self.frames = sprite_cache.get_animation_frames(self.folder_path)

        if not self.frames:
            print(f"No animation frames loaded from {self.folder_path}")

    def update(self):
        """Update the animation state"""
        if not self.frames:
            return None

        # Increment frame counter
        self.frame_counter += 1

        # Check if it's time to advance to the next frame
        if self.frame_counter >= self.frame_duration:
            self.frame_counter = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def get_current_frame(self):
        """Get the current animation frame"""
        if not self.frames:
            return None
        return self.frames[self.current_frame]
