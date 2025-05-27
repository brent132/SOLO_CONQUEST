"""
Brush Manager - handles brush functionality for the edit mode
"""
import pygame
import math

class BrushManager:
    """Manages brush functionality for the edit mode"""
    def __init__(self):
        # Brush settings
        self.brush_size = 1  # Default to 1x1 (single tile)
        self.brush_shape = "square"  # "square" or "circle"

        # Available brush sizes
        self.available_sizes = [1, 3, 5]

        # Available brush shapes
        self.available_shapes = ["square", "circle"]

        # UI elements
        self.size_buttons = {}
        self.shape_buttons = {}

        # Preview surface
        self.preview_surface = None

        # Selected tile for preview
        self.selected_tile = None

        # Update preview
        self.update_preview()

    def update_preview(self):
        """Update the brush preview surface"""
        # Size of the preview in pixels (each tile is 16x16)
        tile_size = 16
        max_size = max(self.available_sizes)
        preview_size = max_size * tile_size

        # Create a transparent surface
        self.preview_surface = pygame.Surface((preview_size, preview_size), pygame.SRCALPHA)

        # Draw the brush preview
        if self.brush_shape == "square":
            self._draw_square_preview(tile_size)
        else:  # circle
            self._draw_circle_preview(tile_size)

    def _draw_square_preview(self, tile_size):
        """Draw a square brush preview"""
        # Calculate the offset to center the brush
        max_size = max(self.available_sizes)
        offset = (max_size - self.brush_size) // 2 * tile_size

        # Draw the square brush
        for y in range(self.brush_size):
            for x in range(self.brush_size):
                rect = pygame.Rect(
                    offset + x * tile_size,
                    offset + y * tile_size,
                    tile_size,
                    tile_size
                )

                # If we have a selected tile, draw it in each brush cell
                if self.selected_tile and 'image' in self.selected_tile:
                    # Scale the tile image to fit the preview cell
                    scaled_image = pygame.transform.scale(self.selected_tile['image'], (tile_size, tile_size))
                    self.preview_surface.blit(scaled_image, rect)
                else:
                    # Fill with semi-transparent blue if no tile is selected
                    pygame.draw.rect(self.preview_surface, (0, 120, 255, 128), rect)

                # Draw border around each cell
                pygame.draw.rect(self.preview_surface, (0, 0, 0, 200), rect, 1)

    def _draw_circle_preview(self, tile_size):
        """Draw a circle brush preview"""
        # Calculate the center of the preview
        max_size = max(self.available_sizes)
        center_x = center_y = max_size * tile_size // 2

        # Calculate the radius in tiles
        radius_tiles = self.brush_size // 2

        # Draw the circle brush
        for y in range(max_size):
            for x in range(max_size):
                # Calculate the center of this tile
                tile_center_x = (x + 0.5) * tile_size
                tile_center_y = (y + 0.5) * tile_size

                # Calculate distance from the center in tile units
                dx = (tile_center_x - center_x) / tile_size
                dy = (tile_center_y - center_y) / tile_size
                distance = math.sqrt(dx*dx + dy*dy)

                # If the tile is within the radius, draw it
                if distance <= radius_tiles:
                    rect = pygame.Rect(
                        x * tile_size,
                        y * tile_size,
                        tile_size,
                        tile_size
                    )

                    # If we have a selected tile, draw it in each brush cell
                    if self.selected_tile and 'image' in self.selected_tile:
                        # Scale the tile image to fit the preview cell
                        scaled_image = pygame.transform.scale(self.selected_tile['image'], (tile_size, tile_size))
                        self.preview_surface.blit(scaled_image, rect)
                    else:
                        # Fill with semi-transparent blue if no tile is selected
                        pygame.draw.rect(self.preview_surface, (0, 120, 255, 128), rect)

                    # Draw border around each cell
                    pygame.draw.rect(self.preview_surface, (0, 0, 0, 200), rect, 1)

    def set_brush_size(self, size):
        """Set the brush size"""
        if size in self.available_sizes:
            self.brush_size = size
            self.update_preview()

    def set_brush_shape(self, shape):
        """Set the brush shape"""
        if shape in self.available_shapes:
            self.brush_shape = shape
            self.update_preview()

    def set_selected_tile(self, tile):
        """Set the selected tile for the brush preview"""
        self.selected_tile = tile
        self.update_preview()

    def create_ui(self, map_area_width, sidebar_width, start_y):
        """Create UI elements for the brush settings"""
        # Calculate button dimensions
        button_width = (sidebar_width - 60) // len(self.available_sizes)
        button_height = 30

        # Create size buttons
        for i, size in enumerate(self.available_sizes):
            x = map_area_width + 20 + i * (button_width + 5)
            y = start_y
            self.size_buttons[size] = pygame.Rect(x, y, button_width, button_height)

        # Create shape buttons
        shape_button_width = (sidebar_width - 40) // len(self.available_shapes)
        for i, shape in enumerate(self.available_shapes):
            x = map_area_width + 20 + i * (shape_button_width + 5)
            y = start_y + button_height + 10
            self.shape_buttons[shape] = pygame.Rect(x, y, shape_button_width, button_height)

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for brush settings"""
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False

        # Check size button clicks
        for size, button in self.size_buttons.items():
            if button.collidepoint(mouse_pos):
                self.set_brush_size(size)
                return True

        # Check shape button clicks
        for shape, button in self.shape_buttons.items():
            if button.collidepoint(mouse_pos):
                self.set_brush_shape(shape)
                return True

        return False

    def draw(self, surface, font):
        """Draw the brush settings UI"""
        # Draw section title
        title = font.render("Brush Settings", True, (50, 50, 50))
        title_rect = title.get_rect(topleft=(self.size_buttons[1].left, self.size_buttons[1].top - 50))
        surface.blit(title, title_rect)

        # Draw size buttons
        size_label = font.render("", True, (50, 50, 50))
        size_label_rect = size_label.get_rect(topleft=(self.size_buttons[1].left - 5, self.size_buttons[1].top - 5))
        size_label_rect.bottom = self.size_buttons[1].top - 5
        surface.blit(size_label, size_label_rect)

        for size, button in self.size_buttons.items():
            # Determine button color based on selection
            if size == self.brush_size:
                bg_color = (180, 200, 255)  # Blue for selected
                text_color = (0, 0, 0)
            else:
                bg_color = (220, 220, 220)  # Light gray for unselected
                text_color = (100, 100, 100)

            # Draw button
            pygame.draw.rect(surface, bg_color, button)
            pygame.draw.rect(surface, (100, 100, 100), button, 1)

            # Draw label
            text = font.render(f"{size}x{size}", True, text_color)
            text_rect = text.get_rect(center=button.center)
            surface.blit(text, text_rect)

        # Draw shape buttons
        shape_label = font.render("", True, (50, 50, 50))
        shape_label_rect = shape_label.get_rect(topleft=(self.shape_buttons["square"].left - 5, self.shape_buttons["square"].top - 5))
        shape_label_rect.bottom = self.shape_buttons["square"].top - 5
        surface.blit(shape_label, shape_label_rect)

        for shape, button in self.shape_buttons.items():
            # Determine button color based on selection
            if shape == self.brush_shape:
                bg_color = (180, 200, 255)  # Blue for selected
                text_color = (0, 0, 0)
            else:
                bg_color = (220, 220, 220)  # Light gray for unselected
                text_color = (100, 100, 100)

            # Draw button
            pygame.draw.rect(surface, bg_color, button)
            pygame.draw.rect(surface, (100, 100, 100), button, 1)

            # Draw label
            text = font.render(shape.capitalize(), True, text_color)
            text_rect = text.get_rect(center=button.center)
            surface.blit(text, text_rect)

        # Draw preview
        preview_label = font.render("Preview:", True, (50, 50, 50))
        preview_y = self.shape_buttons["square"].bottom + 15
        preview_label_rect = preview_label.get_rect(topleft=(self.shape_buttons["square"].left - 5, preview_y))
        surface.blit(preview_label, preview_label_rect)

        # Draw the preview centered below the buttons
        preview_rect = self.preview_surface.get_rect()
        preview_rect.top = preview_y + 25
        preview_rect.centerx = (self.size_buttons[1].left + self.size_buttons[self.available_sizes[-1]].right) // 2
        surface.blit(self.preview_surface, preview_rect)

    def get_brush_tiles(self, center_x, center_y):
        """Get the grid positions for all tiles in the brush"""
        tiles = []

        # Calculate the brush radius (half the size, rounded down)
        radius = self.brush_size // 2

        # For square brush, just return all tiles in the square
        if self.brush_shape == "square":
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    tiles.append((center_x + x, center_y + y))

        # For circle brush, calculate distance from center
        else:  # circle
            for y in range(-radius, radius + 1):
                for x in range(-radius, radius + 1):
                    # Calculate distance from center
                    distance = math.sqrt(x*x + y*y)

                    # If the tile is within the radius, add it
                    if distance <= radius:
                        tiles.append((center_x + x, center_y + y))

        return tiles
