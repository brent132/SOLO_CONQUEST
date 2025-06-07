"""Initialization for the game_core package."""
# Provides shared helper objects like the font loader.

from .font_loader import FontManager, font_loader

__all__ = ["FontManager", "font_loader"]
