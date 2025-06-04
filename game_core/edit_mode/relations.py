"""
Relation components for the Edit Mode
"""
import pygame
from config import *
from font_loader import font_manager


class RelationGroup:
    """A relation group item with modern panel styling like LayerPanel"""
    def __init__(self, id_value, x, y, width=200, height=42):
        self.id = id_value
        self.rect = pygame.Rect(x, y, width, height)
        self.is_selected = False
        self.is_hovered = False

        # Colors matching LayerPanel style
        self.bg_color = (60, 60, 60)
        self.selected_color = (100, 150, 255)
        self.hover_color = (80, 80, 80)
        self.text_color = (220, 220, 220)
        self.border_color = (40, 40, 40)

        # Button colors
        self.button_a_color = (180, 60, 60)  # Darker red
        self.button_a_hover_color = (220, 80, 80)
        self.button_a_selected_color = (255, 100, 100)

        self.button_b_color = (60, 60, 180)  # Darker blue
        self.button_b_hover_color = (80, 80, 220)
        self.button_b_selected_color = (100, 100, 255)

        # UI elements layout
        self.id_rect = pygame.Rect(x + 8, y + 5, 60, 16)
        self.button_a_rect = pygame.Rect(x + width - 70, y + 8, 26, 26)
        self.button_b_rect = pygame.Rect(x + width - 38, y + 8, 26, 26)

        # Button states
        self.button_a_selected = False
        self.button_a_hovered = False
        self.button_b_selected = False
        self.button_b_hovered = False

        # Fonts
        self.id_font = font_loader.get_font('regular', 12)
        self.button_font = font_loader.get_font('regular', 14)

        # Track which button is active
        self.active_button = None  # 'a', 'b', or None

    def set_position(self, x, y):
        """Set the position of the group"""
        width = self.rect.width
        self.rect.topleft = (x, y)
        self.id_rect = pygame.Rect(x + 8, y + 5, 60, 16)
        self.button_a_rect = pygame.Rect(x + width - 70, y + 8, 26, 26)
        self.button_b_rect = pygame.Rect(x + width - 38, y + 8, 26, 26)

    def update(self, mouse_pos):
        """Update hover states based on mouse position"""
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.button_a_hovered = self.button_a_rect.collidepoint(mouse_pos)
        self.button_b_hovered = self.button_b_rect.collidepoint(mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Handle mouse events for the group"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if button A was clicked
            if self.button_a_hovered:
                # Toggle selection state
                was_selected = self.button_a_selected
                self.button_a_selected = not was_selected

                if self.button_a_selected:
                    self.active_button = 'a'
                    # Deselect button B if A is selected
                    self.button_b_selected = False
                else:
                    # Only clear active_button if we're deselecting
                    if was_selected:
                        self.active_button = None
                return True

            # Check if button B was clicked
            elif self.button_b_hovered:
                # Toggle selection state
                was_selected = self.button_b_selected
                self.button_b_selected = not was_selected

                if self.button_b_selected:
                    self.active_button = 'b'
                    # Deselect button A if B is selected
                    self.button_a_selected = False
                else:
                    # Only clear active_button if we're deselecting
                    if was_selected:
                        self.active_button = None
                return True

        return False

    def draw(self, surface):
        """Draw the relation group in LayerPanel style"""
        # Background
        if self.is_selected:
            bg_color = self.selected_color
        elif self.is_hovered:
            bg_color = self.hover_color
        else:
            bg_color = self.bg_color

        pygame.draw.rect(surface, bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 1)

        # ID label
        id_text = self.id_font.render(f"Relation {self.id}", True, self.text_color)
        surface.blit(id_text, (self.id_rect.x, self.id_rect.y))

        # Button A
        if self.button_a_selected:
            a_color = self.button_a_selected_color
        elif self.button_a_hovered:
            a_color = self.button_a_hover_color
        else:
            a_color = self.button_a_color

        pygame.draw.rect(surface, a_color, self.button_a_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.button_a_rect, 2 if self.button_a_selected else 1)

        # Button B
        if self.button_b_selected:
            b_color = self.button_b_selected_color
        elif self.button_b_hovered:
            b_color = self.button_b_hover_color
        else:
            b_color = self.button_b_color

        pygame.draw.rect(surface, b_color, self.button_b_rect)
        pygame.draw.rect(surface, (0, 0, 0), self.button_b_rect, 2 if self.button_b_selected else 1)

        # Button labels
        label_a = self.button_font.render("A", True, (255, 255, 255))
        label_a_rect = label_a.get_rect(center=self.button_a_rect.center)
        surface.blit(label_a, label_a_rect)

        label_b = self.button_font.render("B", True, (255, 255, 255))
        label_b_rect = label_b.get_rect(center=self.button_b_rect.center)
        surface.blit(label_b, label_b_rect)

    @property
    def is_active(self):
        """Check if any button is selected"""
        return self.button_a_selected or self.button_b_selected

    @property
    def height(self):
        """Get the total height of the group"""
        return self.rect.height


class RelationComponent:
    """A modern relations panel with LayerPanel-style interface"""
    def __init__(self, x, y, width=250, height=300):
        # Default dimensions for backward compatibility
        self.rect = pygame.Rect(x, y, width, height)
        self.groups = []
        self.selected_group_index = 0
        self.scroll_offset = 0
        self.max_scroll = 0

        # Panel styling matching LayerPanel
        self.bg_color = (50, 50, 50)
        self.header_color = (40, 40, 40)
        self.border_color = (30, 30, 30)
        self.text_color = (220, 220, 220)

        # Header
        self.header_height = 30
        self.header_rect = pygame.Rect(x, y, width, self.header_height)
        self.content_rect = pygame.Rect(x, y + self.header_height, width, height - self.header_height)

        # Buttons in header (matching LayerPanel style)
        button_size = 20
        button_y = y + 5
        self.add_button = pygame.Rect(x + width - 70, button_y, button_size, button_size)
        self.delete_button = pygame.Rect(x + width - 45, button_y, button_size, button_size)

        # Group item dimensions
        self.item_height = 42
        self.item_spacing = 2

        # Fonts
        self.header_font = font_loader.get_font('regular', 14)

        # Scrolling
        self.scroll_speed = 20

        # Initialize with one group
        self.add_group()

    @property
    def x(self):
        """Get x position for backward compatibility"""
        return self.rect.x

    @property
    def y(self):
        """Get y position for backward compatibility"""
        return self.rect.y

    @property
    def group_spacing(self):
        """Get group spacing for backward compatibility"""
        return self.item_height + self.item_spacing

    def _reposition_groups(self):
        """Legacy method name for backward compatibility"""
        self.reposition_groups()

    def sync_with_relation_points(self, relation_points):
        """Sync the component groups with external relation points data"""
        # Clear existing groups
        self.groups = []

        if not relation_points:
            # If no relation points, create default group
            self.add_group()
            return

        # Sort IDs numerically
        sorted_ids = []
        for id_key in relation_points.keys():
            try:
                sorted_ids.append(int(id_key))
            except ValueError:
                pass
        sorted_ids.sort()

        # Create groups for each ID
        for id_value in sorted_ids:
            group = RelationGroup(
                id_value,
                self.content_rect.x + 2,
                0,  # Will be positioned in reposition_groups
                self.content_rect.width - 4,
                self.item_height
            )
            self.groups.append(group)

        # If no valid groups were created, add default
        if not self.groups:
            self.add_group()
        else:
            # Set selection to first group
            self.selected_group_index = 0
            self.update_selection()
            self.reposition_groups()
            self.update_scroll_bounds()

    def add_group(self):
        """Add a new relation group"""
        group_id = len(self.groups) + 1
        group = RelationGroup(
            group_id,
            self.content_rect.x + 2,
            0,  # Will be positioned in reposition_groups
            self.content_rect.width - 4,
            self.item_height
        )
        self.groups.append(group)
        self.selected_group_index = len(self.groups) - 1
        self.update_selection()
        self.reposition_groups()
        self.update_scroll_bounds()

    def delete_group(self):
        """Delete the currently selected group"""
        if len(self.groups) > 1 and self.selected_group_index < len(self.groups):
            # Get the ID of the group being deleted
            deleted_id = self.groups[self.selected_group_index].id

            # Remove the selected group
            del self.groups[self.selected_group_index]

            # Update group IDs to maintain sequential numbering
            for i, group in enumerate(self.groups):
                group.id = i + 1

            # Adjust selection if needed
            if self.selected_group_index >= len(self.groups):
                self.selected_group_index = len(self.groups) - 1

            self.update_selection()
            self.reposition_groups()
            self.update_scroll_bounds()

            return deleted_id  # Return the ID that was deleted
        return None

    def delete_specific_group(self, group_index):
        """Delete a specific group by index"""
        if len(self.groups) > 1 and 0 <= group_index < len(self.groups):
            # Get the ID of the group being deleted
            deleted_id = self.groups[group_index].id

            # Remove the group
            del self.groups[group_index]

            # Update group IDs to maintain sequential numbering
            for i, group in enumerate(self.groups):
                group.id = i + 1

            # Adjust selection if needed
            if self.selected_group_index >= len(self.groups):
                self.selected_group_index = len(self.groups) - 1
            elif self.selected_group_index > group_index:
                self.selected_group_index -= 1

            self.update_selection()
            self.reposition_groups()
            self.update_scroll_bounds()

            return deleted_id  # Return the ID that was deleted
        return None

    def update_selection(self):
        """Update selection state of all groups"""
        for i, group in enumerate(self.groups):
            group.is_selected = (i == self.selected_group_index)

    def reposition_groups(self):
        """Reposition all groups with scroll offset"""
        for i, group in enumerate(self.groups):
            base_y = self.content_rect.y + i * (self.item_height + self.item_spacing) - self.scroll_offset
            group.set_position(self.content_rect.x + 2, base_y)

    def update_scroll_bounds(self):
        """Update the maximum scroll offset"""
        total_height = len(self.groups) * (self.item_height + self.item_spacing)
        visible_height = self.content_rect.height
        self.max_scroll = max(0, total_height - visible_height)
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

    def scroll(self, delta):
        """Scroll the relations panel"""
        old_offset = self.scroll_offset
        self.scroll_offset += delta * self.scroll_speed
        self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))

        if old_offset != self.scroll_offset:
            self.reposition_groups()
            return True
        return False

    def update(self, mouse_pos):
        """Update all groups"""
        # Update hover states for visible groups
        for group in self.groups:
            if (group.rect.y >= self.content_rect.y and
                group.rect.y + group.rect.height <= self.content_rect.bottom):
                group.update(mouse_pos)

    def handle_event(self, event, mouse_pos):
        """Handle events for the relations panel"""
        # Handle scroll wheel
        if event.type == pygame.MOUSEWHEEL and self.rect.collidepoint(mouse_pos):
            if self.scroll(-event.y):
                return "scrolled"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check header buttons
            if self.add_button.collidepoint(mouse_pos):
                self.add_group()
                return "group_added"
            elif self.delete_button.collidepoint(mouse_pos):
                deleted_id = self.delete_group()
                if deleted_id:
                    return f"group_deleted_{deleted_id}"
                return "group_deleted"

            # Check group items (only if they're visible)
            for i, group in enumerate(self.groups):
                if (group.rect.y >= self.content_rect.y and
                    group.rect.y + group.rect.height <= self.content_rect.bottom):
                    if group.handle_event(event, mouse_pos):
                        # Deselect all other groups
                        for j, other_group in enumerate(self.groups):
                            if j != i:
                                other_group.button_a_selected = False
                                other_group.button_b_selected = False
                                other_group.active_button = None

                        # Set the selected group
                        self.selected_group_index = i
                        self.update_selection()
                        return "group_selected"

        return None

    def draw(self, surface):
        """Draw the relations panel in LayerPanel style"""
        # Panel background
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)

        # Header
        pygame.draw.rect(surface, self.header_color, self.header_rect)
        pygame.draw.line(surface, self.border_color,
                        (self.header_rect.left, self.header_rect.bottom),
                        (self.header_rect.right, self.header_rect.bottom), 1)

        # Header title
        title_text = self.header_font.render("RELATIONS", True, self.text_color)
        title_rect = title_text.get_rect(left=self.header_rect.x + 8, centery=self.header_rect.centery)
        surface.blit(title_text, title_rect)

        # Header buttons
        # Add button (+)
        pygame.draw.rect(surface, (80, 80, 80), self.add_button)
        pygame.draw.rect(surface, self.border_color, self.add_button, 1)
        plus_font = font_loader.get_font('regular', 16)
        plus_text = plus_font.render("+", True, self.text_color)
        plus_rect = plus_text.get_rect(center=self.add_button.center)
        surface.blit(plus_text, plus_rect)

        # Delete button (-)
        pygame.draw.rect(surface, (80, 80, 80), self.delete_button)
        pygame.draw.rect(surface, self.border_color, self.delete_button, 1)
        minus_text = plus_font.render("-", True, self.text_color)
        minus_rect = minus_text.get_rect(center=self.delete_button.center)
        surface.blit(minus_text, minus_rect)

        # Content area background
        pygame.draw.rect(surface, (45, 45, 45), self.content_rect)

        # Set clipping to content area for scrolling
        original_clip = surface.get_clip()
        surface.set_clip(self.content_rect)

        # Draw groups (only visible ones)
        for group in self.groups:
            if (group.rect.bottom >= self.content_rect.y and
                group.rect.y <= self.content_rect.bottom):
                group.draw(surface)

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
        total_height = len(self.groups) * (self.item_height + self.item_spacing)

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

    @property
    def is_active(self):
        """Check if any button in any group is selected"""
        return any(group.is_active for group in self.groups)

    @property
    def active_button(self):
        """Get the active button type ('a', 'b', or None)"""
        if self.selected_group_index < len(self.groups):
            return self.groups[self.selected_group_index].active_button
        return None

    @property
    def current_id(self):
        """Get the ID of the currently selected group"""
        if self.selected_group_index < len(self.groups):
            return self.groups[self.selected_group_index].id
        return 1

    def set_id(self, id_value):
        """Set the ID of the currently selected group (for backward compatibility)"""
        # Find or create a group with the given ID
        for i, group in enumerate(self.groups):
            if group.id == id_value:
                self.selected_group_index = i
                self.update_selection()
                return

        # If not found, create groups up to this ID
        while len(self.groups) < id_value:
            self.add_group()

        # Select the group with the given ID
        self.selected_group_index = id_value - 1
        self.update_selection()

    # Legacy compatibility methods
    def set_button_positions(self, x, y, bottom_y=None):
        """Set the positions of the panel (for backward compatibility)"""
        # Update the entire panel position
        width = self.rect.width
        height = self.rect.height
        self.rect = pygame.Rect(x, y, width, height)
        self.header_rect = pygame.Rect(x, y, width, self.header_height)
        self.content_rect = pygame.Rect(x, y + self.header_height, width, height - self.header_height)

        # Update button positions
        button_size = 20
        button_y = y + 5
        self.add_button = pygame.Rect(x + width - 70, button_y, button_size, button_size)
        self.delete_button = pygame.Rect(x + width - 45, button_y, button_size, button_size)

        # Reposition all groups
        self.reposition_groups()
