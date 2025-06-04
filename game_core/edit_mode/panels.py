"""
Panel components for the Edit Mode
"""
import pygame
from config import *
from font_manager import font_manager


class LayerItem:
    """Photoshop-style layer item with thumbnail, name, visibility, and opacity"""
    def __init__(self, x, y, width, height, layer_index, layer_name="Layer"):
        self.rect = pygame.Rect(x, y, width, height)
        self.layer_index = layer_index
        self.layer_name = layer_name
        self.is_visible = True
        self.is_selected = False
        self.is_hovered = False
        self.opacity = 100  # 0-100%
        self.blend_mode = "Normal"

        # UI elements
        self.thumbnail_rect = pygame.Rect(x + 5, y + 5, 32, 32)
        self.visibility_rect = pygame.Rect(x + 42, y + 12, 18, 18)
        self.name_rect = pygame.Rect(x + 65, y + 5, width - 120, 20)
        self.opacity_rect = pygame.Rect(x + 65, y + 25, width - 120, 12)

        # Colors
        self.bg_color = (60, 60, 60)
        self.selected_color = (100, 150, 255)
        self.hover_color = (80, 80, 80)
        self.text_color = (220, 220, 220)
        self.border_color = (40, 40, 40)

        # Fonts
        self.name_font = font_manager.get_font('regular', 14)
        self.opacity_font = font_manager.get_font('regular', 10)

        # Dragging state
        self.is_dragging = False
        self.drag_offset_y = 0

    def update(self, mouse_pos):
        """Update hover state"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for this layer item"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.visibility_rect.collidepoint(mouse_pos):
                # Toggle visibility
                self.is_visible = not self.is_visible
                return "visibility_toggle"
            elif self.rect.collidepoint(mouse_pos):
                # Select layer
                return "select"
        return None

    def draw(self, surface):
        """Draw the layer item in Photoshop style"""
        # Background
        if self.is_selected:
            bg_color = self.selected_color
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.bg_color

        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 1)

        # Thumbnail (placeholder - could show actual layer preview)
        thumbnail_color = (120, 120, 120) if self.is_visible else (60, 60, 60)
        pygame.draw.rect(surface, thumbnail_color, self.thumbnail_rect)
        pygame.draw.rect(surface, self.border_color, self.thumbnail_rect, 1)

        # Layer number in thumbnail
        thumb_text = self.name_font.render(str(self.layer_index + 1), True, self.text_color)
        thumb_rect = thumb_text.get_rect(center=self.thumbnail_rect.center)
        surface.blit(thumb_text, thumb_rect)

        # Visibility eye icon
        eye_color = (255, 255, 255) if self.is_visible else (100, 100, 100)
        if self.is_visible:
            # Draw eye icon
            pygame.draw.circle(surface, eye_color, self.visibility_rect.center, 6, 2)
            pygame.draw.circle(surface, eye_color, self.visibility_rect.center, 3)
        else:
            # Draw X
            pygame.draw.line(surface, eye_color,
                           (self.visibility_rect.left + 3, self.visibility_rect.top + 3),
                           (self.visibility_rect.right - 3, self.visibility_rect.bottom - 3), 2)
            pygame.draw.line(surface, eye_color,
                           (self.visibility_rect.right - 3, self.visibility_rect.top + 3),
                           (self.visibility_rect.left + 3, self.visibility_rect.bottom - 3), 2)

        # Layer name
        name_text = self.name_font.render(self.layer_name, True, self.text_color)
        surface.blit(name_text, (self.name_rect.x, self.name_rect.y))

        # Opacity percentage
        opacity_text = self.opacity_font.render(f"Opacity: {self.opacity}%", True, (180, 180, 180))
        surface.blit(opacity_text, (self.opacity_rect.x, self.opacity_rect.y))


class LayerPanel:
    """Photoshop-style layer panel"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.layer_items = []
        self.selected_layer = 0
        self.scroll_offset = 0
        self.max_layers = 5
        self.max_scroll = 0

        # Panel styling
        self.bg_color = (50, 50, 50)
        self.header_color = (40, 40, 40)
        self.border_color = (30, 30, 30)
        self.text_color = (220, 220, 220)

        # Header
        self.header_height = 30
        self.header_rect = pygame.Rect(x, y, width, self.header_height)
        self.content_rect = pygame.Rect(x, y + self.header_height, width, height - self.header_height)

        # Buttons
        button_size = 20
        button_y = y + 5
        self.add_button = pygame.Rect(x + width - 70, button_y, button_size, button_size)
        self.delete_button = pygame.Rect(x + width - 45, button_y, button_size, button_size)
        self.show_all_button = pygame.Rect(x + width - 95, button_y, button_size, button_size)

        # Layer item dimensions
        self.item_height = 42
        self.item_spacing = 2

        # Fonts
        self.header_font = font_manager.get_font('regular', 14)

        # Scrolling
        self.scroll_speed = 20

        # Track deleted layers for data cleanup
        self.last_deleted_layer = None

        # Show all layers state
        self.show_all_layers = False

        # Initialize with one layer
        self.add_layer()

    def add_layer(self, name=None):
        """Add a new layer"""
        if len(self.layer_items) < self.max_layers:
            layer_index = len(self.layer_items)
            if name is None:
                name = f"Layer {layer_index + 1}"

            layer_item = LayerItem(
                self.content_rect.x + 2,
                0,  # Will be positioned in reposition_items
                self.content_rect.width - 4,
                self.item_height,
                layer_index,
                name
            )
            self.layer_items.append(layer_item)
            self.selected_layer = layer_index
            self.update_selection()
            self.reposition_items()
            self.update_scroll_bounds()

    def delete_layer(self):
        """Delete the selected layer"""
        if len(self.layer_items) > 1 and self.selected_layer < len(self.layer_items):
            # Store which layer we're deleting for data cleanup
            deleted_layer_index = self.selected_layer
            self.last_deleted_layer = deleted_layer_index

            del self.layer_items[self.selected_layer]

            # Update indices and names for all remaining layers
            for i, item in enumerate(self.layer_items):
                item.layer_index = i
                item.layer_name = f"Layer {i + 1}"

            # Adjust selection
            if self.selected_layer >= len(self.layer_items):
                self.selected_layer = len(self.layer_items) - 1

            self.update_selection()
            self.reposition_items()
            self.update_scroll_bounds()

    def toggle_show_all_layers(self):
        """Toggle show all layers mode"""
        self.show_all_layers = not self.show_all_layers
        return "toggle_show_all"

    def update_selection(self):
        """Update selection state of all layer items"""
        for i, item in enumerate(self.layer_items):
            item.is_selected = (i == self.selected_layer)

    def reposition_items(self):
        """Reposition all layer items with scroll offset"""
        for i, item in enumerate(self.layer_items):
            # Calculate position with scroll offset
            base_y = self.content_rect.y + i * (self.item_height + self.item_spacing) - self.scroll_offset

            item.rect.y = base_y
            item.thumbnail_rect.y = base_y + 5
            item.visibility_rect.y = base_y + 12
            item.name_rect.y = base_y + 5
            item.opacity_rect.y = base_y + 25

    def update_scroll_bounds(self):
        """Update the maximum scroll offset"""
        total_height = len(self.layer_items) * (self.item_height + self.item_spacing)
        visible_height = self.content_rect.height
        self.max_scroll = max(0, total_height - visible_height)

        # Clamp current scroll offset
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def scroll(self, delta):
        """Scroll the layer panel"""
        old_offset = self.scroll_offset
        self.scroll_offset += delta * self.scroll_speed
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        # Reposition items if scroll changed
        if old_offset != self.scroll_offset:
            self.reposition_items()
            return True
        return False

    def handle_event(self, event, mouse_pos):
        """Handle events for the layer panel"""
        # Handle scroll wheel
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos):
            if self.scroll(-event.y):  # Negative for natural scrolling
                return "scrolled"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check header buttons
            if self.add_button.collidepoint(mouse_pos):
                self.add_layer()
                return "layer_added"
            elif self.delete_button.collidepoint(mouse_pos):
                self.delete_layer()
                return "layer_deleted"
            elif self.show_all_button.collidepoint(mouse_pos):
                return self.toggle_show_all_layers()

            # Check layer items (only if they're visible in the content area)
            for i, item in enumerate(self.layer_items):
                # Check if item is visible in the content area
                if (item.rect.y >= self.content_rect.y and
                    item.rect.y + item.rect.height <= self.content_rect.bottom):
                    result = item.handle_event(event, mouse_pos)
                    if result == "select":
                        self.selected_layer = i
                        self.update_selection()
                        return "layer_selected"
                    elif result == "visibility_toggle":
                        return "visibility_changed"

        # Update hover states (only for visible items)
        for item in self.layer_items:
            if (item.rect.y >= self.content_rect.y and
                item.rect.y + item.rect.height <= self.content_rect.bottom):
                item.update(mouse_pos)

        return None

    def draw(self, surface):
        """Draw the layer panel"""
        # Panel background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Header
        pygame.draw.rect(surface, self.header_color, self.header_rect)
        pygame.draw.line(surface, self.border_color,
                        (self.header_rect.left, self.header_rect.bottom),
                        (self.header_rect.right, self.header_rect.bottom), 1)

        # Header title
        title_text = self.header_font.render("LAYERS", True, self.text_color)
        title_rect = title_text.get_rect(left=self.header_rect.x + 8, centery=self.header_rect.centery)
        surface.blit(title_text, title_rect)

        # Header buttons
        # Add button (+)
        pygame.draw.rect(surface, (80, 80, 80), self.add_button)
        pygame.draw.rect(surface, self.border_color, self.add_button, 1)
        plus_font = font_manager.get_font('regular', 16)
        plus_text = plus_font.render("+", True, self.text_color)
        plus_rect = plus_text.get_rect(center=self.add_button.center)
        surface.blit(plus_text, plus_rect)

        # Delete button (-)
        pygame.draw.rect(surface, (80, 80, 80), self.delete_button)
        pygame.draw.rect(surface, self.border_color, self.delete_button, 1)
        minus_text = plus_font.render("-", True, self.text_color)
        minus_rect = minus_text.get_rect(center=self.delete_button.center)
        surface.blit(minus_text, minus_rect)

        # Show all layers button (eye icon)
        button_color = (120, 180, 120) if self.show_all_layers else (80, 80, 80)
        pygame.draw.rect(surface, button_color, self.show_all_button)
        pygame.draw.rect(surface, self.border_color, self.show_all_button, 1)
        eye_text = plus_font.render("👁", True, self.text_color)
        eye_rect = eye_text.get_rect(center=self.show_all_button.center)
        surface.blit(eye_text, eye_rect)

        # Content area background
        pygame.draw.rect(surface, (45, 45, 45), self.content_rect)

        # Set clipping to content area for scrolling
        original_clip = surface.get_clip()
        surface.set_clip(self.content_rect)

        # Layer items (draw in reverse order - top layer first, only visible ones)
        for item in reversed(self.layer_items):
            # Only draw if item is at least partially visible
            if (item.rect.bottom >= self.content_rect.y and
                item.rect.y <= self.content_rect.bottom):
                item.draw(surface)

        # Restore original clipping
        surface.set_clip(original_clip)

        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            self.draw_scroll_indicator(surface)

    def draw_scroll_indicator(self, surface):
        """Draw a scroll indicator on the right side"""
        indicator_width = 4
        indicator_x = self.content_rect.right - indicator_width - 2

        # Calculate indicator position and size
        content_height = self.content_rect.height
        total_height = len(self.layer_items) * (self.item_height + self.item_spacing)

        if total_height > content_height:
            # Calculate indicator height and position
            indicator_height = max(10, int((content_height / total_height) * content_height))
            scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            indicator_y = self.content_rect.y + int(scroll_ratio * (content_height - indicator_height))

            # Draw scroll track
            track_rect = pygame.Rect(indicator_x, self.content_rect.y, indicator_width, content_height)
            pygame.draw.rect(surface, (30, 30, 30), track_rect)

            # Draw scroll thumb
            thumb_rect = pygame.Rect(indicator_x, indicator_y, indicator_width, indicator_height)
            pygame.draw.rect(surface, (100, 100, 100), thumb_rect)


