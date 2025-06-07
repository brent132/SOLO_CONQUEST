# SOLO CONQUEST - Map Editor

A lightweight tile-based map editor built with Pygame. Gameplay code has been
removed for now, leaving only the editor tools.

## Project Structure

```
SOLO_CONQUEST/
├── editor_app.py            # Entry point for the map editor
├── game_core/               # Editor modules and utilities
│   ├── editor/              # Editor package
│   └── font_loader.py       # Font management helper
├── Assets/                  # Raw tilesets and sprites
├── Enemies_Sprites/         # Enemy animation frames
├── Tilesets/                # Processed tilesets used by the editor
├── character/               # Player sprite sheets
├── fonts/                   # Font files used by the UI
├── requirements.txt         # Python dependencies
└── README.md
```

## Features

### Editor Features
- Tile-based map editor with multiple layers
- Animated tiles support
- Enemy placement system
- Collision editing
- Save/load map functionality
- Multiple tileset support

## Application Mode

Only the map editor is included. Run the application with:
```bash
python editor_app.py
```
This launches the editor window for creating tile-based maps.

### Organized Structure Benefits
- ✅ **Clean Root Directory**: Only one entry point and supporting modules
- ✅ **Modular Design**: Editor functionality organized in `game_core/`
- ✅ **Asset Organization**: Sprites and tilesets kept in separate folders

## Controls

### Editor Mode
- **Left click/drag**: Place tiles
- **Right click/drag**: Remove tiles
- **Mouse wheel**: Cycle through tiles
- **Arrow keys or WASD**: Move view
- **Tileset buttons**: Click to switch between tilesets
- **P key**: Toggle tile preview

## Getting Started

### Running the Editor
1. Run `python editor_app.py` to start the map editor
2. Click "Edit Mode" to access the tools
3. Create maps, place tiles, enemies, and set up the player spawn point
4. Save your maps to reuse them later

## Requirements

- Python 3.x
- Pygame 2.5.0 or higher

You can install the required dependencies using:
```
pip install -r requirements.txt
```

## Commenting Guideline
All Python modules contain brief comments explaining their logic.
When you add new code, follow this style and include clear docstrings and inline notes.
