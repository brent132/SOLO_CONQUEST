"""
Player Movement System

This module handles all player movement logic including walking, running,
and directional input processing. It provides a clean separation between
movement mechanics and the main player character class.
"""

import pygame
from typing import Dict


class PlayerMovement:
    """Handles player movement logic including walking and running mechanics"""
    
    def __init__(self, player_character):
        """
        Initialize the movement system
        
        Args:
            player_character: Reference to the PlayerCharacter instance
        """
        self.player = player_character
        
        # Movement speed configuration
        self.base_walk_speed = 1  # Base walking speed
        self.run_speed_multiplier = 1.8  # Running speed multiplier (150% faster)
        
        # Movement state
        self.is_running = False
        self.current_speed = self.base_walk_speed
        
        # Input state tracking
        self.movement_keys_pressed = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
        
    def handle_movement_input(self, keys: pygame.key.ScancodeWrapper) -> Dict[str, any]:
        """
        Process keyboard input for player movement
        
        Args:
            keys: Pygame key state from pygame.key.get_pressed()
            
        Returns:
            Dict containing movement data: {
                'velocity': [x, y],
                'direction': str,
                'state': str,
                'is_running': bool
            }
        """
        # Reset velocity
        velocity = [0, 0]
        direction = self.player.direction  # Keep current direction as default
        state = "idle"
        
        # Check for running (Shift key held)
        shift_held = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.is_running = shift_held
        
        # Calculate current speed based on running state
        base_speed = self.player.base_speed
        if self.is_running:
            self.current_speed = base_speed * self.run_speed_multiplier
        else:
            self.current_speed = base_speed
            
        # Apply any existing speed multipliers (for effects like slowing)
        final_speed = self.current_speed * self.player.speed_multiplier
        
        # Update movement keys state
        self.movement_keys_pressed['left'] = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.movement_keys_pressed['right'] = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        self.movement_keys_pressed['up'] = keys[pygame.K_UP] or keys[pygame.K_w]
        self.movement_keys_pressed['down'] = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        # Process directional input (allow diagonal movement)
        # Handle horizontal movement
        if self.movement_keys_pressed['left']:
            velocity[0] = -final_speed
            direction = "left"
            state = "run"  # Use run animation for all movement
        elif self.movement_keys_pressed['right']:
            velocity[0] = final_speed
            direction = "right"
            state = "run"

        # Handle vertical movement (independent of horizontal)
        if self.movement_keys_pressed['up']:
            velocity[1] = -final_speed
            # Only change direction if not already moving horizontally
            if velocity[0] == 0:
                direction = "up"
            state = "run"
        elif self.movement_keys_pressed['down']:
            velocity[1] = final_speed
            # Only change direction if not already moving horizontally
            if velocity[0] == 0:
                direction = "down"
            state = "run"

        # Normalize diagonal movement to maintain consistent speed
        # If moving diagonally, the combined velocity would be faster due to Pythagorean theorem
        # We need to normalize it to maintain the intended speed
        if velocity[0] != 0 and velocity[1] != 0:
            # Calculate the current diagonal distance (before normalization)
            original_distance = (velocity[0]**2 + velocity[1]**2)**0.5

            # Normalize to the intended speed (final_speed)
            if original_distance > 0:
                normalization_factor = final_speed / original_distance
                velocity[0] *= normalization_factor
                velocity[1] *= normalization_factor

        return {
            'velocity': velocity,
            'direction': direction,
            'state': state,
            'is_running': self.is_running,
            'current_speed': self.current_speed
        }
    
    def is_moving(self) -> bool:
        """Check if the player is currently moving"""
        return any(self.movement_keys_pressed.values())
    
    def get_movement_state_info(self) -> Dict[str, any]:
        """
        Get comprehensive information about the current movement state
        
        Returns:
            Dict containing movement state information
        """
        return {
            'is_running': self.is_running,
            'is_moving': self.is_moving(),
            'current_speed': self.current_speed,
            'base_walk_speed': self.base_walk_speed,
            'run_speed_multiplier': self.run_speed_multiplier,
            'keys_pressed': self.movement_keys_pressed.copy()
        }
    
    def set_base_walk_speed(self, speed: float):
        """Set the base walking speed"""
        self.base_walk_speed = speed
        if hasattr(self.player, 'base_speed'):
            self.player.base_speed = speed
    
    def set_run_speed_multiplier(self, multiplier: float):
        """Set the running speed multiplier"""
        self.run_speed_multiplier = multiplier
    
    def reset_movement_state(self):
        """Reset all movement state to default values"""
        self.is_running = False
        self.current_speed = self.base_walk_speed
        self.movement_keys_pressed = {
            'left': False,
            'right': False,
            'up': False,
            'down': False
        }