class BrushPanel:
    """Modern brush panel with Photoshop-style interface"""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.bg_color = (50, 50, 50)
        self.header_color = (40, 40, 40)
        self.border_color = (30, 30, 30)
        self.text_color = (220, 220, 220)

        # Header
        self.header_height = 30
        self.header_rect = pygame.Rect(x, y, width, self.header_height)
        self.content_rect = pygame.Rect(x, y + self.header_height, width, height - self.header_height)

        # Brush settings
        self.brush_size = 1
        self.brush_shape = "square"
        self.available_sizes = [1, 3, 5, 7]
        self.available_shapes = ["square", "circle"]

        # UI elements
        self.size_buttons = []
        self.shape_buttons = []
        self.preview_rect = None

        # Fonts
        self.header_font = font_manager.get_font('regular', 14)
        self.button_font = font_manager.get_font('regular', 12)

        # Selected tile for preview
        self.selected_tile = None

        # Create UI elements
        self.create_ui_elements()

    def create_ui_elements(self):
        """Create brush UI elements optimized for 250px width"""
        content_x = self.content_rect.x + 8
        content_y = self.content_rect.y + 8
        content_width = self.content_rect.width - 16

        # Size section - arrange in 2x2 grid for better fit
        size_label_y = content_y
        size_buttons_y = size_label_y + 20

        # Arrange size buttons in 2x2 grid
        button_width = (content_width - 5) // 2  # 2 columns with 5px gap
        button_height = 22

        self.size_buttons = []
        for i, size in enumerate(self.available_sizes):
            row = i // 2
            col = i % 2
            x = content_x + col * (button_width + 5)
            y = size_buttons_y + row * (button_height + 5)
            button_rect = pygame.Rect(x, y, button_width, button_height)
            self.size_buttons.append({
                'rect': button_rect,
                'size': size,
                'selected': size == self.brush_size
            })

        # Shape section - arrange horizontally with more spacing
        shape_label_y = size_buttons_y + 2 * (button_height + 5) + 15  # After 2 rows of size buttons + extra space
        shape_buttons_y = shape_label_y + 25  # More space between label and buttons

        shape_button_width = (content_width - 5) // len(self.available_shapes)  # 5 = 1 gap

        self.shape_buttons = []
        for i, shape in enumerate(self.available_shapes):
            x = content_x + i * (shape_button_width + 5)
            button_rect = pygame.Rect(x, shape_buttons_y, shape_button_width, button_height)
            self.shape_buttons.append({
                'rect': button_rect,
                'shape': shape,
                'selected': shape == self.brush_shape
            })

        # No preview section - removed for cleaner, more compact layout
        self.preview_rect = None

    def set_brush_size(self, size):
        """Set brush size and update UI"""
        if size in self.available_sizes:
            self.brush_size = size
            # Update button selection
            for button in self.size_buttons:
                button['selected'] = button['size'] == size

    def set_brush_shape(self, shape):
        """Set brush shape and update UI"""
        if shape in self.available_shapes:
            self.brush_shape = shape
            # Update button selection
            for button in self.shape_buttons:
                button['selected'] = button['shape'] == shape

    def set_selected_tile(self, tile):
        """Set the selected tile for preview"""
        self.selected_tile = tile

    def handle_event(self, event, mouse_pos):
        """Handle mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check size buttons
            for button in self.size_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.set_brush_size(button['size'])
                    return "size_changed"

            # Check shape buttons
            for button in self.shape_buttons:
                if button['rect'].collidepoint(mouse_pos):
                    self.set_brush_shape(button['shape'])
                    return "shape_changed"

        return None

    def draw(self, surface):
        """Draw the brush panel"""
        # Panel background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Header
        pygame.draw.rect(surface, self.header_color, self.header_rect)
        pygame.draw.line(surface, self.border_color,
                        (self.header_rect.left, self.header_rect.bottom),
                        (self.header_rect.right, self.header_rect.bottom), 1)

        # Header title
        title_text = self.header_font.render("BRUSH", True, self.text_color)
        title_rect = title_text.get_rect(left=self.header_rect.x + 8, centery=self.header_rect.centery)
        surface.blit(title_text, title_rect)

        # Content area background
        pygame.draw.rect(surface, (45, 45, 45), self.content_rect)

        # Size section
        size_label = self.button_font.render("Size:", True, self.text_color)
        surface.blit(size_label, (self.content_rect.x + 10, self.content_rect.y + 10))

        # Size buttons
        for button in self.size_buttons:
            if button['selected']:
                bg_color = (100, 150, 255)
                text_color = (255, 255, 255)
                border_color = (80, 130, 235)
            else:
                bg_color = (70, 70, 70)
                text_color = (200, 200, 200)
                border_color = (50, 50, 50)

            pygame.draw.rect(surface, bg_color, button['rect'])
            pygame.draw.rect(surface, border_color, button['rect'], 1)

            text = self.button_font.render(f"{button['size']}x{button['size']}", True, text_color)
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Shape section
        shape_y = self.size_buttons[0]['rect'].bottom + 30  # More space to avoid overlap
        shape_label = self.button_font.render("Shape:", True, self.text_color)
        surface.blit(shape_label, (self.content_rect.x + 8, shape_y))

        # Shape buttons
        for button in self.shape_buttons:
            if button['selected']:
                bg_color = (100, 150, 255)
                text_color = (255, 255, 255)
                border_color = (80, 130, 235)
            else:
                bg_color = (70, 70, 70)
                text_color = (200, 200, 200)
                border_color = (50, 50, 50)

            pygame.draw.rect(surface, bg_color, button['rect'])
            pygame.draw.rect(surface, border_color, button['rect'], 1)

            # Draw shape text
            if button['shape'] == "square":
                shape_text = "Square"
            else:
                shape_text = "Circle"

            text = self.button_font.render(shape_text, True, text_color)
            text_rect = text.get_rect(center=button['rect'].center)
            surface.blit(text, text_rect)

        # Preview section removed for cleaner layout