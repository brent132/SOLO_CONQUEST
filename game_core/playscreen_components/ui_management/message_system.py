"""
Message System - Handles status messages and popup notifications

This module manages:
- Status messages (error messages, loading notifications)
- Popup messages (save notifications, temporary alerts)
- Message timers and automatic dismissal
- Message rendering and display
- Font management for text rendering
"""

import pygame
from typing import Optional, Tuple


class MessageSystem:
    """Handles all message display functionality"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Status message (persistent until dismissed)
        self.status_message = ""
        self.status_timer = 0
        
        # Popup message (temporary notifications)
        self.popup_message = ""
        self.popup_timer = 0
        self.popup_duration = 120  # 2 seconds at 60 FPS
        
        # Font initialization
        self._init_fonts()
        
    def _init_fonts(self):
        """Initialize fonts for message rendering"""
        try:
            # Try to load custom fonts
            self.status_font = pygame.font.Font("fonts/Poppins-Regular.ttf", 24)
            self.popup_font = pygame.font.Font("fonts/Poppins-Medium.ttf", 20)
        except:
            # Fallback to system fonts
            self.status_font = pygame.font.SysFont(None, 32)
            self.popup_font = pygame.font.SysFont(None, 28)
            
    def resize(self, new_width: int, new_height: int):
        """Update message system for new screen dimensions"""
        self.screen_width = new_width
        self.screen_height = new_height
        
    def show_status_message(self, message: str, duration: int = 180):
        """Show a status message (error, loading, etc.)
        
        Args:
            message: Message text to display
            duration: Duration in frames (180 = 3 seconds at 60 FPS)
        """
        self.status_message = message
        self.status_timer = duration
        
    def show_popup_message(self, message: str, duration: Optional[int] = None):
        """Show a temporary popup message
        
        Args:
            message: Message text to display
            duration: Duration in frames (default: 2 seconds)
        """
        self.popup_message = message
        self.popup_timer = duration if duration is not None else self.popup_duration
        
    def clear_status_message(self):
        """Clear the current status message"""
        self.status_message = ""
        self.status_timer = 0
        
    def clear_popup_message(self):
        """Clear the current popup message"""
        self.popup_message = ""
        self.popup_timer = 0
        
    def update(self):
        """Update message timers"""
        # Update status message timer
        if self.status_timer > 0:
            self.status_timer -= 1
            if self.status_timer <= 0:
                self.status_message = ""
                
        # Update popup message timer
        if self.popup_timer > 0:
            self.popup_timer -= 1
            if self.popup_timer <= 0:
                self.popup_message = ""
                
    def has_active_messages(self) -> bool:
        """Check if there are any active messages to display"""
        return bool(self.status_message and self.status_timer > 0) or bool(self.popup_message and self.popup_timer > 0)
        
    def render_messages(self, surface: pygame.Surface):
        """Render all active messages to the surface"""
        # Render status message
        if self.status_message and self.status_timer > 0:
            self._render_status_message(surface)
            
        # Render popup message
        if self.popup_message and self.popup_timer > 0:
            self._render_popup_message(surface)
            
    def _render_status_message(self, surface: pygame.Surface):
        """Render the status message at the bottom center of the screen"""
        # Determine color based on message content
        if "Error" in self.status_message or "error" in self.status_message:
            color = (255, 100, 100)  # Red for errors
        elif "Loading" in self.status_message or "loading" in self.status_message:
            color = (100, 100, 255)  # Blue for loading
        else:
            color = (100, 255, 100)  # Green for success/info
            
        # Render text
        text_surface = self.status_font.render(self.status_message, True, color)
        
        # Position at bottom center
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 50))
        
        # Draw background for better visibility
        bg_rect = text_rect.inflate(20, 10)
        pygame.draw.rect(surface, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(surface, color, bg_rect, 2)
        
        # Draw text
        surface.blit(text_surface, text_rect)
        
    def _render_popup_message(self, surface: pygame.Surface):
        """Render the popup message at the top center of the screen"""
        # Calculate fade effect based on remaining time
        fade_factor = min(1.0, self.popup_timer / 30.0)  # Fade in last 0.5 seconds
        alpha = int(255 * fade_factor)
        
        # Render text with fade
        text_surface = self.popup_font.render(self.popup_message, True, (255, 255, 255))
        text_surface.set_alpha(alpha)
        
        # Position at top center
        text_rect = text_surface.get_rect(center=(self.screen_width // 2, 80))
        
        # Draw background with fade
        bg_rect = text_rect.inflate(20, 10)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, int(120 * fade_factor)))
        surface.blit(bg_surface, bg_rect)
        
        # Draw border
        pygame.draw.rect(surface, (255, 255, 255, int(alpha // 2)), bg_rect, 2)
        
        # Draw text
        surface.blit(text_surface, text_rect)
        
    def get_status_info(self) -> dict:
        """Get current status information for debugging"""
        return {
            "status_message": self.status_message,
            "status_timer": self.status_timer,
            "popup_message": self.popup_message,
            "popup_timer": self.popup_timer,
            "has_active": self.has_active_messages()
        }
