"""
Keyboard Handler - Handles keyboard events and shortcuts

This module manages:
- Keyboard event processing
- Inventory selection shortcuts (number keys, Q/E)
- Zoom control shortcuts (Ctrl+Plus, Ctrl+Minus, Ctrl+0)
- ESC key for inventory toggling
- Modifier key detection (Shift, Ctrl)
"""
import pygame
from typing import Optional, Callable, Any


class KeyboardHandler:
    """Handles keyboard events and shortcuts"""
    
    def __init__(self):
        # Callbacks for different keyboard actions
        self.on_zoom_in = None
        self.on_zoom_out = None
        self.on_zoom_reset = None
        self.on_inventory_slot_selected = None
        self.on_inventory_previous = None
        self.on_inventory_next = None
        self.on_escape_pressed = None
        
    def set_zoom_callbacks(self, zoom_in_callback: Callable, zoom_out_callback: Callable, 
                          zoom_reset_callback: Callable):
        """Set callbacks for zoom operations"""
        self.on_zoom_in = zoom_in_callback
        self.on_zoom_out = zoom_out_callback
        self.on_zoom_reset = zoom_reset_callback
        
    def set_inventory_callbacks(self, slot_selected_callback: Callable, 
                               previous_callback: Callable, next_callback: Callable):
        """Set callbacks for inventory operations"""
        self.on_inventory_slot_selected = slot_selected_callback
        self.on_inventory_previous = previous_callback
        self.on_inventory_next = next_callback
        
    def set_escape_callback(self, escape_callback: Callable):
        """Set callback for ESC key"""
        self.on_escape_pressed = escape_callback
        
    def handle_keydown_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        Handle keyboard down events
        
        Args:
            event: The pygame KEYDOWN event
            
        Returns:
            Optional[str]: Return value from callbacks, or None
        """
        # Check for Ctrl key combinations first
        keys = pygame.key.get_pressed()
        ctrl_held = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        
        if ctrl_held:
            if event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                # Ctrl++ to zoom in
                if self.on_zoom_in:
                    self.on_zoom_in()
                return None
            elif event.key == pygame.K_MINUS:
                # Ctrl+- to zoom out
                if self.on_zoom_out:
                    self.on_zoom_out()
                return None
            elif event.key == pygame.K_0:
                # Ctrl+0 to reset zoom
                if self.on_zoom_reset:
                    self.on_zoom_reset()
                return None

        # ESC key to toggle player inventory
        if event.key == pygame.K_ESCAPE:
            if self.on_escape_pressed:
                return self.on_escape_pressed()

        # Number keys 1-0 for inventory selection (0 is the 10th slot)
        elif pygame.K_1 <= event.key <= pygame.K_9:
            # Convert key to slot index (0-8)
            slot = event.key - pygame.K_1
            if self.on_inventory_slot_selected:
                self.on_inventory_slot_selected(slot)
        elif event.key == pygame.K_0:
            # 0 key selects the 10th slot (index 9)
            if self.on_inventory_slot_selected:
                self.on_inventory_slot_selected(9)

        # Q and E keys for inventory selection
        elif event.key == pygame.K_q:
            # Previous slot
            if self.on_inventory_previous:
                self.on_inventory_previous()
        elif event.key == pygame.K_e:
            # Next slot
            if self.on_inventory_next:
                self.on_inventory_next()

        return None
        
    def is_shift_held(self) -> bool:
        """Check if shift key is currently held"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
    def is_ctrl_held(self) -> bool:
        """Check if ctrl key is currently held"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        
    def is_alt_held(self) -> bool:
        """Check if alt key is currently held"""
        keys = pygame.key.get_pressed()
        return keys[pygame.K_LALT] or keys[pygame.K_RALT]
        
    def get_modifier_state(self) -> dict:
        """Get the current state of all modifier keys"""
        keys = pygame.key.get_pressed()
        return {
            'shift': keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
            'ctrl': keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL],
            'alt': keys[pygame.K_LALT] or keys[pygame.K_RALT]
        }
