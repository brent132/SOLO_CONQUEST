"""
Player Animation System

This module handles all player animation logic including frame management,
timing, state transitions, and animation types. It provides a clean separation
between animation mechanics and the main player character class. This module also
exposes the `blit_aligned` helper used for drawing sprites with proper alignment.
"""
from typing import Dict
import pygame


class PlayerAnimation:
    """Handles all player animation logic and state management"""
    
    def __init__(self, player_character):
        """
        Initialize the animation system
        
        Args:
            player_character: Reference to the PlayerCharacter instance
        """
        self.player = player_character
        
        # Animation timing configuration
        self.animation_speed = 0.1  # Regular animation speed (frames per update)
        self.attack_speed = 0.2  # Attack animation speed (faster than regular)
        self.hit_animation_speed = 0.15  # Hit animation speed
        self.death_animation_speed = 0.1  # Death animation speed
        
        # Animation state tracking
        self.animation_timer = 0.0  # Timer for regular animations
        self.frame = 0  # Current frame for regular animations
        
        # Attack animation state
        self.attack_frame = 0  # Current frame for attack animation
        
        # Hit animation state
        self.hit_frame = 0  # Current frame for hit animation
        
        # Death animation state
        self.death_frame = 0  # Current frame for death animation
        self.death_animation_timer = 0.0  # Timer for death animation
        self.death_animation_complete = False  # Whether death animation finished
        
        # Current animation tracking
        self.current_animation_key = "idle_down"  # Current animation being played
        self.current_animation_image = None  # Current frame image
        
    def get_animation_key(self) -> str:
        """
        Determine the appropriate animation key based on player state
        
        Returns:
            str: Animation key (e.g., "idle_down", "attack_left", etc.)
        """
        # Handle death animation first (highest priority)
        if self.player.is_dead:
            return f"death_{self.player.direction}"
        
        # Handle special states with priority order
        if self.player.is_knocked_back and self.player.is_shielded:
            return f"shield_hit_{self.player.direction}"
        elif self.player.is_knocked_back:
            return f"hit_{self.player.direction}"
        elif self.player.is_attacking:
            return f"attack_{self.player.direction}"
        elif self.player.is_shielded:
            return f"shield_{self.player.direction}"
        else:
            # Regular movement states
            return f"{self.player.state}_{self.player.direction}"
    
    def get_fallback_animation_key(self, requested_key: str) -> str:
        """
        Get a fallback animation key if the requested one doesn't exist
        
        Args:
            requested_key: The originally requested animation key
            
        Returns:
            str: A valid fallback animation key
        """
        sprites = self.player.sprites
        
        # If the requested animation exists, use it
        if requested_key in sprites and sprites[requested_key]:
            return requested_key
        
        # Extract animation type and direction
        parts = requested_key.split("_")
        if len(parts) < 2:
            return "idle_down"  # Ultimate fallback
        
        anim_type = parts[0]
        direction = parts[-1]  # Last part is always direction
        
        # Handle special fallback cases
        if "shield_hit" in requested_key:
            # Try regular hit animation first
            hit_key = f"hit_{direction}"
            if hit_key in sprites and sprites[hit_key]:
                return hit_key
            # Then try shield animation
            shield_key = f"shield_{direction}"
            if shield_key in sprites and sprites[shield_key]:
                return shield_key
        elif anim_type == "attack":
            # Try idle animation for the same direction
            idle_key = f"idle_{direction}"
            if idle_key in sprites and sprites[idle_key]:
                return idle_key
        elif anim_type == "run":
            # Try idle animation for the same direction
            idle_key = f"idle_{direction}"
            if idle_key in sprites and sprites[idle_key]:
                return idle_key
        
        # Ultimate fallback
        return "idle_down"
    
    def update_death_animation(self) -> bool:
        """
        Update death animation
        
        Returns:
            bool: True if animation is complete
        """
        animation_key = f"death_{self.player.direction}"
        sprites = self.player.sprites
        
        # Update death animation timer
        self.death_animation_timer += self.death_animation_speed
        if self.death_animation_timer >= 1:
            self.death_animation_timer = 0
            self.death_frame += 1
            
            # Check if death animation is complete
            if animation_key in sprites and self.death_frame >= len(sprites[animation_key]):
                self.death_frame = len(sprites[animation_key]) - 1  # Stay on last frame
                self.death_animation_complete = True
                
        # Set the current image
        if animation_key in sprites and sprites[animation_key]:
            frame_index = min(self.death_frame, len(sprites[animation_key]) - 1)
            self.current_animation_image = sprites[animation_key][frame_index]
        else:
            # Fallback to idle
            self.current_animation_image = sprites["idle_down"][0]
            
        return self.death_animation_complete
    
    def update_hit_animation(self, animation_key: str):
        """
        Update hit/knockback animation
        
        Args:
            animation_key: The hit animation key to use
        """
        sprites = self.player.sprites
        
        # Update hit animation timer
        self.animation_timer += self.hit_animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.hit_frame += 1
            
            # Check if hit animation is complete
            if animation_key in sprites and self.hit_frame >= len(sprites[animation_key]):
                self.hit_frame = len(sprites[animation_key]) - 1  # Stay on last frame
        
        # Set the current image
        if animation_key in sprites and sprites[animation_key]:
            frame_index = min(self.hit_frame, len(sprites[animation_key]) - 1)
            self.current_animation_image = sprites[animation_key][frame_index]
        else:
            # Fallback to idle
            self.current_animation_image = sprites["idle_down"][0]
    
    def update_attack_animation(self, animation_key: str):
        """
        Update attack animation
        
        Args:
            animation_key: The attack animation key to use
        """
        sprites = self.player.sprites
        
        # Update attack animation timer (faster than regular animations)
        self.animation_timer += self.attack_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            self.attack_frame += 1
            
            # Check if attack animation is complete
            if animation_key in sprites and self.attack_frame >= len(sprites[animation_key]):
                # Attack animation complete, stop attacking
                self.player.is_attacking = False
                self.attack_frame = 0
                
                # Switch to idle animation
                idle_key = f"idle_{self.player.direction}"
                if idle_key in sprites and sprites[idle_key]:
                    self.current_animation_image = sprites[idle_key][0]
                else:
                    self.current_animation_image = sprites["idle_down"][0]
                return
        
        # Set the current image
        if animation_key in sprites and sprites[animation_key]:
            frame_index = min(self.attack_frame, len(sprites[animation_key]) - 1)
            self.current_animation_image = sprites[animation_key][frame_index]
        else:
            # Fallback to idle
            self.current_animation_image = sprites["idle_down"][0]
    
    def update_shield_animation(self, animation_key: str):
        """
        Update shield animation (single frame)
        
        Args:
            animation_key: The shield animation key to use
        """
        sprites = self.player.sprites
        
        # Shield animations have only one frame
        if animation_key in sprites and sprites[animation_key]:
            self.current_animation_image = sprites[animation_key][0]
        else:
            # Fallback to idle
            idle_key = f"idle_{self.player.direction}"
            if idle_key in sprites and sprites[idle_key]:
                self.current_animation_image = sprites[idle_key][0]
            else:
                self.current_animation_image = sprites["idle_down"][0]
    
    def update_regular_animation(self, animation_key: str):
        """
        Update regular animations (idle, run)
        
        Args:
            animation_key: The animation key to use
        """
        sprites = self.player.sprites
        
        # Update animation timer
        self.animation_timer += self.animation_speed
        if self.animation_timer >= 1:
            self.animation_timer = 0
            if animation_key in sprites and sprites[animation_key]:
                self.frame = (self.frame + 1) % len(sprites[animation_key])
        
        # Set the current image
        if animation_key in sprites and sprites[animation_key]:
            self.current_animation_image = sprites[animation_key][self.frame]
        else:
            # Fallback to idle
            self.current_animation_image = sprites["idle_down"][0]

    def update_animation(self) -> Dict[str, any]:
        """
        Main animation update method - determines and updates the current animation

        Returns:
            Dict containing animation data: {
                'image': pygame.Surface,
                'animation_key': str,
                'frame': int,
                'animation_complete': bool
            }
        """
        # Handle death animation first (highest priority)
        if self.player.is_dead:
            animation_complete = self.update_death_animation()
            return {
                'image': self.current_animation_image,
                'animation_key': self.current_animation_key,
                'frame': self.death_frame,
                'animation_complete': animation_complete
            }

        # Get the appropriate animation key
        requested_key = self.get_animation_key()
        animation_key = self.get_fallback_animation_key(requested_key)
        self.current_animation_key = animation_key

        # Update the appropriate animation type
        if self.player.is_knocked_back:
            self.update_hit_animation(animation_key)
        elif self.player.is_attacking:
            self.update_attack_animation(animation_key)
        elif self.player.is_shielded:
            self.update_shield_animation(animation_key)
        else:
            self.update_regular_animation(animation_key)

        return {
            'image': self.current_animation_image,
            'animation_key': animation_key,
            'frame': self.get_current_frame(),
            'animation_complete': False
        }

    def get_current_frame(self) -> int:
        """Get the current frame number for the active animation"""
        if self.player.is_dead:
            return self.death_frame
        elif self.player.is_knocked_back:
            return self.hit_frame
        elif self.player.is_attacking:
            return self.attack_frame
        else:
            return self.frame

    def reset_animation_state(self):
        """Reset all animation state to default values"""
        self.animation_timer = 0.0
        self.frame = 0
        self.attack_frame = 0
        self.hit_frame = 0
        self.death_frame = 0
        self.death_animation_timer = 0.0
        self.death_animation_complete = False
        self.current_animation_key = "idle_down"

    def start_attack_animation(self):
        """Start an attack animation"""
        self.attack_frame = 0
        self.animation_timer = 0.0
        self.player.is_attacking = True

    def start_hit_animation(self):
        """Start a hit/knockback animation"""
        self.hit_frame = 0
        self.animation_timer = 0.0

    def start_death_animation(self):
        """Start the death animation"""
        self.death_frame = 0
        self.death_animation_timer = 0.0
        self.death_animation_complete = False

    def set_animation_speeds(self, regular: float = None, attack: float = None,
                           hit: float = None, death: float = None):
        """
        Set animation speeds for different animation types

        Args:
            regular: Speed for regular animations (idle, run)
            attack: Speed for attack animations
            hit: Speed for hit animations
            death: Speed for death animations
        """
        if regular is not None:
            self.animation_speed = regular
        if attack is not None:
            self.attack_speed = attack
        if hit is not None:
            self.hit_animation_speed = hit
        if death is not None:
            self.death_animation_speed = death

    def get_animation_info(self) -> Dict[str, any]:
        """
        Get comprehensive information about the current animation state

        Returns:
            Dict containing animation state information
        """
        return {
            'current_animation_key': self.current_animation_key,
            'current_frame': self.get_current_frame(),
            'animation_timer': self.animation_timer,
            'is_attacking': self.player.is_attacking,
            'is_knocked_back': self.player.is_knocked_back,
            'is_shielded': self.player.is_shielded,
            'is_dead': self.player.is_dead,
            'death_animation_complete': self.death_animation_complete,
            'animation_speeds': {
                'regular': self.animation_speed,
                'attack': self.attack_speed,
                'hit': self.hit_animation_speed,
                'death': self.death_animation_speed
            }
        }
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
