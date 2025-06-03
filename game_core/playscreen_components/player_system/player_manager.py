"""
Player Manager - Main coordinator for all player-related functionality

Extracted from PlayScreen to handle all player management operations.

RESPONSIBILITY: Main coordinator that brings everything together

FEATURES:
- Provides a single interface for all player operations
- Coordinates creation, positioning, and state management
- Manages player state and interactions
- Provides player information and status
- Handles cleanup and resource management

This is the main entry point for all player-related operations. It coordinates
the individual components (PlayerStateManager, PlayerPositionManager) to provide
a unified interface for creating, managing, and interacting with the player.
"""
from typing import Optional, Tuple, Dict, Any
from character_system import PlayerCharacter
from .player_state_manager import PlayerStateManager
from .player_position_manager import PlayerPositionManager


class PlayerManager:
    """Main coordinator for all player-related functionality"""
    
    def __init__(self, grid_cell_size: int = 16):
        # Initialize components
        self.state_manager = PlayerStateManager()
        self.position_manager = PlayerPositionManager(grid_cell_size)
        
        # Current player instance
        self.player: Optional[PlayerCharacter] = None
        
        # Grid size for calculations
        self.grid_cell_size = grid_cell_size
        
        # Map boundaries
        self.map_width = 0
        self.map_height = 0
        
    def create_player(self, map_data: Dict[str, Any], map_name: str, 
                     map_width: int, map_height: int, 
                     player_location_tracker, is_teleporting: bool = False,
                     teleport_position: Optional[Tuple[int, int]] = None) -> PlayerCharacter:
        """
        Create and initialize a player character.
        
        Args:
            map_data: The loaded map data
            map_name: Name of the current map
            map_width: Width of the map in tiles
            map_height: Height of the map in tiles
            player_location_tracker: The player location tracker instance
            is_teleporting: Whether the player is teleporting
            teleport_position: Position to teleport to (if teleporting)
            
        Returns:
            PlayerCharacter: The created player instance
        """
        # Store map dimensions
        self.map_width = map_width
        self.map_height = map_height
        
        # Determine player position
        if is_teleporting and teleport_position:
            # Use teleport position
            player_x, player_y = teleport_position
            player_direction = "down"  # Default direction after teleport
        else:
            # Use position manager to determine starting position
            player_x, player_y, player_direction = self.position_manager.determine_starting_position(
                map_data, map_name, map_width, map_height, 
                player_location_tracker, self.grid_cell_size
            )
        
        # Create the player character
        self.player = PlayerCharacter(player_x, player_y)
        self.player.direction = player_direction
        
        # Set map boundaries
        self.set_map_boundaries(map_width, map_height)
        
        # Initialize player state from map data or saved data
        self.state_manager.initialize_player_state(
            self.player, map_data, map_name, player_location_tracker, is_teleporting
        )
        
        print(f"Player created at position ({player_x}, {player_y}) facing {player_direction}")
        
        return self.player
    
    def set_map_boundaries(self, map_width: int, map_height: int):
        """Set the map boundaries for the player"""
        if self.player:
            # Always use base grid size (16) for logical coordinates, not the zoomed grid size
            base_grid_size = 16  # This should always be 16 for logical coordinates
            self.player.set_map_boundaries(
                0, 0,  # Min X, Min Y
                map_width * base_grid_size,  # Max X
                map_height * base_grid_size  # Max Y
            )
    
    def update_player(self, collision_handler, expanded_mapping, map_data) -> bool:
        """
        Update the player and handle collisions.
        
        Args:
            collision_handler: The collision handler instance
            expanded_mapping: The tile mapping
            map_data: The map data for collision detection
            
        Returns:
            bool: True if player died this frame
        """
        if not self.player:
            return False
        
        # Check if player is dead and death animation is complete
        if self.player.is_dead and self.player.death_animation_complete:
            return True
        
        # Store original position for collision detection
        original_x = self.player.rect.x
        original_y = self.player.rect.y
        
        # Update player (handles input and animation)
        self.player.update()
        
        # Check for collisions with solid tiles
        if collision_handler.check_collision(self.player.rect, expanded_mapping, map_data):
            # Collision detected, revert to original position
            self.player.rect.x = original_x
            self.player.rect.y = original_y
            
            # If player is being knocked back, reduce knockback velocity to prevent getting stuck
            if self.player.is_knocked_back:
                self.player.knockback_velocity[0] *= 0.5
                self.player.knockback_velocity[1] *= 0.5
        
        return False

    def unstuck_player(self, collision_handler, expanded_mapping, map_data):
        """Attempt to unstuck the player if they're stuck in a collision

        Args:
            collision_handler: The collision handler instance
            expanded_mapping: The tile mapping
            map_data: The map data for collision detection

        Returns:
            bool: True if player was successfully unstuck, False otherwise
        """
        if not self.player:
            return False

        # Check if player is currently stuck in a collision
        if not collision_handler.check_collision(self.player.rect, expanded_mapping, map_data):
            return False  # Player is not stuck

        print(f"Player is stuck at position ({self.player.rect.x}, {self.player.rect.y}), attempting to unstuck...")

        # Find the nearest free space
        free_position = collision_handler.find_nearest_free_space(
            self.player.rect, expanded_mapping, map_data
        )

        if free_position:
            old_x, old_y = self.player.rect.x, self.player.rect.y
            self.player.rect.x, self.player.rect.y = free_position

            # Update the player's position in the physics system
            self.player.update_position()

            # Reset movement states to prevent further issues
            self.player.velocity = [0, 0]
            self.player.is_knocked_back = False
            self.player.knockback_velocity = [0, 0]

            print(f"Player unstuck: moved from ({old_x}, {old_y}) to ({self.player.rect.x}, {self.player.rect.y})")
            return True
        else:
            print("Warning: Could not find free space to unstuck player!")
            return False

    def get_player(self) -> Optional[PlayerCharacter]:
        """Get the current player instance"""
        return self.player
    
    def get_player_position(self) -> Optional[Tuple[int, int]]:
        """Get the current player position"""
        if self.player:
            return (self.player.rect.x, self.player.rect.y)
        return None
    
    def get_player_rect(self):
        """Get the player's rect for collision detection"""
        if self.player:
            return self.player.rect
        return None
    
    def get_player_state(self) -> Dict[str, Any]:
        """Get comprehensive player state information"""
        if not self.player:
            return {}
        
        return {
            "position": (self.player.rect.x, self.player.rect.y),
            "direction": self.player.direction,
            "health": self.player.current_health,
            "max_health": self.player.max_health,
            "shield_durability": self.player.shield_durability,
            "is_dead": self.player.is_dead,
            "is_attacking": self.player.is_attacking,
            "is_shielded": self.player.is_shielded,
            "is_knocked_back": self.player.is_knocked_back,
            "state": self.player.state
        }
    
    def set_player_position(self, x: int, y: int):
        """Set the player's position"""
        if self.player:
            self.player.rect.x = x
            self.player.rect.y = y
            self.player.update_position()
    
    def save_player_location(self, map_name: str, player_location_tracker):
        """Save the current player location"""
        if self.player and map_name:
            self.position_manager.save_player_location(
                self.player, map_name, player_location_tracker
            )
    
    def handle_teleportation(self, target_position: Tuple[int, int], target_direction: str = "down"):
        """Handle player teleportation to a new position"""
        if self.player:
            self.player.rect.x, self.player.rect.y = target_position
            self.player.direction = target_direction
            self.player.update_position()
    
    def reset_player(self):
        """Reset/clear the current player"""
        self.player = None
        self.state_manager.reset()
        self.position_manager.reset()
    
    def is_player_alive(self) -> bool:
        """Check if the player is alive"""
        return self.player is not None and not self.player.is_dead
    
    def get_grid_cell_size(self) -> int:
        """Get the current grid cell size"""
        return self.grid_cell_size
    
    def set_grid_cell_size(self, grid_cell_size: int):
        """Update the grid cell size"""
        self.grid_cell_size = grid_cell_size
        self.position_manager.set_grid_cell_size(grid_cell_size)
        
        # Update map boundaries if we have a player
        if self.player:
            self.set_map_boundaries(self.map_width, self.map_height)
