"""
Edit Mode package - contains all components for the map editor

This package now includes modular UI components organized by functionality:
- buttons.py: Button components (Button, SaveButton, TextButton, TileButton)
- panels.py: Panel components (LayerItem, LayerPanel, BrushPanel)
- inputs.py: Input components (TextInput, DropdownMenu)
- relations.py: Relation components (RelationGroup, RelationComponent)
- scrollable.py: Scrollable components (ScrollableTextArea)
- ui_components.py: Legacy compatibility module that imports all components
"""
from edit_mode.editor import EditScreen

# Import all UI components for easy access
from .buttons import Button, SaveButton, TextButton, TileButton
from .panels import LayerItem, LayerPanel, BrushPanel
from .inputs import TextInput, DropdownMenu
from .relations import RelationGroup, RelationComponent
from .scrollable import ScrollableTextArea

# Export the main EditScreen class and all UI components
__all__ = [
    'EditScreen',
    # Button components
    'Button', 'SaveButton', 'TextButton', 'TileButton',
    # Panel components
    'LayerItem', 'LayerPanel', 'BrushPanel',
    # Input components
    'TextInput', 'DropdownMenu',
    # Relation components
    'RelationGroup', 'RelationComponent',
    # Scrollable components
    'ScrollableTextArea'
]
