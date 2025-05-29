"""
Game State Saver - Handles saving game state to map files
"""
import os
import json

class GameStateSaver:
    """Handles saving game state to map files"""
    def __init__(self):
        pass

    def _get_enemies_data(self, enemies):
        """Get data for all enemies

        Args:
            enemies: List of enemy objects

        Returns:
            List of enemy data dictionaries
        """
        enemy_data = []

        for enemy in enemies:
            # Skip enemies that are dead or being removed
            if enemy.state == "dead" or enemy.state == "removing":
                continue

            # Create enemy data dictionary
            enemy_dict = {
                "type": enemy.enemy_type,
                "position": {
                    "x": enemy.rect.x,
                    "y": enemy.rect.y
                },
                "direction": enemy.direction,
                "health": getattr(enemy, 'current_health', getattr(enemy, 'health', 100)),  # Use current_health if available, fallback to health, default to 100
                "state": enemy.state
            }

            # Add float position if available
            if hasattr(enemy, "float_x") and hasattr(enemy, "float_y"):
                enemy_dict["float_position"] = {
                    "x": enemy.float_x,
                    "y": enemy.float_y
                }

            enemy_data.append(enemy_dict)

        return enemy_data

    def _get_inventory_data(self, inventory):
        """Get data for inventory

        Args:
            inventory: Inventory object

        Returns:
            List of inventory item dictionaries
        """
        inventory_data = []

        # Check if inventory is visible (might be None or hidden)
        if not inventory or not hasattr(inventory, "slots"):
            return inventory_data

        # Get all slots
        for slot_idx, slot in enumerate(inventory.slots):
            # Skip empty slots
            if not slot.item:
                continue

            # Create item data dictionary
            item_dict = {
                "slot": slot_idx,
                "name": slot.item.name,
                "count": slot.item.count
            }

            inventory_data.append(item_dict)

        return inventory_data

    def _get_collected_keys_data(self, key_manager):
        """Get data for collected keys

        Args:
            key_manager: Key item manager object

        Returns:
            List of collected key positions
        """
        collected_keys = []

        # Check if key manager is available
        if not key_manager or not hasattr(key_manager, "collected_keys"):
            return collected_keys

        # Get all collected keys
        for key_pos in key_manager.collected_keys:
            collected_keys.append(key_pos)

        return collected_keys

    def _get_collected_crystals_data(self, crystal_manager):
        """Get data for collected crystals

        Args:
            crystal_manager: Crystal item manager object

        Returns:
            List of collected crystal positions
        """
        collected_crystals = []

        # Check if crystal manager is available
        if not crystal_manager or not hasattr(crystal_manager, "collected_crystals"):
            return collected_crystals

        # Get all collected crystals
        for crystal_pos in crystal_manager.collected_crystals:
            collected_crystals.append(crystal_pos)

        return collected_crystals

    def _get_opened_lootchests_data(self, lootchest_manager):
        """Get data for opened lootchests

        Args:
            lootchest_manager: Lootchest manager object

        Returns:
            List of opened lootchest positions
        """
        opened_lootchests = []

        # Check if lootchest manager is available
        if not lootchest_manager or not hasattr(lootchest_manager, "opened_chests"):
            return opened_lootchests

        # Get all opened lootchests
        for chest_pos in lootchest_manager.opened_chests:
            opened_lootchests.append(chest_pos)

        return opened_lootchests

    def save_game_state(self, play_screen):
        """Save the current game state to the map file"""
        # Check if play screen has a player and map name
        if not play_screen.player or not play_screen.map_name:
            return False, "No player or map to save!"

        # Determine the correct map path - could be a main map or a related map
        map_path = None

        # First check if it's a main map
        main_map_path = os.path.join("Maps", play_screen.map_name, f"{play_screen.map_name}.json")
        if os.path.exists(main_map_path):
            map_path = main_map_path
            print(f"Found main map file for saving: {map_path}")
        else:
            # It might be a related map, search in all map folders
            maps_dir = os.path.join("Maps")
            if os.path.exists(maps_dir):
                folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]
                for folder_name in folders:
                    folder_path = os.path.join(maps_dir, folder_name)
                    related_map_path = os.path.join(folder_path, f"{play_screen.map_name}.json")
                    if os.path.exists(related_map_path):
                        map_path = related_map_path
                        print(f"Found related map file for saving: {map_path}")
                        break

        try:
            # Check if file exists
            if not map_path or not os.path.exists(map_path):
                return False, f"Map file not found: {play_screen.map_name}"

            # Load existing map data
            with open(map_path, 'r') as f:
                map_data = json.load(f)

            # Create a more readable game state
            game_state = {
                # Camera position
                "camera": {
                    "x": play_screen.camera_x,
                    "y": play_screen.camera_y
                },
                # Enemy data
                "enemies": self._get_enemies_data(play_screen.enemy_manager.enemies),
                # HUD Inventory data
                "inventory": self._get_inventory_data(play_screen.hud.inventory),
                # Full player inventory data
                "player_inventory": self._get_inventory_data(play_screen.player_inventory) if play_screen.player_inventory.is_visible() else [],
                # Collected keys data
                "collected_keys": self._get_collected_keys_data(play_screen.key_item_manager),
                # Collected crystals data
                "collected_crystals": self._get_collected_crystals_data(play_screen.crystal_item_manager),
                # Opened lootchests data
                "opened_lootchests": self._get_opened_lootchests_data(play_screen.lootchest_manager),
                # Chest contents data
                "chest_contents": play_screen.lootchest_manager.get_chest_contents_data()
            }

            # Update the map data with game state and save using proper JSON serialization

            # Update relation points if available
            if hasattr(play_screen, 'relation_handler') and play_screen.relation_handler.current_map:
                current_map = play_screen.relation_handler.current_map
                if current_map in play_screen.relation_handler.relation_points:
                    map_data["relation_points"] = play_screen.relation_handler.relation_points[current_map]

            # Add game state to the map data
            map_data["game_state"] = game_state

            # Save the updated map data using compact JSON serialization like house.json
            with open(map_path, 'w') as f:
                # Use custom JSON formatting to match house.json structure
                self._write_compact_json(f, map_data)

            return True, None
        except Exception as e:
            return False, str(e)

    def _write_compact_json(self, f, map_data):
        """Write JSON in compact format matching house.json structure"""
        f.write('{\n')

        # Write basic properties first
        f.write(f'  "name": "{map_data["name"]}",\n')
        f.write(f'  "width": {map_data["width"]},\n')
        f.write(f'  "height": {map_data["height"]},\n')
        f.write(f'  "tile_size": {map_data["tile_size"]},\n')

        # Write is_main if it exists
        if "is_main" in map_data:
            f.write(f'  "is_main": {str(map_data["is_main"]).lower()},\n')

        # Write tile_mapping with proper indentation
        f.write('  "tile_mapping": ')
        tile_mapping_json = json.dumps(map_data["tile_mapping"], indent=4)
        # Adjust indentation to match the structure
        tile_mapping_json = tile_mapping_json.replace('\n', '\n  ')
        f.write(tile_mapping_json)
        f.write(',\n')

        # Write layers with compact map_data arrays
        f.write('  "layers": [\n')
        for layer_idx, layer in enumerate(map_data["layers"]):
            f.write('    {\n')
            f.write('      "visible": true,\n')
            f.write('      "map_data": [\n')

            # Write each row on a single line (compact format like house.json)
            for row_idx, row in enumerate(layer["map_data"]):
                row_str = "        [" + ", ".join(str(tile) for tile in row) + "]"
                if row_idx < len(layer["map_data"]) - 1:
                    row_str += ","
                f.write(row_str + '\n')

            f.write('      ]\n')
            if layer_idx < len(map_data["layers"]) - 1:
                f.write('    },\n')
            else:
                f.write('    }\n')
        f.write('  ],\n')

        # Write collision_data with proper indentation
        f.write('  "collision_data": ')
        collision_data_json = json.dumps(map_data["collision_data"], indent=4)
        # Adjust indentation to match the structure
        collision_data_json = collision_data_json.replace('\n', '\n  ')
        f.write(collision_data_json)

        # Write other sections if they exist
        sections_to_write = []

        # Add player_start if it exists
        if "player_start" in map_data:
            sections_to_write.append(("player_start", map_data["player_start"]))

        # Add enemies if it exists
        if "enemies" in map_data:
            sections_to_write.append(("enemies", map_data["enemies"]))

        # Add relation_points if it exists
        if "relation_points" in map_data:
            sections_to_write.append(("relation_points", map_data["relation_points"]))

        # Add game_state if it exists
        if "game_state" in map_data:
            sections_to_write.append(("game_state", map_data["game_state"]))

        # Write all sections
        for section_name, section_data in sections_to_write:
            f.write(',\n')
            f.write(f'  "{section_name}": ')
            section_json = json.dumps(section_data, indent=4)
            # Adjust indentation to match the structure
            section_json = section_json.replace('\n', '\n  ')
            f.write(section_json)

        f.write('\n}\n')
