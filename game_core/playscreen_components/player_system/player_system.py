"""
Player System - Main coordinator for all player-related functionality

This is the main interface for the player system that coordinates all the
individual components (PlayerManager, PlayerStateManager, PlayerPositionManager).

RESPONSIBILITY: Main coordinator that brings everything together

FEATURES:
- Provides a single interface for all player operations
- Coordinates creation, positioning, and state management
- Manages player interactions and updates
- Provides player information and status
- Handles cleanup and resource management

This is the main entry point for all player-related operations. It coordinates
the individual components to provide a unified interface for creating, managing,
and interacting with the player character throughout the game.
"""
from typing import Optional, Tuple, Dict, Any
from character_system import PlayerCharacter
from .player_manager import PlayerManager


class PlayerSystem:
    """Main coordinator for all player-related functionality"""
    
    def __init__(self, grid_cell_size: int = 16):
        # Initialize the main player manager (which coordinates other components)
        self.player_manager = PlayerManager(grid_cell_size)
        
        # Current state
        self.is_initialized = False
        
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
        player = self.player_manager.create_player(
            map_data, map_name, map_width, map_height,
            player_location_tracker, is_teleporting, teleport_position
        )
        
        self.is_initialized = True
        return player
    
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
        return self.player_manager.update_player(collision_handler, expanded_mapping, map_data)

    def unstuck_player(self, collision_handler, expanded_mapping, map_data):
        """Attempt to unstuck the player if they're stuck in a collision

        Args:
            collision_handler: The collision handler instance
            expanded_mapping: The tile mapping
            map_data: The map data for collision detection

        Returns:
            bool: True if player was successfully unstuck, False otherwise
        """
        return self.player_manager.unstuck_player(collision_handler, expanded_mapping, map_data)

    def get_player(self) -> Optional[PlayerCharacter]:
        """Get the current player instance"""
        return self.player_manager.get_player()
    
    def get_player_rect(self):
        """Get the player's rect for collision detection"""
        return self.player_manager.get_player_rect()
    
    def get_player_position(self) -> Optional[Tuple[int, int]]:
        """Get the current player position"""
        return self.player_manager.get_player_position()
    
    def set_player_position(self, x: int, y: int):
        """Set the player's position"""
        self.player_manager.set_player_position(x, y)
    
    def handle_teleportation(self, target_position: Tuple[int, int], target_direction: str = "down"):
        """Handle player teleportation to a new position"""
        self.player_manager.handle_teleportation(target_position, target_direction)
    
    def save_player_location(self, map_name: str, player_location_tracker):
        """Save the current player location"""
        self.player_manager.save_player_location(map_name, player_location_tracker)
    
    def get_player_state(self) -> Dict[str, Any]:
        """Get comprehensive player state information"""
        return self.player_manager.get_player_state()
    
    def get_player_health_info(self) -> Dict[str, Any]:
        """Get player health information"""
        player = self.get_player()
        if player:
            return self.player_manager.state_manager.get_player_health_info(player)
        return {}
    
    def get_player_shield_info(self) -> Dict[str, Any]:
        """Get player shield information"""
        player = self.get_player()
        if player:
            return self.player_manager.state_manager.get_player_shield_info(player)
        return {}
    
    def get_player_status_info(self) -> Dict[str, Any]:
        """Get player status information"""
        player = self.get_player()
        if player:
            return self.player_manager.state_manager.get_player_status_info(player)
        return {}
    
    def get_position_info(self) -> Dict[str, Any]:
        """Get player position information"""
        player = self.get_player()
        if player:
            return self.player_manager.position_manager.get_position_info(player)
        return {}
    
    def heal_player(self, amount: int = 10) -> bool:
        """Heal the player by the specified amount"""
        player = self.get_player()
        if player:
            return self.player_manager.state_manager.heal_player(player, amount)
        return False
    
    def damage_player(self, amount: int = 10) -> bool:
        """Damage the player by the specified amount"""
        player = self.get_player()
        if player:
            return self.player_manager.state_manager.damage_player(player, amount)
        return False
    
    def revive_player(self, health: int = None):
        """Revive a dead player"""
        player = self.get_player()
        if player:
            self.player_manager.state_manager.revive_player(player, health)
    
    def is_player_alive(self) -> bool:
        """Check if the player is alive"""
        return self.player_manager.is_player_alive()
    
    def is_player_dead(self) -> bool:
        """Check if the player is dead"""
        player = self.get_player()
        return player is not None and player.is_dead
    
    def is_death_animation_complete(self) -> bool:
        """Check if death animation is complete"""
        player = self.get_player()
        return player is not None and getattr(player, 'death_animation_complete', False)
    
    def set_grid_cell_size(self, grid_cell_size: int):
        """Update the grid cell size"""
        self.player_manager.set_grid_cell_size(grid_cell_size)
    
    def set_map_boundaries(self, map_width: int, map_height: int):
        """Set the map boundaries for the player"""
        self.player_manager.set_map_boundaries(map_width, map_height)
    
    def clear_player(self):
        """Clear/reset the current player"""
        self.player_manager.reset_player()
        self.is_initialized = False
    
    def get_memory_usage_info(self) -> Dict[str, Any]:
        """Get memory usage information for the player system"""
        player = self.get_player()
        
        return {
            "is_initialized": self.is_initialized,
            "has_player": player is not None,
            "player_state": self.get_player_state() if player else {},
            "grid_cell_size": self.player_manager.get_grid_cell_size()
        }
