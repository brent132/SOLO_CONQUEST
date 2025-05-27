"""
Animated Tile - handles animated tiles for the game
"""
import os
import pygame

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
        """Load all animation frames from the folder"""
        # Get all PNG files in the folder
        try:
            frame_files = [f for f in os.listdir(self.folder_path) if f.endswith('.png')]
            frame_files.sort()  # Sort files to ensure consistent order

            # Load each frame
            for frame_file in frame_files:
                frame_path = os.path.join(self.folder_path, frame_file)
                try:
                    frame_img = pygame.image.load(frame_path).convert_alpha()
                    self.frames.append(frame_img)
                except Exception as e:
                    print(f"Error loading animation frame {frame_path}: {e}")

            # Animation frames loaded successfully
        except Exception as e:
            print(f"Error loading animation folder {self.folder_path}: {e}")

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
