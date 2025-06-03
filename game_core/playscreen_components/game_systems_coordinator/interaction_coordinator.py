"""
Interaction Coordinator - Handles player interactions with world objects

This module manages:
- Loot chest interactions and right-click handling
- Teleportation point detection and coordination
- World object interaction logic
- Mouse interaction coordinate conversion
"""
from typing import Optional, Dict, Any, List, Tuple
import pygame


class InteractionCoordinator:
    """Coordinates player interactions with world objects"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # System references
        self.lootchest_manager = None
        self.player_system = None
        self.relation_handler = None
        
    def initialize(self, lootchest_manager, player_system, relation_handler):
        """Initialize with interaction systems"""
        self.lootchest_manager = lootchest_manager
        self.player_system = player_system
        self.relation_handler = relation_handler
        
    def handle_teleportation_check(self, player) -> Optional[Dict]:
        """
        Check for teleportation and handle coordination
        
        Args:
            player: The player character
            
        Returns:
            Dict with teleportation info if teleportation should occur, None otherwise
        """
        if not self.relation_handler or not player:
            return None
            
        # Check for collisions with relation points
        relation = self.relation_handler.check_player_collision(player.rect)
        if relation:
            # Player touched a relation point, prepare teleportation data
            print(f"Player touched relation point: {relation['from_point']} -> {relation['to_point']} in map {relation['to_map']}")
            print(f"Teleporting to position: {relation['to_position']}")
            
            return relation
            
        return None
        
    def handle_lootchest_interaction(self, mouse_pos: Tuple[int, int], camera_x: int, 
                                   camera_y: int, center_offset_x: float, center_offset_y: float,
                                   zoom_factor_inv: float, player_rect: pygame.Rect) -> Any:
        """
        Handle loot chest right-click interactions
        
        Args:
            mouse_pos: Mouse position on screen
            camera_x: Camera X position
            camera_y: Camera Y position
            center_offset_x: Center offset X for coordinate conversion
            center_offset_y: Center offset Y for coordinate conversion
            zoom_factor_inv: Inverse zoom factor for coordinate conversion
            player_rect: Player rectangle for distance checking
            
        Returns:
            Result from lootchest interaction
        """
        if not self.lootchest_manager:
            return None
            
        # Convert screen coordinates to world coordinates accounting for zoom
        world_mouse_x = mouse_pos[0] * zoom_factor_inv
        world_mouse_y = mouse_pos[1] * zoom_factor_inv

        # Calculate grid position from world mouse position
        grid_x = int((world_mouse_x + camera_x) // self.base_grid_cell_size)
        grid_y = int((world_mouse_y + camera_y) // self.base_grid_cell_size)
        
        print(f"Right-click at mouse position: {mouse_pos}")
        print(f"Camera position: ({camera_x}, {camera_y})")
        print(f"World mouse position: ({world_mouse_x}, {world_mouse_y})")
        print(f"Calculated grid position: ({grid_x}, {grid_y})")

        # Check if there's a lootchest at this position
        position = (grid_x, grid_y)
        if position in self.lootchest_manager.lootchests:
            print(f"Found lootchest at position {position}")
        else:
            print(f"No lootchest found at position {position}")
            print(f"Available lootchests: {list(self.lootchest_manager.lootchests.keys())}")

        # For smaller maps, the center offset represents how much the map is shifted to center it
        # We need to account for this when converting mouse coordinates to world coordinates
        # The mouse position needs to be adjusted by subtracting the center offset
        # But the camera position should remain as-is since it's already in world coordinates
        adjusted_mouse_pos = (
            world_mouse_x - center_offset_x,
            world_mouse_y - center_offset_y
        )

        # Camera position should not be adjusted by center offset for coordinate calculation
        # The center offset is already accounted for in the rendering system
        adjusted_camera_x = camera_x
        adjusted_camera_y = camera_y

        print(f"Adjusted mouse position: {adjusted_mouse_pos}")
        print(f"Adjusted camera position: ({adjusted_camera_x}, {adjusted_camera_y})")

        result = self.lootchest_manager.handle_right_click(
            adjusted_mouse_pos,
            adjusted_camera_x,
            adjusted_camera_y,
            self.base_grid_cell_size,
            player_rect
        )
        print(f"Lootchest interaction result: {result}")
        
        return result
        
    def check_lootchest_at_position(self, mouse_pos: Tuple[int, int], camera_x: int, 
                                  camera_y: int, center_offset_x: float, center_offset_y: float,
                                  zoom_factor_inv: float, layers: List[Dict], 
                                  lootchest_id: int) -> bool:
        """
        Check if there's a lootchest at the given position
        
        Args:
            mouse_pos: Mouse position on screen
            camera_x: Camera X position
            camera_y: Camera Y position
            center_offset_x: Center offset X for coordinate conversion
            center_offset_y: Center offset Y for coordinate conversion
            zoom_factor_inv: Inverse zoom factor for coordinate conversion
            layers: Map layers to check
            lootchest_id: ID of lootchest tiles
            
        Returns:
            True if there's a lootchest at the position
        """
        if not self.lootchest_manager:
            return False
            
        # Convert screen coordinates to world coordinates
        world_mouse_x = mouse_pos[0] * zoom_factor_inv
        world_mouse_y = mouse_pos[1] * zoom_factor_inv

        # Adjust for center offset
        adjusted_world_x = world_mouse_x - center_offset_x
        adjusted_world_y = world_mouse_y - center_offset_y

        # Calculate grid position
        grid_x = int((adjusted_world_x + camera_x) // self.base_grid_cell_size)
        grid_y = int((adjusted_world_y + camera_y) // self.base_grid_cell_size)
        
        position = (grid_x, grid_y)

        # Check if this position is in the lootchests dictionary
        if position in self.lootchest_manager.lootchests:
            return True

        # Check if this position is in the opened chests list
        if position in self.lootchest_manager.opened_chests:
            return True

        # Check each layer for a lootchest at this position
        for layer_idx, layer in enumerate(layers):
            layer_data = layer["data"]
            if 0 <= grid_y < len(layer_data) and 0 <= grid_x < len(layer_data[grid_y]):
                if layer_data[grid_y][grid_x] == lootchest_id:
                    return True

        return False
        
    def handle_chest_opened_callback(self, chest_pos: Tuple[int, int], chest_contents: List):
        """
        Handle when a chest is opened
        
        Args:
            chest_pos: Position of the chest
            chest_contents: Contents of the chest
            
        Returns:
            Processed chest contents
        """
        print(f"InteractionCoordinator.handle_chest_opened_callback called with chest_pos={chest_pos}")

        # Make sure chest_contents is a list
        if not isinstance(chest_contents, list):
            print(f"Warning: chest_contents is not a list, it's a {type(chest_contents)}")
            chest_contents = []

        # If chest_contents is empty, initialize with empty slots
        if not chest_contents:
            print("Chest contents is empty, initializing with empty slots")
            chest_contents = [None] * 60  # 10x6 grid
            
        return chest_contents
