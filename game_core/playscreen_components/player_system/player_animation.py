"""
Player Animation System

This module handles all player animation logic including frame management,
timing, state transitions, and animation types. It provides a clean separation
between animation mechanics and the main player character class.
"""

from typing import Dict


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
