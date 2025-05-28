# SOLO CONQUEST - 2D Adventure Game & Map Editor

A 2D adventure game with a built-in map editor, featuring tile-based maps, enemy systems, and character progression.

## Project Structure

```
SOLO_TEST/
├── gameplay_app.py          # Main gameplay application
├── editor_app.py            # Main map editor application
├── game_core/               # Core game modules and packages
│   ├── settings.py          # Game settings and constants
│   ├── menu.py              # Menu and UI components
│   ├── base_screen.py       # Base screen class
│   ├── debug_utils.py       # Debug utilities
│   ├── performance_monitor.py # Performance monitoring
│   ├── font_manager.py      # Font management
│   ├── gameplay/            # Gameplay-specific modules
│   ├── edit_mode/           # Map editor modules
│   ├── character_system/    # Character and animation system
│   └── enemy_system/        # Enemy AI and management
├── Assets/                  # Game assets and sprites
├── character/               # Character sprites and animations
├── Enemies_Sprites/         # Enemy sprites and animations
├── Tilesets/               # Map tilesets and tiles
├── Menu Assets/            # Menu graphics and UI elements
├── fonts/                  # Game fonts
├── Maps/                   # Game maps and levels
├── SaveData/               # Save files and game state
└── world_icons/            # World/map icons
```

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

The project is organized into two independent applications with all supporting code in the `game_core/` folder:

### Gameplay Mode
```bash
python gameplay_app.py
```
- **Purpose**: Complete gaming experience for players
- **Features**: Splash screen, settings, map selection, and full gameplay
- **Interface**: Clean, player-focused interface without editor clutter
- **Dependencies**: Automatically imports required modules from `game_core/`

### Editor Mode
```bash
python editor_app.py
```
- **Purpose**: Map creation and editing tools for developers
- **Features**: Simplified splash screen with direct access to map editor
- **Interface**: Developer-focused interface without gameplay features
- **Dependencies**: Automatically imports required modules from `game_core/`

### Organized Structure Benefits
- ✅ **Clean Root Directory**: Only the two main applications in root
- ✅ **Modular Design**: All supporting code organized in `game_core/`
- ✅ **Easy Maintenance**: Related functionality grouped together
- ✅ **Clear Separation**: Gameplay and editor features completely separated
- ✅ **Asset Organization**: Game assets remain easily accessible in root

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
- **Tileset buttons**: Click to switch between tilesets
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
