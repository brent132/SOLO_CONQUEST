"""
Mouse Handler - Handles mouse events and interactions

This module manages:
- Mouse button events (left, right, wheel)
- Inventory interactions (HUD, player, chest)
- Lootchest interactions
- Player attack handling
- Mouse wheel inventory selection
- Coordinate conversion for world interactions
"""
import pygame
from typing import Optional, Callable, Tuple, Any, List, Dict


class MouseHandler:
    """Handles mouse events and interactions"""

    def __init__(self, base_grid_cell_size: int = 16):
        self.base_grid_cell_size = base_grid_cell_size

        # Callbacks for different mouse actions
        self.on_inventory_wheel_up = None
        self.on_inventory_wheel_down = None
        self.on_inventory_slot_clicked = None
        self.on_player_attack = None
        self.on_lootchest_interaction = None

        # References to game systems (set by InputSystem)
        self.hud = None
        self.player_inventory = None
        self.chest_inventory = None
        self.player = None
        self.game_systems_coordinator = None

    def set_game_references(self, hud, player_inventory, chest_inventory, player, game_systems_coordinator):
        """Set references to game systems"""
        self.hud = hud
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.player = player
        self.game_systems_coordinator = game_systems_coordinator

    def set_inventory_callbacks(self, wheel_up_callback: Callable, wheel_down_callback: Callable,
                               slot_clicked_callback: Callable):
        """Set callbacks for inventory operations"""
        self.on_inventory_wheel_up = wheel_up_callback
        self.on_inventory_wheel_down = wheel_down_callback
        self.on_inventory_slot_clicked = slot_clicked_callback

    def set_player_attack_callback(self, attack_callback: Callable):
        """Set callback for player attacks"""
        self.on_player_attack = attack_callback

    def set_lootchest_callback(self, lootchest_callback: Callable):
        """Set callback for lootchest interactions"""
        self.on_lootchest_interaction = lootchest_callback

    def handle_mouse_button_down(self, event: pygame.event.Event, mouse_pos: Tuple[int, int],
                                shift_held: bool, camera_x: float, camera_y: float,
                                center_offset_x: float, center_offset_y: float,
                                zoom_factor_inv: float) -> Optional[Any]:
        """
        Handle mouse button down events

        Args:
            event: The pygame MOUSEBUTTONDOWN event
            mouse_pos: Current mouse position
            shift_held: Whether shift key is held
            camera_x: Camera X position
            camera_y: Camera Y position
            center_offset_x: Center offset X for coordinate conversion
            center_offset_y: Center offset Y for coordinate conversion
            zoom_factor_inv: Inverse zoom factor for coordinate conversion

        Returns:
            Optional result from event handling
        """
        if not self.player:
            return None

        # Handle mouse wheel for inventory selection
        if event.button == 4:  # Mouse wheel up
            if self.on_inventory_wheel_up:
                self.on_inventory_wheel_up()
        elif event.button == 5:  # Mouse wheel down
            if self.on_inventory_wheel_down:
                self.on_inventory_wheel_down()
        # Handle left-click for inventory slots, player inventory, and attacks
        elif event.button == 1:  # Left mouse button
            return self._handle_left_click(mouse_pos, shift_held)
        # Handle right-click for inventory item picking or lootchest interaction
        elif event.button == 3:  # Right mouse button
            return self._handle_right_click(mouse_pos, shift_held, camera_x, camera_y,
                                          center_offset_x, center_offset_y, zoom_factor_inv)

        return None

    def _handle_left_click(self, mouse_pos: Tuple[int, int], shift_held: bool) -> Optional[Any]:
        """Handle left mouse button clicks"""
        # NOTE: Inventory clicks are now handled by UIManager → InventoryManager
        # This handler should only deal with non-inventory interactions

        # Check if any inventory is visible - if so, don't handle clicks here
        # The UIManager will handle inventory clicks with proper bounds checking
        if ((self.chest_inventory and self.chest_inventory.is_visible()) or
            (self.player_inventory and self.player_inventory.is_visible())):
            # Inventory is visible, UIManager should handle this
            return None

        # Check if clicking on an inventory slot in the HUD
        elif self.hud and self.hud.inventory.hovered_slot != -1:
            # Select the clicked slot
            if self.on_inventory_slot_clicked:
                self.on_inventory_slot_clicked(self.hud.inventory.hovered_slot)
        else:
            # No inventory slot clicked, use left-click for attack
            if self.on_player_attack:
                self.on_player_attack(mouse_pos)

        return None

    def _handle_right_click(self, mouse_pos: Tuple[int, int], shift_held: bool,
                           camera_x: float, camera_y: float, center_offset_x: float,
                           center_offset_y: float, zoom_factor_inv: float) -> Optional[Any]:
        """Handle right mouse button clicks"""
        # NOTE: Inventory clicks are now handled by UIManager → InventoryManager
        # This handler should only deal with non-inventory interactions

        # Check if any inventory is visible - if so, don't handle clicks here
        # The UIManager will handle inventory clicks with proper bounds checking
        if ((self.chest_inventory and self.chest_inventory.is_visible()) or
            (self.player_inventory and self.player_inventory.is_visible())):
            # Inventory is visible, UIManager should handle this
            return None

        # Check if clicking on a lootchest (only when inventories are not visible)
        elif self.player and not self.player.is_dead:
            # Use game systems coordinator to handle lootchest interaction
            if self.on_lootchest_interaction:
                return self.on_lootchest_interaction(
                    mouse_pos, camera_x, camera_y, center_offset_x, center_offset_y,
                    zoom_factor_inv, self.player.rect
                )

        return None

    def check_lootchest_hover(self, mouse_pos: Tuple[int, int], camera_x: float, camera_y: float,
                             center_offset_x: float, center_offset_y: float, zoom_factor_inv: float,
                             layers: List[Dict], lootchest_id: int) -> bool:
        """
        Check if mouse is hovering over a lootchest

        Args:
            mouse_pos: Current mouse position
            camera_x: Camera X position
            camera_y: Camera Y position
            center_offset_x: Center offset X for coordinate conversion
            center_offset_y: Center offset Y for coordinate conversion
            zoom_factor_inv: Inverse zoom factor for coordinate conversion
            layers: Map layers to check
            lootchest_id: ID of lootchest tiles

        Returns:
            True if hovering over a lootchest
        """
        if not self.game_systems_coordinator:
            return False

        return self.game_systems_coordinator.check_lootchest_at_position(
            mouse_pos, camera_x, camera_y, center_offset_x, center_offset_y,
            zoom_factor_inv, layers, lootchest_id
        )
