"""
Main Editor class - integrates all components of the edit mode
"""
import pygame
import os
import json
from config import *
from edit_mode.ui_components import SaveButton, TextInput, ScrollableTextArea
from edit_mode.tileset_manager import TilesetManager
from edit_mode.map_saver import MapSaver
from edit_mode.map_manager import MapManager
from edit_mode.layer_manager import LayerManager
from edit_mode.tab_manager import TabManager
from edit_mode.collision_manager import CollisionManager
from edit_mode.brush_manager import BrushManager
from edit_mode.edit_screen_ui import EditScreenUI

from base_screen import BaseScreen

class EditScreen(BaseScreen):
    """Edit mode screen with grid and tileset selection"""
    def __init__(self, width, height):
        # Initialize the base screen
        super().__init__(width, height)

        # Grid settings
        self.base_grid_cell_size = 16  # Base 16x16 grid cells
        self.grid_cell_size = 16  # Current grid cell size (affected by zoom)

        # Zoom settings - limited to 100% minimum
        self.zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0]
        self.current_zoom_index = 0  # Start at 1.0x zoom (index 0)
        self.zoom_factor = self.zoom_levels[self.current_zoom_index]

        # Sidebar settings
        self.sidebar_width = 500  # Increased width to show full tileset at 1.5x scale

        # Map area (main editing area)
        self.map_area_width = self.width - self.sidebar_width
        self.map_area_height = self.height

        # Current selected tile and tileset
        self.selected_tile = None
        self.selected_tileset_index = 0

        # Mouse cursor position for tile preview
        self.mouse_pos = (0, 0)
        self.show_tile_preview = True

        # Initialize tileset manager
        self.tileset_manager = TilesetManager(
            self.sidebar_width,
            self.map_area_width,
            self.grid_cell_size
        )

        # Position the tileset buttons
        self.tileset_manager.position_tileset_buttons(self.selected_tileset_index)

        # Map data (initialize empty with layers)
        self.map_data = {}  # Will store {layer: {(x, y): tile_info}} for placed tiles

        # Initialize tab manager
        self.tab_manager = TabManager(self.map_area_width, self.sidebar_width)

        # Initialize layer manager
        self.layer_manager = LayerManager(self.sidebar_width)
        self.layer_manager.create_ui(self.map_area_width, self.height)

        # Initialize collision manager
        self.collision_manager = CollisionManager()

        # Initialize brush manager
        self.brush_manager = BrushManager()
        self.brush_manager.create_ui(self.map_area_width, self.sidebar_width, 150)

        # Entrance manager removed

        # Initialize map data for each layer
        for i in range(self.layer_manager.max_layers):
            self.map_data[i] = {}

        # Camera/viewport for large maps
        self.camera_x = 0
        self.camera_y = 0

        # Camera movement settings
        self.camera_speed = self.base_grid_cell_size * 0.5  # Base speed (pixels per update) - reduced by half
        self.camera_acceleration = 0.1  # How quickly the camera speeds up when key is held - reduced
        self.camera_max_speed = self.base_grid_cell_size * 1.5  # Maximum camera speed - reduced

        # Key state tracking for smooth camera movement
        self.keys_pressed = {
            pygame.K_w: False,
            pygame.K_a: False,
            pygame.K_s: False,
            pygame.K_d: False,
            pygame.K_UP: False,
            pygame.K_LEFT: False,
            pygame.K_DOWN: False,
            pygame.K_RIGHT: False
        }

        # Key press duration tracking
        self.key_press_time = {k: 0 for k in self.keys_pressed}
        self.current_camera_speed = {k: self.camera_speed for k in self.keys_pressed}

        # Drag placement state
        self.is_dragging = False
        self.drag_button = 0  # 1 = left click (place), 3 = right click (erase)
        self.last_drag_pos = None  # Last grid position where a tile was placed/erased

        # Initialize map saver and manager
        self.map_saver = MapSaver()
        self.map_manager = MapManager(self.sidebar_width, self.map_area_width)

        # Save functionality
        self.map_name_input = TextInput(self.map_area_width + 20, self.height - 60, 180, 30)
        self.save_button = SaveButton(self.map_area_width + 210, self.height - 60)

        # Save options
        from edit_mode.ui_components import TextButton, DropdownMenu, RelationComponent
        option_y = 250  # Fixed Y position for save option buttons (below map name input)
        self.main_map_button = TextButton(self.map_area_width + 20, option_y, 120, 30, "Main Map")
        self.related_map_button = TextButton(self.map_area_width + 150, option_y, 120, 30, "Related Map")
        self.main_map_button.is_selected = True  # Default to Main Map
        self.folder_dropdown = DropdownMenu(self.map_area_width + 20, option_y + 40, 250, 30)
        self.save_mode = "main"  # "main" or "related"

        # Import UI components for relation points
        # RelationGroup is used indirectly when loading relation points

        # Relations component
        self.relation_component = RelationComponent(self.map_area_width + 20, 150)

        # Track placed relation points with IDs
        # Format: {id: {'a': (grid_x, grid_y), 'b': (grid_x, grid_y)}}
        self.relation_points = {}

        # Mode buttons - position them at the top with proper spacing
        from edit_mode.ui_components import TextButton
        mode_button_width = 80
        mode_button_height = 30
        mode_button_y = 10
        mode_button_spacing = 5

        self.edit_mode_button = TextButton(self.map_area_width + 5, mode_button_y, mode_button_width, mode_button_height, "Edit", 16)
        self.browse_mode_button = TextButton(self.map_area_width + 5 + mode_button_width + mode_button_spacing, mode_button_y, mode_button_width, mode_button_height, "Browse", 16)
        self.new_map_button = TextButton(self.map_area_width + 5 + 2 * (mode_button_width + mode_button_spacing), mode_button_y, mode_button_width, mode_button_height, "New Map", 16)

        # Set edit mode as selected by default
        self.edit_mode_button.is_selected = True

        # Tileset switching buttons
        from edit_mode.ui_components import TextButton
        tileset_button_width = 30
        tileset_button_height = 25
        tileset_button_y = 120  # Position below the tab area
        tileset_button_spacing = 5

        self.tileset_buttons = [
            TextButton(self.map_area_width + 20, tileset_button_y, tileset_button_width, tileset_button_height, "1", 16),
            TextButton(self.map_area_width + 20 + tileset_button_width + tileset_button_spacing, tileset_button_y, tileset_button_width, tileset_button_height, "2", 16),
            TextButton(self.map_area_width + 20 + 2 * (tileset_button_width + tileset_button_spacing), tileset_button_y, tileset_button_width, tileset_button_height, "3", 16)
        ]

        # Set the first tileset button as selected by default
        self.tileset_buttons[0].is_selected = True

        # Current mode
        self.current_mode = "edit"  # "edit" or "browse"

        # Track the current main map name (for saving entrance maps)
        self.current_main_map = None

        # Initialize UI manager
        self.ui_manager = EditScreenUI(self.map_area_width, self.sidebar_width, self.height)

        # Collision toggle rect
        self.collision_toggle_rect = None

        # Help text area for scrollable help content
        self.help_text_area = ScrollableTextArea(
            self.map_area_width + 20,  # x position
            120 + 40,                  # y position (120 is the content_y value from EditScreenUI)
            self.sidebar_width - 40,   # width
            self.height - 200          # height
        )

    def handle_event(self, event):
        """Handle events for the edit screen"""
        mouse_pos = pygame.mouse.get_pos()

        # Update mouse position for tile preview
        self.mouse_pos = mouse_pos

        # Update mode buttons
        self.edit_mode_button.update(mouse_pos)
        self.browse_mode_button.update(mouse_pos)
        self.new_map_button.update(mouse_pos)

        # Update tileset buttons
        for button in self.tileset_buttons:
            button.update(mouse_pos)

        # Handle common events (back and reload buttons)
        result = self.handle_common_events(event, mouse_pos)
        if result:
            return result

        # Check for mode button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.edit_mode_button.is_clicked(event):
                self.current_mode = "edit"
                # Update button selection states
                self.edit_mode_button.is_selected = True
                self.browse_mode_button.is_selected = False
                self.new_map_button.is_selected = False
                return None

            if self.browse_mode_button.is_clicked(event):
                # Clear relation points when switching to browse mode without saving
                # This prevents relation points from being carried over between maps
                self.relation_points = {}

                self.current_mode = "browse"
                # Update button selection states
                self.edit_mode_button.is_selected = False
                self.browse_mode_button.is_selected = True
                self.new_map_button.is_selected = False
                # Refresh map list and position items
                self.map_manager.refresh_map_list()
                self.map_manager.position_map_items(
                    self.map_area_width + 20,
                    120,
                    self.sidebar_width - 40,
                    300
                )
                return None

            if self.new_map_button.is_clicked(event):
                # Create a new map - clear all data and switch to edit mode
                self.create_new_map()
                self.current_mode = "edit"
                # Update button selection states
                self.edit_mode_button.is_selected = True
                self.browse_mode_button.is_selected = False
                self.new_map_button.is_selected = False
                return None

            # Handle tileset button clicks
            for i, button in enumerate(self.tileset_buttons):
                if button.is_clicked(event):
                    # Deselect all tileset buttons
                    for btn in self.tileset_buttons:
                        btn.is_selected = False
                    # Select the clicked button
                    button.is_selected = True
                    # Switch to the corresponding tileset
                    self.selected_tileset_index = i
                    self.selected_tile = None
                    # Clear the brush manager's selected tile
                    self.brush_manager.set_selected_tile(None)
                    # Position the tileset buttons
                    self.tileset_manager.position_tileset_buttons(self.selected_tileset_index)
                    return None

        # Handle events based on current mode
        if self.current_mode == "edit":
            # No automatic saving when switching tabs
            if event.type == pygame.MOUSEBUTTONDOWN and self.tab_manager.is_tab_click(mouse_pos):
                # Changes are only saved when the save button is clicked
                pass

            # Handle tab manager events
            if self.tab_manager.handle_event(event, mouse_pos):
                # If the Help tab was clicked, update the help text area
                if self.tab_manager.active_tab == "Help" and self.tab_manager.show_tips:
                    # Set the help text content
                    self.help_text_area.set_text(self.get_help_instructions())
                return None

            # Handle help text area events if Help tab is active
            if self.tab_manager.active_tab == "Help" and self.tab_manager.show_tips:
                if self.help_text_area.handle_event(event, mouse_pos):
                    return None

            # Handle relation component events if Relations tab is active
            if self.tab_manager.active_tab == "Relations":
                # Update the relation component
                self.relation_component.update(mouse_pos)

                # Handle relation component events (button selection)
                result = self.relation_component.handle_event(event, mouse_pos)
                if result:
                    # Check if a specific group was deleted
                    if result.startswith("group_deleted_"):
                        deleted_id = result.split("_")[-1]
                        # Remove the relation points for this specific ID
                        if deleted_id in self.relation_points:
                            del self.relation_points[deleted_id]
                            print(f"Removed relation points with ID {deleted_id}")
                        return None

                    # Handle other events (group selection, etc.)
                    # Get the current ID
                    current_id = str(self.relation_component.current_id)

                    # Make sure the current ID exists in relation_points
                    if current_id not in self.relation_points:
                        self.relation_points[current_id] = {}

                    # Clean up relation_points to match the groups in the component
                    valid_ids = [str(group.id) for group in self.relation_component.groups]
                    ids_to_remove = [id_key for id_key in self.relation_points.keys()
                                    if id_key.isdigit() and id_key not in valid_ids]

                    for id_key in ids_to_remove:
                        del self.relation_points[id_key]
                        print(f"Removed relation points with ID {id_key}")

                    # No automatic saving when handling relation component events
                    # Changes are only saved when the save button is clicked
                    pass

                    return None

                # Handle placing or removing relation points on the map
                if event.type == pygame.MOUSEBUTTONDOWN and mouse_pos[0] < self.map_area_width:
                    # Convert mouse position to grid cell
                    grid_x = (mouse_pos[0] + self.camera_x) // self.grid_cell_size
                    grid_y = (mouse_pos[1] + self.camera_y) // self.grid_cell_size
                    current_pos = (grid_x, grid_y)

                    # Get current ID
                    current_id = str(self.relation_component.current_id)

                    # Check for right-click to remove existing points
                    if event.button == 3:  # Right mouse button
                        # Check if we clicked on any point
                        for id_key, points in list(self.relation_points.items()):  # Use list() to avoid modification during iteration
                            if 'a' in points and points['a'] == current_pos:
                                del self.relation_points[id_key]['a']
                                print(f"Removed relation point A with ID {id_key}")
                                # If no points left for this ID, remove the ID entry
                                if not self.relation_points[id_key]:
                                    del self.relation_points[id_key]

                                # No automatic saving when removing relation points
                                # Changes are only saved when the save button is clicked
                                pass

                                return None

                            if 'b' in points and points['b'] == current_pos:
                                del self.relation_points[id_key]['b']
                                print(f"Removed relation point B with ID {id_key}")
                                # If no points left for this ID, remove the ID entry
                                if not self.relation_points[id_key]:
                                    del self.relation_points[id_key]

                                # No automatic saving when removing relation points
                                # Changes are only saved when the save button is clicked
                                pass
                                return None

                        # If we didn't click on any point, check if the delete button was clicked
                        # This is handled in the relation_component.handle_event method

                    # Left-click to place points (only if a button is selected)
                    elif event.button == 1 and self.relation_component.active_button:
                        active_button = self.relation_component.active_button

                        # Initialize the ID entry if it doesn't exist
                        if current_id not in self.relation_points:
                            self.relation_points[current_id] = {}

                        # Check if we're trying to place point A and B on the same map
                        other_button = 'b' if active_button == 'a' else 'a'

                        if other_button in self.relation_points[current_id]:
                            # Can't place both points on the same map
                            self.map_saver.status_message = "Error: Cannot place both points on the same map!"
                            self.map_saver.status_timer = 180
                            return None

                        # Check if there's a corresponding point in another map
                        for map_name, points in self.relation_points.items():
                            if map_name != self.current_main_map and current_id in points and other_button in points[current_id]:
                                # Found a corresponding point in another map
                                # Check if they're in the same folder
                                if not self.are_maps_in_same_folder(self.current_main_map, map_name):
                                    self.map_saver.status_message = f"Warning: Map '{map_name}' is not in the same folder as '{self.current_main_map}'!"
                                    self.map_saver.status_timer = 180
                                    print(f"Warning: Maps {self.current_main_map} and {map_name} are not in the same folder. Relation points will not work.")
                                    # Still allow placement, but warn the user

                        # Place the relation point
                        # Make sure we're using a tuple for the position to avoid JSON serialization issues
                        self.relation_points[current_id][active_button] = tuple(current_pos)


                        # No automatic saving when placing relation points
                        # Changes are only saved when the save button is clicked
                        pass

                        # Deselect the button after placing
                        # Get the currently selected group
                        if self.relation_component.selected_group_index < len(self.relation_component.groups):
                            current_group = self.relation_component.groups[self.relation_component.selected_group_index]
                            if active_button == 'a':
                                current_group.button_a_selected = False
                            else:
                                current_group.button_b_selected = False
                            current_group.active_button = None

                        return None

            # Handle layer manager events if Tiles tab is active
            if self.tab_manager.active_tab == "Tiles" and self.layer_manager.handle_event(event, mouse_pos, self.map_data):
                # Layer manager now handles map data cleanup automatically
                return None

            # Update text input and save button only if Save tab is active
            if self.tab_manager.active_tab == "Save":
                self.map_name_input.update([event])
                self.save_button.update(mouse_pos)
                self.main_map_button.update(mouse_pos)
                self.related_map_button.update(mouse_pos)

                # Update folder dropdown if in related map mode
                if self.save_mode == "related":
                    self.folder_dropdown.update(mouse_pos)

                # Check for main map button click
                if event.type == pygame.MOUSEBUTTONDOWN and self.main_map_button.is_clicked(event):
                    self.main_map_button.is_selected = True
                    self.related_map_button.is_selected = False
                    self.save_mode = "main"
                    return None

                # Check for related map button click
                if event.type == pygame.MOUSEBUTTONDOWN and self.related_map_button.is_clicked(event):
                    self.main_map_button.is_selected = False
                    self.related_map_button.is_selected = True
                    self.save_mode = "related"
                    # Update the dropdown with the latest folder list
                    self.folder_dropdown.set_options(self.map_manager.get_main_map_folders())
                    return None

                # Handle dropdown events if in related map mode
                if self.save_mode == "related":
                    if self.folder_dropdown.handle_event(event, mouse_pos):
                        return None

                # Check for save button click
                if event.type == pygame.MOUSEBUTTONDOWN and self.save_button.is_clicked(event):
                    if self.save_mode == "main":
                        # Save as main map
                        self.map_saver.save_map(
                            self.map_data,
                            self.map_name_input.text,
                            self.grid_cell_size,
                            self.tileset_manager,
                            self.layer_manager,
                            self.collision_manager,
                            self.relation_points,  # Pass relation points
                            is_main=True
                        )
                    else:
                        # Save as related map
                        if not self.folder_dropdown.selected_option:
                            # No folder selected, show error
                            self.map_saver.status_message = "Error: Please select a parent folder!"
                            self.map_saver.status_timer = 180
                        else:
                            # Save as related map to selected folder
                            self.map_saver.save_map(
                                self.map_data,
                                self.map_name_input.text,
                                self.grid_cell_size,
                                self.tileset_manager,
                                self.layer_manager,
                                self.collision_manager,
                                self.relation_points,  # Pass relation points
                                is_main=False,
                                parent_folder=self.folder_dropdown.selected_option
                            )
            # Handle tileset button clicks for Tiles and Collision tabs
            if self.tab_manager.active_tab in ["Tiles", "Collision"]:
                clicked_tile = self.tileset_manager.handle_tileset_click(
                    event,
                    mouse_pos,
                    self.selected_tileset_index
                )
                if clicked_tile:
                    self.selected_tile = clicked_tile
                    # Update the brush manager with the selected tile
                    self.brush_manager.set_selected_tile(clicked_tile)
                    # Return early to prevent brush manager from handling the same click
                    return None

                # Handle brush manager events if Tiles tab is active (only if no tile was selected)
                if self.tab_manager.active_tab == "Tiles" and self.brush_manager.handle_event(event, mouse_pos):
                    return None

                # Handle collision dot clicks if in Collision tab
                if self.tab_manager.active_tab == "Collision" and event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if click was on a regular tile in the tileset
                    for button_data in self.tileset_manager.tileset_buttons[self.selected_tileset_index]:
                        button = button_data['button']
                        if button and button.rect.collidepoint(mouse_pos):
                            # Check if click was on a collision dot
                            # Note: Collision dots in sidebar don't need zoom scaling since they're UI elements
                            source_path = button_data.get('source_path', '')
                            if source_path:
                                if self.collision_manager.handle_collision_click(mouse_pos, button.rect, source_path, 1.0):
                                    return None

                    # Check if click was on an animated tile (only if we're on the last tileset)
                    if self.selected_tileset_index == len(self.tileset_manager.tileset_buttons) - 1:
                        for button_data in self.tileset_manager.animated_tile_buttons:
                            button = button_data['button']
                            if button and button.rect.collidepoint(mouse_pos):
                                # Check if click was on a collision dot
                                # Note: Collision dots in sidebar don't need zoom scaling since they're UI elements
                                source_path = button_data.get('source_path', '')
                                if source_path:
                                    if self.collision_manager.handle_collision_click(mouse_pos, button.rect, source_path, 1.0):
                                        return None

            # Handle mouse wheel events
            if event.type == pygame.MOUSEWHEEL:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]:
                    # Ctrl + scroll for zooming
                    if event.y > 0:
                        self.zoom_in()
                    elif event.y < 0:
                        self.zoom_out()
                    return None
                elif keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    # Shift + scroll for horizontal tile selection movement
                    self._move_tile_selection_horizontal(-event.y)  # Negative for natural scrolling
                    return None
                elif keys[pygame.K_LALT] or keys[pygame.K_RALT]:
                    # Alt + scroll for vertical tile selection movement
                    self._move_tile_selection_vertical(event.y)  # Positive for natural scrolling
                    return None
                # Note: Regular scroll (no modifiers) is now disabled
                return None

            # Handle starting drag placement/erasure
            if event.type == pygame.MOUSEBUTTONDOWN and mouse_pos[0] < self.map_area_width:
                # Start dragging if left or right mouse button is pressed
                if event.button in (1, 3):  # 1 = left click (place), 3 = right click (erase)
                    self.is_dragging = True
                    self.drag_button = event.button

                    # Convert mouse position to grid cell
                    grid_x = (mouse_pos[0] + self.camera_x) // self.grid_cell_size
                    grid_y = (mouse_pos[1] + self.camera_y) // self.grid_cell_size
                    self.last_drag_pos = (grid_x, grid_y)

                    # Place or remove tiles using the brush
                    if self.layer_manager.select_all_mode:
                        # In select all mode, affect all visible layers
                        if event.button == 1 and self.selected_tile:  # Left click to place
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                for layer in range(self.layer_manager.layer_count):
                                    if self.layer_manager.layer_visibility[layer]:
                                        # Check if we're placing a player character tile
                                        if self.selected_tile.get('is_player'):
                                            # For player character, only place it once and only in the current layer
                                            # First remove any existing player character tiles
                                            for l in range(self.layer_manager.layer_count):
                                                for pos, tile in list(self.map_data[l].items()):
                                                    if isinstance(tile, dict) and tile.get('is_player'):
                                                        del self.map_data[l][pos]
                                            # Now place the new player character tile only in the current layer
                                            self.map_data[self.layer_manager.current_layer][(tile_x, tile_y)] = self.selected_tile
                                            # Break out of the layer loop since we only want to place it once
                                            break
                                        else:
                                            # Normal tile placement in all visible layers
                                            self.map_data[layer][(tile_x, tile_y)] = self.selected_tile
                        elif event.button == 3:  # Right click to remove
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                for layer in range(self.layer_manager.layer_count):
                                    if self.layer_manager.layer_visibility[layer]:
                                        if (tile_x, tile_y) in self.map_data[layer]:
                                            del self.map_data[layer][(tile_x, tile_y)]
                    else:
                        # Normal mode - affect only the current layer
                        current_layer = self.layer_manager.current_layer
                        if event.button == 1 and self.selected_tile:  # Left click to place
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                # Check if we're placing a player character tile
                                if self.selected_tile.get('is_player'):
                                    # Remove any existing player character tiles first
                                    for layer in range(self.layer_manager.layer_count):
                                        for pos, tile in list(self.map_data[layer].items()):
                                            if isinstance(tile, dict) and tile.get('is_player'):
                                                del self.map_data[layer][pos]
                                    # Now place the new player character tile
                                    self.map_data[current_layer][(tile_x, tile_y)] = self.selected_tile
                                else:
                                    # Normal tile placement
                                    self.map_data[current_layer][(tile_x, tile_y)] = self.selected_tile
                        elif event.button == 3:  # Right click to remove
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                if (tile_x, tile_y) in self.map_data[current_layer]:
                                    del self.map_data[current_layer][(tile_x, tile_y)]

            # Handle ending drag
            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_dragging = False
                self.last_drag_pos = None

            # Handle key releases for camera movement
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = False
                    self.key_press_time[event.key] = 0

            # Handle drag placement/erasure
            elif event.type == pygame.MOUSEMOTION and self.is_dragging and mouse_pos[0] < self.map_area_width:
                # Convert mouse position to grid cell
                grid_x = (mouse_pos[0] + self.camera_x) // self.grid_cell_size
                grid_y = (mouse_pos[1] + self.camera_y) // self.grid_cell_size
                current_pos = (grid_x, grid_y)

                # Only place/erase if we've moved to a new grid cell
                if current_pos != self.last_drag_pos:
                    self.last_drag_pos = current_pos

                    # Place or remove tiles using the brush
                    if self.layer_manager.select_all_mode:
                        # In select all mode, affect all visible layers
                        if self.drag_button == 1 and self.selected_tile:  # Left drag to place
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                for layer in range(self.layer_manager.layer_count):
                                    if self.layer_manager.layer_visibility[layer]:
                                        # Check if we're placing a player character tile
                                        if self.selected_tile.get('is_player'):
                                            # For player character, only place it once and only in the current layer
                                            # First remove any existing player character tiles
                                            for l in range(self.layer_manager.layer_count):
                                                for pos, tile in list(self.map_data[l].items()):
                                                    if isinstance(tile, dict) and tile.get('is_player'):
                                                        del self.map_data[l][pos]
                                            # Now place the new player character tile only in the current layer
                                            self.map_data[self.layer_manager.current_layer][(tile_x, tile_y)] = self.selected_tile
                                            # Break out of the layer loop since we only want to place it once
                                            break
                                        else:
                                            # Normal tile placement in all visible layers
                                            self.map_data[layer][(tile_x, tile_y)] = self.selected_tile
                        elif self.drag_button == 3:  # Right drag to remove
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                for layer in range(self.layer_manager.layer_count):
                                    if self.layer_manager.layer_visibility[layer]:
                                        if (tile_x, tile_y) in self.map_data[layer]:
                                            del self.map_data[layer][(tile_x, tile_y)]
                    else:
                        # Normal mode - affect only the current layer
                        current_layer = self.layer_manager.current_layer
                        if self.drag_button == 1 and self.selected_tile:  # Left drag to place
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                # Check if we're placing a player character tile
                                if self.selected_tile.get('is_player'):
                                    # Remove any existing player character tiles first
                                    for layer in range(self.layer_manager.layer_count):
                                        for pos, tile in list(self.map_data[layer].items()):
                                            if isinstance(tile, dict) and tile.get('is_player'):
                                                del self.map_data[layer][pos]
                                    # Now place the new player character tile
                                    self.map_data[current_layer][(tile_x, tile_y)] = self.selected_tile
                                else:
                                    # Normal tile placement
                                    self.map_data[current_layer][(tile_x, tile_y)] = self.selected_tile
                        elif self.drag_button == 3:  # Right drag to remove
                            # Get all tiles in the brush
                            brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                            for tile_x, tile_y in brush_tiles:
                                if (tile_x, tile_y) in self.map_data[current_layer]:
                                    del self.map_data[current_layer][(tile_x, tile_y)]

            # Handle keyboard events for camera movement
            if event.type == pygame.KEYDOWN:
                # Track key presses for WASD and arrow keys
                if event.key in self.keys_pressed:
                    self.keys_pressed[event.key] = True
                    self.key_press_time[event.key] = pygame.time.get_ticks()
                    self.current_camera_speed[event.key] = self.camera_speed  # Reset speed when key is first pressed
                # Note: Tileset switching is now handled by buttons instead of keyboard shortcuts
                # Toggle tile preview with P key
                elif event.key == pygame.K_p:
                    self.show_tile_preview = not self.show_tile_preview

        elif self.current_mode == "browse":
            # Handle map browser events
            result = self.map_manager.handle_event(event, mouse_pos)

            if result:
                if result.get("action") == "edit":
                    # Save relation points before loading a new map
                    if self.current_main_map and self.relation_points:
                        try:
                            # Get the map file path
                            map_path = os.path.join("Maps", self.current_main_map, f"{self.current_main_map}.json")

                            # Check if file exists
                            if os.path.exists(map_path):
                                # Load existing map data
                                with open(map_path, 'r') as f:
                                    map_data_to_save = json.load(f)

                                # Clean up relation_points to match the groups in the component
                                valid_ids = [str(group.id) for group in self.relation_component.groups]
                                ids_to_remove = [id_key for id_key in self.relation_points.keys()
                                                if id_key.isdigit() and id_key not in valid_ids]

                                for id_key in ids_to_remove:
                                    del self.relation_points[id_key]

                                # Save the updated relation points
                                if self.relation_points:
                                    # Make a deep copy to avoid reference issues
                                    import copy
                                    relation_points_copy = copy.deepcopy(self.relation_points)

                                    # Ensure all positions are tuples
                                    for id_key, points in relation_points_copy.items():
                                        if 'a' in points and isinstance(points['a'], list):
                                            relation_points_copy[id_key]['a'] = tuple(points['a'])
                                        if 'b' in points and isinstance(points['b'], list):
                                            relation_points_copy[id_key]['b'] = tuple(points['b'])

                                    map_data_to_save["relation_points"] = relation_points_copy

                                    # Save the updated map data
                                    try:
                                        # First create a temporary file to avoid corruption
                                        temp_file_path = map_path + ".tmp"
                                        with open(temp_file_path, 'w') as f:
                                            json.dump(map_data_to_save, f, indent=2)

                                        # If the write was successful, rename the temporary file to the actual file
                                        if os.path.exists(map_path):
                                            os.remove(map_path)
                                        os.rename(temp_file_path, map_path)
                                    except Exception as e:

                                        # If there was an error, try the direct approach as a fallback
                                        with open(map_path, 'w') as f:
                                            json.dump(map_data_to_save, f, indent=2)


                        except Exception:
                            pass

                    # Clear relation points before loading a new map
                    # This prevents relation points from being carried over between maps
                    self.relation_points = {}

                    # Check if we're loading an entrance map
                    if result.get("entrance"):
                        # Load the entrance map
                        map_data = self.map_manager.load_map(result.get("map"), result.get("entrance"))
                        # Set the current main map (for saving entrance maps)
                        self.current_main_map = result.get("map")
                    else:
                        # Load the main map
                        map_data = self.map_manager.load_map(result.get("map"))
                        # Set the current main map
                        self.current_main_map = result.get("map")

                    if map_data:
                        # Clear current map data for all layers
                        for i in range(self.layer_manager.max_layers):
                            self.map_data[i] = {}

                        # Reset layer count to 1
                        self.layer_manager.layer_count = 1
                        self.layer_manager.current_layer = 0

                        # Check if this is a layered map
                        if "layers" in map_data:
                            # Set the layer count
                            self.layer_manager.layer_count = min(
                                len(map_data["layers"]),
                                self.layer_manager.max_layers
                            )

                            # Load tiles from each layer
                            for layer_idx, layer_data in enumerate(map_data["layers"]):
                                if layer_idx >= self.layer_manager.max_layers:
                                    break

                                # Set layer visibility
                                if "visible" in layer_data:
                                    self.layer_manager.layer_visibility[layer_idx] = layer_data["visible"]

                                # Load tiles for this layer
                                for _, tile_info in layer_data.get("tiles", {}).items():
                                    grid_x, grid_y = tile_info.get("position", [0, 0])
                                    source_path = tile_info.get("source_path", "")

                                    # Check if this is an animated tile
                                    if source_path.startswith("animated:"):
                                        # This is an animated tile, find it in the animated tile buttons
                                        for tile_data in self.tileset_manager.animated_tile_buttons:
                                            if tile_data.get("source_path") == source_path:
                                                # Found the animated tile, add it to the map
                                                self.map_data[layer_idx][(grid_x, grid_y)] = tile_data
                                                break
                                    else:
                                        # Regular tile, find it in the tileset buttons
                                        for _, tileset in enumerate(self.tileset_manager.tileset_buttons):
                                            for tile_data in tileset:
                                                if tile_data.get("source_path") == source_path:
                                                    # Found the tile, add it to the map
                                                    self.map_data[layer_idx][(grid_x, grid_y)] = tile_data
                                                    break
                        else:
                            # Legacy format - load all tiles into layer 0
                            for _, tile_info in map_data.get("tiles", {}).items():
                                grid_x, grid_y = tile_info.get("position", [0, 0])
                                source_path = tile_info.get("source_path", "")

                                # Check if this is an animated tile
                                if source_path.startswith("animated:"):
                                    # This is an animated tile, find it in the animated tile buttons
                                    for tile_data in self.tileset_manager.animated_tile_buttons:
                                        if tile_data.get("source_path") == source_path:
                                            # Found the animated tile, add it to the map
                                            self.map_data[0][(grid_x, grid_y)] = tile_data
                                            break
                                else:
                                    # Regular tile, find it in the tileset buttons
                                    for _, tileset in enumerate(self.tileset_manager.tileset_buttons):
                                        for tile_data in tileset:
                                            if tile_data.get("source_path") == source_path:
                                                # Found the tile, add it to the map
                                                self.map_data[0][(grid_x, grid_y)] = tile_data
                                                break

                        # Sync layer manager state to the layer panel UI
                        # This ensures the layer panel shows the correct number of layers
                        self.layer_manager.sync_to_panel()

                        # Load collision data if available
                        if "collision_data" in map_data:
                            self.collision_manager.load_collision_data(map_data["collision_data"])

                        # Load relation points if available
                        # Reset relation points first - this is critical to prevent points from being carried over between maps
                        self.relation_points = {}

                        # Reset the relation component groups
                        # Use the new sync method
                        self.relation_component.sync_with_relation_points({})

                        if "relation_points" in map_data:
                            # Make a deep copy of the relation data to avoid reference issues
                            import copy
                            relation_data = copy.deepcopy(map_data["relation_points"])

                            # Check if it's the old format (without IDs)
                            if 'a' in relation_data or 'b' in relation_data:
                                # Convert old format to new format with ID 1
                                self.relation_points["1"] = {}

                                if 'a' in relation_data:
                                    if isinstance(relation_data['a'], list):
                                        self.relation_points["1"]['a'] = tuple(relation_data['a'])
                                    else:
                                        self.relation_points["1"]['a'] = relation_data['a']


                                if 'b' in relation_data:
                                    if isinstance(relation_data['b'], list):
                                        self.relation_points["1"]['b'] = tuple(relation_data['b'])
                                    else:
                                        self.relation_points["1"]['b'] = relation_data['b']


                                # Set the relation component ID to 1
                                self.relation_component.set_id(1)
                            else:
                                # New format with IDs
                                # Convert relation_data to a new dictionary to avoid reference issues
                                self.relation_points = {}

                                # Ensure all positions are tuples
                                for id_key, points in relation_data.items():
                                    self.relation_points[id_key] = {}

                                    # Handle point A
                                    if 'a' in points:
                                        if isinstance(points['a'], list):
                                            # Convert list to tuple
                                            self.relation_points[id_key]['a'] = tuple(points['a'])

                                        elif isinstance(points['a'], tuple):
                                            # Already a tuple, use it directly
                                            self.relation_points[id_key]['a'] = points['a']

                                        else:
                                            # Unknown format, try to handle it
                                            try:
                                                # Try to convert to tuple if it's iterable
                                                self.relation_points[id_key]['a'] = tuple(points['a'])

                                            except (TypeError, ValueError):
                                                # If conversion fails, use as is
                                                self.relation_points[id_key]['a'] = points['a']


                                    # Handle point B
                                    if 'b' in points:
                                        if isinstance(points['b'], list):
                                            # Convert list to tuple
                                            self.relation_points[id_key]['b'] = tuple(points['b'])

                                        elif isinstance(points['b'], tuple):
                                            # Already a tuple, use it directly
                                            self.relation_points[id_key]['b'] = points['b']

                                        else:
                                            # Unknown format, try to handle it
                                            try:
                                                # Try to convert to tuple if it's iterable
                                                self.relation_points[id_key]['b'] = tuple(points['b'])

                                            except (TypeError, ValueError):
                                                # If conversion fails, use as is
                                                self.relation_points[id_key]['b'] = points['b']


                                # Use the new sync method
                                self.relation_component.sync_with_relation_points(self.relation_points)



                        # Set the map name in the input field
                        if result.get("entrance"):
                            # For entrance maps, use the entrance name
                            self.map_name_input.text = result.get("entrance")
                        else:
                            # For main maps, use the map name
                            self.map_name_input.text = result.get("map")

                        self.map_name_input.text_surf = self.map_name_input.font.render(
                            self.map_name_input.text, True, (0, 0, 0))
                        self.map_name_input.text_rect = self.map_name_input.text_surf.get_rect(
                            midleft=(self.map_name_input.rect.x + 5, self.map_name_input.rect.centery))

                        # Switch to edit mode
                        self.current_mode = "edit"

                elif result.get("action") == "cancel":
                    # Switch back to edit mode
                    self.current_mode = "edit"

        return None

    def update(self):
        """Update edit screen logic"""
        # Update map saver status
        self.map_saver.update()

        # Update map manager status
        self.map_manager.update()

        # Handle continuous camera movement with key presses
        self.update_camera_movement()

    def update_camera_movement(self):
        """Handle continuous camera movement with key presses"""
        current_time = pygame.time.get_ticks()

        # Calculate acceleration based on how long keys have been pressed
        for key in self.keys_pressed:
            if self.keys_pressed[key] and self.key_press_time[key] > 0:
                # Calculate how long the key has been pressed (in seconds)
                press_duration = (current_time - self.key_press_time[key]) / 1000.0

                # Increase speed based on duration, but cap at max speed
                target_speed = min(
                    self.camera_speed + (press_duration * self.camera_acceleration * self.camera_speed),
                    self.camera_max_speed
                )

                # Smooth acceleration (reduced smoothing factor for more gradual acceleration)
                self.current_camera_speed[key] += (target_speed - self.current_camera_speed[key]) * 0.05

        # Apply camera movement based on keys pressed
        # Vertical movement (W/S or UP/DOWN)
        if self.keys_pressed[pygame.K_w] or self.keys_pressed[pygame.K_UP]:
            speed = max(self.current_camera_speed[pygame.K_w], self.current_camera_speed[pygame.K_UP])
            # Make sure we move at least 1 pixel if the key is pressed
            move_amount = max(1, int(speed)) if speed > 0.1 else 0
            self.camera_y = max(0, self.camera_y - move_amount)

        if self.keys_pressed[pygame.K_s] or self.keys_pressed[pygame.K_DOWN]:
            speed = max(self.current_camera_speed[pygame.K_s], self.current_camera_speed[pygame.K_DOWN])
            # Make sure we move at least 1 pixel if the key is pressed
            move_amount = max(1, int(speed)) if speed > 0.1 else 0
            self.camera_y += move_amount

        # Horizontal movement (A/D or LEFT/RIGHT)
        if self.keys_pressed[pygame.K_a] or self.keys_pressed[pygame.K_LEFT]:
            speed = max(self.current_camera_speed[pygame.K_a], self.current_camera_speed[pygame.K_LEFT])
            # Make sure we move at least 1 pixel if the key is pressed
            move_amount = max(1, int(speed)) if speed > 0.1 else 0
            self.camera_x = max(0, self.camera_x - move_amount)

        if self.keys_pressed[pygame.K_d] or self.keys_pressed[pygame.K_RIGHT]:
            speed = max(self.current_camera_speed[pygame.K_d], self.current_camera_speed[pygame.K_RIGHT])
            # Make sure we move at least 1 pixel if the key is pressed
            move_amount = max(1, int(speed)) if speed > 0.1 else 0
            self.camera_x += move_amount

    def zoom_in(self):
        """Zoom in to the next zoom level"""
        if self.current_zoom_index < len(self.zoom_levels) - 1:
            # Store the center point of the current view
            center_x = self.camera_x + (self.map_area_width // 2)
            center_y = self.camera_y + (self.map_area_height // 2)

            # Update zoom
            self.current_zoom_index += 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self.update_zoom()

            # Adjust camera to keep the same center point
            self.camera_x = center_x - (self.map_area_width // 2)
            self.camera_y = center_y - (self.map_area_height // 2)

            # Ensure camera stays within bounds
            self.camera_x = max(0, self.camera_x)
            self.camera_y = max(0, self.camera_y)

    def zoom_out(self):
        """Zoom out to the previous zoom level"""
        if self.current_zoom_index > 0:
            # Store the center point of the current view
            center_x = self.camera_x + (self.map_area_width // 2)
            center_y = self.camera_y + (self.map_area_height // 2)

            # Update zoom
            self.current_zoom_index -= 1
            self.zoom_factor = self.zoom_levels[self.current_zoom_index]
            self.update_zoom()

            # Adjust camera to keep the same center point
            self.camera_x = center_x - (self.map_area_width // 2)
            self.camera_y = center_y - (self.map_area_height // 2)

            # Ensure camera stays within bounds
            self.camera_x = max(0, self.camera_x)
            self.camera_y = max(0, self.camera_y)

    def reset_zoom(self):
        """Reset zoom to 1.0x (100%)"""
        # Store the center point of the current view
        center_x = self.camera_x + (self.map_area_width // 2)
        center_y = self.camera_y + (self.map_area_height // 2)

        # Reset zoom to 1.0x
        self.current_zoom_index = 0  # 1.0x is at index 0
        self.zoom_factor = self.zoom_levels[self.current_zoom_index]
        self.update_zoom()

        # Adjust camera to keep the same center point
        self.camera_x = center_x - (self.map_area_width // 2)
        self.camera_y = center_y - (self.map_area_height // 2)

        # Ensure camera stays within bounds
        self.camera_x = max(0, self.camera_x)
        self.camera_y = max(0, self.camera_y)

    def update_zoom(self):
        """Update grid cell size and camera speed based on current zoom factor"""
        self.grid_cell_size = int(self.base_grid_cell_size * self.zoom_factor)

        # Update camera speeds based on new grid size
        self.camera_speed = self.grid_cell_size * 0.5
        self.camera_max_speed = self.grid_cell_size * 1.5

        # Update current camera speeds for all keys
        for key in self.current_camera_speed:
            self.current_camera_speed[key] = self.camera_speed

    def draw(self, surface):
        """Draw the edit screen"""
        if self.current_mode == "edit":
            # Fill the background with white
            surface.fill((255, 255, 255))

            # Draw the grid
            self.ui_manager.draw_grid(surface, self.camera_x, self.camera_y, self.map_area_height, self.grid_cell_size)

            # Draw placed tiles
            self.ui_manager.draw_map_tiles(
                surface,
                self.map_data,
                self.layer_manager,
                self.grid_cell_size,
                self.camera_x,
                self.camera_y,
                self.map_area_width,
                self.map_area_height
            )

            # Player position is now handled as a tile in the map data

            # Draw tile preview at mouse cursor if enabled
            if self.show_tile_preview and self.selected_tile and self.mouse_pos[0] < self.map_area_width:
                # Only show preview in the map area (not in sidebar)
                if 'image' in self.selected_tile:
                    # Calculate grid position
                    grid_x = (self.mouse_pos[0] + self.camera_x) // self.grid_cell_size
                    grid_y = (self.mouse_pos[1] + self.camera_y) // self.grid_cell_size

                    # Calculate screen position
                    screen_x = grid_x * self.grid_cell_size - self.camera_x
                    screen_y = grid_y * self.grid_cell_size - self.camera_y

                    # Scale and draw the tile with semi-transparency
                    scaled_preview = pygame.transform.scale(self.selected_tile['image'], (self.grid_cell_size, self.grid_cell_size))
                    scaled_preview.set_alpha(128)  # Semi-transparent

                    # If using brush, draw all tiles in the brush
                    if self.tab_manager.active_tab == "Brush" or self.brush_manager.brush_size > 1:
                        brush_tiles = self.brush_manager.get_brush_tiles(grid_x, grid_y)
                        for tile_x, tile_y in brush_tiles:
                            # Calculate screen position for each tile in the brush
                            tile_screen_x = tile_x * self.grid_cell_size - self.camera_x
                            tile_screen_y = tile_y * self.grid_cell_size - self.camera_y

                            # Draw the tile preview
                            surface.blit(scaled_preview, (tile_screen_x, tile_screen_y))
                    else:
                        # Draw single tile preview
                        surface.blit(scaled_preview, (screen_x, screen_y))

            # Draw relation points if they exist (always draw them regardless of active tab)
            for id_key, points in self.relation_points.items():
                # Draw point A (red)
                if 'a' in points:
                    grid_x, grid_y = points['a']
                    screen_x = grid_x * self.grid_cell_size - self.camera_x
                    screen_y = grid_y * self.grid_cell_size - self.camera_y

                    # Draw a red square with semi-transparency
                    point_rect = pygame.Rect(screen_x, screen_y, self.grid_cell_size, self.grid_cell_size)

                    # Use full opacity when Relations tab is active, semi-transparent otherwise
                    if self.tab_manager.active_tab == "Relations":
                        pygame.draw.rect(surface, (220, 60, 60), point_rect)  # Red
                        pygame.draw.rect(surface, (0, 0, 0), point_rect, 2)  # Black border

                        # Draw "A" label with ID
                        font = pygame.font.SysFont(None, 24)
                        label = font.render(f"A{id_key}", True, (255, 255, 255))
                        label_rect = label.get_rect(center=(screen_x + self.grid_cell_size // 2, screen_y + self.grid_cell_size // 2))
                        surface.blit(label, label_rect)
                    else:
                        # Semi-transparent version for other tabs
                        point_surface = pygame.Surface((self.grid_cell_size, self.grid_cell_size), pygame.SRCALPHA)
                        point_surface.fill((220, 60, 60, 128))  # Semi-transparent red
                        pygame.draw.rect(point_surface, (0, 0, 0, 128), pygame.Rect(0, 0, self.grid_cell_size, self.grid_cell_size), 2)  # Semi-transparent border

                        # Draw "A" label with ID and semi-transparency
                        font = pygame.font.SysFont(None, 24)
                        label = font.render(f"A{id_key}", True, (255, 255, 255, 200))
                        label_rect = label.get_rect(center=(self.grid_cell_size // 2, self.grid_cell_size // 2))
                        point_surface.blit(label, label_rect)

                        # Draw the point
                        surface.blit(point_surface, point_rect)

                # Draw point B (blue)
                if 'b' in points:
                    grid_x, grid_y = points['b']
                    screen_x = grid_x * self.grid_cell_size - self.camera_x
                    screen_y = grid_y * self.grid_cell_size - self.camera_y

                    # Draw a blue square
                    point_rect = pygame.Rect(screen_x, screen_y, self.grid_cell_size, self.grid_cell_size)

                    # Use full opacity when Relations tab is active, semi-transparent otherwise
                    if self.tab_manager.active_tab == "Relations":
                        pygame.draw.rect(surface, (60, 60, 220), point_rect)  # Blue
                        pygame.draw.rect(surface, (0, 0, 0), point_rect, 2)  # Black border

                        # Draw "B" label with ID
                        font = pygame.font.SysFont(None, 24)
                        label = font.render(f"B{id_key}", True, (255, 255, 255))
                        label_rect = label.get_rect(center=(screen_x + self.grid_cell_size // 2, screen_y + self.grid_cell_size // 2))
                        surface.blit(label, label_rect)
                    else:
                        # Semi-transparent version for other tabs
                        point_surface = pygame.Surface((self.grid_cell_size, self.grid_cell_size), pygame.SRCALPHA)
                        point_surface.fill((60, 60, 220, 128))  # Semi-transparent blue
                        pygame.draw.rect(point_surface, (0, 0, 0, 128), pygame.Rect(0, 0, self.grid_cell_size, self.grid_cell_size), 2)  # Semi-transparent border

                        # Draw "B" label with ID and semi-transparency
                        font = pygame.font.SysFont(None, 24)
                        label = font.render(f"B{id_key}", True, (255, 255, 255, 200))
                        label_rect = label.get_rect(center=(self.grid_cell_size // 2, self.grid_cell_size // 2))
                        point_surface.blit(label, label_rect)

                        # Draw the point
                        surface.blit(point_surface, point_rect)

            # Draw sidebar
            self.ui_manager.draw_sidebar(
                surface,
                self.tab_manager,
                self.tileset_manager,
                self.layer_manager,
                self.map_saver,
                self.map_name_input,
                self.save_button,
                self.edit_mode_button,
                self.browse_mode_button,
                self.new_map_button,
                self.selected_tileset_index,
                self.collision_manager,
                None,  # collision_toggle_rect removed
                self.brush_manager,
                self  # Pass self as the editor instance
            )

            # Draw zoom indicator in the bottom-left corner of the map area
            zoom_text = f"Zoom: {int(self.zoom_factor * 100)}%"
            font = pygame.font.SysFont(None, 24)
            zoom_surface = font.render(zoom_text, True, (50, 50, 50))
            zoom_rect = zoom_surface.get_rect(bottomleft=(10, self.map_area_height - 10))
            surface.blit(zoom_surface, zoom_rect)

        elif self.current_mode == "browse":
            # Fill the background with a light color
            surface.fill((240, 240, 245))

            # Draw sidebar for map browser
            self.ui_manager.draw_browser_sidebar(
                surface,
                self.map_manager,
                self.edit_mode_button,
                self.browse_mode_button,
                self.new_map_button
            )

        # Draw common elements (back and reload buttons)
        self.draw_common_elements(surface)

    def handle_common_events(self, event, mouse_pos):
        """Handle events common to all screens (back button)"""
        # Update back button
        self.back_button.update(mouse_pos)

        # Check for button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if back button was clicked
            if self.back_button.is_clicked(event):
                # No saving when clicking back - changes are only saved when the save button is clicked
                return "back"

        return None

    def get_map_folder(self, map_name):
        """Get the folder that contains a map

        Args:
            map_name: Name of the map

        Returns:
            Folder name if found, None otherwise
        """
        maps_dir = "Maps"

        # First check if it's a main map (folder name matches map name)
        main_map_path = os.path.join(maps_dir, map_name, f"{map_name}.json")
        if os.path.exists(main_map_path):
            return map_name  # The map is in its own folder

        # If not a main map, search in all folders
        if os.path.exists(maps_dir):
            folders = [f for f in os.listdir(maps_dir) if os.path.isdir(os.path.join(maps_dir, f))]

            for folder_name in folders:
                folder_path = os.path.join(maps_dir, folder_name)
                map_path = os.path.join(folder_path, f"{map_name}.json")

                if os.path.exists(map_path):
                    return folder_name  # Found the folder containing this map

        return None  # Map not found in any folder

    def are_maps_in_same_folder(self, map1, map2):
        """Check if two maps are in the same folder

        Args:
            map1: Name of the first map
            map2: Name of the second map

        Returns:
            True if both maps are in the same folder, False otherwise
        """
        folder1 = self.get_map_folder(map1)
        folder2 = self.get_map_folder(map2)

        # Both maps must be found and in the same folder
        return folder1 is not None and folder1 == folder2

    def create_new_map(self):
        """Create a new empty map by clearing all data"""
        # Clear map data for all layers
        for layer in range(self.layer_manager.layer_count):
            self.map_data[layer] = {}

        # Clear relation points
        self.relation_points = {}

        # Clear the map name input
        self.map_name_input.text = ""
        self.map_name_input.text_surf = self.map_name_input.font.render("", True, (0, 0, 0))

        # Reset to main map mode
        self.save_mode = "main"
        self.main_map_button.is_selected = True
        self.related_map_button.is_selected = False

        # Clear current main map reference
        self.current_main_map = None

        # Reset selected tile
        self.selected_tile = None

        # Clear brush manager selection
        self.brush_manager.set_selected_tile(None)

        # Deselect all tileset buttons
        for tileset_buttons in self.tileset_manager.tileset_buttons:
            for button_data in tileset_buttons:
                if button_data['button']:
                    button_data['button'].is_selected = False

        # Deselect animated tile buttons
        for button_data in self.tileset_manager.animated_tile_buttons:
            if button_data['button']:
                button_data['button'].is_selected = False

        # Reset camera position
        self.camera_x = 0
        self.camera_y = 0

        # Reset zoom to 100%
        self.reset_zoom()

        # Clear any status messages
        self.map_saver.status_message = ""
        self.map_saver.status_timer = 0

        # Reset relation component to initial state by recreating it
        from edit_mode.ui_components import RelationComponent
        self.relation_component = RelationComponent(self.map_area_width + 20, 150)

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Call the base class resize method
        super().resize(new_width, new_height)

        # Import needed components
        from edit_mode.ui_components import RelationComponent

        # Update map area dimensions (only the width changes)
        self.map_area_width = self.width - self.sidebar_width
        self.map_area_height = self.height

        # Update map_area_width in the tileset_manager
        self.tileset_manager.map_area_width = self.map_area_width

        # Update mode buttons position with proper spacing
        mode_button_width = 80
        mode_button_height = 30
        mode_button_y = 10
        mode_button_spacing = 5

        self.edit_mode_button.rect.topleft = (self.map_area_width + 5, mode_button_y)
        self.browse_mode_button.rect.topleft = (self.map_area_width + 5 + mode_button_width + mode_button_spacing, mode_button_y)
        self.new_map_button.rect.topleft = (self.map_area_width + 5 + 2 * (mode_button_width + mode_button_spacing), mode_button_y)

        # Update tileset button positions
        tileset_button_width = 30
        tileset_button_height = 25
        tileset_button_y = 120
        tileset_button_spacing = 5

        for i, button in enumerate(self.tileset_buttons):
            button.rect.topleft = (
                self.map_area_width + 20 + i * (tileset_button_width + tileset_button_spacing),
                tileset_button_y
            )

        # Recreate tab manager first
        self.tab_manager = TabManager(self.map_area_width, self.sidebar_width)

        # Update UI manager
        self.ui_manager.resize(new_width, new_height)

        # Update save controls position (fixed position)
        save_y = 500  # Fixed Y position for save controls
        self.map_name_input.rect.topleft = (self.map_area_width + 20, save_y)
        self.map_name_input.text_rect = self.map_name_input.text_surf.get_rect(
            midleft=(self.map_name_input.rect.x + 5, self.map_name_input.rect.centery))
        self.save_button.rect.topleft = (self.map_area_width + 210, save_y)

        # Update save option buttons position
        option_y = 250  # Fixed Y position for save option buttons (below map name input)
        self.main_map_button.rect.topleft = (self.map_area_width + 20, option_y)
        self.related_map_button.rect.topleft = (self.map_area_width + 150, option_y)
        self.folder_dropdown.rect.topleft = (self.map_area_width + 20, option_y + 40)

        # If in related map mode, refresh the folder list
        if self.save_mode == "related":
            self.folder_dropdown.set_options(self.map_manager.get_main_map_folders())

        # Update relation component position
        # Save the current relation points
        saved_relation_points = self.relation_points.copy()

        # Create a new relation component
        self.relation_component = RelationComponent(self.map_area_width + 20, 150)

        # Restore the relation points
        self.relation_points = saved_relation_points

        # Sync the relation component with the saved relation points
        self.relation_component.sync_with_relation_points(saved_relation_points)

        # Always reposition tileset buttons with fixed start_y
        self.tileset_manager.position_tileset_buttons(self.selected_tileset_index, start_y=150)

        # Recreate layer manager UI with fixed position
        # We'll pass a fixed height value to maintain consistent positioning
        fixed_height = 720  # Use a fixed reference height
        self.layer_manager.create_ui(self.map_area_width, fixed_height)

        # Recreate brush manager UI
        self.brush_manager.create_ui(self.map_area_width, self.sidebar_width, 150)

        # Entrance manager UI recreation removed

        # Reposition map browser items with fixed dimensions
        self.map_manager.position_map_items(
            self.map_area_width + 20,
            120,
            self.sidebar_width - 40,
            300  # Fixed height for map browser
        )

        # Update help text area position and size
        self.help_text_area = ScrollableTextArea(
            self.map_area_width + 20,  # x position
            120 + 40,                  # y position (120 is the content_y value from EditScreenUI)
            self.sidebar_width - 40,   # width
            self.height - 200          # height
        )

    def get_help_instructions(self):
        """Get the help instructions for the scrollable text area"""
        return [
            "Left click/drag: Place tiles",
            "Right click/drag: Remove tiles",
            "Arrow keys or WASD: Move view (hold for acceleration)",
            "P key: Toggle tile preview following cursor",
            "Shift + scroll: Move selection horizontally",
            "Alt + scroll: Move selection vertically",
            "Ctrl + scroll: Zoom in/out",
            "",
            "Brush:",
            "- Brush controls are integrated into the Tiles tab",
            "- Sizes: 1x1, 3x3, 5x5, 7x7",
            "- Shapes: Square, Circle",
            "",
            "Layers:",
            "- Left-click a layer number to select it",
            "- Right-click a layer number to toggle full opacity",
            "- Toggle visibility with eye buttons",
            "- Use + and - to add/remove layers",
            "- Onion skin shows inactive layers with transparency",
            "- Show All displays all layers without transparency",
            "",
            "Relations:",
            "- Map teleportation points",
            "- Connect different maps together",
            "- Point A (red) and Point B (blue) must be on different maps",
            "- Right-click to remove placed points",
            "",
            "Save:",
            "- Choose Main Map or Related Map",
            "- Main Map creates a new folder",
            "- Only Main Maps appear in selection screen",
            "- Related Map saves to existing folder",
            "- Enter a name and click Save",
            "",
            "Keyboard Shortcuts:",
            "- Ctrl+Z: Undo last action (not implemented yet)",
            "- Ctrl+Y: Redo last action (not implemented yet)",
            "- Ctrl+S: Quick save (not implemented yet)",
            "",
            "Tips:",
            "- Use layers to organize your map elements",
            "- Layer 0 is typically used for ground/floor tiles",
            "- Higher layers are for objects, walls, decorations",
            "- Use the onion skin feature to see how layers interact",
            "- Save frequently to avoid losing work",
            "- Create a main map first before creating related maps",
            "- Use descriptive names for your maps",
            "",
            "Collision:",
            "- Each tile has 4 collision points (corners)",
            "- Click on dots to toggle collision",
            "- Red dots indicate collision is enabled",
            "- Gray dots indicate no collision",
            "- Collision affects player movement in-game",
            "- Use collision for walls, furniture, obstacles",
            "",
            "Map Organization:",
            "- Main maps appear in the world selection screen",
            "- Related maps are accessed through teleportation",
            "- Use relation points to connect maps",
            "- Maps in the same folder can be connected",
            "- Plan your world structure before creating maps"
        ]

    def _move_tile_selection_horizontal(self, direction):
        """Move tile selection horizontally through the palette grid"""
        if not self.selected_tile:
            return

        # Get the current tileset buttons
        buttons = self.tileset_manager.tileset_buttons[self.selected_tileset_index]

        # Find the current tile's position in the grid
        current_row = self.selected_tile['original_row']
        current_col = self.selected_tile['original_col']

        # Get the tileset layout to understand the grid structure
        layout = self.tileset_manager.tileset_layouts[self.selected_tileset_index]
        tiles_per_row = layout["tiles_per_row"]

        # Calculate new column position
        new_col = current_col + direction

        # Find a tile at the new position
        target_tile = None
        for button_data in buttons:
            if (button_data['original_row'] == current_row and
                button_data['original_col'] == new_col):
                target_tile = button_data
                break

        # If no tile found at exact position, try wrapping to next/previous row
        if not target_tile:
            if direction > 0:  # Moving right, wrap to next row
                new_row = current_row + 1
                new_col = 0
            else:  # Moving left, wrap to previous row
                new_row = current_row - 1
                new_col = tiles_per_row - 1

            # Find tile at wrapped position
            for button_data in buttons:
                if (button_data['original_row'] == new_row and
                    button_data['original_col'] == new_col):
                    target_tile = button_data
                    break

        # If we found a target tile, select it
        if target_tile and target_tile['button']:
            self._select_tile(target_tile)

    def _move_tile_selection_vertical(self, direction):
        """Move tile selection vertically through the palette grid"""
        if not self.selected_tile:
            return

        # Get the current tileset buttons
        buttons = self.tileset_manager.tileset_buttons[self.selected_tileset_index]

        # Find the current tile's position in the grid
        current_row = self.selected_tile['original_row']
        current_col = self.selected_tile['original_col']

        # Calculate new row position
        new_row = current_row + direction

        # Find a tile at the new position
        target_tile = None
        for button_data in buttons:
            if (button_data['original_row'] == new_row and
                button_data['original_col'] == current_col):
                target_tile = button_data
                break

        # If we found a target tile, select it
        if target_tile and target_tile['button']:
            self._select_tile(target_tile)

    def _select_tile(self, target_tile):
        """Helper method to select a specific tile"""
        # Get the current tileset buttons
        buttons = self.tileset_manager.tileset_buttons[self.selected_tileset_index]

        # Deselect all buttons (regular and animated)
        for button_data in buttons:
            if button_data['button']:
                button_data['button'].is_selected = False

        for button_data in self.tileset_manager.animated_tile_buttons:
            if button_data['button']:
                button_data['button'].is_selected = False

        # Select the target tile
        target_tile['button'].is_selected = True
        self.selected_tile = target_tile
        # Update the brush manager with the selected tile
        self.brush_manager.set_selected_tile(target_tile)
