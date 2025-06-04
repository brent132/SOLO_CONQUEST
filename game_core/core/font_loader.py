"""
Font Manager module - handles loading and managing fonts
"""
import os
import logging
import pygame

logger = logging.getLogger(__name__)

class FontManager:
    """Manages loading and caching fonts"""
    def __init__(self):
        # Initialize pygame font module
        pygame.font.init()

        # Font cache to avoid reloading the same fonts
        self.font_cache = {}

        # Default font paths
        self.font_paths = {
            'regular': 'fonts/Poppins-Regular.ttf',
            'bold': 'fonts/Poppins-Bold.ttf',
            'medium': 'fonts/Poppins-Medium.ttf',
            'light': 'fonts/Poppins-Light.ttf',
            'semibold': 'fonts/Poppins-SemiBold.ttf',
            'thin': 'fonts/Poppins-Thin.ttf',
            'extralight': 'fonts/Poppins-ExtraLight.ttf',
            'extrabold': 'fonts/Poppins-ExtraBold.ttf',
            'black': 'fonts/Poppins-Black.ttf',
            'italic': 'fonts/Poppins-Italic.ttf'
        }

        # Fallback to system font if custom font fails to load
        self.fallback_font = None

    def get_font(self, style='regular', size=24):
        """
        Get a font with the specified style and size

        Args:
            style (str): Font style ('regular', 'bold', 'medium', 'light', 'semibold')
            size (int): Font size in points

        Returns:
            pygame.font.Font: The requested font
        """
        # Create a cache key
        cache_key = f"{style}_{size}"

        # Check if font is already in cache
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]

        # Get the font path
        font_path = self.font_paths.get(style, self.font_paths['regular'])

        # Try to load the custom font
        try:
            if os.path.exists(font_path):
                font = pygame.font.Font(font_path, size)
                self.font_cache[cache_key] = font
                return font
        except Exception as e:
            logger.warning(f"Error loading font {font_path}: {e}")

        # If custom font fails, use system font as fallback
        if self.fallback_font is None:
            self.fallback_font = pygame.font.SysFont(None, size)

        # Cache the fallback font
        self.font_cache[cache_key] = pygame.font.SysFont(None, size)
        return self.font_cache[cache_key]

# Create a global instance of the font manager
font_manager = FontManager()
