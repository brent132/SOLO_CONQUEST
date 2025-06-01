"""
Game Systems Coordinator - Main coordinator for all game system interactions

This class coordinates between different game systems including:
- Enemy management and player interactions
- Item collection and inventory management
- Loot chest interactions
- Teleportation and map transitions
- Game state management (death, game over)
"""
from typing import Optional, Tuple, Dict, Any, List
import pygame

from .enemy_coordinator import EnemyCoordinator
from .item_coordinator import ItemCoordinator
from .inventory_coordinator import InventoryCoordinator
from .interaction_coordinator import InteractionCoordinator


class GameSystemsCoordinator:
    """Main coordinator for all game system interactions"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Initialize sub-coordinators
        self.enemy_coordinator = EnemyCoordinator()
        self.item_coordinator = ItemCoordinator(base_grid_cell_size)
        self.inventory_coordinator = InventoryCoordinator()
        self.interaction_coordinator = InteractionCoordinator(base_grid_cell_size)
        
        # Game state
        self.game_over_triggered = False
        
    def initialize_systems(self, enemy_manager, key_item_manager, crystal_item_manager, 
                          lootchest_manager, hud, animated_tile_manager, player_system,
                          relation_handler):
        """Initialize all game systems with their managers"""
        self.enemy_coordinator.initialize(enemy_manager)
        self.item_coordinator.initialize(key_item_manager, crystal_item_manager, animated_tile_manager)
        self.inventory_coordinator.initialize(hud)
        self.interaction_coordinator.initialize(lootchest_manager, player_system, relation_handler)
        
    def scan_and_setup_items(self, layers: List[Dict], key_item_id: Optional[int], 
                           crystal_item_id: Optional[int], lootchest_item_id: Optional[int]):
        """Scan through map layers and setup items"""
        return self.item_coordinator.scan_and_setup_items(
            layers, key_item_id, crystal_item_id, lootchest_item_id
        )
        
    def update_game_systems(self, player, collision_handler, expanded_mapping, 
                           collision_map_data, layers) -> bool:
        """
        Update all game systems and handle interactions
        
        Returns:
            bool: True if player died this frame
        """
        if not player:
            return False
            
        # Update enemy systems
        player_died = self.enemy_coordinator.update_enemy_systems(
            player, collision_handler, expanded_mapping, collision_map_data, layers
        )
        
        if player_died and not self.game_over_triggered:
            self.game_over_triggered = True
            return True
            
        # Handle item collections
        self.item_coordinator.handle_item_collections(player)
        
        # Handle inventory updates from item collections
        self.inventory_coordinator.handle_inventory_updates(
            self.item_coordinator.get_collected_items()
        )
        
        # Clear collected items after processing
        self.item_coordinator.clear_collected_items()
        
        return False
        
    def handle_teleportation_check(self, player) -> Optional[Dict]:
        """Check for teleportation and handle it"""
        return self.interaction_coordinator.handle_teleportation_check(player)
        
    def handle_lootchest_interaction(self, mouse_pos: Tuple[int, int], camera_x: int, 
                                   camera_y: int, center_offset_x: float, center_offset_y: float,
                                   zoom_factor_inv: float, player_rect: pygame.Rect) -> Any:
        """Handle loot chest right-click interactions"""
        return self.interaction_coordinator.handle_lootchest_interaction(
            mouse_pos, camera_x, camera_y, center_offset_x, center_offset_y,
            zoom_factor_inv, player_rect
        )
        
    def check_lootchest_at_position(self, mouse_pos: Tuple[int, int], camera_x: int, 
                                  camera_y: int, center_offset_x: float, center_offset_y: float,
                                  zoom_factor_inv: float, layers: List[Dict], 
                                  lootchest_id: int) -> bool:
        """Check if there's a lootchest at the given position"""
        return self.interaction_coordinator.check_lootchest_at_position(
            mouse_pos, camera_x, camera_y, center_offset_x, center_offset_y,
            zoom_factor_inv, layers, lootchest_id
        )
        
    def handle_chest_opened_callback(self, chest_pos: Tuple[int, int], chest_contents: List):
        """Handle when a chest is opened"""
        return self.interaction_coordinator.handle_chest_opened_callback(chest_pos, chest_contents)
        
    def reset_game_over_state(self):
        """Reset the game over state"""
        self.game_over_triggered = False
        
    def get_enemy_coordinator(self) -> EnemyCoordinator:
        """Get the enemy coordinator"""
        return self.enemy_coordinator
        
    def get_item_coordinator(self) -> ItemCoordinator:
        """Get the item coordinator"""
        return self.item_coordinator
        
    def get_inventory_coordinator(self) -> InventoryCoordinator:
        """Get the inventory coordinator"""
        return self.inventory_coordinator
        
    def get_interaction_coordinator(self) -> InteractionCoordinator:
        """Get the interaction coordinator"""
        return self.interaction_coordinator
