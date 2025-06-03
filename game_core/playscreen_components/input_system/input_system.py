"""
Input System - Main coordinator for all input-related functionality

This is the main entry point for all input operations. It coordinates
the individual components (MouseHandler, KeyboardHandler, ZoomController, CursorManager)
to provide a unified interface for handling input events throughout the game.

RESPONSIBILITY: Main coordinator that brings everything together

FEATURES:
- Provides a single interface for all input operations
- Coordinates mouse, keyboard, zoom, and cursor management
- Manages input state and event processing
- Handles input-related callbacks and notifications
- Integrates with other game systems for input handling
"""
import pygame
from typing import Optional, Tuple, Any, List, Dict, Callable

from .mouse_handler import MouseHandler
from .keyboard_handler import KeyboardHandler
from .zoom_controller import ZoomController
from .cursor_manager import CursorManager


class InputSystem:
    """Main coordinator for all input-related functionality"""

    def __init__(self, width: int, height: int, base_grid_cell_size: int = 16):
        # Initialize all components
        self.mouse_handler = MouseHandler(base_grid_cell_size)
        self.keyboard_handler = KeyboardHandler()
        self.zoom_controller = ZoomController(width, height, base_grid_cell_size)
        self.cursor_manager = CursorManager()

        # Current state
        self.is_initialized = False

        # Game system references
        self.hud = None
        self.player_inventory = None
        self.chest_inventory = None
        self.player = None
        self.game_systems_coordinator = None
        self.animated_tile_manager = None

        # Collision system references for unstuck functionality
        self.player_system = None
        self.collision_handler = None
        self.expanded_mapping = None
        self.map_data = None
        self.map_width = 0
        self.map_height = 0

        # Setup callbacks between components
        self._setup_callbacks()

    def initialize_systems(self, hud, player_inventory, chest_inventory, player,
                          game_systems_coordinator, animated_tile_manager):
        """Initialize the input system with game references"""
        self.hud = hud
        self.player_inventory = player_inventory
        self.chest_inventory = chest_inventory
        self.player = player
        self.game_systems_coordinator = game_systems_coordinator
        self.animated_tile_manager = animated_tile_manager

        # Set references in mouse handler
        self.mouse_handler.set_game_references(
            hud, player_inventory, chest_inventory, player, game_systems_coordinator
        )

        # Setup shared cursor system
        self.cursor_manager.setup_shared_cursor_system(player_inventory, chest_inventory)

        self.is_initialized = True

    def set_collision_system(self, player_system, collision_handler, expanded_mapping, map_data, map_width, map_height):
        """Set collision system references for unstuck functionality

        Args:
            player_system: The player system instance
            collision_handler: The collision handler instance
            expanded_mapping: The tile mapping
            map_data: The map data for collision detection
            map_width: Map width in tiles
            map_height: Map height in tiles
        """
        self.player_system = player_system
        self.collision_handler = collision_handler
        self.expanded_mapping = expanded_mapping
        self.map_data = map_data
        self.map_width = map_width
        self.map_height = map_height

    def _setup_callbacks(self):
        """Setup callbacks between input components"""
        # Zoom callbacks
        self.keyboard_handler.set_zoom_callbacks(
            self.zoom_controller.zoom_in,
            self.zoom_controller.zoom_out,
            self.zoom_controller.reset_zoom
        )

        # Inventory callbacks
        self.keyboard_handler.set_inventory_callbacks(
            self._on_inventory_slot_selected,
            self._on_inventory_previous,
            self._on_inventory_next
        )

        self.mouse_handler.set_inventory_callbacks(
            self._on_inventory_wheel_up,
            self._on_inventory_wheel_down,
            self._on_inventory_slot_clicked
        )

        # Other callbacks
        self.keyboard_handler.set_escape_callback(self._on_escape_pressed)
        self.keyboard_handler.set_unstuck_callback(self._on_unstuck_player)
        self.mouse_handler.set_player_attack_callback(self._on_player_attack)
        self.mouse_handler.set_lootchest_callback(self._on_lootchest_interaction)

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> Optional[str]:
        """
        Handle input events

        Args:
            event: The pygame event
            mouse_pos: Current mouse position

        Returns:
            Optional[str]: Return value from event handling
        """
        if not self.is_initialized:
            return None

        # Handle keyboard events
        if event.type == pygame.KEYDOWN:
            return self.keyboard_handler.handle_keydown_event(event)

        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.player:
                shift_held = self.keyboard_handler.is_shift_held()
                zoom_info = self.zoom_controller.get_zoom_info()

                return self.mouse_handler.handle_mouse_button_down(
                    event, mouse_pos, shift_held,
                    zoom_info['camera_x'], zoom_info['camera_y'],
                    zoom_info['center_offset_x'], zoom_info['center_offset_y'],
                    zoom_info['zoom_factor_inv']
                )

        return None

    def update(self, mouse_pos: Tuple[int, int]):
        """Update input system state"""
        if not self.is_initialized:
            return

        # Check if mouse is hovering over a lootchest
        hovered_lootchest = self._check_lootchest_hover(mouse_pos)

        # Update cursor based on hover state
        hud_hovered_slot = self.hud.inventory.hovered_slot if self.hud else -1
        self.cursor_manager.update_cursor_state(hud_hovered_slot, hovered_lootchest)

    def _check_lootchest_hover(self, mouse_pos: Tuple[int, int]) -> bool:
        """Check if mouse is hovering over a lootchest"""
        if not self.animated_tile_manager or not hasattr(self, 'layers'):
            return False

        # Get the lootchest item ID
        lootchest_id = self.animated_tile_manager.get_animated_tile_id("lootchest_item")
        if not lootchest_id:
            return False

        zoom_info = self.zoom_controller.get_zoom_info()
        return self.mouse_handler.check_lootchest_hover(
            mouse_pos, zoom_info['camera_x'], zoom_info['camera_y'],
            zoom_info['center_offset_x'], zoom_info['center_offset_y'],
            zoom_info['zoom_factor_inv'], getattr(self, 'layers', []), lootchest_id
        )

    # Callback implementations
    def _on_inventory_slot_selected(self, slot: int):
        """Handle inventory slot selection"""
        if self.hud:
            self.hud.inventory.selected_slot = slot

    def _on_inventory_previous(self):
        """Handle previous inventory slot selection"""
        if self.hud:
            num_slots = self.hud.inventory.num_slots
            self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot - 1) % num_slots

    def _on_inventory_next(self):
        """Handle next inventory slot selection"""
        if self.hud:
            num_slots = self.hud.inventory.num_slots
            self.hud.inventory.selected_slot = (self.hud.inventory.selected_slot + 1) % num_slots

    def _on_inventory_wheel_up(self):
        """Handle mouse wheel up for inventory"""
        self._on_inventory_previous()

    def _on_inventory_wheel_down(self):
        """Handle mouse wheel down for inventory"""
        self._on_inventory_next()

    def _on_inventory_slot_clicked(self, slot: int):
        """Handle inventory slot click"""
        if self.hud:
            self.hud.inventory.selected_slot = slot

    def _on_player_attack(self, mouse_pos: Tuple[int, int]):
        """Handle player attack"""
        if self.player:
            # Create a mock mouse event for the player
            mock_event = type('MockEvent', (), {
                'type': pygame.MOUSEBUTTONDOWN,
                'button': 1,
                'pos': mouse_pos
            })()
            self.player.handle_mouse_event(mock_event)

    def _on_lootchest_interaction(self, mouse_pos: Tuple[int, int], camera_x: float, camera_y: float,
                                 center_offset_x: float, center_offset_y: float, zoom_factor_inv: float,
                                 player_rect: pygame.Rect) -> Any:
        """Handle lootchest interaction"""
        if self.game_systems_coordinator:
            return self.game_systems_coordinator.handle_lootchest_interaction(
                mouse_pos, camera_x, camera_y, center_offset_x, center_offset_y,
                zoom_factor_inv, player_rect
            )
        return None

    def _on_escape_pressed(self) -> Optional[str]:
        """Handle ESC key press for inventory toggling"""
        # This will be implemented by the PlayScreen
        # Return a signal that ESC was pressed
        return "escape_pressed"

    def _on_unstuck_player(self):
        """Handle unstuck player request"""
        if not all([self.player_system, self.collision_handler, self.expanded_mapping, self.map_data]):
            print("Warning: Cannot unstuck player - collision system not initialized")
            return

        # Attempt to unstuck the player
        unstuck_success = self.player_system.unstuck_player(
            self.collision_handler, self.expanded_mapping, self.map_data, self.map_width, self.map_height
        )

        if not unstuck_success:
            print("Player is not stuck or could not be unstuck")

    # Public interface methods
    def get_zoom_controller(self) -> ZoomController:
        """Get the zoom controller"""
        return self.zoom_controller

    def get_cursor_manager(self) -> CursorManager:
        """Get the cursor manager"""
        return self.cursor_manager

    def set_map_data(self, layers: List[Dict], map_width: int, map_height: int):
        """Set map data for input processing"""
        self.layers = layers
        self.zoom_controller.set_map_dimensions(map_width, map_height)

    def set_player(self, player):
        """Set the current player"""
        self.player = player
        self.mouse_handler.player = player

    def update_player(self, player):
        """Update the current player reference"""
        self.player = player
        self.mouse_handler.player = player

    def resize(self, new_width: int, new_height: int):
        """Handle screen resize by updating all input components"""
        # Update zoom controller dimensions
        self.zoom_controller.resize(new_width, new_height)
