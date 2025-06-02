"""
UI Renderer - Handles rendering of user interface elements

This class manages the rendering of all UI elements including HUD,
inventories, game over screen, and common UI components.

RESPONSIBILITY: UI element rendering

FEATURES:
- Renders HUD with health bars and inventory
- Renders player and chest inventories with proper layering
- Renders game over screen
- Renders common UI elements (back button, zoom indicator)
- Handles inventory background and positioning
- Manages UI element visibility and states
"""
import pygame
from typing import Optional


class UIRenderer:
    """Handles rendering of all UI elements"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        # System references
        self.hud = None
        self.player_inventory = None
        self.chest_inventory = None
        self.game_over_screen = None
        self.ui_manager = None  # Will be set from PlayScreen
        self.cursor_manager = None  # Will be set from PlayScreen

        # UI state
        self.back_button = None  # Will be set from PlayScreen
        
    def initialize_systems(self, hud, player_inventory, chest_inventory, game_over_screen):
        """Initialize with UI system references"""
        self.hud = hud
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.game_over_screen = game_over_screen
    
    def set_back_button(self, back_button):
        """Set the back button reference"""
        self.back_button = back_button

    def set_ui_manager(self, ui_manager):
        """Set the UI manager reference"""
        self.ui_manager = ui_manager

    def set_cursor_manager(self, cursor_manager):
        """Set the cursor manager reference"""
        self.cursor_manager = cursor_manager
    
    def render_hud(self, surface: pygame.Surface, player):
        """Render the HUD with player information"""
        if self.hud and player:
            self.hud.draw(surface, player)
    
    def render_inventories(self, surface: pygame.Surface):
        """Render player and chest inventories with proper layering"""
        # Check if both inventories are visible for shared background
        if (self.chest_inventory and self.chest_inventory.is_visible() and 
            self.player_inventory and self.player_inventory.is_visible()):
            
            # Draw shared semi-transparent black background
            bg_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, 180))  # Semi-transparent black
            surface.blit(bg_surface, (0, 0))
            
            # Draw inventories in the correct order (chest inventory first, player inventory on top)
            # First draw chest inventory without its own background
            self.chest_inventory.draw(surface, skip_background=True)
            
            # Then draw player inventory without its own background (on top)
            self.player_inventory.draw(surface, skip_background=True)
            
        else:
            # Draw individual inventories with their own backgrounds
            if self.chest_inventory and self.chest_inventory.is_visible():
                self.chest_inventory.draw(surface)
            
            if self.player_inventory and self.player_inventory.is_visible():
                self.player_inventory.draw(surface)

        # Render cursor item on top of everything
        if self.cursor_manager:
            self.cursor_manager.render_cursor_item(surface)
    
    def render_game_over_screen(self, surface: pygame.Surface):
        """Render the game over screen"""
        if self.game_over_screen:
            self.game_over_screen.draw(surface)
    
    def render_common_ui(self, surface: pygame.Surface, zoom_factor: float):
        """Render common UI elements like back button and zoom indicator"""
        # Draw back button
        if self.back_button:
            self.back_button.draw(surface)
        
        # Draw zoom indicator in the bottom-left corner
        if zoom_factor != 1.0:  # Only show when not at 100%
            self._render_zoom_indicator(surface, zoom_factor)

        # Render UI manager messages (status and popup messages)
        if self.ui_manager:
            self.ui_manager.render_ui_elements(surface)
    
    def _render_zoom_indicator(self, surface: pygame.Surface, zoom_factor: float):
        """Render the zoom level indicator"""
        zoom_text = f"Zoom: {int(zoom_factor * 100)}%"
        font = pygame.font.SysFont(None, 24)
        zoom_surface = font.render(zoom_text, True, (255, 255, 255))
        zoom_rect = zoom_surface.get_rect(bottomleft=(10, self.height - 10))
        surface.blit(zoom_surface, zoom_rect)
