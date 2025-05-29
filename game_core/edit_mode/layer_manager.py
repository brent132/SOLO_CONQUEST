"""
Layer Manager - handles layer operations for the edit mode with Photoshop-style interface
"""
import pygame
from edit_mode.ui_components import LayerPanel, LayerItem

class LayerManager:
    """Manages layers for the edit mode with Photoshop-style interface"""
    def __init__(self, sidebar_width, max_layers=5):
        self.sidebar_width = sidebar_width
        self.max_layers = max_layers
        self.current_layer = 0
        self.layer_count = 1  # Start with one layer
        self.layer_visibility = [True] * max_layers  # All layers visible by default
        self.layer_full_opacity = [False] * max_layers  # Tracks which layers should be shown at full opacity
        self.onion_skin_enabled = True
        self.show_all_layers = False  # Flag for showing all layers without transparency
        self.select_all_mode = False  # Flag for editing all layers at once
        self.reference_layer = 0  # Reference layer when in select_all_mode

        # Photoshop-style layer panel
        self.layer_panel = None

        # Legacy UI properties (kept for compatibility)
        self.layer_buttons = []
        self.layer_visibility_buttons = []
        self.add_layer_button = None
        self.remove_layer_button = None
        self.onion_skin_button = None
        self.show_all_button = None

        # Font for layer labels
        self.font = pygame.font.SysFont(None, 20)

        # Layer panel dimensions
        self.panel_height = 0

    def create_ui(self, map_area_width, _height=None):
        """Create UI components for layer management"""
        # Create Photoshop-style layer panel (positioned side by side with brush panel)
        # Right side of sidebar (second half)
        brush_panel_width = (self.sidebar_width - 30) // 2  # Half sidebar width minus spacing
        panel_x = map_area_width + 10 + brush_panel_width + 10  # After brush panel + spacing
        panel_y = 510  # Same Y position as brush panel
        panel_width = (self.sidebar_width - 30) // 2  # Half sidebar width minus spacing
        panel_height = 200

        self.layer_panel = LayerPanel(panel_x, panel_y, panel_width, panel_height)

        # Sync initial state
        self.sync_to_panel()

        # Legacy button creation for compatibility
        self.create_legacy_ui(map_area_width)

    def create_legacy_ui(self, map_area_width):
        """Create legacy UI for compatibility"""
        panel_y = 510
        left_padding = 30
        button_width = 30
        button_height = 25
        spacing = 8

        # Clear previous buttons
        self.layer_buttons = []
        self.layer_visibility_buttons = []

        # Create layer selection buttons
        for i in range(self.max_layers):
            button_x = map_area_width + left_padding
            button_y = panel_y + i * (button_height + spacing)
            layer_button = pygame.Rect(button_x, button_y, button_width, button_height)
            self.layer_buttons.append(layer_button)

            visibility_x = button_x + button_width + spacing
            visibility_button = pygame.Rect(visibility_x, button_y, button_width, button_height)
            self.layer_visibility_buttons.append(visibility_button)

        # Control buttons
        control_y = panel_y + self.max_layers * (button_height + spacing) + 15
        self.add_layer_button = pygame.Rect(map_area_width + left_padding, control_y, button_width, button_height)
        self.remove_layer_button = pygame.Rect(map_area_width + left_padding + button_width + spacing, control_y, button_width, button_height)

        # Toggle buttons
        self.onion_skin_button = pygame.Rect(
            map_area_width + left_padding + (button_width + spacing) * 2 + 15,
            panel_y,
            button_width * 2 + spacing,
            button_height
        )
        self.show_all_button = pygame.Rect(
            map_area_width + left_padding + (button_width + spacing) * 2 + (button_width * 2 + spacing) + 25,
            panel_y,
            button_width * 2 + spacing,
            button_height
        )

        if self.show_all_button:
            self.panel_height = (self.show_all_button.bottom - panel_y) + 15

    def sync_to_panel(self):
        """Sync layer manager state to the layer panel"""
        if not self.layer_panel:
            return

        # Clear existing items and rebuild
        self.layer_panel.layer_items.clear()

        # Add layers to match current state
        for i in range(self.layer_count):
            layer_name = f"Layer {i + 1}"
            self.layer_panel.layer_items.append(
                LayerItem(
                    self.layer_panel.content_rect.x + 2,
                    0,  # Will be positioned in reposition_items
                    self.layer_panel.content_rect.width - 4,
                    self.layer_panel.item_height,
                    i,
                    layer_name
                )
            )

        # Sync visibility and selection
        for i, item in enumerate(self.layer_panel.layer_items):
            if i < len(self.layer_visibility):
                item.is_visible = self.layer_visibility[i]

        self.layer_panel.selected_layer = self.current_layer
        self.layer_panel.show_all_layers = self.show_all_layers
        self.layer_panel.update_selection()
        self.layer_panel.reposition_items()
        self.layer_panel.update_scroll_bounds()

    def sync_from_panel(self):
        """Sync layer panel state back to layer manager"""
        if not self.layer_panel:
            return

        self.layer_count = len(self.layer_panel.layer_items)
        self.current_layer = self.layer_panel.selected_layer
        self.show_all_layers = self.layer_panel.show_all_layers

        # Sync visibility
        for i, item in enumerate(self.layer_panel.layer_items):
            if i < len(self.layer_visibility):
                self.layer_visibility[i] = item.is_visible

    def handle_event(self, event, mouse_pos, map_data=None):
        """Handle mouse events for layer controls"""
        # First try the new layer panel
        if self.layer_panel:
            result = self.layer_panel.handle_event(event, mouse_pos)
            if result:
                # Check if a layer was deleted and clean up map data
                if result == "layer_deleted" and map_data is not None:
                    # Use the tracked deleted layer index for proper data shifting
                    if hasattr(self.layer_panel, 'last_deleted_layer') and self.layer_panel.last_deleted_layer is not None:
                        self.delete_layer_with_data_cleanup(map_data, self.layer_panel.last_deleted_layer)
                        self.layer_panel.last_deleted_layer = None  # Reset after use
                    else:
                        self.cleanup_map_data_after_deletion(map_data)
                # Handle show all layers toggle
                elif result == "toggle_show_all":
                    self.show_all_layers = not self.show_all_layers
                # Sync changes back to layer manager
                self.sync_from_panel()
                return True

        # Fallback to legacy controls
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        # Check layer selection buttons
        for i, button in enumerate(self.layer_buttons):
            if i < self.layer_count and button.collidepoint(mouse_pos):
                # Handle right-click for toggling full opacity for this layer
                if event.button == 3:  # Right mouse button
                    # Toggle full opacity for this specific layer
                    self.layer_full_opacity[i] = not self.layer_full_opacity[i]
                    return True
                # Handle left-click for normal selection
                elif event.button == 1:  # Left mouse button
                    # Turn off select all mode if it was on
                    self.select_all_mode = False
                    self.current_layer = i
                    self.sync_to_panel()  # Sync to panel
                    return True

        # Check visibility toggle buttons
        for i, button in enumerate(self.layer_visibility_buttons):
            if i < self.layer_count and button.collidepoint(mouse_pos):
                self.layer_visibility[i] = not self.layer_visibility[i]
                self.sync_to_panel()  # Sync to panel
                return True

        # Check add layer button
        if self.add_layer_button.collidepoint(mouse_pos):
            self.add_layer()
            return True

        # Check remove layer button
        if self.remove_layer_button.collidepoint(mouse_pos):
            old_layer_count = self.layer_count
            self.remove_layer()
            # Clean up map data if a layer was actually removed
            if self.layer_count < old_layer_count and map_data is not None:
                self.cleanup_map_data_after_deletion(map_data)
            return True

        # Check onion skin toggle button
        if self.onion_skin_button.collidepoint(mouse_pos):
            self.onion_skin_enabled = not self.onion_skin_enabled
            return True

        # Check show all layers button
        if self.show_all_button.collidepoint(mouse_pos):
            self.show_all_layers = not self.show_all_layers
            return True

        return False

    def cleanup_map_data_after_deletion(self, map_data):
        """Clean up map data after a layer is deleted"""
        if not map_data:
            return

        # Get the current layer count after deletion
        current_count = self.layer_count

        # Clear all layers beyond the current count
        for layer_index in range(current_count, self.max_layers):
            if layer_index in map_data:
                map_data[layer_index].clear()

        # Ensure we have empty dictionaries for all valid layers
        for layer_index in range(current_count):
            if layer_index not in map_data:
                map_data[layer_index] = {}

    def delete_layer_with_data_cleanup(self, map_data, deleted_layer_index):
        """Delete a layer and properly shift map data"""
        if not map_data or self.layer_count <= 1:
            return

        # Store the current layer count before deletion
        old_count = self.layer_count

        # Shift map data down for layers above the deleted one
        for layer_index in range(deleted_layer_index, old_count - 1):
            if layer_index + 1 in map_data:
                map_data[layer_index] = map_data[layer_index + 1].copy()
            else:
                map_data[layer_index] = {}

        # Clear the top layer (which is now empty after shifting)
        if old_count - 1 in map_data:
            map_data[old_count - 1].clear()

        # Update layer count and selection
        self.layer_count -= 1
        if self.current_layer >= self.layer_count:
            self.current_layer = self.layer_count - 1

    def add_layer(self):
        """Add a new layer if under the maximum"""
        if self.layer_count < self.max_layers:
            self.layer_count += 1
            # Set the new layer as the current one
            self.current_layer = self.layer_count - 1
            self.sync_to_panel()

    def remove_layer(self):
        """Remove the current layer if more than one exists"""
        if self.layer_count > 1:
            # Shift layers up if removing a layer that's not the last one
            if self.current_layer < self.layer_count - 1:
                # We'll handle the actual data shifting in the EditScreen class
                pass

            self.layer_count -= 1
            # Adjust current layer if needed
            if self.current_layer >= self.layer_count:
                self.current_layer = self.layer_count - 1
            self.sync_to_panel()

    def draw(self, surface):
        """Draw the layer management UI"""
        # Draw the new Photoshop-style layer panel
        if self.layer_panel:
            self.layer_panel.draw(surface)
            return

        # Fallback to legacy UI
        self.draw_legacy_ui(surface)

    def draw_legacy_ui(self, surface):
        """Draw the legacy layer management UI"""
        # Check if buttons are initialized
        if not self.layer_buttons:
            return

        # Get the position of the first layer button
        first_button = self.layer_buttons[0]

        # Draw layer title with more space
        title = self.font.render("Layer Controls", True, (50, 50, 50))
        title_rect = title.get_rect(topleft=(first_button.x, first_button.y - 30))
        surface.blit(title, title_rect)

        # Draw layer buttons
        for i, button in enumerate(self.layer_buttons):
            if i < self.layer_count:
                # Determine button color based on selection state
                if self.select_all_mode:
                    # In select all mode, highlight all buttons with a special color
                    color = (255, 200, 100)  # Orange-yellow for select all mode
                    # Make the reference layer slightly brighter
                    if i == self.reference_layer:
                        color = (255, 220, 120)
                else:
                    # Normal mode - highlight only the current layer
                    if self.layer_full_opacity[i]:
                        # Use a bright green color for layers with full opacity enabled
                        color = (100, 255, 150) if i == self.current_layer else (150, 255, 200)
                    else:
                        # Regular colors for normal layers
                        color = (100, 150, 255) if i == self.current_layer else (200, 200, 200)

                pygame.draw.rect(surface, color, button)

                # Draw a thicker border for select all mode or full opacity
                border_width = 2 if (self.select_all_mode or self.layer_full_opacity[i]) else 1
                border_color = (0, 150, 0) if self.layer_full_opacity[i] else (100, 100, 100)
                pygame.draw.rect(surface, border_color, button, border_width)

                # Draw layer number
                text = self.font.render(str(i + 1), True, (0, 0, 0))
                text_rect = text.get_rect(center=button.center)
                surface.blit(text, text_rect)

                # Draw visibility button
                vis_color = (150, 255, 150) if self.layer_visibility[i] else (255, 150, 150)
                pygame.draw.rect(surface, vis_color, self.layer_visibility_buttons[i])
                pygame.draw.rect(surface, (100, 100, 100), self.layer_visibility_buttons[i], 1)

                # Draw eye icon or X
                if self.layer_visibility[i]:
                    text = self.font.render("👁", True, (0, 0, 0))
                else:
                    text = self.font.render("✕", True, (0, 0, 0))
                text_rect = text.get_rect(center=self.layer_visibility_buttons[i].center)
                surface.blit(text, text_rect)

        # Draw add/remove layer buttons
        pygame.draw.rect(surface, (150, 255, 150), self.add_layer_button)
        pygame.draw.rect(surface, (100, 100, 100), self.add_layer_button, 1)
        text = self.font.render("+", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.add_layer_button.center)
        surface.blit(text, text_rect)

        pygame.draw.rect(surface, (255, 150, 150), self.remove_layer_button)
        pygame.draw.rect(surface, (100, 100, 100), self.remove_layer_button, 1)
        text = self.font.render("-", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.remove_layer_button.center)
        surface.blit(text, text_rect)

        # Draw onion skin toggle button
        onion_color = (150, 255, 150) if self.onion_skin_enabled else (200, 200, 200)
        pygame.draw.rect(surface, onion_color, self.onion_skin_button)
        pygame.draw.rect(surface, (100, 100, 100), self.onion_skin_button, 1)
        text = self.font.render("Onion", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.onion_skin_button.center)
        surface.blit(text, text_rect)

        # Draw show all layers button
        show_all_color = (150, 255, 150) if self.show_all_layers else (200, 200, 200)
        pygame.draw.rect(surface, show_all_color, self.show_all_button)
        pygame.draw.rect(surface, (100, 100, 100), self.show_all_button, 1)
        text = self.font.render("Show all", True, (0, 0, 0))
        text_rect = text.get_rect(center=self.show_all_button.center)
        surface.blit(text, text_rect)
