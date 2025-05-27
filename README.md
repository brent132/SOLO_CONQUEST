# SOLO CONQUEST - 2D Adventure Game & Map Editor

A 2D adventure game with a built-in map editor, featuring tile-based maps, enemy systems, and character progression.

## Features

### Gameplay Features
- Top-down adventure gameplay
- Player character with combat mechanics
- Enemy AI system with multiple enemy types
- Item collection and inventory management
- Map teleportation and world system
- Save/load game state functionality
- Health and shield mechanics

### Editor Features
- Tile-based map editor with multiple layers
- Animated tiles support
- Enemy placement system
- Collision editing
- Save/load map functionality
- Multiple tileset support

## Application Modes

The game has two separate applications that can be launched independently:

### Gameplay Mode
```bash
python gameplay_app.py
```
- Launches the game with splash screen, settings, map selection, and gameplay
- Clean interface focused on playing the game
- No editor functionality to keep the interface simple for players

### Editor Mode
```bash
python editor_app.py
```
- Launches the map editor with a simplified splash screen
- Direct access to the map editing tools
- No gameplay features to keep the interface focused for developers

## Controls

### Gameplay Mode
- **WASD**: Move player character
- **Space**: Activate shield
- **Left click**: Attack
- **ESC**: Open/close inventory
- **1-0 keys**: Select inventory slots
- **Right click**: Interact with objects (chests, etc.)

### Editor Mode
- **Left click/drag**: Place tiles
- **Right click/drag**: Remove tiles
- **Mouse wheel**: Cycle through tiles
- **Arrow keys or WASD**: Move view
- **1-3 keys**: Switch between tilesets
- **P key**: Toggle tile preview

## Getting Started

### For Players
1. Run `python gameplay_app.py` to start the game
2. Click "Start" to select a world/map
3. Use WASD to move and explore the world

### For Map Creators
1. Run `python editor_app.py` to start the map editor
2. Click "Edit Mode" to access the map editor
3. Create maps, place tiles, enemies, and set up the player spawn point
4. Save your maps and test them by running `python gameplay_app.py`

## Requirements

- Python 3.x
- Pygame 2.5.0 or higher

You can install the required dependencies using:
```
pip install -r requirements.txt
```
"# SOLO_CONQUEST"
