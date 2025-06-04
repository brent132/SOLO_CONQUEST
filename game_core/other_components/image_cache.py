"""
Sprite Cache System - Centralized sprite and image caching to reduce memory usage
"""
import os
import pygame
import weakref
from typing import Dict, Optional, Tuple, List
import gc

class SpriteCache:
    """
    Centralized sprite caching system that reduces memory usage by avoiding duplicate image loads.
    Implements singleton pattern to ensure only one cache instance exists.
    """
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SpriteCache, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if not SpriteCache._initialized:
            # Main cache dictionary: path -> pygame.Surface
            self._cache: Dict[str, pygame.Surface] = {}

            # Sprite sheet cache: (path, rect) -> pygame.Surface
            self._sprite_sheet_cache: Dict[Tuple[str, Tuple[int, int, int, int]], pygame.Surface] = {}

            # Animation frame cache: (folder_path, frame_index) -> pygame.Surface
            self._animation_cache: Dict[Tuple[str, int], pygame.Surface] = {}

            # Scaled sprite cache: (path, size) -> pygame.Surface
            self._scaled_cache: Dict[Tuple[str, Tuple[int, int]], pygame.Surface] = {}

            # Cache statistics
            self._cache_hits = 0
            self._cache_misses = 0
            self._max_cache_size = 1000  # Maximum number of cached images
            self._max_scaled_cache_size = 2000  # Maximum number of scaled sprites

            # Working directory for relative paths
            self._base_path = os.getcwd()

            SpriteCache._initialized = True
    
    def get_sprite(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load and cache a sprite from the given path.
        
        Args:
            path (str): Path to the image file (relative or absolute)
            convert_alpha (bool): Whether to convert the image with alpha channel
            
        Returns:
            pygame.Surface: The loaded sprite, or None if loading failed
        """
        # Normalize the path
        normalized_path = self._normalize_path(path)
        
        # Check if already cached
        if normalized_path in self._cache:
            self._cache_hits += 1
            return self._cache[normalized_path]
        
        # Load the image
        sprite = self._load_image(normalized_path, convert_alpha)
        if sprite is not None:
            # Cache the sprite if we haven't exceeded the limit
            if len(self._cache) < self._max_cache_size:
                self._cache[normalized_path] = sprite
            else:
                # If cache is full, remove oldest entries (simple LRU approximation)
                self._cleanup_cache()
                self._cache[normalized_path] = sprite
            
            self._cache_misses += 1
        
        return sprite
    
    def get_sprite_from_sheet(self, sheet_path: str, rect: Tuple[int, int, int, int], 
                            convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Extract and cache a sprite from a sprite sheet.
        
        Args:
            sheet_path (str): Path to the sprite sheet
            rect (tuple): Rectangle (x, y, width, height) defining the sprite area
            convert_alpha (bool): Whether to convert the image with alpha channel
            
        Returns:
            pygame.Surface: The extracted sprite, or None if loading failed
        """
        normalized_path = self._normalize_path(sheet_path)
        cache_key = (normalized_path, rect)
        
        # Check if already cached
        if cache_key in self._sprite_sheet_cache:
            self._cache_hits += 1
            return self._sprite_sheet_cache[cache_key]
        
        # Load the sprite sheet
        sheet = self.get_sprite(sheet_path, convert_alpha)
        if sheet is None:
            return None
        
        # Extract the sprite
        try:
            x, y, width, height = rect
            sprite = sheet.subsurface((x, y, width, height)).copy()
            
            # Cache the extracted sprite
            if len(self._sprite_sheet_cache) < self._max_cache_size:
                self._sprite_sheet_cache[cache_key] = sprite
            
            self._cache_misses += 1
            return sprite
            
        except Exception as e:
            pass  # Error extracting sprite from sheet
            return None
    
    def get_animation_frames(self, folder_path: str, convert_alpha: bool = True) -> List[pygame.Surface]:
        """
        Load and cache all animation frames from a folder.
        
        Args:
            folder_path (str): Path to the folder containing animation frames
            convert_alpha (bool): Whether to convert images with alpha channel
            
        Returns:
            List[pygame.Surface]: List of animation frames
        """
        normalized_folder = self._normalize_path(folder_path)
        frames = []
        
        try:
            # Get all PNG files in the folder
            frame_files = [f for f in os.listdir(normalized_folder) if f.endswith('.png')]
            frame_files.sort()  # Ensure consistent order
            
            for i, frame_file in enumerate(frame_files):
                cache_key = (normalized_folder, i)
                
                # Check if frame is already cached
                if cache_key in self._animation_cache:
                    frames.append(self._animation_cache[cache_key])
                    self._cache_hits += 1
                else:
                    # Load the frame
                    frame_path = os.path.join(normalized_folder, frame_file)
                    frame = self._load_image(frame_path, convert_alpha)
                    
                    if frame is not None:
                        frames.append(frame)
                        
                        # Cache the frame
                        if len(self._animation_cache) < self._max_cache_size:
                            self._animation_cache[cache_key] = frame
                        
                        self._cache_misses += 1
                    
        except Exception as e:
            pass  # Error loading animation frames
        
        return frames

    def get_scaled_sprite(self, path: str, size: Tuple[int, int], convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load and cache a scaled sprite from the given path.

        Args:
            path (str): Path to the image file (relative or absolute)
            size (tuple): Target size (width, height) for scaling
            convert_alpha (bool): Whether to convert the image with alpha channel

        Returns:
            pygame.Surface: The scaled sprite, or None if loading failed
        """
        # Normalize the path
        normalized_path = self._normalize_path(path)
        cache_key = (normalized_path, size)

        # Check if already cached
        if cache_key in self._scaled_cache:
            self._cache_hits += 1
            return self._scaled_cache[cache_key]

        # Load the original sprite first
        original_sprite = self.get_sprite(path, convert_alpha)
        if original_sprite is None:
            return None

        # Check if scaling is needed
        if original_sprite.get_size() == size:
            # No scaling needed, return original
            self._cache_hits += 1
            return original_sprite

        # Scale the sprite
        try:
            scaled_sprite = pygame.transform.scale(original_sprite, size)

            # Cache the scaled sprite if we haven't exceeded the limit
            if len(self._scaled_cache) < self._max_scaled_cache_size:
                self._scaled_cache[cache_key] = scaled_sprite
            else:
                # If cache is full, remove oldest entries
                self._cleanup_scaled_cache()
                self._scaled_cache[cache_key] = scaled_sprite

            self._cache_misses += 1
            return scaled_sprite

        except Exception as e:
            pass  # Error scaling sprite
            return original_sprite

    def _normalize_path(self, path: str) -> str:
        """Normalize a file path to be consistent for caching."""
        if os.path.isabs(path):
            return os.path.normpath(path)
        else:
            return os.path.normpath(os.path.join(self._base_path, path))
    
    def _load_image(self, path: str, convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        Load an image from disk with error handling.
        
        Args:
            path (str): Normalized path to the image
            convert_alpha (bool): Whether to convert with alpha channel
            
        Returns:
            pygame.Surface: The loaded image, or None if loading failed
        """
        try:
            if not os.path.exists(path):
                pass  # Image file not found
                return None
            
            image = pygame.image.load(path)
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()
            
            return image
            
        except Exception as e:
            pass  # Error loading image
            return None
    
    def _cleanup_cache(self):
        """Remove some entries from cache when it gets too full."""
        # Simple cleanup: remove 20% of entries
        cleanup_count = max(1, len(self._cache) // 5)

        # Remove oldest entries (this is a simple approximation)
        keys_to_remove = list(self._cache.keys())[:cleanup_count]
        for key in keys_to_remove:
            del self._cache[key]

        # Also cleanup sprite sheet cache
        if len(self._sprite_sheet_cache) > self._max_cache_size // 2:
            cleanup_count = len(self._sprite_sheet_cache) // 5
            keys_to_remove = list(self._sprite_sheet_cache.keys())[:cleanup_count]
            for key in keys_to_remove:
                del self._sprite_sheet_cache[key]

    def _cleanup_scaled_cache(self):
        """Remove some entries from scaled cache when it gets too full."""
        # Simple cleanup: remove 25% of entries
        cleanup_count = max(1, len(self._scaled_cache) // 4)

        # Remove oldest entries (this is a simple approximation)
        keys_to_remove = list(self._scaled_cache.keys())[:cleanup_count]
        for key in keys_to_remove:
            del self._scaled_cache[key]
    
    def clear_cache(self):
        """Clear all cached sprites to free memory."""
        self._cache.clear()
        self._sprite_sheet_cache.clear()
        self._animation_cache.clear()
        self._scaled_cache.clear()
        gc.collect()  # Force garbage collection
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics for debugging and optimization."""
        return {
            'cache_size': len(self._cache),
            'sprite_sheet_cache_size': len(self._sprite_sheet_cache),
            'animation_cache_size': len(self._animation_cache),
            'scaled_cache_size': len(self._scaled_cache),
            'cache_hits': self._cache_hits,
            'cache_misses': self._cache_misses,
            'hit_ratio': self._cache_hits / max(1, self._cache_hits + self._cache_misses)
        }

    def print_cache_stats(self):
        """Print cache statistics to console for debugging."""
        # Cache stats printing disabled
        pass
    
    def create_placeholder(self, size: Tuple[int, int] = (16, 16), 
                         color: Tuple[int, int, int, int] = (255, 0, 0, 128)) -> pygame.Surface:
        """
        Create a placeholder sprite for when image loading fails.
        
        Args:
            size (tuple): Size of the placeholder (width, height)
            color (tuple): RGBA color of the placeholder
            
        Returns:
            pygame.Surface: A placeholder sprite
        """
        placeholder = pygame.Surface(size, pygame.SRCALPHA)
        placeholder.fill(color)
        return placeholder

# Global instance of the sprite cache
sprite_cache = SpriteCache()
