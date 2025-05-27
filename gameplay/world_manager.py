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
        self.worlds_file = "C:/Users/BR3NT3/Music/TEST/SaveData/worlds.json"
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

            # Update our worlds dictionary with all worlds (existing and new)
            self.worlds = existing_worlds

            # If we found any worlds, save them to the worlds.json file in SaveData folder
            if self.worlds:
                self.save_worlds()
            else:
                # If no worlds were found, create default worlds
                self.create_default_worlds()

        except Exception as e:
            print(f"Error loading worlds: {e}")
            # Create default worlds based on folders in Maps directory
            self.create_default_worlds()

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
