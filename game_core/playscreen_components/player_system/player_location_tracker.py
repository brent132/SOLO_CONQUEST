"""
Player Location Tracker - Tracks player locations across multiple worlds
"""
import os
import json

class PlayerLocationTracker:
    """Tracks player locations across multiple worlds"""
    def __init__(self):
        # Default location structure for a single world
        self.default_location = {
            "map_name": "",
            "x": 0,
            "y": 0,
            "direction": "down",
            "health": 100,
            "shield_durability": 3
        }

        # Store locations for all worlds - each world stores one location that gets updated
        # Structure: {world_name: location_data}
        self.world_locations = {}

        # Track the current/latest world and location
        self.current_world = "main"
        self.latest_location = self.default_location.copy()

        self.save_path = "SaveData/player_location.json"
        self.load_location()

    def _determine_folder_name(self, map_name):
        """Determine which folder/world a map belongs to

        Args:
            map_name: Name of the map

        Returns:
            String: The folder name that contains this map
        """
        # Check if map_name contains a folder path
        if "/" in map_name:
            parts = map_name.split("/")
            return parts[0]
        elif "\\" in map_name:
            parts = map_name.split("\\")
            return parts[0]
        else:
            # Try to find the folder by looking in Maps directory
            maps_dir = "Maps"
            if os.path.exists(maps_dir):
                # First check if it's a main map (has its own folder with same name)
                main_map_path = os.path.join(maps_dir, map_name, f"{map_name}.json")
                if os.path.exists(main_map_path):
                    return map_name

                # If not a main map, search in all folders for this map
                for folder in os.listdir(maps_dir):
                    folder_path = os.path.join(maps_dir, folder)
                    if os.path.isdir(folder_path):
                        map_path = os.path.join(folder_path, f"{map_name}.json")
                        if os.path.exists(map_path):
                            return folder

            # If still no folder name found, use "main" as default
            return "main"

    def save_location(self, map_name, x, y, direction="down", health=100, shield_durability=3, folder_name=None):
        """Save player location for a specific world

        Args:
            map_name: Name of the map
            x: X position
            y: Y position
            direction: Player direction (default: "down")
            health: Player health (default: 100)
            shield_durability: Shield durability (default: 3)
            folder_name: Name of the folder containing the map (default: None, will be auto-determined)
        """
        # Determine folder name if not provided
        if folder_name is None:
            folder_name = self._determine_folder_name(map_name)

        # Create location data for this world (includes current map name)
        location_data = {
            "map_name": map_name,
            "x": x,
            "y": y,
            "direction": direction,
            "health": health,
            "shield_durability": shield_durability
        }

        # Update the world location (one location per world)
        self.world_locations[folder_name] = location_data

        # Update current world and latest location
        self.current_world = folder_name
        self.latest_location = location_data.copy()

        # Save to file
        self.save_to_file()

    def get_latest_location(self):
        """Get the latest player location

        Returns:
            Dictionary with map_name, x, y, direction, health, shield_durability, and folder_name
        """
        # For backward compatibility, include folder_name in the returned data
        result = self.latest_location.copy()
        result["folder_name"] = self.current_world
        return result

    def get_world_location(self, folder_name):
        """Get player location for a specific world

        Args:
            folder_name: Name of the world folder

        Returns:
            Dictionary with location data if found, None otherwise
        """
        return self.world_locations.get(folder_name)

    def get_location_for_world(self, map_name, world_name):
        """Get player location for a specific map in a specific world

        Args:
            map_name: Name of the map
            world_name: Name of the world/folder

        Returns:
            Dictionary with x, y, direction if found, None otherwise
        """
        if world_name in self.world_locations:
            location = self.world_locations[world_name]
            # Return the location regardless of map name (since each world has one location)
            return {
                "x": location["x"],
                "y": location["y"],
                "direction": location["direction"]
            }
        return None

    def get_location(self, map_name):
        """Get player location for a specific map (for backward compatibility)

        Args:
            map_name: Name of the map

        Returns:
            Dictionary with x, y, direction if found, None otherwise
        """
        # First check if it's the latest location
        if self.latest_location.get("map_name") == map_name:
            return {
                "x": self.latest_location["x"],
                "y": self.latest_location["y"],
                "direction": self.latest_location["direction"]
            }

        # Try to find the map in any world (for backward compatibility)
        for world_name, location in self.world_locations.items():
            if location.get("map_name") == map_name:
                return {
                    "x": location["x"],
                    "y": location["y"],
                    "direction": location["direction"]
                }

        return None

    def has_location(self, map_name):
        """Check if a location exists for a specific map

        Args:
            map_name: Name of the map

        Returns:
            True if location exists for this map, False otherwise
        """
        if self.latest_location.get("map_name") == map_name:
            return True

        # Try to find the map in any world
        for world_name, location in self.world_locations.items():
            if location.get("map_name") == map_name:
                return True

        return False

    def save_to_file(self):
        """Save all world locations to file"""
        try:
            # Create the data structure to save
            data = {
                "current_world": self.current_world,
                "worlds": self.world_locations
            }

            with open(self.save_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving player location: {e}")
            return False

    def load_location(self):
        """Load world locations from file"""
        try:
            if os.path.exists(self.save_path):
                with open(self.save_path, 'r') as f:
                    data = json.load(f)

                # Check if this is the new format with multiple worlds
                if isinstance(data, dict) and "worlds" in data:
                    self.world_locations = data["worlds"]
                    self.current_world = data.get("current_world", "main")

                    # Set latest location to the current world's location
                    if self.current_world in self.world_locations:
                        self.latest_location = self.world_locations[self.current_world].copy()
                    else:
                        # If current world not found, use default
                        self.latest_location = self.default_location.copy()

                # Handle old format (backward compatibility)
                else:
                    # Convert old format to new format
                    folder_name = data.get("folder_name", "main")

                    # Create location data with map_name included
                    location_data = {
                        "map_name": data.get("map_name", ""),
                        "x": data.get("x", 0),
                        "y": data.get("y", 0),
                        "direction": data.get("direction", "down"),
                        "health": data.get("health", 100),
                        "shield_durability": data.get("shield_durability", 3)
                    }

                    # Update structures in new format
                    self.world_locations[folder_name] = location_data
                    self.current_world = folder_name
                    self.latest_location = location_data.copy()

                    # Save in new format
                    self.save_to_file()

                print(f"Loaded player locations for {len(self.world_locations)} worlds")
            else:
                print("No player location file found, starting with default location")
        except Exception as e:
            print(f"Error loading player location: {e}")
            # Keep default values
