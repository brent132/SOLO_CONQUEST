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
                "health": enemy.health,
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

            # We'll write the game state directly to the file

            # Save the updated map data with proper formatting
            with open(map_path, 'w') as f:
                # Start the JSON object
                f.write('{\n')

                # Write the basic properties
                f.write(f'  "name": "{map_data["name"]}",\n')
                f.write(f'  "width": {map_data["width"]},\n')
                f.write(f'  "height": {map_data["height"]},\n')
                f.write(f'  "tile_size": {map_data["tile_size"]},\n')

                # Preserve the is_main property if it exists
                if "is_main" in map_data:
                    f.write(f'  "is_main": {str(map_data["is_main"]).lower()},\n')

                # Write the tile mapping
                f.write('  "tile_mapping": ')
                f.write(json.dumps(map_data["tile_mapping"], indent=4).replace('\n', '\n  '))

                # Write the layers
                f.write(',\n  "layers": [\n')

                # Write each layer
                for i, layer in enumerate(map_data["layers"]):
                    f.write('    {\n')
                    f.write('      "visible": true,\n')
                    f.write('      "map_data": ')

                    # Format the map data with each row on its own line
                    map_data_str = "[\n"

                    # Format each row
                    for row_idx, row in enumerate(layer["map_data"]):
                        row_str = "        [" + ", ".join(str(tile) for tile in row) + "]"
                        if row_idx < len(layer["map_data"]) - 1:
                            row_str += ","
                        map_data_str += row_str + "\n"

                    map_data_str += "      ]"
                    f.write(map_data_str)

                    if i < len(map_data["layers"]) - 1:
                        f.write('\n    },\n')
                    else:
                        f.write('\n    }\n')

                f.write('  ]')

                # Add collision data if available
                if "collision_data" in map_data and map_data["collision_data"]:
                    f.write(',\n  "collision_data": ')

                    # Check if collision data is a list of lists or a more complex structure
                    if isinstance(map_data["collision_data"], list) and all(isinstance(item, list) for item in map_data["collision_data"]):
                        # Simple list of coordinates
                        f.write('[\n')

                        # Format each collision point
                        for col_idx, col_point in enumerate(map_data["collision_data"]):
                            if isinstance(col_point, list) and len(col_point) >= 2:
                                f.write(f'    [{col_point[0]}, {col_point[1]}]')
                                if col_idx < len(map_data["collision_data"]) - 1:
                                    f.write(',\n')
                                else:
                                    f.write('\n')

                        f.write('  ]')
                    else:
                        # More complex structure - use json.dumps with proper indentation
                        collision_str = json.dumps(map_data["collision_data"], indent=4).replace('\n', '\n  ')
                        f.write(collision_str)

                # Add player start position if available
                if "player_start" in map_data and map_data["player_start"]:
                    f.write(',\n  "player_start": {\n')
                    f.write(f'    "x": {map_data["player_start"]["x"]},\n')
                    f.write(f'    "y": {map_data["player_start"]["y"]},\n')
                    f.write(f'    "direction": "{map_data["player_start"]["direction"]}"\n')
                    f.write('  }')

                # Add enemy data if available
                if "enemies" in map_data and map_data["enemies"]:
                    f.write(',\n  "enemies": [\n')

                    # Format each enemy
                    for enemy_idx, enemy in enumerate(map_data["enemies"]):
                        f.write('    {\n')
                        f.write(f'      "x": {enemy["x"]},\n')
                        f.write(f'      "y": {enemy["y"]},\n')
                        f.write(f'      "type": "{enemy["type"]}"\n')

                        if enemy_idx < len(map_data["enemies"]) - 1:
                            f.write('    },\n')
                        else:
                            f.write('    }\n')

                    f.write('  ]')

                # Add relation points if available in the map data
                if "relation_points" in map_data:
                    f.write(',\n  "relation_points": ')

                    # Get relation points from the current map data
                    relation_points = map_data["relation_points"]

                    # Update with any relation points from the play screen
                    if hasattr(play_screen, 'relation_handler') and play_screen.relation_handler.current_map:
                        current_map = play_screen.relation_handler.current_map
                        if current_map in play_screen.relation_handler.relation_points:
                            relation_points = play_screen.relation_handler.relation_points[current_map]

                    # Check if relation_points is empty
                    if not relation_points:
                        f.write('{}')  # Empty object
                    else:
                        # Check if it's in the new format with IDs
                        if any(isinstance(relation_points.get(key), dict) for key in relation_points):
                            # New format with IDs - use json.dumps with proper indentation
                            relation_str = json.dumps(relation_points, indent=4).replace('\n', '\n  ')
                            f.write(relation_str)
                        else:
                            # Old format without IDs - write manually
                            f.write('{\n')

                            # Write point A if available
                            if 'a' in relation_points:
                                f.write(f'    "a": [{relation_points["a"][0]}, {relation_points["a"][1]}]')

                                # Add comma if point B is also available
                                if 'b' in relation_points:
                                    f.write(',\n')
                                else:
                                    f.write('\n')

                            # Write point B if available
                            if 'b' in relation_points:
                                f.write(f'    "b": [{relation_points["b"][0]}, {relation_points["b"][1]}]\n')

                            f.write('  }')

                # Add game state data
                f.write(',\n  "game_state": {\n')

                # Write camera data
                f.write('    "camera": {\n')
                f.write(f'      "x": {game_state["camera"]["x"]},\n')
                f.write(f'      "y": {game_state["camera"]["y"]}\n')
                f.write('    },\n')

                # Write enemies data
                f.write('    "enemies": [\n')

                # Format each enemy
                for enemy_idx, enemy in enumerate(game_state["enemies"]):
                    f.write('      {\n')
                    f.write(f'        "type": "{enemy["type"]}",\n')
                    f.write('        "position": {\n')
                    f.write(f'          "x": {enemy["position"]["x"]},\n')
                    f.write(f'          "y": {enemy["position"]["y"]}\n')
                    f.write('        },\n')
                    f.write(f'        "direction": "{enemy["direction"]}",\n')
                    f.write(f'        "health": {enemy["health"]},\n')
                    f.write(f'        "state": "{enemy["state"]}"')

                    # Add float position if available
                    if "float_position" in enemy:
                        f.write(',\n')
                        f.write('        "float_position": {\n')
                        f.write(f'          "x": {enemy["float_position"]["x"]},\n')
                        f.write(f'          "y": {enemy["float_position"]["y"]}\n')
                        f.write('        }\n')
                    else:
                        f.write('\n')

                    if enemy_idx < len(game_state["enemies"]) - 1:
                        f.write('      },\n')
                    else:
                        f.write('      }\n')

                f.write('    ],\n')

                # Write inventory data
                f.write('    "inventory": [\n')

                # Format each inventory item
                for item_idx, item in enumerate(game_state["inventory"]):
                    f.write('      {\n')
                    f.write(f'        "slot": {item["slot"]},\n')
                    f.write(f'        "name": "{item["name"]}",\n')
                    f.write(f'        "count": {item["count"]}\n')

                    if item_idx < len(game_state["inventory"]) - 1:
                        f.write('      },\n')
                    else:
                        f.write('      }\n')

                f.write('    ],\n')

                # Write player inventory data
                f.write('    "player_inventory": [\n')

                # Format each player inventory item
                for item_idx, item in enumerate(game_state["player_inventory"]):
                    f.write('      {\n')
                    f.write(f'        "slot": {item["slot"]},\n')
                    f.write(f'        "name": "{item["name"]}",\n')
                    f.write(f'        "count": {item["count"]}\n')

                    if item_idx < len(game_state["player_inventory"]) - 1:
                        f.write('      },\n')
                    else:
                        f.write('      }\n')

                f.write('    ],\n')

                # Write collected keys data
                f.write('    "collected_keys": [\n')

                # Format each collected key position
                for key_idx, key_pos in enumerate(game_state["collected_keys"]):
                    f.write(f'      [{key_pos[0]}, {key_pos[1]}]')

                    if key_idx < len(game_state["collected_keys"]) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')

                f.write('    ],\n')

                # Write collected crystals data
                f.write('    "collected_crystals": [\n')

                # Format each collected crystal position
                for crystal_idx, crystal_pos in enumerate(game_state["collected_crystals"]):
                    f.write(f'      [{crystal_pos[0]}, {crystal_pos[1]}]')

                    if crystal_idx < len(game_state["collected_crystals"]) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')

                f.write('    ],\n')

                # Write opened lootchests data
                f.write('    "opened_lootchests": [\n')

                # Format each opened lootchest position
                for chest_idx, chest_pos in enumerate(game_state["opened_lootchests"]):
                    f.write(f'      [{chest_pos[0]}, {chest_pos[1]}]')

                    if chest_idx < len(game_state["opened_lootchests"]) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')

                f.write('    ],\n')

                # Write chest contents data
                f.write('    "chest_contents": {\n')

                # Format each chest's contents
                chest_positions = list(game_state["chest_contents"].keys())
                for pos_idx, pos_str in enumerate(chest_positions):
                    contents = game_state["chest_contents"][pos_str]

                    # Write position
                    f.write(f'      "{pos_str}": ')

                    # Check if we're using the new compact format (dictionary) or old format (list)
                    if isinstance(contents, dict):
                        # New compact format - dictionary with slot indices as keys
                        f.write('{\n')

                        # Get all slot indices
                        slot_indices = list(contents.keys())
                        for slot_idx, slot in enumerate(slot_indices):
                            item = contents[slot]

                            # Write slot index
                            f.write(f'        "{slot}": ')

                            # Convert item to JSON
                            item_json = json.dumps(item)
                            f.write(item_json)

                            if slot_idx < len(slot_indices) - 1:
                                f.write(',\n')
                            else:
                                f.write('\n')

                        f.write('      }')
                    else:
                        # Old format - list of items (possibly with nulls)
                        # Write contents as JSON array
                        if not contents:
                            f.write('[]')  # Empty array
                        else:
                            f.write('[\n')

                            # Format each item
                            for item_idx, item in enumerate(contents):
                                # Convert item to JSON
                                item_json = json.dumps(item, indent=8)
                                # Fix indentation (json.dumps adds too much)
                                item_json = item_json.replace('\n        ', '\n          ')

                                f.write(f'          {item_json}')

                                if item_idx < len(contents) - 1:
                                    f.write(',\n')
                                else:
                                    f.write('\n')

                            f.write('        ]')

                    if pos_idx < len(chest_positions) - 1:
                        f.write(',\n')
                    else:
                        f.write('\n')

                f.write('    }')

                f.write('\n  }')

                # Close the JSON object
                f.write('\n}')

            return True, None
        except Exception as e:
            return False, str(e)
