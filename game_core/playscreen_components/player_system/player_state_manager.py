"""
Player State Manager - Handles player state management

Extracted from PlayScreen to handle player state operations.

RESPONSIBILITY: Loading and managing player state

FEATURES:
- Loads player state from saved data
- Handles player health and shield management
- Manages player direction and animation state
- Provides state information and updates
- Integrates with save/load systems

This component manages all aspects of player state including health, shield,
direction, and other status information. It handles loading state from saved
data and maintaining state consistency throughout the game.
"""
from typing import Dict, Any, Optional
from playscreen_components.player_system import PlayerCharacter


class PlayerStateManager:
    """Handles player state management and persistence"""
    
    def __init__(self):
        # Default player state values
        self.default_health = 100
        self.default_shield_durability = 3
        self.default_direction = "down"
        
    def initialize_player_state(self, player: PlayerCharacter, map_data: Dict[str, Any], 
                               map_name: str, player_location_tracker, 
                               is_teleporting: bool = False):
        """
        Initialize player state from saved data or defaults.
        
        Args:
            player: The player character instance
            map_data: The loaded map data
            map_name: Name of the current map
            player_location_tracker: The player location tracker instance
            is_teleporting: Whether the player is teleporting
        """
        if is_teleporting:
            # When teleporting, try to load state from game state in map data
            self._load_state_from_game_data(player, map_data)
        else:
            # Normal map loading - try to load from saved location first
            self._load_state_from_saved_location(player, map_name, player_location_tracker)
            
            # If no saved state, try to load from game state in map data
            if not self._has_custom_state(player):
                self._load_state_from_game_data(player, map_data)
    
    def _load_state_from_saved_location(self, player: PlayerCharacter, map_name: str, 
                                       player_location_tracker):
        """Load player state from saved location data"""
        try:
            # Determine which folder (world) this map belongs to
            folder_name = player_location_tracker._determine_folder_name(map_name)
            
            # Get the location for this specific world
            world_location = player_location_tracker.get_world_location(folder_name)
            
            if world_location:
                # Load state from world-specific location
                player.current_health = world_location.get("health", self.default_health)
                player.shield_durability = world_location.get("shield_durability", self.default_shield_durability)
                print(f"Loaded player state from world '{folder_name}': Health={player.current_health}, Shield={player.shield_durability}")
                return True
            
            # Fallback: check if there's a saved location for this specific map
            elif player_location_tracker.has_location(map_name):
                saved_location = player_location_tracker.get_location(map_name)
                if saved_location:
                    # Use saved state, but with default values for cross-world compatibility
                    player.current_health = saved_location.get("health", self.default_health)
                    player.shield_durability = saved_location.get("shield_durability", self.default_shield_durability)
                    print(f"Loaded player state from map '{map_name}' (fallback): Health={player.current_health}, Shield={player.shield_durability}")
                    return True
                    
        except Exception as e:
            print(f"Error loading player state from saved location: {e}")
        
        return False
    
    def _load_state_from_game_data(self, player: PlayerCharacter, map_data: Dict[str, Any]):
        """Load player state from game state data in map file"""
        try:
            if "game_state" in map_data and "player" in map_data["game_state"]:
                player_data = map_data["game_state"]["player"]
                
                if "health" in player_data:
                    player.current_health = player_data["health"]
                    print(f"Loaded player health from game state: {player.current_health}")
                
                if "shield_durability" in player_data:
                    player.shield_durability = player_data["shield_durability"]
                    print(f"Loaded player shield from game state: {player.shield_durability}")
                
                return True
                
        except Exception as e:
            print(f"Error loading player state from game data: {e}")
        
        return False
    
    def _has_custom_state(self, player: PlayerCharacter) -> bool:
        """Check if player has non-default state values"""
        return (player.current_health != self.default_health or 
                player.shield_durability != self.default_shield_durability)
    
    def get_player_health_info(self, player: PlayerCharacter) -> Dict[str, Any]:
        """Get player health information"""
        if not player:
            return {}
        
        return {
            "current_health": player.current_health,
            "max_health": player.max_health,
            "health_percentage": (player.current_health / player.max_health) * 100,
            "is_dead": player.is_dead,
            "invincibility_timer": getattr(player, 'invincibility_timer', 0)
        }
    
    def get_player_shield_info(self, player: PlayerCharacter) -> Dict[str, Any]:
        """Get player shield information"""
        if not player:
            return {}
        
        return {
            "shield_durability": player.shield_durability,
            "max_shield_durability": getattr(player, 'max_shield_durability', 3),
            "is_shielded": player.is_shielded
        }
    
    def get_player_status_info(self, player: PlayerCharacter) -> Dict[str, Any]:
        """Get comprehensive player status information"""
        if not player:
            return {}
        
        return {
            "direction": player.direction,
            "state": player.state,
            "is_attacking": player.is_attacking,
            "is_knocked_back": player.is_knocked_back,
            "is_dead": player.is_dead,
            "death_animation_complete": getattr(player, 'death_animation_complete', False)
        }
    
    def set_player_health(self, player: PlayerCharacter, health: int):
        """Set player health"""
        if player:
            player.current_health = max(0, min(health, player.max_health))
    
    def set_player_shield(self, player: PlayerCharacter, shield_durability: int):
        """Set player shield durability"""
        if player:
            max_shield = getattr(player, 'max_shield_durability', 3)
            player.shield_durability = max(0, min(shield_durability, max_shield))
    
    def heal_player(self, player: PlayerCharacter, amount: int = 10) -> bool:
        """Heal the player by the specified amount"""
        if player and not player.is_dead:
            old_health = player.current_health
            player.heal(amount)
            return player.current_health > old_health
        return False
    
    def damage_player(self, player: PlayerCharacter, amount: int = 10) -> bool:
        """Damage the player by the specified amount"""
        if player and not player.is_dead:
            return player.take_damage(amount)
        return False
    
    def revive_player(self, player: PlayerCharacter, health: int = None):
        """Revive a dead player"""
        if player and player.is_dead:
            player.is_dead = False
            player.death_animation_complete = False
            player.current_health = health if health is not None else self.default_health
            player.shield_durability = self.default_shield_durability
            print(f"Player revived with {player.current_health} health")
    
    def reset(self):
        """Reset the state manager"""
        # Reset any internal state if needed
        pass
    
    def get_state_for_saving(self, player: PlayerCharacter) -> Dict[str, Any]:
        """Get player state data for saving to file"""
        if not player:
            return {}
        
        return {
            "health": player.current_health,
            "shield_durability": player.shield_durability,
            "direction": player.direction,
            "is_dead": player.is_dead
        }
