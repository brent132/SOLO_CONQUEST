"""
Camera Follower - Handles camera following logic for player movement

This module manages:
- Player following camera logic
- Smooth camera movement
- Camera boundary clamping
- Target position calculations
- Camera interpolation
"""


class CameraFollower:
    """Handles camera following logic for player movement"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Camera smoothing settings
        self.camera_smoothing = 1.0  # Set to 1.0 to disable smoothing and eliminate black lines
        
        # Map boundaries
        self.map_width = 0
        self.map_height = 0
        
    def set_map_dimensions(self, map_width: int, map_height: int):
        """Set map dimensions for boundary calculations"""
        self.map_width = map_width
        self.map_height = map_height
        
    def set_camera_smoothing(self, smoothing: float):
        """Set camera smoothing factor (0.0 = no smoothing, 1.0 = instant)"""
        self.camera_smoothing = max(0.0, min(1.0, smoothing))
        
    def calculate_target_camera_position(self, player_rect, effective_screen_width: float, effective_screen_height: float):
        """Calculate the target camera position to center on player
        
        Args:
            player_rect: Player rectangle with position information
            effective_screen_width: Effective screen width (accounting for zoom)
            effective_screen_height: Effective screen height (accounting for zoom)
            
        Returns:
            tuple: (target_camera_x, target_camera_y) - the target camera position
        """
        if not player_rect:
            return 0, 0
            
        # Center camera on player
        player_center_x = player_rect.centerx
        player_center_y = player_rect.centery

        # Calculate desired camera position (centered on player)
        target_camera_x = player_center_x - (effective_screen_width // 2)
        target_camera_y = player_center_y - (effective_screen_height // 2)

        return target_camera_x, target_camera_y
        
    def clamp_camera_to_boundaries(self, camera_x: float, camera_y: float, 
                                 effective_screen_width: float, effective_screen_height: float):
        """Clamp camera position to map boundaries
        
        Args:
            camera_x: Current camera X position
            camera_y: Current camera Y position
            effective_screen_width: Effective screen width (accounting for zoom)
            effective_screen_height: Effective screen height (accounting for zoom)
            
        Returns:
            tuple: (clamped_camera_x, clamped_camera_y) - the clamped camera position
        """
        # Calculate map boundaries (use base grid size for logical coordinates)
        max_camera_x = max(0, self.map_width * self.base_grid_cell_size - effective_screen_width)
        max_camera_y = max(0, self.map_height * self.base_grid_cell_size - effective_screen_height)

        # Clamp camera to boundaries
        clamped_camera_x = max(0, min(camera_x, max_camera_x))
        clamped_camera_y = max(0, min(camera_y, max_camera_y))

        return clamped_camera_x, clamped_camera_y
        
    def update_camera_following(self, current_camera_x: float, current_camera_y: float,
                              player_rect, effective_screen_width: float, effective_screen_height: float):
        """Update camera to follow player with smooth movement
        
        Args:
            current_camera_x: Current camera X position
            current_camera_y: Current camera Y position
            player_rect: Player rectangle with position information
            effective_screen_width: Effective screen width (accounting for zoom)
            effective_screen_height: Effective screen height (accounting for zoom)
            
        Returns:
            tuple: (new_camera_x, new_camera_y) - the updated camera position
        """
        if not player_rect:
            return current_camera_x, current_camera_y
            
        # Calculate target camera position
        target_camera_x, target_camera_y = self.calculate_target_camera_position(
            player_rect, effective_screen_width, effective_screen_height
        )
        
        # Clamp target to map boundaries
        target_camera_x, target_camera_y = self.clamp_camera_to_boundaries(
            target_camera_x, target_camera_y, effective_screen_width, effective_screen_height
        )
        
        # Apply smoothing
        new_camera_x = target_camera_x * self.camera_smoothing + current_camera_x * (1 - self.camera_smoothing)
        new_camera_y = target_camera_y * self.camera_smoothing + current_camera_y * (1 - self.camera_smoothing)
        
        return new_camera_x, new_camera_y
        
    def center_camera_on_player(self, player_rect, effective_screen_width: float, effective_screen_height: float):
        """Instantly center camera on player (for teleportation, map loading, etc.)
        
        Args:
            player_rect: Player rectangle with position information
            effective_screen_width: Effective screen width (accounting for zoom)
            effective_screen_height: Effective screen height (accounting for zoom)
            
        Returns:
            tuple: (camera_x, camera_y) - the centered camera position
        """
        if not player_rect:
            return 0, 0
            
        # Calculate target position
        target_camera_x, target_camera_y = self.calculate_target_camera_position(
            player_rect, effective_screen_width, effective_screen_height
        )
        
        # Clamp to boundaries and return
        return self.clamp_camera_to_boundaries(
            target_camera_x, target_camera_y, effective_screen_width, effective_screen_height
        )
