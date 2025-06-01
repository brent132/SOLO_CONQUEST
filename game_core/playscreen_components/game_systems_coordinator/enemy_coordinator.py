"""
Enemy Coordinator - Handles enemy-player interactions and combat coordination

This module manages:
- Enemy updates and AI
- Enemy-player collision detection and knockback
- Player attack vs enemy collision detection
- Combat state management
"""
from typing import Optional, Dict, Any, List
import pygame


class EnemyCoordinator:
    """Coordinates enemy systems and player interactions"""
    
    def __init__(self):
        self.enemy_manager = None
        
    def initialize(self, enemy_manager):
        """Initialize with the enemy manager"""
        self.enemy_manager = enemy_manager
        
    def update_enemy_systems(self, player, collision_handler, expanded_mapping, 
                           collision_map_data, layers) -> bool:
        """
        Update enemy systems and handle all enemy-player interactions
        
        Args:
            player: The player character
            collision_handler: Collision detection handler
            expanded_mapping: Tile mapping for collision detection
            collision_map_data: Map data for collision detection
            layers: Map layers for validation
            
        Returns:
            bool: True if player died this frame
        """
        if not self.enemy_manager or not player or not collision_handler:
            return False
            
        # Update enemy AI and movement
        self.enemy_manager.update(
            player.rect.centerx,
            player.rect.centery,
            collision_handler=collision_handler,
            tile_mapping=expanded_mapping,
            map_data=collision_map_data
        )
        
        # Check for enemy-player collisions and apply knockback
        if layers:
            self.enemy_manager.check_player_collisions(
                player,
                collision_handler=collision_handler,
                tile_mapping=expanded_mapping,
                map_data=collision_map_data
            )
        
        # Check if player's attack hits any enemies
        self.enemy_manager.check_player_attacks(
            player,
            collision_handler=collision_handler,
            tile_mapping=expanded_mapping,
            map_data=collision_map_data
        )
        
        # Check if player died from enemy interactions
        if hasattr(player, 'is_dead') and player.is_dead:
            return True
            
        return False
        
    def get_enemy_manager(self):
        """Get the enemy manager instance"""
        return self.enemy_manager
