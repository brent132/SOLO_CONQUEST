"""
UI Components for the Edit Mode - Legacy file, now imports from modular components.
This file is kept for backward compatibility.
"""

# Import all components from the new modular structure
from .buttons import Button, SaveButton, TextButton, TileButton
from .panels import LayerItem, LayerPanel, BrushPanel
from .inputs import TextInput, DropdownMenu
from .relations import RelationGroup, RelationComponent
from .scrollable import ScrollableTextArea

# Re-export all components for backward compatibility
__all__ = [
    'Button', 'SaveButton', 'TextButton', 'TileButton',
    'LayerItem', 'LayerPanel', 'BrushPanel',
    'TextInput', 'DropdownMenu',
    'RelationGroup', 'RelationComponent',
    'ScrollableTextArea'
]