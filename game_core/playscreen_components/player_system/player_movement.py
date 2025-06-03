"""
Player Movement System

This module handles all player movement logic including walking, running,
and directional input processing. It provides a clean separation between
movement mechanics and the main player character class.
"""

import pygame
from typing import Dict, Tuple, Optional


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

        # Enhanced debug output for all movement keys
        if any(self.movement_keys_pressed.values()):
            running_status = "RUNNING" if self.is_running else "WALKING"
            keys_active = []
            if self.movement_keys_pressed['left']: keys_active.append("A(left)")
            if self.movement_keys_pressed['right']: keys_active.append("D(right)")
            if self.movement_keys_pressed['up']: keys_active.append("W(up)")
            if self.movement_keys_pressed['down']: keys_active.append("S(down)")

            shift_status = "SHIFT_HELD" if shift_held else "NO_SHIFT"
            keys_str = "+".join(keys_active)

            # Calculate actual movement distance for this frame
            movement_distance = (velocity[0]**2 + velocity[1]**2)**0.5

            print(f"🔍 {keys_str} {running_status} {shift_status}: velocity=({velocity[0]:.1f}, {velocity[1]:.1f}) distance={movement_distance:.1f}")
            print(f"   📊 base_speed={base_speed:.1f}, current_speed={self.current_speed:.1f}, final_speed={final_speed:.1f}, speed_multiplier={self.player.speed_multiplier:.1f}")

            # Store velocity for position tracking
            self.last_velocity = velocity.copy()

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
