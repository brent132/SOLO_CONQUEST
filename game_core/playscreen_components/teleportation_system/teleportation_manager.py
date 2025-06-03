"""
Teleportation Manager - Handles all teleportation logic and map switching

This module manages:
- Teleportation detection and processing
- Map switching during teleportation
- Player positioning at destination points
- Teleportation state management
- Relation point coordination
"""


class TeleportationManager:
    """Manages teleportation between maps and relation points"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Teleportation state
        self.is_teleporting = False
        self.teleport_info = None
        
        # System references
        self.player_system = None
        self.camera_controller = None
        self.relation_handler = None
        self.player_location_tracker = None
        self.save_callback = None
        self.load_map_callback = None

        # Collision system references for unstuck logic
        self.collision_handler = None
        self.expanded_mapping = None
        self.map_data = None
        
    def initialize(self, player_system, camera_controller, relation_handler, 
                  player_location_tracker, save_callback, load_map_callback):
        """Initialize teleportation manager with required systems"""
        self.player_system = player_system
        self.camera_controller = camera_controller
        self.relation_handler = relation_handler
        self.player_location_tracker = player_location_tracker
        self.save_callback = save_callback
        self.load_map_callback = load_map_callback

    def set_collision_system(self, collision_handler, expanded_mapping, map_data):
        """Set collision system references for unstuck logic

        Args:
            collision_handler: The collision handler instance
            expanded_mapping: The tile mapping
            map_data: The map data for collision detection
        """
        self.collision_handler = collision_handler
        self.expanded_mapping = expanded_mapping
        self.map_data = map_data
        
    def handle_teleportation(self, relation, current_map_name):
        """Handle teleportation when player touches a relation point
        
        Args:
            relation: Relation data containing teleportation information
            current_map_name: Name of the current map
            
        Returns:
            bool: True if teleportation was initiated, False otherwise
        """
        if not relation:
            return False
            
        player = self.player_system.get_player()
        if not player:
            return False
            
        print(f"Player touched relation point: {relation['from_point']} -> {relation['to_point']} in map {relation['to_map']}")
        print(f"Teleporting to position: {relation['to_position']}")

        # Save the current player position using the player system
        self.player_system.save_player_location(current_map_name, self.player_location_tracker)
        print(f"Saved player location for map {current_map_name}: ({player.rect.x}, {player.rect.y}, {player.direction})")

        # Save the current game state before teleporting
        if self.save_callback:
            self.save_callback()

        # Store the target position before loading the map
        target_position = relation['to_position']
        target_map = relation['to_map']
        print(f"Loading target map: {target_map}")
        print(f"Target position: {target_position}")

        # Set teleportation state
        self.is_teleporting = True
        self.teleport_info = {
            'target_position': target_position,
            'target_map': target_map,
            'to_point': relation['to_point']
        }

        # Prepare relation handler for map switch
        self._prepare_relation_handler_for_teleport()

        # Load the target map
        if self.load_map_callback:
            load_success = self.load_map_callback(target_map)
            print(f"Map load success: {load_success}")
            
            if load_success:
                self._complete_teleportation(target_position, target_map, relation)
                return True
                
        return False
        
    def _prepare_relation_handler_for_teleport(self):
        """Prepare relation handler for teleportation"""
        if not self.relation_handler:
            return
            
        # Make sure we have all relation points loaded before switching maps
        self.relation_handler.load_all_relation_points()

        # Print all available relation points for debugging
        print(f"Available relation points before map load: {self.relation_handler.relation_points}")
        
    def _complete_teleportation(self, target_position, target_map, relation):
        """Complete the teleportation process after map load"""
        player = self.player_system.get_player()
        if not player or not self.is_teleporting:
            return
            
        # Make sure the relation handler has the current map set correctly
        if self.relation_handler:
            self.relation_handler.current_map = target_map
            print(f"Set relation handler current map to: {self.relation_handler.current_map}")

            # Set the current teleport point to the destination point
            # This prevents immediate re-teleportation until player steps off and back on
            grid_x, grid_y = target_position

            # Find the ID of the destination point
            point_id = None
            if target_map in self.relation_handler.relation_points:
                for id_key, points in self.relation_handler.relation_points[target_map].items():
                    if relation['to_point'] in points and points[relation['to_point']] == target_position:
                        point_id = id_key
                        break

            self.relation_handler.current_teleport_point = {
                'point_type': relation['to_point'],
                'position': target_position,
                'id': point_id
            }
            print(f"Set current teleport point to: {self.relation_handler.current_teleport_point}")

            # Print all available relation points after map load
            print(f"Available relation points after map load: {self.relation_handler.relation_points}")

        # Position the player exactly at the center of the target relation point
        self._position_player_at_teleport_point(target_position, target_map)
        
        # Reset teleportation state
        self.is_teleporting = False
        self.teleport_info = None
        
    def _position_player_at_teleport_point(self, target_position, target_map):
        """Position player at the exact center of the teleport point"""
        player = self.player_system.get_player()
        if not player:
            return
            
        # Convert grid coordinates to pixel coordinates using base grid size (logical coordinates)
        grid_x, grid_y = target_position
        pixel_x = grid_x * self.base_grid_cell_size
        pixel_y = grid_y * self.base_grid_cell_size

        # Calculate the exact center of the teleport point
        point_center_x = pixel_x + (self.base_grid_cell_size // 2)
        point_center_y = pixel_y + (self.base_grid_cell_size // 2)

        # Set player position directly at the center of the teleport point
        # Use the center of the player's rect to align with the center of the point
        player.rect.centerx = point_center_x
        player.rect.centery = point_center_y

        # Save this position using the player system
        self.player_system.save_player_location(target_map, self.player_location_tracker)
        print(f"DEBUG: Saved teleport position for map {target_map}: ({player.rect.x}, {player.rect.y}, {player.direction})")

        # Reset movement states
        player.velocity = [0, 0]
        player.is_knocked_back = False
        player.knockback_velocity = [0, 0]

        print(f"Positioned player exactly at center of teleport point: ({point_center_x}, {point_center_y})")

        # Update the player's position in the physics system
        # This ensures animations and collision detection work correctly
        player.update_position()

        # Check if player is stuck in collision after teleportation and unstuck if needed
        self._unstuck_player_after_teleport()

        # Update camera to center on player using camera controller
        if self.camera_controller:
            self.camera_controller.center_camera_on_player()

    def _unstuck_player_after_teleport(self):
        """Check if player is stuck after teleportation and unstuck if needed"""
        if not all([self.player_system, self.collision_handler, self.expanded_mapping, self.map_data]):
            print("Warning: Cannot perform unstuck check - collision system not initialized")
            return

        # Attempt to unstuck the player if they're stuck in a collision
        unstuck_success = self.player_system.unstuck_player(
            self.collision_handler, self.expanded_mapping, self.map_data
        )

        if unstuck_success:
            print("Player was unstuck after teleportation")
            # Update camera position after unstuck
            if self.camera_controller:
                self.camera_controller.center_camera_on_player()

    def get_teleportation_state(self):
        """Get current teleportation state
        
        Returns:
            dict: Current teleportation state information
        """
        return {
            "is_teleporting": self.is_teleporting,
            "teleport_info": self.teleport_info
        }
        
    def set_teleportation_state(self, is_teleporting: bool, teleport_info=None):
        """Set teleportation state (for loading from save data)"""
        self.is_teleporting = is_teleporting
        self.teleport_info = teleport_info
        
    def clear_teleportation_state(self):
        """Clear teleportation state"""
        self.is_teleporting = False
        self.teleport_info = None
