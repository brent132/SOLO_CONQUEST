"""Configuration settings for the map editor."""

# Screen settings
WIDTH, HEIGHT = 1280, 720  # Default window size

# Frame rate
FPS = 60  # Target frames per second

# Colors used by the editor
BACKGROUND_COLOR = (20, 40, 20)  # dark green background
FONT_COLOR = (255, 255, 255)

# Path to default font
FONT_PATH = 'fonts/Poppins-Regular.ttf'


def maintain_aspect_ratio(width: int, height: int, target_ratio: float = 16/9):
    """Adjust the width and height to maintain the target aspect ratio."""
    current_ratio = width / height
    if current_ratio > target_ratio:
        new_width = int(height * target_ratio)
        return new_width, height
    elif current_ratio < target_ratio:
        new_height = int(width / target_ratio)
        return width, new_height
    return width, height
