"""
Animation handler module - handles character animations and alignment
"""
import pygame

def blit_aligned(surface, image, position, base_size=(16, 16), animation_type="idle", direction="down"):
    """
    Blits an image to a surface with proper alignment based on animation type and direction.

    Args:
        surface (pygame.Surface): The surface to blit the image onto
        image (pygame.Surface): The image to blit
        position (tuple): The (x, y) position where the reference point should be
        base_size (tuple): The base size of the character (default: 16x16)
        animation_type (str): The type of animation ("idle", "attack", "hit", or "run")
        direction (str): The direction the character is facing ("up", "down", "left", "right")

    This function handles different alignments for different animation types and directions:
    - Idle animations (16x16): Aligned by bottom center
    - Attack animations (32x48):
      - Right: Left edge aligned with idle's left edge, vertically centered
      - Left: Right edge aligned with idle's right edge, vertically centered
      - Up: Bottom edge aligned with idle's bottom edge, horizontally centered
      - Down: Top edge aligned with idle's top edge, horizontally centered
    - Run animations (16x16): Aligned by bottom center (same as idle)
    - Hit animations (16x16): Aligned by bottom center (same as idle)
    """
    # Get the width and height of the image and base size
    width, height = image.get_rect().size
    base_width, base_height = base_size
    x, y = position

    if animation_type == "attack" or animation_type == "hit":
        if direction == "right":
            # For right attack, align left edge with idle's left edge
            # Calculate where the left edge of the idle sprite would be
            idle_left = x - base_width // 2

            # Set the left edge of the attack sprite to match
            pos_x = idle_left

            # Calculate vertical center offset
            # This centers the attack animation vertically relative to the idle animation
            # First, find where the top of the idle sprite would be
            idle_top = y - base_height
            # Then, find where the center of the idle sprite would be
            idle_center_y = idle_top + base_height // 2
            # Finally, position the attack sprite so its center aligns with the idle center
            pos_y = idle_center_y - height // 2

        elif direction == "left":
            # For left attack, align right edge with idle's right edge
            # Calculate where the right edge of the idle sprite would be
            idle_right = x + base_width // 2

            # Set the right edge of the attack sprite to match
            pos_x = idle_right - width

            # Calculate vertical center offset
            idle_top = y - base_height
            idle_center_y = idle_top + base_height // 2
            pos_y = idle_center_y - height // 2

        elif direction == "up":
            # For up attack (48x32), we want to align it so that:
            # 1. The bottom edge of the attack animation aligns with the bottom edge of the idle animation
            # 2. The attack animation is centered horizontally relative to the idle animation

            # Calculate where the bottom edge of the idle sprite would be
            idle_bottom = y

            # Calculate where the left edge of the idle sprite would be
            idle_left = x - base_width // 2

            # Calculate where the right edge of the idle sprite would be
            idle_right = x + base_width // 2

            # Calculate where the center of the idle sprite would be horizontally
            idle_center_x = (idle_left + idle_right) // 2

            # Set the bottom edge of the attack sprite to match idle's bottom edge
            pos_y = idle_bottom - height

            # Center the attack animation horizontally relative to the idle animation
            pos_x = idle_center_x - width // 2

        else:  # down
            # For down attack (48x32), we want to align it so that:
            # 1. The top edge of the attack animation aligns with the top edge of the idle animation
            # 2. The attack animation is centered horizontally relative to the idle animation

            # Calculate where the top edge of the idle sprite would be
            idle_top = y - base_height

            # Calculate where the left edge of the idle sprite would be
            idle_left = x - base_width // 2

            # Calculate where the right edge of the idle sprite would be
            idle_right = x + base_width // 2

            # Calculate where the center of the idle sprite would be horizontally
            idle_center_x = (idle_left + idle_right) // 2

            # Set the top edge of the attack sprite to match idle's top edge
            pos_y = idle_top

            # Center the attack animation horizontally relative to the idle animation
            pos_x = idle_center_x - width // 2
    else:
        # For idle animations, center horizontally and align bottom
        pos_x = x - width // 2
        pos_y = y - height

    # Blit the image at the calculated position
    surface.blit(image, (pos_x, pos_y))

    # Debug: Draw dots to show alignment points
    # Uncomment these to see the alignment points
    # pygame.draw.circle(surface, (255, 0, 0), (x, y), 2)  # Reference point (red)
    # pygame.draw.circle(surface, (0, 255, 0), (pos_x, pos_y), 2)  # Top-left corner (green)
    # pygame.draw.circle(surface, (0, 0, 255), (pos_x + width, pos_y + height), 2)  # Bottom-right corner (blue)
    #
    # # Draw idle sprite boundaries for reference
    # if animation_type == "attack":
    #     # Draw where the idle sprite would be
    #     idle_left = x - base_width // 2
    #     idle_top = y - base_height
    #     pygame.draw.rect(surface, (255, 255, 0), (idle_left, idle_top, base_width, base_height), 1)  # Yellow rectangle
