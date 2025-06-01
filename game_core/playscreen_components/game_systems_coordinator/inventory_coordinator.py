"""
Inventory Coordinator - Handles inventory management and updates

This module manages:
- Inventory updates from item collections
- Item stacking and counting logic
- Inventory slot management
- HUD inventory integration
"""
from typing import Optional, Dict, Any, List
import pygame


class InventoryCoordinator:
    """Coordinates inventory management and updates"""
    
    def __init__(self):
        self.hud = None
        
    def initialize(self, hud):
        """Initialize with the HUD system"""
        self.hud = hud
        
    def handle_inventory_updates(self, collected_items: List[Dict]):
        """
        Handle inventory updates from collected items
        
        Args:
            collected_items: List of items collected this frame
        """
        if not self.hud or not collected_items:
            return
            
        for item in collected_items:
            item_type = item.get('type')
            item_name = item.get('name')
            item_image = item.get('image')
            item_position = item.get('position')
            
            if item_type == 'key':
                self._add_key_to_inventory(item_name, item_image, item_position)
            elif item_type == 'crystal':
                self._add_crystal_to_inventory(item_name, item_image, item_position)
                
    def _add_key_to_inventory(self, item_name: str, item_image, item_position: tuple):
        """Add a key item to the inventory"""
        if not self.hud or not hasattr(self.hud, 'inventory'):
            return
            
        # Check if we already have a key in the inventory
        key_slot = -1
        for i in range(self.hud.inventory.num_slots):
            if (self.hud.inventory.inventory_items[i] and 
                self.hud.inventory.inventory_items[i]["name"] == item_name):
                # Found an existing key, increment its count
                key_slot = i
                if "count" in self.hud.inventory.inventory_items[i]:
                    self.hud.inventory.inventory_items[i]["count"] += 1
                else:
                    # First time adding a count to this key
                    self.hud.inventory.inventory_items[i]["count"] = 2
                break

        # If no key was found, add to first empty slot
        if key_slot == -1:
            for i in range(self.hud.inventory.num_slots):
                if not self.hud.inventory.inventory_items[i]:
                    # Add key to this slot with count of 1
                    self.hud.inventory.inventory_items[i] = {
                        "name": item_name,
                        "image": item_image,
                        "count": 1
                    }
                    break
                    
        # Remove the key from map layers
        if item_position:
            self._remove_key_from_map_layers(item_position[0], item_position[1])
            
    def _add_crystal_to_inventory(self, item_name: str, item_image, item_position: tuple):
        """Add a crystal item to the inventory"""
        if not self.hud or not hasattr(self.hud, 'inventory'):
            return
            
        # Check if we already have a crystal in the inventory
        crystal_slot = -1
        for i in range(self.hud.inventory.num_slots):
            if (self.hud.inventory.inventory_items[i] and 
                self.hud.inventory.inventory_items[i]["name"] == item_name):
                # Found an existing crystal, increment its count
                crystal_slot = i
                if "count" in self.hud.inventory.inventory_items[i]:
                    self.hud.inventory.inventory_items[i]["count"] += 1
                else:
                    # First time adding a count to this crystal
                    self.hud.inventory.inventory_items[i]["count"] = 2
                break

        # If no crystal was found, add to first empty slot
        if crystal_slot == -1:
            for i in range(self.hud.inventory.num_slots):
                if not self.hud.inventory.inventory_items[i]:
                    # Add crystal to this slot with count of 1
                    self.hud.inventory.inventory_items[i] = {
                        "name": item_name,
                        "image": item_image,
                        "count": 1
                    }
                    break
                    
        # Remove the crystal from map layers
        if item_position:
            self._remove_crystal_from_map_layers(item_position[0], item_position[1])
            
    def _remove_key_from_map_layers(self, grid_x: int, grid_y: int):
        """Remove a key from all map layers"""
        # This will be implemented to interface with the map system
        # For now, we'll need to coordinate with PlayScreen to handle this
        # TODO: Move this logic to map system or create a proper interface
        pass
        
    def _remove_crystal_from_map_layers(self, grid_x: int, grid_y: int):
        """Remove a crystal from all map layers"""
        # This will be implemented to interface with the map system
        # For now, we'll need to coordinate with PlayScreen to handle this
        # TODO: Move this logic to map system or create a proper interface
        pass
        
    def load_inventory_from_save_data(self, inventory_data: List, animated_tile_manager):
        """Load inventory from save data"""
        if not self.hud or not hasattr(self.hud, 'inventory') or not inventory_data:
            return
            
        for slot, item_data in enumerate(inventory_data):
            if item_data and slot < self.hud.inventory.num_slots:
                item_name = item_data.get("name", "")
                item_count = item_data.get("count", 1)
                
                # For keys, get the image from the animated tile manager
                if item_name == "Key":
                    key_item_id = self._get_key_item_id(animated_tile_manager)
                    if key_item_id:
                        self.hud.inventory.inventory_items[slot] = {
                            "name": item_name,
                            "count": item_count,
                            "image": animated_tile_manager.get_animated_tile_frame(key_item_id)
                        }
                # For crystals, get the image from the animated tile manager
                elif item_name == "Crystal":
                    crystal_item_id = self._get_crystal_item_id(animated_tile_manager)
                    if crystal_item_id:
                        self.hud.inventory.inventory_items[slot] = {
                            "name": item_name,
                            "count": item_count,
                            "image": animated_tile_manager.get_animated_tile_frame(crystal_item_id)
                        }
                        
    def _get_key_item_id(self, animated_tile_manager) -> Optional[int]:
        """Get the key item ID from the animated tile manager"""
        if animated_tile_manager and hasattr(animated_tile_manager, 'animated_tile_ids'):
            for tile_id, name in animated_tile_manager.animated_tile_ids.items():
                if name == 'key_item':
                    return tile_id
        return None
        
    def _get_crystal_item_id(self, animated_tile_manager) -> Optional[int]:
        """Get the crystal item ID from the animated tile manager"""
        if animated_tile_manager and hasattr(animated_tile_manager, 'animated_tile_ids'):
            for tile_id, name in animated_tile_manager.animated_tile_ids.items():
                if name == 'crystal_item':
                    return tile_id
        return None
