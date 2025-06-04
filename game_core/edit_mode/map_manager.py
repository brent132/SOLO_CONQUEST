"""
Map Manager - handles loading, listing, and deleting maps
"""
import os
import json
import pygame
from edit_mode.ui_components import Button

class MapListItem:
    """Button-like item for a map in the list"""
    def __init__(self, x, y, width, height, map_name, font_size=24, is_entrance=False, main_map=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.map_name = map_name
        self.font = pygame.font.SysFont(None, font_size)
        self.is_entrance = is_entrance
        self.main_map = main_map

        # Use different text color for entrance maps
        text_color = (0, 100, 150) if is_entrance else (0, 0, 0)

        # Add indent for entrance maps
        indent = 20 if is_entrance else 0
        self.text_surf = self.font.render(map_name, True, text_color)
        self.text_rect = self.text_surf.get_rect(midleft=(self.rect.x + 10 + indent, self.rect.centery))

        self.is_hovered = False
        self.is_selected = False

    def update(self, mouse_pos):
        """Update button state based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface):
        """Draw the map list item"""
        # Draw background
        if self.is_selected:
            color = (180, 200, 255)  # Blue when selected
        elif self.is_hovered:
            color = (220, 220, 220)  # Light gray when hovered
        else:
            color = (240, 240, 240)  # Very light gray normally
        pygame.draw.rect(surface, color, self.rect)

        # Draw border
        border_color = (100, 150, 255) if self.is_selected else (200, 200, 200)
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Draw text
        surface.blit(self.text_surf, self.text_rect)

    def is_clicked(self, event):
        """Check if item was clicked"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False

class MapManager:
    """Manages map operations: loading, listing, deleting"""
    def __init__(self, sidebar_width, map_area_width):
        self.sidebar_width = sidebar_width
        self.map_area_width = map_area_width
        self.maps_dir = "Maps"
        self.map_list = []
        self.map_items = []
        self.selected_map = None
        self.status_message = ""
        self.status_timer = 0

        # Create Maps directory if it doesn't exist
        os.makedirs(self.maps_dir, exist_ok=True)

        # Load map list
        self.refresh_map_list()

        # Action buttons
        self.edit_button = Button(0, 0, "edit_mode", scale=0.7)
        self.delete_button = Button(0, 0, "delete", scale=0.7)
        self.cancel_button = Button(0, 0, "cancel", scale=0.7)

    def refresh_map_list(self):
        """Refresh the list of available maps"""
        self.map_list = []

        # Check if directory exists
        if not os.path.exists(self.maps_dir):
            return

        # Get all folders in the Maps directory
        for folder_name in os.listdir(self.maps_dir):
            folder_path = os.path.join(self.maps_dir, folder_name)

            # Skip if not a directory
            if not os.path.isdir(folder_path):
                continue

            # Look for a map file in this folder
            map_file_path = os.path.join(folder_path, f"{folder_name}.json")

            if os.path.exists(map_file_path):
                self.map_list.append(folder_name)

        # Sort alphabetically
        self.map_list.sort()

    def position_map_items(self, start_x, start_y, width, max_height):
        """Position map items in the sidebar"""
        self.map_items = []

        item_height = 40
        spacing = 5
        current_y = start_y

        for map_name in self.map_list:
            # Stop if we're going beyond the available height
            if current_y + item_height > start_y + max_height:
                break

            # Add the main map item
            self.map_items.append(MapListItem(start_x, current_y, width, item_height, map_name))
            current_y += item_height + spacing

            # Get entrance maps for this main map
            entrance_maps = self.get_entrance_maps(map_name)

            # Add entrance map items
            for entrance_name in entrance_maps:
                # Stop if we're going beyond the available height
                if current_y + item_height > start_y + max_height:
                    break

                # Add the entrance map item
                self.map_items.append(MapListItem(
                    start_x,
                    current_y,
                    width,
                    item_height,
                    entrance_name,
                    is_entrance=True,
                    main_map=map_name
                ))
                current_y += item_height + spacing

        # Position action buttons
        button_y = start_y + max_height + 20
        self.edit_button.rect.topleft = (start_x, button_y)
        self.delete_button.rect.topleft = (start_x + 90, button_y)
        self.cancel_button.rect.topleft = (start_x + 180, button_y)

    def handle_event(self, event, mouse_pos):
        """Handle events for the map browser"""
        # Update map items
        for item in self.map_items:
            item.update(mouse_pos)

        # Update action buttons
        self.edit_button.update(mouse_pos)
        self.delete_button.update(mouse_pos)
        self.cancel_button.update(mouse_pos)

        # Handle clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check map item clicks
            for item in self.map_items:
                if item.is_clicked(event):
                    # Deselect all items
                    for other_item in self.map_items:
                        other_item.is_selected = False

                    # Select this item
                    item.is_selected = True
                    self.selected_map = item.map_name
                    return None

            # Check action button clicks
            if self.selected_map:
                if self.edit_button.is_clicked(event):
                    # Find the selected item to determine if it's an entrance map
                    for item in self.map_items:
                        if item.is_selected:
                            if item.is_entrance:
                                # It's an entrance map, load it with the main map name
                                return {"action": "edit", "map": item.main_map, "entrance": item.map_name}
                            else:
                                # It's a main map
                                return {"action": "edit", "map": self.selected_map}

                    # Fallback if no item is found
                    return {"action": "edit", "map": self.selected_map}

                if self.delete_button.is_clicked(event):
                    # Find the selected item to determine if it's an entrance map
                    for item in self.map_items:
                        if item.is_selected:
                            if item.is_entrance:
                                # Delete just the entrance map file
                                self.delete_entrance_map(item.main_map, item.map_name)
                            else:
                                # Delete the entire map folder
                                self.delete_map(self.selected_map)
                            return {"action": "refresh"}

            if self.cancel_button.is_clicked(event):
                return {"action": "cancel"}

        return None

    def delete_entrance_map(self, main_map_name, entrance_name):
        """Delete an entrance map file

        Args:
            main_map_name: Name of the main map
            entrance_name: Name of the entrance map to delete
        """
        file_path = os.path.join(self.maps_dir, main_map_name, f"{entrance_name}.json")

        try:
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                self.status_message = f"Entrance map '{entrance_name}' deleted"
                self.status_timer = 180

                # Refresh map list
                self.refresh_map_list()

                # Clear selection if the deleted map was selected
                if self.selected_map == entrance_name:
                    self.selected_map = None

                # Reposition items with the updated list
                self.position_map_items(
                    self.map_area_width + 20,
                    120,
                    self.sidebar_width - 40,
                    300
                )
            else:
                self.status_message = f"Error: Entrance map file not found"
                self.status_timer = 180
        except Exception as e:
            self.status_message = f"Error deleting entrance map: {str(e)}"
            self.status_timer = 180

    def delete_map(self, map_name):
        """Delete a map folder and all its contents"""
        folder_path = os.path.join(self.maps_dir, map_name)

        try:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                # Delete all files in the folder
                for filename in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)

                # Delete the folder itself
                os.rmdir(folder_path)
                self.status_message = f"Map folder '{map_name}' deleted"
                self.status_timer = 180

                # Refresh map list
                self.refresh_map_list()

                # Clear selection if the deleted map was selected
                if self.selected_map == map_name:
                    self.selected_map = None

                # Reposition items with the updated list
                self.position_map_items(
                    self.map_area_width + 20,
                    120,
                    self.sidebar_width - 40,
                    300
                )
            else:
                self.status_message = f"Error: Map folder not found"
                self.status_timer = 180
        except Exception as e:
            self.status_message = f"Error deleting map: {str(e)}"
            self.status_timer = 180

    def get_entrance_maps(self, main_map_name):
        """Get a list of entrance maps for a main map

        Args:
            main_map_name: Name of the main map

        Returns:
            List of entrance map names
        """
        entrance_maps = []
        folder_path = os.path.join(self.maps_dir, main_map_name)

        # Check if folder exists
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return entrance_maps

        # Get all JSON files in the folder
        for filename in os.listdir(folder_path):
            # Skip the main map file
            if filename == f"{main_map_name}.json":
                continue

            # Check if it's a JSON file
            if filename.endswith('.json'):
                entrance_name = filename[:-5]  # Remove .json extension
                entrance_maps.append(entrance_name)

        return entrance_maps

    def load_map(self, map_name, entrance_name=None):
        """Load a map from file

        Args:
            map_name: Name of the main map
            entrance_name: Optional name of an entrance map to load

        Returns:
            Map data in editor format
        """
        if entrance_name:
            # Load an entrance map
            file_path = os.path.join(self.maps_dir, map_name, f"{entrance_name}.json")
        else:
            # Load the main map
            file_path = os.path.join(self.maps_dir, map_name, f"{map_name}.json")

        try:
            with open(file_path, 'r') as f:
                map_data = json.load(f)

            # Check which format the map is in
            if "layers" in map_data and "tile_mapping" in map_data:
                # New layered format - convert to editor format
                converted_map_data = self.convert_layered_to_editor_format(map_data)
                return converted_map_data
            elif "map_data" in map_data and "tile_mapping" in map_data:
                # Single-layer array format - convert to editor format
                converted_map_data = self.convert_array_to_editor_format(map_data)
                return converted_map_data
            else:
                # Old direct format, return as is
                return map_data
        except Exception as e:
            self.status_message = f"Error loading map: {str(e)}"
            self.status_timer = 180
            return None

    def convert_layered_to_editor_format(self, layered_map_data):
        """Convert layered map data to the format expected by the editor"""
        # Create a new map data structure
        editor_map_data = {
            "name": layered_map_data["name"],
            "width": layered_map_data["width"],
            "height": layered_map_data["height"],
            "tile_size": layered_map_data["tile_size"],
            "layers": []
        }

        # Include collision data if available
        if "collision_data" in layered_map_data:
            editor_map_data["collision_data"] = layered_map_data["collision_data"]

        # Include relation points if available
        if "relation_points" in layered_map_data:
            editor_map_data["relation_points"] = layered_map_data["relation_points"]
            pass  # Included relation points in editor format

        # Get the tile mapping
        tile_mapping = layered_map_data["tile_mapping"]

        # Expand any loop patterns in the tile mapping
        expanded_mapping = self._expand_tile_mapping(tile_mapping)

        # Process each layer
        for layer_data in layered_map_data["layers"]:
            layer_tiles = {}

            # Convert the 2D array to the editor format for this layer
            for y, row in enumerate(layer_data["map_data"]):
                for x, tile_id in enumerate(row):
                    if tile_id != -1:  # Skip empty tiles
                        # Get the tile path from the expanded mapping
                        tile_info = expanded_mapping.get(str(tile_id))
                        if tile_info:
                            key = f"{x},{y}"
                            layer_tiles[key] = {
                                "source_path": tile_info["path"],
                                "position": [x, y],
                                "tileset": tile_info["tileset"]
                            }

            # Add the layer to the editor data
            editor_layer = {
                "tiles": layer_tiles,
                "visible": layer_data.get("visible", True)
            }
            editor_map_data["layers"].append(editor_layer)

        return editor_map_data

    def _expand_tile_mapping(self, tile_mapping):
        """Helper method to expand tile mapping patterns"""
        expanded_mapping = {}

        # Process the tile mapping to handle loop patterns
        for key, value in tile_mapping.items():
            if isinstance(value, dict) and value.get("type") == "loop":
                # This is a loop pattern
                start_id = value["start_id"]
                count = value["count"]
                pattern = value["pattern"]

                # Generate all the paths from the pattern
                for i in range(count):
                    tile_id = start_id + i
                    number = pattern["start"] + i
                    path = f"{pattern['prefix']}{number:0{pattern['digits']}d}{pattern['suffix']}"

                    expanded_mapping[str(tile_id)] = {
                        "path": path,
                        "tileset": int(key.split('_')[1]) if key.startswith('tileset_') else 0
                    }
            else:
                # This is a regular mapping
                expanded_mapping[key] = value

        return expanded_mapping

    def convert_array_to_editor_format(self, array_map_data):
        """Convert array-based map data to the format expected by the editor"""
        # Create a new map data structure
        editor_map_data = {
            "name": array_map_data["name"],
            "width": array_map_data["width"],
            "height": array_map_data["height"],
            "tile_size": array_map_data["tile_size"],
            "tiles": {}
        }

        # Include collision data if available
        if "collision_data" in array_map_data:
            editor_map_data["collision_data"] = array_map_data["collision_data"]

        # Include relation points if available
        if "relation_points" in array_map_data:
            editor_map_data["relation_points"] = array_map_data["relation_points"]
            pass  # Included relation points in editor format

        # Get the tile mapping
        tile_mapping = array_map_data["tile_mapping"]

        # Expand any loop patterns in the tile mapping
        expanded_mapping = self._expand_tile_mapping(tile_mapping)

        # Convert the 2D array to the editor format
        for y, row in enumerate(array_map_data["map_data"]):
            for x, tile_id in enumerate(row):
                if tile_id != -1:  # Skip empty tiles
                    # Get the tile path from the expanded mapping
                    tile_info = expanded_mapping.get(str(tile_id))
                    if tile_info:
                        key = f"{x},{y}"
                        editor_map_data["tiles"][key] = {
                            "source_path": tile_info["path"],
                            "position": [x, y],
                            "tileset": tile_info["tileset"]
                        }

        return editor_map_data

    def get_main_map_folders(self):
        """Get a list of all main map folders

        Returns:
            List of main map folder names
        """
        # Refresh the map list to ensure it's up to date
        self.refresh_map_list()

        # Return the list of main maps
        return self.map_list

    def update(self):
        """Update status message timer"""
        if self.status_timer > 0:
            self.status_timer -= 1

    def draw(self, surface, font):
        """Draw the map browser"""
        # Draw title
        title = font.render("Map Browser", True, (50, 50, 50))
        title_rect = title.get_rect(topleft=(self.map_area_width + 20, 60))
        surface.blit(title, title_rect)

        # Draw map items
        for item in self.map_items:
            item.draw(surface)

        # Draw action buttons (only if a map is selected)
        if self.selected_map:
            self.edit_button.draw(surface)
            self.delete_button.draw(surface)

        self.cancel_button.draw(surface)

        # Draw status message
        if self.status_timer > 0:
            status_color = (0, 150, 0) if "Error" not in self.status_message else (200, 0, 0)
            status_text = font.render(self.status_message, True, status_color)
            status_rect = status_text.get_rect(topleft=(self.map_area_width + 20, 500))
            surface.blit(status_text, status_rect)
