"""
DEPRECATED: Character Inventory Saver

⚠️  WARNING: This module is DEPRECATED and should not be used! ⚠️

This functionality has been consolidated into PlayerInventory class for better
architecture and to eliminate redundant inventory logic.

Use PlayerInventory.save_to_file() and PlayerInventory.load_from_file() instead.

This file will be removed in a future update.
"""
import os
import json
import pygame

class CharacterInventorySaver:
    """Handles saving and loading character inventory data"""
    def __init__(self):
        """Initialize the character inventory saver"""
        # Create the save directory if it doesn't exist
        self.save_dir = "SaveData"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        # Path to the character inventory save file
        self.inventory_save_path = os.path.join(self.save_dir, "character_inventory.json")

    def save_inventory(self, player_inventory):
        """Save the player's inventory to a file

        Args:
            player_inventory: The player's inventory object

        Returns:
            tuple: (success, message)
        """
        try:
            # Skip if inventory is not visible (not initialized)
            if not hasattr(player_inventory, 'inventory_items'):
                return False, "Inventory not initialized"

            # Extract inventory data
            inventory_data = self._get_inventory_data(player_inventory)

            # Create the save data structure
            save_data = {
                "version": 1,
                "inventory": inventory_data
            }

            # Save to file
            with open(self.inventory_save_path, 'w') as f:
                json.dump(save_data, f, indent=2)

            return True, "Character inventory saved successfully"
        except Exception as e:
            return False, f"Error saving character inventory: {str(e)}"

    def load_inventory(self, player_inventory):
        """Load the player's inventory from the save file

        Args:
            player_inventory: The player's inventory object to update

        Returns:
            tuple: (success, message)
        """
        try:
            # Check if save file exists
            if not os.path.exists(self.inventory_save_path):
                return False, "No saved inventory found"

            # Load the save data
            with open(self.inventory_save_path, 'r') as f:
                save_data = json.load(f)

            # Check version
            if "version" not in save_data or save_data["version"] != 1:
                return False, "Incompatible save version"

            # Check if inventory data exists
            if "inventory" not in save_data:
                return False, "No inventory data in save file"

            # Update the player's inventory
            self._update_inventory(player_inventory, save_data["inventory"])

            return True, "Character inventory loaded successfully"
        except Exception as e:
            return False, f"Error loading character inventory: {str(e)}"

    def _get_inventory_data(self, inventory):
        """Extract inventory data for saving

        Args:
            inventory: The inventory object

        Returns:
            list: List of item data dictionaries
        """
        inventory_data = []

        # Go through each inventory slot
        for i in range(inventory.num_slots):
            item = inventory.inventory_items[i]
            if item:
                # Create a simplified item data structure
                item_data = {
                    "slot": i,
                    "name": item.get("name", "Unknown"),
                    "count": item.get("count", 1)
                }
                inventory_data.append(item_data)

        return inventory_data

    def _update_inventory(self, inventory, inventory_data):
        """Update the inventory with loaded data

        Args:
            inventory: The inventory object to update
            inventory_data: List of item data dictionaries
        """
        # We don't clear the existing inventory completely
        # This allows us to keep any existing images for items

        # Load each inventory item
        for item_data in inventory_data:
            slot = item_data.get("slot", 0)
            if 0 <= slot < inventory.num_slots:
                # Create the item
                item_name = item_data.get("name", "Unknown")
                item_count = item_data.get("count", 1)

                # Create a placeholder image if needed
                placeholder_image = pygame.Surface((16, 16), pygame.SRCALPHA)

                # Set different colors based on item type for placeholder
                if item_name == "Key":
                    placeholder_image.fill((255, 215, 0, 200))  # Gold for keys
                elif item_name == "Crystal":
                    placeholder_image.fill((0, 191, 255, 200))  # Blue for crystals
                else:
                    placeholder_image.fill((255, 0, 0, 200))  # Red for unknown items

                # Add to inventory with placeholder image
                inventory.inventory_items[slot] = {
                    "name": item_name,
                    "count": item_count,
                    "image": placeholder_image  # Add placeholder image
                }
