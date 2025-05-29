"""
Edit Screen UI module - handles drawing the UI elements for the edit screen
"""
import pygame
from settings import *
from font_manager import font_manager

class EditScreenUI:
    """Handles drawing the UI elements for the edit screen"""
    def __init__(self, map_area_width, sidebar_width, height):
        self.map_area_width = map_area_width
        self.sidebar_width = sidebar_width
        self.height = height

        # Sidebar settings
        self.sidebar_color = (240, 240, 240)  # Light gray sidebar
        self.sidebar_border_color = (180, 180, 180)

        # Grid settings (will be updated dynamically based on zoom)
        self.grid_color = (200, 200, 200)  # Light gray grid lines
        self.grid_line_width = 1

        # Edit screen title
        self.title_font = font_manager.get_font('semibold', FONT_SIZE_LARGE)
        self.title_text = ""
        self.title_surf = self.title_font.render(self.title_text, True, (50, 50, 50))
        # Position title below the mode buttons
        self.title_rect = self.title_surf.get_rect(topleft=(self.map_area_width + 20, 80))

    def draw_grid(self, surface, camera_x, camera_y, map_area_height, grid_cell_size):
        """Draw the grid lines"""
        # Draw vertical lines
        for x in range(0, self.map_area_width + 1, grid_cell_size):
            adjusted_x = x - (camera_x % grid_cell_size)
            pygame.draw.line(surface, self.grid_color, (adjusted_x, 0),
                            (adjusted_x, map_area_height), self.grid_line_width)

        # Draw horizontal lines
        for y in range(0, map_area_height + 1, grid_cell_size):
            adjusted_y = y - (camera_y % grid_cell_size)
            pygame.draw.line(surface, self.grid_color, (0, adjusted_y),
                            (self.map_area_width, adjusted_y), self.grid_line_width)

    def draw_sidebar(self, surface, tab_manager, tileset_manager, layer_manager,
                    map_saver, map_name_input, save_button, edit_mode_button,
                    browse_mode_button, new_map_button, selected_tileset_index, collision_manager=None,
                    collision_toggle_rect=None, brush_manager=None, editor=None):
        """Draw the sidebar with tabs and content based on active tab"""
        # Draw sidebar background
        sidebar_rect = pygame.Rect(self.map_area_width, 0, self.sidebar_width, self.height)
        pygame.draw.rect(surface, self.sidebar_color, sidebar_rect)
        pygame.draw.line(surface, self.sidebar_border_color,
                        (self.map_area_width, 0), (self.map_area_width, self.height), 2)

        # Draw mode buttons
        edit_mode_button.draw(surface)
        browse_mode_button.draw(surface)
        new_map_button.draw(surface)

        # Draw tabs first
        tab_manager.draw(surface)

        # Draw title - positioned below the tabs
        surface.blit(self.title_surf, self.title_rect)

        # Create a content area with fixed position
        content_y = 120  # Fixed position for content area

        # Draw content based on active tab
        font = font_manager.get_font('regular', FONT_SIZE_MEDIUM)
        small_font = font_manager.get_font('light', FONT_SIZE_SMALL)

        # Draw status message if active (always visible)
        map_saver.draw_status(
            surface,
            self.map_area_width + 20,
            self.height - 30,
            font
        )

        # Draw content based on active tab
        if tab_manager.active_tab == "Tiles":
            # Draw tileset switching buttons (handled by editor)
            if editor and hasattr(editor, 'tileset_buttons'):
                for button in editor.tileset_buttons:
                    button.draw(surface)

            # Draw tileset buttons
            tileset_manager.draw_tileset(surface, selected_tileset_index)

            # Draw brush panel (integrated into Tiles tab)
            if brush_manager:
                brush_manager.draw(surface, font)

            # Draw a separator line at a fixed position
            separator_y = 490  # Fixed position for separator line

            # Draw a nicer separator with padding
            pygame.draw.rect(surface, (220, 220, 220),
                           pygame.Rect(self.map_area_width + 10, separator_y - 5,
                                      self.sidebar_width - 20, 10))
            pygame.draw.line(surface, (180, 180, 180),
                            (self.map_area_width + 15, separator_y),
                            (self.map_area_width + self.sidebar_width - 15, separator_y), 2)

            # Draw layer manager UI below the separator
            layer_manager.draw(surface)

        elif tab_manager.active_tab == "Collision" and collision_manager:
            # Draw tileset switching buttons (handled by editor)
            if editor and hasattr(editor, 'tileset_buttons'):
                for button in editor.tileset_buttons:
                    button.draw(surface)

            # Draw tileset with collision dots
            tileset_manager.draw_tileset(surface, selected_tileset_index)

            # Draw collision dots on each regular tile
            # Note: Collision dots in the sidebar don't need zoom scaling since they're UI elements
            for button_data in tileset_manager.tileset_buttons[selected_tileset_index]:
                button = button_data['button']
                if button:
                    source_path = button_data.get('source_path', '')
                    if source_path:
                        collision_manager.draw_collision_dots(surface, button.rect, source_path, 1.0)

            # Draw collision dots on animated tiles if we're on the last tileset
            if selected_tileset_index == len(tileset_manager.tileset_buttons) - 1 and tileset_manager.animated_tile_buttons:
                for button_data in tileset_manager.animated_tile_buttons:
                    button = button_data['button']
                    if button:
                        source_path = button_data.get('source_path', '')
                        if source_path:
                            collision_manager.draw_collision_dots(surface, button.rect, source_path, 1.0)

            # Toggle dots visibility button removed

        elif tab_manager.active_tab == "Save":
            # Draw save controls
            save_title = font.render("Save Map", True, (50, 50, 50))
            title_rect = save_title.get_rect(topleft=(self.map_area_width + 20, content_y))
            surface.blit(save_title, title_rect)

            # Use the editor instance passed as parameter

            # Draw map name label first (at the top)
            map_name_label = font.render("Map Name:", True, (50, 50, 50))
            label_rect = map_name_label.get_rect(topleft=(self.map_area_width + 20, content_y + 40))
            surface.blit(map_name_label, label_rect)

            # Position and draw text input and save button
            map_name_input.rect.topleft = (self.map_area_width + 20, content_y + 70)
            map_name_input.text_rect = map_name_input.text_surf.get_rect(
                midleft=(map_name_input.rect.x + 5, map_name_input.rect.centery))
            save_button.rect.topleft = (self.map_area_width + 210, content_y + 70)

            # Draw text input and save button
            map_name_input.draw(surface)
            save_button.draw(surface)

            # Draw save options section below the map name
            options_y = content_y + 120
            options_title = font.render("Save Options:", True, (50, 50, 50))
            options_rect = options_title.get_rect(topleft=(self.map_area_width + 20, options_y))
            surface.blit(options_title, options_rect)

            # Position and draw save option buttons
            option_y = options_y + 30
            if editor:
                # Update button positions
                editor.main_map_button.rect.topleft = (self.map_area_width + 20, option_y)
                editor.related_map_button.rect.topleft = (self.map_area_width + 150, option_y)

                # Draw the buttons
                editor.main_map_button.draw(surface)
                editor.related_map_button.draw(surface)

                # If related map is selected, show the dropdown
                if editor.save_mode == "related":
                    # Draw dropdown label
                    folder_label = font.render("Select Parent Folder:", True, (50, 50, 50))
                    folder_rect = folder_label.get_rect(topleft=(self.map_area_width + 20, option_y + 40))
                    surface.blit(folder_label, folder_rect)

                    # Position and draw the dropdown
                    editor.folder_dropdown.rect.topleft = (self.map_area_width + 20, option_y + 70)
                    editor.folder_dropdown.draw(surface)



        elif tab_manager.active_tab == "Relations":
            # Draw the relation component if editor is provided
            if editor and hasattr(editor, 'relation_component'):
                # Position the relation component directly without instructions
                y_pos = content_y + 20

                # Calculate the available height for the relation groups
                available_height = self.height - y_pos - 50  # Leave 50 pixels at the bottom for add/delete buttons

                # Position the relation component with add/delete buttons at the bottom
                editor.relation_component.set_button_positions(
                    self.map_area_width + 20,
                    y_pos,
                    self.height - 40  # Position 40 pixels from the bottom
                )

                # Draw the relation component
                editor.relation_component.draw(surface)

        elif tab_manager.active_tab == "Help":
            # Draw help content
            help_title = font.render("Controls & Tips", True, (50, 50, 50))
            title_rect = help_title.get_rect(topleft=(self.map_area_width + 20, content_y))
            surface.blit(help_title, title_rect)

            # Draw instructions if show_tips is enabled
            if tab_manager.show_tips:
                # Use the scrollable text area from the editor
                if editor and hasattr(editor, 'help_text_area'):
                    # Draw the scrollable text area
                    editor.help_text_area.draw(surface)
            else:
                # Show a message to click for tips
                text = font.render("Click this tab again to show tips", True, (100, 100, 100))
                text_rect = text.get_rect(topleft=(self.map_area_width + 20, content_y + 40))
                surface.blit(text, text_rect)

        return None  # collision_toggle_rect removed

    def draw_browser_sidebar(self, surface, map_manager, edit_mode_button, browse_mode_button, new_map_button):
        """Draw the sidebar for the map browser"""
        # Draw sidebar background
        sidebar_rect = pygame.Rect(0, 0, self.map_area_width + self.sidebar_width, self.height)
        pygame.draw.rect(surface, (240, 240, 240), sidebar_rect)

        # Draw mode buttons
        edit_mode_button.draw(surface)
        browse_mode_button.draw(surface)
        new_map_button.draw(surface)

        # Draw map browser
        font = font_manager.get_font('regular', FONT_SIZE_MEDIUM)
        map_manager.draw(surface, font)

    def draw_map_tiles(self, surface, map_data, layer_manager, grid_cell_size, camera_x, camera_y, map_area_width, map_area_height):
        """Draw the placed tiles on the map with layer support"""
        # Draw layers from bottom to top
        for layer in range(layer_manager.layer_count):
            # Skip if layer is not visible
            if not layer_manager.layer_visibility[layer]:
                continue

            # Apply onion skin effect for non-active layers
            alpha = 255  # Full opacity by default

            # Layer should be at full opacity if any of these conditions are true:
            # 1. It's the current active layer
            # 2. show_all_layers is enabled (global setting)
            # 3. This specific layer has full opacity enabled (via right-click)
            # 4. Onion skin is disabled

            # Only apply transparency if all these conditions are met:
            # 1. It's not the current layer
            # 2. Onion skin is enabled
            # 3. show_all_layers is disabled
            # 4. This specific layer doesn't have full opacity enabled
            if (layer != layer_manager.current_layer and
                layer_manager.onion_skin_enabled and
                not layer_manager.show_all_layers and
                not layer_manager.layer_full_opacity[layer]):
                # Create a semi-transparent surface for onion skin effect
                alpha = 128  # Half opacity for non-active layers

            # Draw all tiles in this layer
            for (grid_x, grid_y), tile_data in map_data[layer].items():
                # Calculate screen position
                screen_x = grid_x * grid_cell_size - camera_x
                screen_y = grid_y * grid_cell_size - camera_y

                # Skip tiles outside the visible area
                if (screen_x < -grid_cell_size or screen_x > map_area_width or
                    screen_y < -grid_cell_size or screen_y > map_area_height):
                    continue

                # Check if this is an animated tile
                if 'animated_tile_id' in tile_data:
                    # Get the singleton instance of AnimatedTileManager
                    from gameplay.animated_tile_manager import AnimatedTileManager
                    animated_tile_manager = AnimatedTileManager()  # This will return the singleton instance

                    # Get the current frame of the animated tile
                    animated_tile_id = tile_data['animated_tile_id']
                    frame = animated_tile_manager.get_animated_tile_frame(animated_tile_id)

                    if frame:
                        # Scale the frame to match the grid cell size
                        scaled_frame = pygame.transform.scale(frame, (grid_cell_size, grid_cell_size))

                        # Draw the animated tile frame with appropriate alpha
                        if alpha == 255:
                            # Full opacity - draw directly
                            surface.blit(scaled_frame, (screen_x, screen_y))
                        else:
                            # Create a copy with adjusted alpha for onion skin effect
                            frame_copy = scaled_frame.copy()
                            frame_copy.set_alpha(alpha)
                            surface.blit(frame_copy, (screen_x, screen_y))
                else:
                    # Regular tile - scale to match grid cell size
                    scaled_image = pygame.transform.scale(tile_data['image'], (grid_cell_size, grid_cell_size))

                    # Draw with appropriate alpha
                    if alpha == 255:
                        # Full opacity - draw directly
                        surface.blit(scaled_image, (screen_x, screen_y))
                    else:
                        # Create a copy with adjusted alpha for onion skin effect
                        tile_copy = scaled_image.copy()
                        tile_copy.set_alpha(alpha)
                        surface.blit(tile_copy, (screen_x, screen_y))

    def resize(self, new_width, new_height):
        """Handle screen resize"""
        # Update dimensions
        self.map_area_width = new_width - self.sidebar_width
        self.height = new_height

        # Update title position - below the tabs (fixed position)
        self.title_rect = self.title_surf.get_rect(topleft=(self.map_area_width + 20, 80))
