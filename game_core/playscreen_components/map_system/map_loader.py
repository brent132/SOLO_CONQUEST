"""
Map Loader - Handles loading and parsing map files

Extracted from PlayScreen to handle all map file loading operations.

RESPONSIBILITY: Loading and parsing map files from disk

FEATURES:
- Finds map files in the Maps directory structure
- Handles both main maps and related maps
- Loads and parses JSON map data
- Provides detailed error handling and debugging

This component is responsible for all file system operations related to maps,
including discovering map files, loading them from disk, and parsing the JSON data.
It handles the complex directory structure where maps can be either main maps
(in their own folders) or related maps (in other map folders).
"""
import os
import json
from typing import Dict, Any, Optional, Tuple


class MapLoader:
    """Handles loading and parsing map files from disk"""
    
    def __init__(self):
        self.current_dir = os.getcwd()
        self.maps_dir = self._find_maps_directory()
    
    def _find_maps_directory(self) -> str:
        """Find the Maps directory relative to current working directory"""
        current_dir = self.current_dir
        
        # Try to find the Maps directory
        # First check if Maps is in the current directory
        if os.path.exists(os.path.join(current_dir, "Maps")):
            return os.path.join(current_dir, "Maps")
        # Then check if Maps is in the parent directory
        elif os.path.exists(os.path.join(current_dir, "..", "Maps")):
            return os.path.join(current_dir, "..", "Maps")
        # Then check if Maps is in the grandparent directory
        elif os.path.exists(os.path.join(current_dir, "..", "..", "Maps")):
            return os.path.join(current_dir, "..", "..", "Maps")
        else:
            # Default to the relative path
            return "Maps"
    
    def find_map_file(self, map_name: str) -> Optional[str]:
        """
        Find the map file for the given map name.
        
        Args:
            map_name (str): Name of the map to find
            
        Returns:
            Optional[str]: Path to the map file, or None if not found
        """
        # First check if it's a main map
        main_map_path = os.path.join(self.maps_dir, map_name, f"{map_name}.json")
        pass  # DEBUG: Requested map name
        pass  # DEBUG: Checking for main map file
        
        if os.path.exists(main_map_path):
            pass  # DEBUG: Found main map file
            return main_map_path
        
        # It might be a related map, search in all map folders
        pass  # DEBUG: Not a main map, searching in folders
        
        # Check if Maps directory exists
        if not os.path.exists(self.maps_dir):
            pass  # Maps directory does not exist
            return None
        
        pass  # Maps directory exists
        
        # List all folders in the Maps directory
        try:
            folders = [f for f in os.listdir(self.maps_dir) 
                      if os.path.isdir(os.path.join(self.maps_dir, f))]
            pass  # Found folders in Maps directory
            
            for folder_name in folders:
                folder_path = os.path.join(self.maps_dir, folder_name)
                pass  # Checking folder
                
                # List all files in this folder
                files = [f for f in os.listdir(folder_path) 
                        if os.path.isfile(os.path.join(folder_path, f))]
                pass  # Files in folder
                
                # Check if this folder contains our map
                related_map_path = os.path.join(folder_path, f"{map_name}.json")
                pass  # Checking for related map file
                
                if os.path.exists(related_map_path):
                    pass  # Found related map file
                    return related_map_path
                    
        except Exception as e:
            pass  # Error searching for map files
            return None
        
        return None
    
    def load_map_data(self, map_name: str) -> Tuple[bool, Optional[Dict[Any, Any]], str]:
        """
        Load map data from file.
        
        Args:
            map_name (str): Name of the map to load
            
        Returns:
            Tuple[bool, Optional[Dict], str]: (success, map_data, error_message)
        """
        try:
            # Find the map file
            map_path = self.find_map_file(map_name)
            if not map_path:
                return False, None, f"Map file not found: {map_name}"
            
            pass  # DEBUG: Final map path being loaded
            pass  # Loading map data
            
            # Load map data
            with open(map_path, 'r') as f:
                map_data = json.load(f)
            
            pass  # DEBUG: Loaded map data
            pass  # DEBUG: Map dimensions
            
            return True, map_data, ""
            
        except FileNotFoundError:
            error_msg = f"Map file not found: {map_name}"
            pass  # ERROR: Map file not found
            return False, None, error_msg
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in map file {map_name}: {str(e)}"
            pass  # ERROR: Invalid JSON
            return False, None, error_msg
            
        except Exception as e:
            error_msg = f"Error loading map {map_name}: {str(e)}"
            pass  # ERROR: Error loading map
            return False, None, error_msg
    
    def get_map_info(self, map_data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Extract basic map information from map data.
        
        Args:
            map_data (Dict): The loaded map data
            
        Returns:
            Dict[str, Any]: Map information including dimensions, format, etc.
        """
        info = {
            'name': map_data.get('name', 'Unknown'),
            'width': map_data.get('width', 0),
            'height': map_data.get('height', 0),
            'has_layers': 'layers' in map_data and 'tile_mapping' in map_data,
            'has_single_layer': 'map_data' in map_data and 'tile_mapping' in map_data,
            'is_old_format': not ('layers' in map_data or 'map_data' in map_data),
            'has_collision_data': 'collision_data' in map_data,
            'has_relation_points': 'relation_points' in map_data,
            'has_game_state': 'game_state' in map_data,
            'has_player_start': 'player_start' in map_data,
            'has_enemies': 'enemies' in map_data
        }
        
        return info
