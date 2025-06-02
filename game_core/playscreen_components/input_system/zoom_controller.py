"""
Zoom Controller - Handles zoom functionality and camera management

This module manages:
- Zoom levels and zoom factor calculations
- Zoom in/out operations with camera positioning
- Zoom reset functionality
- Grid size updates based on zoom
- Camera bounds clamping
- Effective screen size calculations
"""


class ZoomController:
    """Handles zoom functionality and camera management"""
    
    def __init__(self, width: int, height: int, base_grid_cell_size: int = 16):
        self.width = width
        self.height = height
        self.base_grid_cell_size = base_grid_cell_size
        
        # Zoom settings - limited to 100% minimum
        self.zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0]
        self.current_zoom_index = 0  # Start at 1.0x zoom (index 0)
        self.zoom_factor = self.zoom_levels[self.current_zoom_index]
        
        # Current grid cell size (affected by zoom)
        self.grid_cell_size = base_grid_cell_size
        
        # Pre-calculate zoom-related values for performance
        self.zoom_factor_inv = 1.0 / self.zoom_factor
        self.effective_screen_width = self.width * self.zoom_factor_inv
        self.effective_screen_height = self.height * self.zoom_factor_inv
        
        # Camera/viewport for large maps
        self.camera_x = 0
        self.camera_y = 0
        
        # Offset for centering small maps
        self.center_offset_x = 0
        self.center_offset_y = 0
        
        # Map dimensions for camera bounds
        self.map_width = 0
        self.map_height = 0
        
        # Callbacks for notifying other systems of zoom changes
        self.on_zoom_changed_callbacks = []
        
    def add_zoom_changed_callback(self, callback):
        """Add a callback to be called when zoom changes"""
        self.on_zoom_changed_callbacks.append(callback)
        
    def set_map_dimensions(self, map_width: int, map_height: int):
        """Set the map dimensions for camera bounds calculation"""
        self.map_width = map_width
        self.map_height = map_height
        
    def set_center_offset(self, center_offset_x: float, center_offset_y: float):
        """Set the center offset for small maps"""
        self.center_offset_x = center_offset_x
        self.center_offset_y = center_offset_y
        
    def zoom_in(self, player_rect=None) -> bool:
        """
        Zoom in to the next zoom level
        
        Args:
            player_rect: Optional player rectangle for centering
            
        Returns:
            bool: True if zoom changed, False if already at max zoom
        """
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            # Store the center point of the current view (player position)
            if player_rect:
                center_x = player_rect.centerx
                center_y = player_rect.centery
            else:
                center_x = self.camera_x + (self.width // 2)
                center_y = self.camera_y + (self.height // 2)

            # Update zoom
            self.current_zoom_index += 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self._update_zoom_values()

            # Recalculate camera position to maintain the same center point
            self._recalculate_camera_position(center_x, center_y)
            
            # Notify other systems
            self._notify_zoom_changed()
            return True
        return False

    def zoom_out(self, player_rect=None) -> bool:
        """
        Zoom out to the previous zoom level
        
        Args:
            player_rect: Optional player rectangle for centering
            
        Returns:
            bool: True if zoom changed, False if already at min zoom
        """
        if self.current_zoom_index > 0:
            # Store the center point of the current view (player position)
            if player_rect:
                center_x = player_rect.centerx
                center_y = player_rect.centery
            else:
                center_x = self.camera_x + (self.width // 2)
                center_y = self.camera_y + (self.height // 2)

            # Update zoom
            self.current_zoom_index -= 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self._update_zoom_values()

            # Recalculate camera position to maintain the same center point
            self._recalculate_camera_position(center_x, center_y)
            
            # Notify other systems
            self._notify_zoom_changed()
            return True
        return False

    def reset_zoom(self, player_rect=None) -> bool:
        """
        Reset zoom to 1.0x (100%)
        
        Args:
            player_rect: Optional player rectangle for centering
            
        Returns:
            bool: True if zoom changed, False if already at 1.0x
        """
        if self.current_zoom_index != 0:
            # Store the center point of the current view (player position)
            if player_rect:
                center_x = player_rect.centerx
                center_y = player_rect.centery
            else:
                center_x = self.camera_x + (self.width // 2)
                center_y = self.camera_y + (self.height // 2)

            # Reset zoom to 1.0x
            self.current_zoom_index = 0  # 1.0x is at index 0
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self._update_zoom_values()

            # Recalculate camera position to maintain the same center point
            self._recalculate_camera_position(center_x, center_y)
            
            # Notify other systems
            self._notify_zoom_changed()
            return True
        return False
        
    def _update_zoom_values(self):
        """Update grid cell size and cached values based on current zoom factor"""
        self.grid_cell_size = int(self.base_grid_cell_size * self.zoom_factor)
        
        # Pre-calculate frequently used values to avoid repeated calculations
        self.zoom_factor_inv = 1.0 / self.zoom_factor  # Cache inverse for performance
        self.effective_screen_width = self.width * self.zoom_factor_inv
        self.effective_screen_height = self.height * self.zoom_factor_inv
        
    def _recalculate_camera_position(self, center_x: float, center_y: float):
        """Recalculate camera position to maintain the same center point"""
        # When zoomed, the effective screen size in logical coordinates changes
        effective_screen_width = self.width / self.zoom_factor
        effective_screen_height = self.height / self.zoom_factor

        self.camera_x = center_x - (effective_screen_width // 2)
        self.camera_y = center_y - (effective_screen_height // 2)

        # Clamp camera to map boundaries (use base grid size for logical coordinates)
        max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
        max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)
        self.camera_x = max(0, min(self.camera_x, max_camera_x))
        self.camera_y = max(0, min(self.camera_y, max_camera_y))
        
    def _notify_zoom_changed(self):
        """Notify all registered callbacks that zoom has changed"""
        for callback in self.on_zoom_changed_callbacks:
            try:
                callback(self.grid_cell_size, self.zoom_factor, self.zoom_factor_inv)
            except Exception as e:
                print(f"Error in zoom changed callback: {e}")

    def resize(self, new_width: int, new_height: int):
        """Handle screen resize by updating dimensions and recalculating zoom values"""
        self.width = new_width
        self.height = new_height

        # Recalculate zoom-related values with new screen dimensions
        self._update_zoom_values()
                
    def get_zoom_info(self) -> dict:
        """Get current zoom information"""
        return {
            'zoom_factor': self.zoom_factor,
            'zoom_factor_inv': self.zoom_factor_inv,
            'zoom_index': self.current_zoom_index,
            'grid_cell_size': self.grid_cell_size,
            'effective_screen_width': self.effective_screen_width,
            'effective_screen_height': self.effective_screen_height,
            'camera_x': self.camera_x,
            'camera_y': self.camera_y,
            'center_offset_x': self.center_offset_x,
            'center_offset_y': self.center_offset_y
        }
        
    def set_camera_position(self, camera_x: float, camera_y: float):
        """Set the camera position directly"""
        self.camera_x = camera_x
        self.camera_y = camera_y
