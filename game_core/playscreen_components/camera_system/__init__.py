"""
Camera System - Comprehensive camera and viewport management

This package provides:
- Camera positioning and movement
- Viewport calculations and centering
- Player following logic
- Zoom-aware camera management
- Screen resize handling
- Map boundary clamping
"""

from .camera_controller import CameraController
from .viewport_calculator import ViewportCalculator
from .camera_follower import CameraFollower

__all__ = [
    'CameraController',
    'ViewportCalculator', 
    'CameraFollower'
]
