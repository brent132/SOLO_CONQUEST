"""
Camera Controller - Main camera management system

This module manages:
- Camera position and movement
- Integration with zoom controller
- Viewport calculations
- Player following logic
- Screen resize handling
- Camera state management
"""

from .viewport_calculator import ViewportCalculator
from .camera_follower import CameraFollower


class CameraController:
    """Main camera management system that coordinates all camera functionality"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Initialize sub-components
        self.viewport_calculator = ViewportCalculator(base_grid_cell_size)
        self.camera_follower = CameraFollower(base_grid_cell_size)
        
        # Camera state
        self.camera_x = 0
        self.camera_y = 0
        
        # References to external systems
        self.zoom_controller = None
        self.player = None
        
        # Map data
        self.map_width = 0
        self.map_height = 0
        
    def initialize(self, zoom_controller, player=None):
        """Initialize camera controller with required systems
        
        Args:
            zoom_controller: The zoom controller instance
            player: Optional player reference
        """
        self.zoom_controller = zoom_controller
        self.player = player
        
    def set_player(self, player):
        """Set the player reference for camera following"""
        self.player = player
        
    def set_map_data(self, layers, map_data, map_width: int, map_height: int, expanded_mapping):
        """Set map data for camera calculations
        
        Args:
            layers: Map layer data
            map_data: Legacy map data format
            map_width: Map width in tiles
            map_height: Map height in tiles
            expanded_mapping: Tile mapping data
        """
        self.map_width = map_width
        self.map_height = map_height
        
        # Update sub-components
        self.viewport_calculator.set_map_data(layers, map_data, map_width, map_height, expanded_mapping)
        self.camera_follower.set_map_dimensions(map_width, map_height)
        
    def get_camera_position(self):
        """Get current camera position
        
        Returns:
            tuple: (camera_x, camera_y)
        """
        return self.camera_x, self.camera_y
        
    def set_camera_position(self, x: float, y: float):
        """Set camera position directly
        
        Args:
            x: Camera X position
            y: Camera Y position
        """
        self.camera_x = x
        self.camera_y = y
        
        # Update zoom controller camera position
        if self.zoom_controller:
            self.zoom_controller.camera_x = x
            self.zoom_controller.camera_y = y
            
    def get_effective_screen_size(self):
        """Get effective screen size from zoom controller
        
        Returns:
            tuple: (effective_width, effective_height)
        """
        if self.zoom_controller:
            return self.zoom_controller.effective_screen_width, self.zoom_controller.effective_screen_height
        return 800, 600  # Default fallback
        
    def calculate_center_offset(self):
        """Calculate center offset for small maps
        
        Returns:
            tuple: (center_offset_x, center_offset_y)
        """
        effective_width, effective_height = self.get_effective_screen_size()
        center_offset_x, center_offset_y = self.viewport_calculator.calculate_center_offset(
            effective_width, effective_height
        )
        
        # Update zoom controller center offset
        if self.zoom_controller:
            self.zoom_controller.set_center_offset(center_offset_x, center_offset_y)
            
        return center_offset_x, center_offset_y
        
    def center_camera_on_player(self):
        """Instantly center camera on player (for teleportation, map loading, etc.)"""
        if not self.player:
            return
            
        effective_width, effective_height = self.get_effective_screen_size()
        camera_x, camera_y = self.camera_follower.center_camera_on_player(
            self.player.rect, effective_width, effective_height
        )
        
        self.set_camera_position(camera_x, camera_y)
        pass  # Camera position
        
    def update_camera_following(self):
        """Update camera to follow player with smooth movement"""
        if not self.player:
            return
            
        effective_width, effective_height = self.get_effective_screen_size()
        new_camera_x, new_camera_y = self.camera_follower.update_camera_following(
            self.camera_x, self.camera_y, self.player.rect, effective_width, effective_height
        )
        
        self.set_camera_position(new_camera_x, new_camera_y)
        
    def handle_resize(self, old_center_offset_x: float, old_center_offset_y: float):
        """Handle screen resize by adjusting camera position
        
        Args:
            old_center_offset_x: Previous center offset X
            old_center_offset_y: Previous center offset Y
        """
        # Recalculate center offset for small maps
        new_center_offset_x, new_center_offset_y = self.calculate_center_offset()
        
        if self.player:
            # Update camera to center on player with new screen dimensions
            self.center_camera_on_player()
        else:
            # If no player, adjust camera based on the change in center offset
            delta_offset_x = new_center_offset_x - old_center_offset_x
            delta_offset_y = new_center_offset_y - old_center_offset_y
            
            # Adjust camera position to account for the change in center offset
            new_camera_x = self.camera_x - delta_offset_x
            new_camera_y = self.camera_y - delta_offset_y
            
            # Clamp to boundaries
            effective_width, effective_height = self.get_effective_screen_size()
            new_camera_x, new_camera_y = self.camera_follower.clamp_camera_to_boundaries(
                new_camera_x, new_camera_y, effective_width, effective_height
            )
            
            self.set_camera_position(new_camera_x, new_camera_y)
            
    def set_camera_from_save_data(self, camera_x: float, camera_y: float):
        """Set camera position from saved game data
        
        Args:
            camera_x: Saved camera X position
            camera_y: Saved camera Y position
        """
        self.set_camera_position(camera_x, camera_y)
        
    def get_camera_save_data(self):
        """Get camera data for saving
        
        Returns:
            dict: Camera save data
        """
        return {
            "x": self.camera_x,
            "y": self.camera_y
        }
