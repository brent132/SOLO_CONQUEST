"""
Layer Manager - handles layer operations for the edit mode
"""
import pygame

class LayerManager:
    """Manages layers for the edit mode"""
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

        # UI properties
        self.layer_buttons = []
        self.layer_visibility_buttons = []
        self.add_layer_button = None
        self.remove_layer_button = None
        self.onion_skin_button = None
        self.show_all_button = None  # Button for showing all layers without transparency

        # Font for layer labels
        self.font = pygame.font.SysFont(None, 20)

        # Layer panel dimensions will be calculated based on buttons
        self.panel_height = 0  # Will be set in create_ui

    def create_ui(self, map_area_width, _height=None):
        """Create UI components for layer management"""
        # Use a fixed position for the layer panel regardless of screen height
        panel_y = 510  # Fixed position for layer panel

        # Increase padding from the left edge
        left_padding = 30

        # Create layer buttons
        button_width = 30
        button_height = 25
        spacing = 8  # Increased spacing between buttons

        # Clear previous buttons
        self.layer_buttons = []
        self.layer_visibility_buttons = []

        # Create layer selection buttons
        for i in range(self.max_layers):
            # Layer button (for selection)
            button_x = map_area_width + left_padding
            button_y = panel_y + i * (button_height + spacing)

            # Create a rect for the layer button
            layer_button = pygame.Rect(button_x, button_y, button_width, button_height)
            self.layer_buttons.append(layer_button)

            # Layer visibility toggle button
            visibility_x = button_x + button_width + spacing
            visibility_button = pygame.Rect(visibility_x, button_y, button_width, button_height)
            self.layer_visibility_buttons.append(visibility_button)

        # Add/Remove layer buttons - add more space before control buttons
        control_y = panel_y + self.max_layers * (button_height + spacing) + 15

        # Add layer button
        self.add_layer_button = pygame.Rect(
            map_area_width + left_padding,
            control_y,
            button_width,
            button_height
        )

        # Remove layer button
        self.remove_layer_button = pygame.Rect(
            map_area_width + left_padding + button_width + spacing,
            control_y,
            button_width,
            button_height
        )

        # Onion skin toggle button - position it to the right of the layer 1 visibility button
        self.onion_skin_button = pygame.Rect(
            map_area_width + left_padding + (button_width + spacing) * 2 + 15,  # Position to the right of visibility button
            panel_y,  # Same y as the first layer button (layer 1)
            button_width * 2 + spacing,
            button_height
        )

        # Show all layers button - position it to the right of the onion skin button
        self.show_all_button = pygame.Rect(
            map_area_width + left_padding + (button_width + spacing) * 2 + (button_width * 2 + spacing) + 25,  # Further right
            panel_y,  # Same y as the first layer button (layer 1)
            button_width * 2 + spacing,
            button_height
        )

        # Calculate panel height based on the buttons
        if self.show_all_button:
            # Panel height is the distance from the first button to the last button plus padding
            self.panel_height = (self.show_all_button.bottom - panel_y) + 15

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for layer controls"""
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
                    return True

        # Check visibility toggle buttons
        for i, button in enumerate(self.layer_visibility_buttons):
            if i < self.layer_count and button.collidepoint(mouse_pos):
                self.layer_visibility[i] = not self.layer_visibility[i]
                return True

        # Check add layer button
        if self.add_layer_button.collidepoint(mouse_pos):
            self.add_layer()
            return True

        # Check remove layer button
        if self.remove_layer_button.collidepoint(mouse_pos):
            self.remove_layer()
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

    def add_layer(self):
        """Add a new layer if under the maximum"""
        if self.layer_count < self.max_layers:
            self.layer_count += 1
            # Set the new layer as the current one
            self.current_layer = self.layer_count - 1

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

    def draw(self, surface):
        """Draw the layer management UI"""
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
