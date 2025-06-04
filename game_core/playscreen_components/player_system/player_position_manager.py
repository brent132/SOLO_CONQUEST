"""
Player Position Manager - Handles player positioning and location tracking

Extracted from PlayScreen to handle player positioning operations.

RESPONSIBILITY: Loading and managing player positioning

FEATURES:
- Determines player starting positions from various sources
- Handles saved location loading and fallbacks
- Manages map-specific player start positions
- Provides default positioning for new maps
- Integrates with player location tracking system

This component handles all aspects of player positioning including determining
where to place the player when loading a map, handling saved locations,
and managing the various fallback strategies for player placement.
"""
from typing import Tuple, Dict, Any, Optional
# Import PlayerCharacter using a relative import to avoid circular
# dependencies with the package's __init__ module during startup.
from .player_character import PlayerCharacter


class PlayerPositionManager:
    """Handles player positioning and location tracking"""
    
    def __init__(self, grid_cell_size: int = 16):
        self.grid_cell_size = grid_cell_size
        
    def determine_starting_position(self, map_data: Dict[str, Any], map_name: str,
                                  map_width: int, map_height: int,
                                  player_location_tracker, grid_cell_size: int) -> Tuple[int, int, str]:
        """
        Determine where to place the player when loading a map.
        
        Args:
            map_data: The loaded map data
            map_name: Name of the current map
            map_width: Width of the map in tiles
            map_height: Height of the map in tiles
            player_location_tracker: The player location tracker instance
            grid_cell_size: Size of grid cells in pixels
            
        Returns:
            Tuple[int, int, str]: (x, y, direction) for player placement
        """
        # Priority 1: Check for saved world-specific location
        world_position = self._get_world_location(map_name, player_location_tracker)
        if world_position:
            return world_position
        
        # Priority 2: Check for saved map-specific location (fallback)
        map_position = self._get_map_location(map_name, player_location_tracker)
        if map_position:
            return map_position
        
        # Priority 3: Check for map-defined player start position
        map_start_position = self._get_map_start_position(map_data, grid_cell_size)
        if map_start_position:
            return map_start_position
        
        # Priority 4: Default to center of map
        return self._get_default_position(map_width, map_height, grid_cell_size)
    
    def _get_world_location(self, map_name: str, player_location_tracker) -> Optional[Tuple[int, int, str]]:
        """Get player position from world-specific saved location"""
        try:
            # Determine which folder (world) this map belongs to
            folder_name = player_location_tracker._determine_folder_name(map_name)
            
            # Get the location for this specific world
            world_location = player_location_tracker.get_world_location(folder_name)
            
            if world_location:
                player_x = world_location["x"]
                player_y = world_location["y"]
                player_direction = world_location["direction"]
                
                pass  # DEBUG: Loading map in world
                pass  # DEBUG: Saved location was for map
                pass  # DEBUG: Using saved position for world
                
                return (player_x, player_y, player_direction)
                
        except Exception as e:
            pass  # Error getting world location
        
        return None
    
    def _get_map_location(self, map_name: str, player_location_tracker) -> Optional[Tuple[int, int, str]]:
        """Get player position from map-specific saved location (fallback)"""
        try:
            if player_location_tracker.has_location(map_name):
                saved_location = player_location_tracker.get_location(map_name)
                if saved_location:
                    player_x = saved_location["x"]
                    player_y = saved_location["y"]
                    player_direction = saved_location["direction"]
                    
                    pass  # Loaded saved position for map from any world (fallback)
                    
                    return (player_x, player_y, player_direction)
                    
        except Exception as e:
            pass  # Error getting map location
        
        return None
    
    def _get_map_start_position(self, map_data: Dict[str, Any], grid_cell_size: int) -> Optional[Tuple[int, int, str]]:
        """Get player position from map-defined player start position"""
        try:
            if "player_start" in map_data:
                # Use the player starting position from the map data
                player_grid_x = map_data["player_start"].get("x", 0)
                player_grid_y = map_data["player_start"].get("y", 0)
                player_x = player_grid_x * grid_cell_size
                player_y = player_grid_y * grid_cell_size
                player_direction = map_data["player_start"].get("direction", "down")
                
                pass  # Using map's player_start position
                
                return (player_x, player_y, player_direction)
                
        except Exception as e:
            pass  # Error getting map start position
        
        return None
    
    def _get_default_position(self, map_width: int, map_height: int, grid_cell_size: int) -> Tuple[int, int, str]:
        """Get default center position for the map"""
        # Default to the middle of the map
        player_x = (map_width * grid_cell_size) // 2
        player_y = (map_height * grid_cell_size) // 2
        player_direction = "down"
        
        pass  # Using default center position
        
        return (player_x, player_y, player_direction)
    
    def save_player_location(self, player: PlayerCharacter, map_name: str, player_location_tracker):
        """Save the current player location"""
        try:
            # Determine which folder (world) the current map belongs to
            current_folder_name = player_location_tracker._determine_folder_name(map_name)
            
            pass  # DEBUG: Saving player location for world
            
            # Save the current player position for the current map and world
            player_location_tracker.save_location(
                map_name,
                player.rect.x,
                player.rect.y,
                player.direction,
                player.current_health,
                player.shield_durability,
                current_folder_name
            )
            
            # Save to file
            player_location_tracker.save_to_file()
            
        except Exception as e:
            pass  # Error saving player location
    
    def get_position_info(self, player: PlayerCharacter) -> Dict[str, Any]:
        """Get comprehensive position information"""
        if not player:
            return {}
        
        return {
            "x": player.rect.x,
            "y": player.rect.y,
            "center_x": player.rect.centerx,
            "center_y": player.rect.centery,
            "grid_x": player.rect.x // self.grid_cell_size,
            "grid_y": player.rect.y // self.grid_cell_size,
            "direction": player.direction
        }
    
    def set_position(self, player: PlayerCharacter, x: int, y: int, direction: str = None):
        """Set player position and optionally direction"""
        if player:
            player.rect.x = x
            player.rect.y = y
            if direction:
                player.direction = direction
            player.update_position()
    
    def move_player_to_grid(self, player: PlayerCharacter, grid_x: int, grid_y: int):
        """Move player to a specific grid position"""
        if player:
            pixel_x = grid_x * self.grid_cell_size
            pixel_y = grid_y * self.grid_cell_size
            self.set_position(player, pixel_x, pixel_y)
    
    def get_grid_position(self, player: PlayerCharacter) -> Optional[Tuple[int, int]]:
        """Get player's current grid position"""
        if player:
            grid_x = player.rect.x // self.grid_cell_size
            grid_y = player.rect.y // self.grid_cell_size
            return (grid_x, grid_y)
        return None
    
    def is_within_map_bounds(self, player: PlayerCharacter, map_width: int, map_height: int) -> bool:
        """Check if player is within map boundaries"""
        if not player:
            return False
        
        max_x = map_width * self.grid_cell_size
        max_y = map_height * self.grid_cell_size
        
        return (0 <= player.rect.x < max_x and 
                0 <= player.rect.y < max_y)
    
    def clamp_to_map_bounds(self, player: PlayerCharacter, map_width: int, map_height: int):
        """Clamp player position to map boundaries"""
        if not player:
            return
        
        max_x = map_width * self.grid_cell_size - player.rect.width
        max_y = map_height * self.grid_cell_size - player.rect.height
        
        player.rect.x = max(0, min(player.rect.x, max_x))
        player.rect.y = max(0, min(player.rect.y, max_y))
        player.update_position()
    
    def set_grid_cell_size(self, grid_cell_size: int):
        """Update the grid cell size"""
        self.grid_cell_size = grid_cell_size
    
    def reset(self):
        """Reset the position manager"""
        # Reset any internal state if needed
        pass
