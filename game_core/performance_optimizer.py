"""
Performance Optimizer - Handles performance optimizations for fullscreen and high-resolution gameplay
"""
import pygame
import time
from typing import Dict, List, Tuple, Optional

class PerformanceOptimizer:
    """
    Handles performance optimizations for the game, especially for fullscreen mode.
    """
    
    def __init__(self):
        # Performance tracking
        self.frame_times: List[float] = []
        self.max_frame_history = 60  # Track last 60 frames
        
        # Optimization settings
        self.enable_dirty_rect_optimization = True
        self.enable_surface_caching = True
        self.enable_culling = True
        
        # Dirty rectangles for optimized drawing
        self.dirty_rects: List[pygame.Rect] = []
        
        # Surface cache for complex UI elements
        self.ui_surface_cache: Dict[str, pygame.Surface] = {}
        
        # Performance thresholds
        self.target_fps = 60
        self.low_fps_threshold = 30
        self.critical_fps_threshold = 15
        
        # Adaptive quality settings
        self.current_quality_level = "high"  # high, medium, low
        self.quality_levels = {
            "high": {
                "enable_shadows": True,
                "enable_particles": True,
                "enable_smooth_scaling": True,
                "max_visible_entities": 100,
                "animation_quality": 1.0
            },
            "medium": {
                "enable_shadows": False,
                "enable_particles": True,
                "enable_smooth_scaling": True,
                "max_visible_entities": 75,
                "animation_quality": 0.8
            },
            "low": {
                "enable_shadows": False,
                "enable_particles": False,
                "enable_smooth_scaling": False,
                "max_visible_entities": 50,
                "animation_quality": 0.6
            }
        }
    
    def start_frame(self):
        """Call at the beginning of each frame to start performance tracking."""
        self.frame_start_time = time.time()
        self.dirty_rects.clear()
    
    def end_frame(self):
        """Call at the end of each frame to update performance metrics."""
        frame_time = time.time() - self.frame_start_time
        self.frame_times.append(frame_time)
        
        # Keep only recent frame times
        if len(self.frame_times) > self.max_frame_history:
            self.frame_times.pop(0)
        
        # Adaptive quality adjustment
        self._adjust_quality_if_needed()
    
    def get_average_fps(self) -> float:
        """Get the average FPS over recent frames."""
        if not self.frame_times:
            return 0.0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_current_fps(self) -> float:
        """Get the current FPS based on the last frame."""
        if not self.frame_times:
            return 0.0
        
        last_frame_time = self.frame_times[-1]
        return 1.0 / last_frame_time if last_frame_time > 0 else 0.0
    
    def _adjust_quality_if_needed(self):
        """Automatically adjust quality settings based on performance."""
        if len(self.frame_times) < 10:  # Need enough samples
            return
        
        avg_fps = self.get_average_fps()
        
        # Downgrade quality if performance is poor
        if avg_fps < self.critical_fps_threshold and self.current_quality_level != "low":
            if self.current_quality_level == "high":
                self.current_quality_level = "medium"
            else:
                self.current_quality_level = "low"
            print(f"Performance: Reduced quality to {self.current_quality_level} (FPS: {avg_fps:.1f})")
        
        # Upgrade quality if performance is good
        elif avg_fps > self.target_fps * 0.9 and self.current_quality_level != "high":
            if self.current_quality_level == "low":
                self.current_quality_level = "medium"
            else:
                self.current_quality_level = "high"
            print(f"Performance: Increased quality to {self.current_quality_level} (FPS: {avg_fps:.1f})")
    
    def get_quality_setting(self, setting_name: str):
        """Get a specific quality setting for the current quality level."""
        return self.quality_levels[self.current_quality_level].get(setting_name, True)
    
    def add_dirty_rect(self, rect: pygame.Rect):
        """Add a dirty rectangle for optimized drawing."""
        if self.enable_dirty_rect_optimization:
            self.dirty_rects.append(rect)
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """Get all dirty rectangles for this frame."""
        return self.dirty_rects.copy()
    
    def should_cull_object(self, obj_rect: pygame.Rect, screen_rect: pygame.Rect, margin: int = 50) -> bool:
        """Determine if an object should be culled (not drawn) based on visibility."""
        if not self.enable_culling:
            return False
        
        # Add margin for objects that might be partially visible
        expanded_screen = screen_rect.inflate(margin * 2, margin * 2)
        return not obj_rect.colliderect(expanded_screen)
    
    def cache_ui_surface(self, cache_key: str, surface: pygame.Surface):
        """Cache a UI surface for reuse."""
        if self.enable_surface_caching:
            self.ui_surface_cache[cache_key] = surface.copy()
    
    def get_cached_ui_surface(self, cache_key: str) -> Optional[pygame.Surface]:
        """Get a cached UI surface."""
        return self.ui_surface_cache.get(cache_key)
    
    def clear_ui_cache(self):
        """Clear the UI surface cache."""
        self.ui_surface_cache.clear()
    
    def optimize_surface_for_blitting(self, surface: pygame.Surface) -> pygame.Surface:
        """Optimize a surface for faster blitting."""
        if surface.get_flags() & pygame.SRCALPHA:
            return surface.convert_alpha()
        else:
            return surface.convert()
    
    def get_performance_info(self) -> Dict[str, any]:
        """Get comprehensive performance information."""
        return {
            "current_fps": self.get_current_fps(),
            "average_fps": self.get_average_fps(),
            "quality_level": self.current_quality_level,
            "dirty_rects_count": len(self.dirty_rects),
            "ui_cache_size": len(self.ui_surface_cache),
            "frame_history_size": len(self.frame_times)
        }
    
    def print_performance_stats(self):
        """Print performance statistics to console."""
        info = self.get_performance_info()
        print(f"Performance: {info['current_fps']:.1f} FPS (avg: {info['average_fps']:.1f}), "
              f"Quality: {info['quality_level']}, "
              f"Dirty rects: {info['dirty_rects_count']}, "
              f"UI cache: {info['ui_cache_size']}")

# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
