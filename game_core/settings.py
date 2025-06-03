"""
Game settings module - contains all game configuration parameters
   - Screen dimensions and FPS
   - Color definitions
   - Font settings
   - The aspect ratio maintenance function
"""

# Screen settings
WIDTH, HEIGHT = 1280, 720  # Initial dimensions (16:9 aspect ratio)
ORIGINAL_WIDTH, ORIGINAL_HEIGHT = WIDTH, HEIGHT

# Frame rate settings
FPS = 60  # Target frame rate (locked to 30 FPS for consistent performance)
ENABLE_VSYNC = True  # Enable VSync for smoother frame pacing
FRAME_RATE_STRICT = True  # Enforce strict 30 FPS cap (prevents going higher)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Font settings
FONT_REGULAR = 'fonts/Poppins-Regular.ttf'
FONT_BOLD = 'fonts/Poppins-Bold.ttf'
FONT_MEDIUM = 'fonts/Poppins-Medium.ttf'
FONT_LIGHT = 'fonts/Poppins-Light.ttf'
FONT_SEMIBOLD = 'fonts/Poppins-SemiBold.ttf'

# Font sizes - web-like typography
FONT_SIZE_TINY = 10      # For very small labels, hints
FONT_SIZE_SMALL = 14     # For secondary text, descriptions
FONT_SIZE_MEDIUM = 18    # For primary UI text, buttons
FONT_SIZE_LARGE = 24     # For section headers, important labels
FONT_SIZE_TITLE = 32     # For screen titles, main headers

# Function to maintain aspect ratio when resizing
def maintain_aspect_ratio(width, height, target_ratio=16/9):
    current_ratio = width / height

    if current_ratio > target_ratio:
        # Too wide, adjust width
        new_width = int(height * target_ratio)
        return new_width, height
    elif current_ratio < target_ratio:
        # Too tall, adjust height
        new_height = int(width / target_ratio)
        return width, new_height
    else:
        # Ratio is already correct
        return width, height
