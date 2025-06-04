"""
Effects Renderer - Handles rendering of visual effects and animations

This class manages the rendering of visual effects, particle systems,
and other dynamic visual elements.

RESPONSIBILITY: Visual effects rendering

FEATURES:
- Renders particle effects and animations
- Handles visual feedback for game events
- Manages effect layering and blending
- Supports zoom-aware effect scaling
- Handles effect lifecycle and cleanup
"""
import pygame
from typing import List, Dict, Any, Optional
from game_core.core.perf_optimizer import perf_optimizer


class EffectsRenderer:
    """Handles rendering of visual effects and animations"""
    
    def __init__(self):
        self.zoom_factor = 1.0
        
        # System references
        self.animated_tile_manager = None
        
        # Effect state
        self.active_effects = []
        
    def initialize_systems(self, animated_tile_manager):
        """Initialize with system references"""
        self.animated_tile_manager = animated_tile_manager
    
    def set_zoom_factor(self, zoom_factor: float):
        """Set the current zoom factor for effect scaling"""
        self.zoom_factor = zoom_factor
    
    def render_effects(self, surface: pygame.Surface, camera_x: int, camera_y: int,
                      center_offset_x: int, center_offset_y: int):
        """Render all active visual effects"""
        if not perf_optimizer.get_quality_setting("enable_particles"):
            return
        # Calculate camera offset
        camera_offset_x = camera_x - center_offset_x
        camera_offset_y = camera_y - center_offset_y
        
        # Render each active effect
        for effect in self.active_effects:
            self._render_effect(surface, effect, camera_offset_x, camera_offset_y)
    
    def add_effect(self, effect_type: str, position: tuple, duration: int = 60, **kwargs):
        """Add a new visual effect"""
        effect = {
            'type': effect_type,
            'position': position,
            'duration': duration,
            'timer': 0,
            'properties': kwargs
        }
        self.active_effects.append(effect)
    
    def update_effects(self):
        """Update all active effects and remove expired ones"""
        # Update effect timers
        for effect in self.active_effects[:]:  # Copy list to avoid modification during iteration
            effect['timer'] += 1
            
            # Remove expired effects
            if effect['timer'] >= effect['duration']:
                self.active_effects.remove(effect)
    
    def clear_effects(self):
        """Clear all active effects"""
        self.active_effects.clear()
    
    def _render_effect(self, surface: pygame.Surface, effect: Dict[str, Any], 
                      camera_offset_x: int, camera_offset_y: int):
        """Render a single visual effect"""
        effect_type = effect['type']
        position = effect['position']
        timer = effect['timer']
        duration = effect['duration']
        properties = effect['properties']
        
        # Calculate screen position with zoom
        screen_x = (position[0] - camera_offset_x) * self.zoom_factor
        screen_y = (position[1] - camera_offset_y) * self.zoom_factor
        
        # Render based on effect type
        if effect_type == 'particle':
            self._render_particle_effect(surface, screen_x, screen_y, timer, duration, properties)
        elif effect_type == 'flash':
            self._render_flash_effect(surface, screen_x, screen_y, timer, duration, properties)
        elif effect_type == 'fade':
            self._render_fade_effect(surface, screen_x, screen_y, timer, duration, properties)
    
    def _render_particle_effect(self, surface: pygame.Surface, x: float, y: float, 
                               timer: int, duration: int, properties: Dict[str, Any]):
        """Render a particle effect"""
        # Basic particle effect implementation
        color = properties.get('color', (255, 255, 255))
        size = properties.get('size', 2)
        
        # Fade out over time
        alpha = int(255 * (1 - timer / duration))
        if alpha > 0:
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (*color, alpha), (size, size), size)
            surface.blit(particle_surface, (x - size, y - size))
    
    def _render_flash_effect(self, surface: pygame.Surface, x: float, y: float,
                            timer: int, duration: int, properties: Dict[str, Any]):
        """Render a flash effect"""
        # Basic flash effect implementation
        color = properties.get('color', (255, 255, 255))
        radius = properties.get('radius', 20)
        
        # Flash intensity decreases over time
        intensity = 1 - (timer / duration)
        if intensity > 0:
            alpha = int(255 * intensity)
            flash_surface = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(flash_surface, (*color, alpha), (radius * 2, radius * 2), int(radius * intensity))
            surface.blit(flash_surface, (x - radius * 2, y - radius * 2))
    
    def _render_fade_effect(self, surface: pygame.Surface, x: float, y: float,
                           timer: int, duration: int, properties: Dict[str, Any]):
        """Render a fade effect"""
        # Basic fade effect implementation
        color = properties.get('color', (0, 0, 0))
        size = properties.get('size', (50, 50))
        
        # Fade alpha over time
        alpha = int(255 * (timer / duration))
        if alpha < 255:
            fade_surface = pygame.Surface(size, pygame.SRCALPHA)
            fade_surface.fill((*color, alpha))
            surface.blit(fade_surface, (x - size[0] // 2, y - size[1] // 2))
