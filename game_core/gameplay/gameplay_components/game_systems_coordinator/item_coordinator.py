"""
Item Coordinator - Handles item collection and management

This module manages:
- Item scanning and setup from map layers
- Item collision detection with player
- Item collection logic
- Item removal from map layers
"""
from typing import Optional, Dict, Any, List, Tuple
import pygame


class ItemCoordinator:
    """Coordinates item systems and collection logic"""
    
    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size
        
        # Item managers
        self.key_item_manager = None
        self.crystal_item_manager = None
        self.animated_tile_manager = None
        
        # Collected items this frame
        self.collected_items = []
        
    def initialize(self, key_item_manager, crystal_item_manager, animated_tile_manager):
        """Initialize with item managers"""
        self.key_item_manager = key_item_manager
        self.crystal_item_manager = crystal_item_manager
        self.animated_tile_manager = animated_tile_manager
        
    def scan_and_setup_items(self, layers: List[Dict], key_item_id: Optional[int], 
                           crystal_item_id: Optional[int], lootchest_item_id: Optional[int]):
        """
        Scan through all layers for special items and set them up
        
        Args:
            layers: Map layers to scan
            key_item_id: ID of key items
            crystal_item_id: ID of crystal items
            lootchest_item_id: ID of lootchest items
        """
        if not layers:
            return
            
        for layer_idx, layer in enumerate(layers):
            if not layer.get("visible", True):
                continue

            layer_data = layer.get("data", [])

            for y, row in enumerate(layer_data):
                for x, tile_id in enumerate(row):
                    # Check for key items
                    if key_item_id and tile_id == key_item_id and self.key_item_manager:
                        self.key_item_manager.add_key_item(x, y, tile_id, layer_idx)

                    # Check for crystal items
                    elif crystal_item_id and tile_id == crystal_item_id and self.crystal_item_manager:
                        self.crystal_item_manager.add_crystal_item(x, y, tile_id, layer_idx)

                    # Note: lootchest items are handled by the interaction coordinator
                    # since they involve more complex interaction logic
                    
    def handle_item_collections(self, player):
        """
        Handle all item collections for this frame
        
        Args:
            player: The player character
        """
        if not player:
            return
            
        # Clear collected items from previous frame
        self.collected_items.clear()
        
        # Check for key item collections
        if self.key_item_manager:
            collected_key = self.key_item_manager.check_player_collision(
                player.rect, self.base_grid_cell_size
            )
            if collected_key:
                self.collected_items.append({
                    'type': 'key',
                    'position': collected_key,
                    'name': 'Key',
                    'image': self.animated_tile_manager.get_animated_tile_frame(
                        self._get_key_item_id()
                    ) if self.animated_tile_manager else None
                })
                
        # Check for crystal item collections
        if self.crystal_item_manager:
            collected_crystal = self.crystal_item_manager.check_player_collision(
                player.rect, self.base_grid_cell_size
            )
            if collected_crystal:
                self.collected_items.append({
                    'type': 'crystal',
                    'position': collected_crystal,
                    'name': 'Crystal',
                    'image': self.animated_tile_manager.get_animated_tile_frame(
                        self._get_crystal_item_id()
                    ) if self.animated_tile_manager else None
                })
                
    def get_collected_items(self) -> List[Dict]:
        """Get items collected this frame"""
        return self.collected_items.copy()
        
    def clear_collected_items(self):
        """Clear the collected items list"""
        self.collected_items.clear()
        
    def _get_key_item_id(self) -> Optional[int]:
        """Get the key item ID from the animated tile manager"""
        if self.animated_tile_manager and hasattr(self.animated_tile_manager, 'animated_tile_ids'):
            for tile_id, name in self.animated_tile_manager.animated_tile_ids.items():
                if name == 'key_item':
                    return tile_id
        return None
        
    def _get_crystal_item_id(self) -> Optional[int]:
        """Get the crystal item ID from the animated tile manager"""
        if self.animated_tile_manager and hasattr(self.animated_tile_manager, 'animated_tile_ids'):
            for tile_id, name in self.animated_tile_manager.animated_tile_ids.items():
                if name == 'crystal_item':
                    return tile_id
        return None
