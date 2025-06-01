"""
World Manager - manages worlds and their metadata
"""
import os
import json
import pygame

class WorldManager:
    """Manages worlds and their metadata"""
    def __init__(self):
        self.worlds = {}  # Format: {folder_name: world_data}
        self.worlds_file = "SaveData/worlds.json"
        self.default_icon = None
        self.load_worlds()

    def load_worlds(self):
        """Load worlds from the worlds.json file in SaveData folder and scan for new folders"""
        try:
            # Dictionary to track existing worlds
            existing_worlds = {}

            # Check if the worlds file exists
            if os.path.exists(self.worlds_file):
                with open(self.worlds_file, 'r') as f:
                    data = json.load(f)

                # Process each world from the file
                for world in data.get("worlds", []):
                    folder_name = world.get("folder_name")
                    if folder_name:
                        # Check if this world has a main map
                        main_map_path = os.path.join("Maps", folder_name, f"{folder_name}.json")
                        world["has_main_map"] = os.path.exists(main_map_path)
                        existing_worlds[folder_name] = world

                print(f"Loaded {len(existing_worlds)} worlds from {self.worlds_file}")
            else:
                print(f"No worlds file found at {self.worlds_file}")

            # Now scan the Maps directory for any new folders
            maps_dir = "Maps"
            if os.path.exists(maps_dir) and os.path.isdir(maps_dir):
                # Get all folders in the Maps directory
                for folder_name in os.listdir(maps_dir):
                    folder_path = os.path.join(maps_dir, folder_name)
                    if os.path.isdir(folder_path):
                        # Check if this folder is already in our worlds list
                        if folder_name not in existing_worlds:
                            # Check if this folder has at least one map
                            has_maps = False
                            main_map_exists = False
                            main_map_path = os.path.join(folder_path, f"{folder_name}.json")

                            # Check if the main map exists (same name as folder)
                            if os.path.exists(main_map_path):
                                has_maps = True
                                main_map_exists = True
                            else:
                                # Check if there are any other maps in the folder
                                for file_name in os.listdir(folder_path):
                                    if file_name.endswith(".json"):
                                        has_maps = True
                                        break

                            if has_maps:
                                # Create a default world for this folder
                                display_name = folder_name.replace("_", " ").title()
                                existing_worlds[folder_name] = {
                                    "folder_name": folder_name,
                                    "display_name": display_name,
                                    "description": f"World located in {folder_name}",
                                    "icon": "",
                                    "has_main_map": main_map_exists
                                }
                                print(f"Added new world from folder: {folder_name}")

            # Clean up worlds that no longer have corresponding map folders
            worlds_to_remove = []
            for folder_name, world_data in existing_worlds.items():
                folder_path = os.path.join("Maps", folder_name)
                if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                    # Folder doesn't exist anymore, mark for removal
                    worlds_to_remove.append(folder_name)
                    print(f"Removing world '{folder_name}' - folder no longer exists")
                else:
                    # Check if folder has any map files
                    has_maps = False
                    for file_name in os.listdir(folder_path):
                        if file_name.endswith(".json"):
                            has_maps = True
                            break

                    if not has_maps:
                        # No map files in folder, mark for removal
                        worlds_to_remove.append(folder_name)
                        print(f"Removing world '{folder_name}' - no map files found")

            # Remove worlds that no longer exist
            for folder_name in worlds_to_remove:
                del existing_worlds[folder_name]

            # Clean up save data for deleted worlds
            if worlds_to_remove:
                self.cleanup_save_data_for_deleted_worlds(worlds_to_remove)

            # Update our worlds dictionary with all worlds (existing and new)
            self.worlds = existing_worlds

            # Also clean up any orphaned player location data that doesn't match existing worlds
            self.cleanup_orphaned_player_location_data()

            # If we found any worlds, save them to the worlds.json file in SaveData folder
            if self.worlds:
                self.save_worlds()
            else:
                # No worlds found - this is normal when no maps have been created yet
                print("No worlds found - waiting for user to create maps")

        except Exception as e:
            print(f"Error loading worlds: {e}")
            # Don't create default worlds - let the user create maps naturally

    def cleanup_save_data_for_deleted_worlds(self, deleted_worlds):
        """Clean up save data for worlds that have been deleted

        Args:
            deleted_worlds: List of world folder names that were deleted
        """
        try:
            # Clean up player location data
            self.cleanup_player_location_data(deleted_worlds)

            # Note: We intentionally keep global_collision_data.json as requested
            # Note: character_inventory.json is kept as it may contain items that can be used across worlds

        except Exception as e:
            print(f"Error cleaning up save data: {e}")

    def cleanup_player_location_data(self, deleted_worlds):
        """Remove player location data for deleted worlds

        Args:
            deleted_worlds: List of world folder names that were deleted
        """
        try:
            player_location_file = "SaveData/player_location.json"

            if os.path.exists(player_location_file):
                with open(player_location_file, 'r') as f:
                    player_data = json.load(f)

                # Check if we have the new format with multiple worlds
                if isinstance(player_data, dict) and "worlds" in player_data:
                    # Remove data for deleted worlds
                    worlds_data = player_data["worlds"]
                    for world_name in deleted_worlds:
                        if world_name in worlds_data:
                            del worlds_data[world_name]
                            print(f"Cleaned up player location data for deleted world: {world_name}")

                    # If current_world was deleted, reset to first available world or None
                    current_world = player_data.get("current_world")
                    if current_world in deleted_worlds:
                        if worlds_data:
                            # Set to first available world
                            player_data["current_world"] = list(worlds_data.keys())[0]
                            print(f"Reset current world from '{current_world}' to '{player_data['current_world']}'")
                        else:
                            # No worlds left, reset to default
                            player_data["current_world"] = "main"
                            print(f"Reset current world to 'main' (no worlds available)")

                    # Save the cleaned data
                    with open(player_location_file, 'w') as f:
                        json.dump(player_data, f, indent=2)

                else:
                    # Old format - check if the deleted world matches the saved location
                    folder_name = player_data.get("folder_name")
                    if folder_name in deleted_worlds:
                        # Reset to default location
                        default_location = {
                            "map_name": "",
                            "x": 0,
                            "y": 0,
                            "direction": "down",
                            "health": 100,
                            "shield_durability": 3,
                            "folder_name": "main"
                        }
                        with open(player_location_file, 'w') as f:
                            json.dump(default_location, f, indent=2)
                        print(f"Reset player location data (old format) for deleted world: {folder_name}")

        except Exception as e:
            print(f"Error cleaning up player location data: {e}")

    def cleanup_orphaned_player_location_data(self):
        """Clean up player location data for worlds that no longer exist"""
        try:
            player_location_file = "SaveData/player_location.json"

            if os.path.exists(player_location_file):
                with open(player_location_file, 'r') as f:
                    player_data = json.load(f)

                # Check if we have the new format with multiple worlds
                if isinstance(player_data, dict) and "worlds" in player_data:
                    worlds_data = player_data["worlds"]
                    orphaned_worlds = []

                    # Check each world in player location data
                    for world_name in list(worlds_data.keys()):
                        world_folder_path = os.path.join("Maps", world_name)
                        if not os.path.exists(world_folder_path) or not os.path.isdir(world_folder_path):
                            # World folder doesn't exist
                            orphaned_worlds.append(world_name)
                        else:
                            # Check if world folder has any map files
                            has_maps = False
                            for file_name in os.listdir(world_folder_path):
                                if file_name.endswith(".json"):
                                    has_maps = True
                                    break
                            if not has_maps:
                                orphaned_worlds.append(world_name)

                    # Remove orphaned world data
                    for world_name in orphaned_worlds:
                        if world_name in worlds_data:
                            del worlds_data[world_name]
                            print(f"Cleaned up orphaned player location data for world: {world_name}")

                    # If current_world was orphaned, reset to first available world or default
                    current_world = player_data.get("current_world")
                    if current_world in orphaned_worlds:
                        if worlds_data:
                            # Set to first available world
                            player_data["current_world"] = list(worlds_data.keys())[0]
                            print(f"Reset current world from orphaned '{current_world}' to '{player_data['current_world']}'")
                        else:
                            # No worlds left, reset to default
                            player_data["current_world"] = "main"
                            print(f"Reset current world to 'main' (no valid worlds available)")

                    # If we removed any orphaned data, save the cleaned file
                    if orphaned_worlds:
                        with open(player_location_file, 'w') as f:
                            json.dump(player_data, f, indent=2)

                        # If no worlds left, delete the file to start fresh
                        if not worlds_data:
                            os.remove(player_location_file)
                            print("Removed empty player location file")

        except Exception as e:
            print(f"Error cleaning up orphaned player location data: {e}")

    def create_default_worlds(self):
        """Create default worlds based on folders in Maps directory"""
        try:
            # Create a default "main" world if no worlds exist
            self.worlds = {
                "main": {
                    "folder_name": "main",
                    "display_name": "Main World",
                    "description": "The main world of the game",
                    "icon": "world_icons/main.png",
                    "has_main_map": False
                }
            }

            # Create the Maps/main directory if it doesn't exist
            main_dir = os.path.join("Maps", "main")
            if not os.path.exists(main_dir):
                os.makedirs(main_dir, exist_ok=True)
                print(f"Created default 'main' directory at {main_dir}")

            print(f"Created default 'main' world")

            # Save the default worlds to the worlds.json file in SaveData folder
            self.save_worlds()
        except Exception as e:
            print(f"Error creating default worlds: {e}")

    def save_worlds(self):
        """Save worlds to the worlds.json file in SaveData folder"""
        try:
            # Convert worlds dictionary to list
            worlds_list = list(self.worlds.values())

            # Create the data structure
            data = {
                "worlds": worlds_list
            }

            # Save to file
            with open(self.worlds_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Saved {len(worlds_list)} worlds to {self.worlds_file}")
            return True
        except Exception as e:
            print(f"Error saving worlds: {e}")
            return False

    def get_world(self, folder_name):
        """Get world data for a specific folder

        Args:
            folder_name: Name of the folder

        Returns:
            World data dictionary if found, None otherwise
        """
        return self.worlds.get(folder_name)

    def get_all_worlds(self):
        """Get all worlds

        Returns:
            List of world data dictionaries
        """
        return list(self.worlds.values())

    def load_world_icon(self, world):
        """Load the icon for a world

        Args:
            world: World data dictionary

        Returns:
            Pygame surface with the icon, or default icon if not found
        """
        icon_path = world.get("icon", "")

        # Try to load the icon
        if icon_path and os.path.exists(icon_path):
            try:
                return pygame.image.load(icon_path).convert_alpha()
            except Exception as e:
                print(f"Error loading world icon {icon_path}: {e}")

        # Use default icon if no icon found or error loading
        if self.default_icon is None:
            # Create a default icon (colored rectangle)
            self.default_icon = pygame.Surface((64, 64), pygame.SRCALPHA)
            self.default_icon.fill((100, 150, 200))

            # Add a border
            pygame.draw.rect(self.default_icon, (50, 100, 150), pygame.Rect(0, 0, 64, 64), 2)

            # Add some decoration
            pygame.draw.circle(self.default_icon, (150, 200, 250), (32, 32), 16)

        return self.default_icon
