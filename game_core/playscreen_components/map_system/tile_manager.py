"""
Tile Manager - Handles tile loading and caching

Extracted from PlayScreen to handle all tile-related operations including loading,
caching, and managing different tile types.

RESPONSIBILITY: Loading and managing tiles

FEATURES:
- Loads tiles from expanded mapping
- Caches loaded tiles for performance
- Skips enemy and player tiles appropriately
- Provides memory usage information
- Integrates with the sprite cache system

This component manages all tile-related operations, including loading tiles from
the file system, caching them for performance, and providing efficient access
to tile data. It intelligently skips tiles that shouldn't be loaded (like enemy
and player sprites) and integrates with the sprite cache system for optimal
memory usage and performance.
"""
import pygame
from typing import Dict, Optional, Set
from game_core.other_components.image_cache import sprite_cache


class TileManager:
    """Handles loading and managing tiles for the map system"""
    
    def __init__(self):
        self.tiles: Dict[int, pygame.Surface] = {}
        self.excluded_paths: Set[str] = {
            "Enemies_Sprites/Phantom_Sprites",
            "Enemies_Sprites/Bomberplant_Sprites", 
            "Enemies_Sprites/Spider_Sprites",
            "Enemies_Sprites/Pinkslime_Sprites",
            "Enemies_Sprites/Pinkbat_Sprites",
            "Enemies_Sprites/Spinner_Sprites",
            "character/char_idle_"
        }
    
    def load_tiles_from_mapping(self, expanded_mapping: Dict[str, Dict]) -> Dict[str, str]:
        """
        Load all tiles from the expanded mapping.
        
        Args:
            expanded_mapping (Dict): The expanded tile mapping
            
        Returns:
            Dict[str, str]: Dictionary of any loading errors
        """
        errors = {}
        
        for tile_id, tile_info in expanded_mapping.items():
            path = tile_info["path"]
            
            try:
                # Skip animated tiles - they're handled separately
                if not path.startswith("animated:"):
                    # Skip enemy tiles and player character tiles
                    if self._should_skip_tile(path):
                        self._log_skipped_tile(path)
                        continue
                    
                    # Load the tile using sprite cache
                    sprite = sprite_cache.get_sprite(path)
                    if sprite:
                        self.tiles[int(tile_id)] = sprite
                    else:
                        errors[tile_id] = f"Failed to load sprite from {path}"
                        
            except Exception as e:
                error_msg = f"Error loading tile {path}: {e}"
                print(error_msg)
                errors[tile_id] = error_msg
        
        return errors
    
    def _should_skip_tile(self, path: str) -> bool:
        """
        Check if a tile should be skipped during loading.
        
        Args:
            path (str): The tile path to check
            
        Returns:
            bool: True if the tile should be skipped
        """
        return any(excluded_path in path for excluded_path in self.excluded_paths)
    
    def _log_skipped_tile(self, path: str):
        """Log information about skipped tiles"""
        if "Enemies_Sprites/Phantom_Sprites" in path:
            print(f"Skipping phantom enemy tile: {path}")
        elif "Enemies_Sprites/Bomberplant_Sprites" in path:
            print(f"Skipping bomberplant enemy tile: {path}")
        elif "Enemies_Sprites/Spider_Sprites" in path:
            print(f"Skipping spider enemy tile: {path}")
        elif "Enemies_Sprites/Pinkslime_Sprites" in path:
            print(f"Skipping pinkslime enemy tile: {path}")
        elif "Enemies_Sprites/Pinkbat_Sprites" in path:
            print(f"Skipping pinkbat enemy tile: {path}")
        elif "Enemies_Sprites/Spinner_Sprites" in path:
            print(f"Skipping spinner enemy tile: {path}")
        elif "character/char_idle_" in path:
            print(f"Skipping player character tile: {path}")
    
    def get_tile(self, tile_id: int) -> Optional[pygame.Surface]:
        """
        Get a loaded tile by its ID.
        
        Args:
            tile_id (int): The tile ID to retrieve
            
        Returns:
            Optional[pygame.Surface]: The tile surface, or None if not found
        """
        return self.tiles.get(tile_id)
    
    def has_tile(self, tile_id: int) -> bool:
        """
        Check if a tile is loaded.
        
        Args:
            tile_id (int): The tile ID to check
            
        Returns:
            bool: True if the tile is loaded
        """
        return tile_id in self.tiles
    
    def get_tile_count(self) -> int:
        """
        Get the number of loaded tiles.
        
        Returns:
            int: Number of loaded tiles
        """
        return len(self.tiles)
    
    def clear_tiles(self):
        """Clear all loaded tiles"""
        self.tiles.clear()
    
    def add_tile(self, tile_id: int, surface: pygame.Surface):
        """
        Add a tile surface manually.
        
        Args:
            tile_id (int): The tile ID
            surface (pygame.Surface): The tile surface
        """
        self.tiles[tile_id] = surface
    
    def remove_tile(self, tile_id: int) -> bool:
        """
        Remove a tile from the loaded tiles.
        
        Args:
            tile_id (int): The tile ID to remove
            
        Returns:
            bool: True if the tile was removed, False if it wasn't found
        """
        if tile_id in self.tiles:
            del self.tiles[tile_id]
            return True
        return False
    
    def get_loaded_tile_ids(self) -> list:
        """
        Get a list of all loaded tile IDs.
        
        Returns:
            list: List of loaded tile IDs
        """
        return list(self.tiles.keys())
    
    def preload_common_tiles(self, tile_ids: list) -> Dict[str, str]:
        """
        Preload a list of commonly used tiles.
        
        Args:
            tile_ids (list): List of tile IDs to preload
            
        Returns:
            Dict[str, str]: Dictionary of any loading errors
        """
        errors = {}
        
        for tile_id in tile_ids:
            if not self.has_tile(tile_id):
                # This would require access to the expanded mapping
                # For now, just log that we would preload this tile
                print(f"Would preload tile ID: {tile_id}")
        
        return errors
    
    def get_memory_usage_info(self) -> Dict[str, any]:
        """
        Get information about memory usage of loaded tiles.
        
        Returns:
            Dict[str, any]: Memory usage information
        """
        total_pixels = 0
        total_tiles = len(self.tiles)
        
        for surface in self.tiles.values():
            if surface:
                total_pixels += surface.get_width() * surface.get_height()
        
        # Estimate memory usage (assuming 32-bit RGBA)
        estimated_bytes = total_pixels * 4
        estimated_mb = estimated_bytes / (1024 * 1024)
        
        return {
            "total_tiles": total_tiles,
            "total_pixels": total_pixels,
            "estimated_memory_mb": round(estimated_mb, 2),
            "estimated_memory_bytes": estimated_bytes
        }
