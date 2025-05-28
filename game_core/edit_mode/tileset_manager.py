"""
Tileset Manager - handles loading and managing tilesets
"""
import os
import pygame
from edit_mode.ui_components import TileButton
from gameplay.animated_tile_manager import AnimatedTileManager

class TilesetManager:
    """Manages loading and displaying tilesets"""
    def __init__(self, sidebar_width, map_area_width, grid_cell_size):
        self.sidebar_width = sidebar_width
        self.map_area_width = map_area_width
        self.grid_cell_size = grid_cell_size

        # Track when the sidebar position changes
        self.last_map_area_width = map_area_width

        # Initialize height for scroll calculations
        self.height = 720  # Default height

        # Scroll offset for the palette (not used for tile selection movement)
        self.scroll_offset_y = 0

        # Tileset folders and their original dimensions
        self.tileset_info = [
            {"folder": "Tilesets/Dungeon", "width": 192, "height": 208},  # 12x13 tiles (16x16 each)
            {"folder": "Tilesets/Overworld", "width": 288, "height": 208},  # 18x13 tiles (16x16 each)
            {"folder": "Enemies_Sprites", "width": 96, "height": 96}  # Enemy tileset (updated for 6 rows)
        ]

        self.tileset_buttons = []
        self.tileset_layouts = []  # Will store the layout info for each tileset

        # Initialize animated tile manager
        self.animated_tile_manager = AnimatedTileManager()

        # Add animated tiles to the tileset buttons
        self.animated_tile_buttons = []

        # Add enemy tiles to the tileset buttons
        self.enemy_tile_buttons = []

        # Load tilesets
        self.load_tilesets()

    def load_tilesets(self):
        """Load and process tilesets from individual tile files"""
        # Load tiles from each folder
        for i, tileset in enumerate(self.tileset_info):
            folder = tileset["folder"]
            try:
                buttons = []

                # Special handling for enemy tileset
                if i == 2:  # Enemy tileset (index 2)
                    # Load phantom enemy tiles
                    self.load_enemy_tileset(buttons)
                else:
                    # Regular tileset loading
                    # Get all PNG files in the folder
                    tile_files = [f for f in os.listdir(folder) if f.endswith('.png')]
                    tile_files.sort()  # Sort files to ensure consistent order

                    # Calculate grid dimensions based on original tileset dimensions
                    tiles_per_row = tileset["width"] // self.grid_cell_size

                    # Load each individual tile
                    for tile_file in tile_files:
                        tile_path = os.path.join(folder, tile_file)
                        try:
                            # Extract tile index from filename (assuming format like "tile123.png")
                            tile_index = int(tile_file.replace("tile", "").replace(".png", ""))

                            # Calculate original position in tileset
                            original_row = tile_index // tiles_per_row
                            original_col = tile_index % tiles_per_row

                            # Load the tile image
                            tile_img = pygame.image.load(tile_path).convert_alpha()

                            # Create a button for this tile (positions will be set later)
                            buttons.append({
                                'image': tile_img,
                                'source_path': tile_path,
                                'original_row': original_row,
                                'original_col': original_col,
                                'button': None  # Will be created when positioning buttons
                            })
                        except Exception as e:
                            print(f"Error loading tile {tile_path}: {e}")

                self.tileset_buttons.append(buttons)
                self.tileset_layouts.append({
                    "tiles_per_row": tiles_per_row if i != 2 else 6,  # 6 tiles per row for enemy tileset
                    "total_rows": tileset["height"] // self.grid_cell_size
                })
                # Loaded tiles successfully
            except Exception as e:
                print(f"Error loading tileset folder {folder}: {e}")

        # Load animated tiles
        self.load_animated_tiles()

    def load_enemy_tileset(self, buttons):
        """Load enemy tiles into the enemy tileset"""
        # Load player character tile in a separate row for better visibility
        player_path = "character/char_idle_down/tile000.png"
        if os.path.exists(player_path):
            try:
                player_image = pygame.image.load(player_path).convert_alpha()
                buttons.append({
                    'image': player_image,
                    'source_path': player_path,
                    'original_row': 0,  # Place in first row
                    'original_col': 0,  # First column
                    'button': None,
                    'is_player': True,
                    'is_enemy': False,
                    'player_direction': "down"  # Default direction
                })
                # Player tile loaded successfully
            except Exception as e:
                print(f"Error loading player tile: {e}")

        # Load phantom enemy - right facing
        phantom_right_path = "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_right/tile000.png"
        if os.path.exists(phantom_right_path):
            try:
                phantom_right_image = pygame.image.load(phantom_right_path).convert_alpha()
                buttons.append({
                    'image': phantom_right_image,
                    'source_path': phantom_right_path,
                    'original_row': 1,  # Place in second row
                    'original_col': 0,
                    'button': None,
                    'is_enemy': True,
                    'is_player': False,
                    'enemy_type': "phantom_right"
                })
            except Exception as e:
                print(f"Error loading phantom right enemy tile: {e}")

        # Load phantom enemy - left facing
        phantom_left_path = "Enemies_Sprites/Phantom_Sprites/phantom_idle_anim_left/tile000.png"
        if os.path.exists(phantom_left_path):
            try:
                phantom_left_image = pygame.image.load(phantom_left_path).convert_alpha()
                buttons.append({
                    'image': phantom_left_image,
                    'source_path': phantom_left_path,
                    'original_row': 1,  # Place in second row
                    'original_col': 1,
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "phantom_left"
                })
            except Exception as e:
                print(f"Error loading phantom left enemy tile: {e}")

        # Load bomberplant enemy
        bomberplant_path = "Enemies_Sprites/Bomberplant_Sprites/bomberplant_idle_anim_all_dir/tile000.png"
        if os.path.exists(bomberplant_path):
            try:
                bomberplant_image = pygame.image.load(bomberplant_path).convert_alpha()
                buttons.append({
                    'image': bomberplant_image,
                    'source_path': bomberplant_path,
                    'original_row': 2,  # Place in third row
                    'original_col': 0,
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "bomberplant"
                })
            except Exception as e:
                print(f"Error loading bomberplant enemy tile: {e}")

        # Load spinner enemy
        spinner_path = "Enemies_Sprites/Spinner_Sprites/spinner_idle_anim_all_dir/tile000.png"
        if os.path.exists(spinner_path):
            try:
                spinner_image = pygame.image.load(spinner_path).convert_alpha()
                buttons.append({
                    'image': spinner_image,
                    'source_path': spinner_path,
                    'original_row': 2,  # Place in third row
                    'original_col': 1,  # Next to bomberplant
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "spinner"
                })
            except Exception as e:
                print(f"Error loading spinner enemy tile: {e}")

        # Load spider enemy
        spider_path = "Enemies_Sprites/Spider_Sprites/spider_idle_anim_all_dir/tile000.png"
        if os.path.exists(spider_path):
            try:
                spider_image = pygame.image.load(spider_path).convert_alpha()
                buttons.append({
                    'image': spider_image,
                    'source_path': spider_path,
                    'original_row': 3,  # Place in fourth row to avoid overlap
                    'original_col': 0,  # First column in the new row
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "spider"
                })
            except Exception as e:
                print(f"Error loading spider enemy tile: {e}")

        # Load pinkslime enemy
        pinkslime_path = "Enemies_Sprites/Pinkslime_Sprites/pinkslime_idle_anim_all_dir/tile000.png"
        if os.path.exists(pinkslime_path):
            try:
                pinkslime_image = pygame.image.load(pinkslime_path).convert_alpha()
                buttons.append({
                    'image': pinkslime_image,
                    'source_path': pinkslime_path,
                    'original_row': 3,  # Place in fourth row
                    'original_col': 1,  # Second column in the fourth row
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "pinkslime"
                })
            except Exception as e:
                print(f"Error loading pinkslime enemy tile: {e}")

        # Load pinkbat enemy - left facing
        pinkbat_left_path = "Enemies_Sprites/Pinkbat_Sprites/pinkbat_idle_left_anim/tile000.png"
        if os.path.exists(pinkbat_left_path):
            try:
                pinkbat_left_image = pygame.image.load(pinkbat_left_path).convert_alpha()
                buttons.append({
                    'image': pinkbat_left_image,
                    'source_path': pinkbat_left_path,
                    'original_row': 4,  # Place in fifth row
                    'original_col': 0,  # First column in the fifth row
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "pinkbat_left"
                })
            except Exception as e:
                print(f"Error loading pinkbat left enemy tile: {e}")

        # Load pinkbat enemy - right facing
        pinkbat_right_path = "Enemies_Sprites/Pinkbat_Sprites/pinkbat_idle_right_anim/tile000.png"
        if os.path.exists(pinkbat_right_path):
            try:
                pinkbat_right_image = pygame.image.load(pinkbat_right_path).convert_alpha()
                buttons.append({
                    'image': pinkbat_right_image,
                    'source_path': pinkbat_right_path,
                    'original_row': 4,  # Place in fifth row
                    'original_col': 1,  # Second column in the fifth row
                    'button': None,
                    'is_enemy': True,
                    'enemy_type': "pinkbat_right"
                })
            except Exception as e:
                print(f"Error loading pinkbat right enemy tile: {e}")

    def load_animated_tiles(self):
        """Load animated tiles and add them to the tileset buttons"""
        # Create a new row for animated tiles
        animated_buttons = []

        # Get all animated tiles from the manager
        for tile_id, tile_name in self.animated_tile_manager.animated_tile_ids.items():
            animated_tile = self.animated_tile_manager.get_animated_tile_by_id(tile_id)
            if animated_tile and animated_tile.frames:
                # Use the first frame as the preview image, or a custom preview if available
                if hasattr(self.animated_tile_manager, 'editor_preview_frames') and tile_name in self.animated_tile_manager.editor_preview_frames:
                    # Use custom preview frame for this tile
                    preview_frame = self.animated_tile_manager.editor_preview_frames[tile_name]
                else:
                    # Use the first frame as the preview image
                    preview_frame = animated_tile.frames[0]

                # Create a button for this animated tile (positions will be set later)
                animated_buttons.append({
                    'image': preview_frame,
                    'source_path': f"animated:{tile_name}",  # Special prefix to identify animated tiles
                    'original_row': 0,  # All animated tiles will be in the first row
                    'original_col': len(animated_buttons),  # Column based on order
                    'button': None,  # Will be created when positioning buttons
                    'animated_tile_id': tile_id  # Store the animated tile ID
                })
                # Animated tile added successfully

        # Add animated tiles as a separate "tileset"
        if animated_buttons:
            self.animated_tile_buttons = animated_buttons
            # All animated tiles loaded successfully



    def position_tileset_buttons(self, selected_tileset_index, start_y=155):
        """Position the tileset buttons in the sidebar to match original tileset layout"""
        if not self.tileset_buttons or not self.tileset_layouts or selected_tileset_index >= len(self.tileset_buttons):
            return

        # Check if map_area_width has changed (window resized)
        if self.map_area_width != self.last_map_area_width:
            self.last_map_area_width = self.map_area_width

        # Only show buttons for the currently selected tileset
        buttons = self.tileset_buttons[selected_tileset_index]
        layout = self.tileset_layouts[selected_tileset_index]

        # Get the original tileset dimensions
        tiles_per_row = layout["tiles_per_row"]

        # Use a 1.5x scale factor as requested
        button_size = self.grid_cell_size
        scale_factor = 1.5  # 1.5x scale up

        # Calculate available width for the tileset
        available_width = self.sidebar_width - 60  # 30px padding on each side

        # Adjust button size
        display_button_size = int(button_size * scale_factor)

        # Position each button according to its original position in the tileset
        start_x = self.map_area_width + 30  # Increased left padding

        # Check if we can fit the entire tileset width with the 1.5x scale
        tileset_width_scaled = tiles_per_row * display_button_size

        # Center the tileset in the available width if it fits
        if tileset_width_scaled <= available_width:
            # Calculate the starting x position to center the tileset
            start_x = self.map_area_width + (self.sidebar_width - tileset_width_scaled) // 2



        # Position each button according to its original position in the tileset
        for button_data in buttons:
            # Get the original position
            row = button_data['original_row']
            col = button_data['original_col']

            # Calculate position in the sidebar - maintain original layout
            x = start_x + col * display_button_size
            y = start_y + row * display_button_size

            # Create a scaled version of the image
            scaled_image = pygame.transform.scale(
                button_data['image'],
                (display_button_size, display_button_size)
            )

            # Create or update the button with the scaled image
            button_data['button'] = TileButton(x, y, display_button_size, display_button_size, scaled_image)

        # Special case: If we're on the last tileset, also position animated tiles
        if selected_tileset_index == len(self.tileset_buttons) - 1 and self.animated_tile_buttons:
            # Position animated tiles in a new row below the regular tileset
            animated_start_y = start_y + (layout["total_rows"] + 1) * display_button_size

            # Add a header for animated tiles
            self.animated_header_y = animated_start_y - 30

            # Calculate how many animated tiles can fit in a row
            animated_tiles_per_row = min(tiles_per_row, len(self.animated_tile_buttons))

            # Position each animated tile button
            for i, button_data in enumerate(self.animated_tile_buttons):
                # Calculate row and column for the animated tile
                row = i // animated_tiles_per_row
                col = i % animated_tiles_per_row

                # Calculate position
                x = start_x + col * display_button_size
                y = animated_start_y + row * display_button_size

                # Create a scaled version of the image
                scaled_image = pygame.transform.scale(
                    button_data['image'],
                    (display_button_size, display_button_size)
                )

                # Create or update the button with the scaled image
                button_data['button'] = TileButton(x, y, display_button_size, display_button_size, scaled_image)

    def draw_tileset(self, surface, selected_tileset_index):
        """Draw the currently selected tileset"""
        if selected_tileset_index >= len(self.tileset_buttons) or selected_tileset_index >= len(self.tileset_layouts):
            return

        buttons = self.tileset_buttons[selected_tileset_index]

        # Draw border around the entire tileset
        if buttons and len(buttons) > 0:
            # Find the first and last button to determine the bounds
            first_button = None
            max_right = 0
            max_bottom = 0

            for button_data in buttons:
                button = button_data['button']
                if button:
                    if first_button is None:
                        first_button = button
                    max_right = max(max_right, button.rect.right)
                    max_bottom = max(max_bottom, button.rect.bottom)

            if first_button:
                # Draw border around the entire tileset
                tileset_rect = pygame.Rect(
                    first_button.rect.left - 2,
                    first_button.rect.top - 2,
                    max_right - first_button.rect.left + 4,
                    max_bottom - first_button.rect.top + 4
                )
                pygame.draw.rect(surface, (100, 100, 100), tileset_rect, 2)

        # Draw all buttons
        for button_data in buttons:
            button = button_data['button']
            if button:
                button.draw(surface)

                # Add a highlight for the player character tile (but no text)
                if selected_tileset_index == 2 and button_data.get('is_player'):
                    # Draw a highlight around the player character tile
                    pygame.draw.rect(surface, (0, 255, 0), button.rect, 2)

        # Special case: If we're on the last tileset, also draw animated tiles
        if selected_tileset_index == len(self.tileset_buttons) - 1 and self.animated_tile_buttons:
            # Draw animated tile buttons (no header text)
            for button_data in self.animated_tile_buttons:
                if button_data['button']:
                    button_data['button'].draw(surface)

    def get_tileset_name(self, index):
        """Get the name of the tileset at the given index"""
        if 0 <= index < len(self.tileset_info):
            return self.tileset_info[index]["folder"].split('/')[-1]
        return "Unknown"

    def handle_tileset_click(self, event, mouse_pos, selected_tileset_index):
        """Handle clicks on the tileset buttons"""
        if selected_tileset_index >= len(self.tileset_buttons):
            return None

        # First check regular tileset buttons
        buttons = self.tileset_buttons[selected_tileset_index]
        for button_data in buttons:
            button = button_data['button']
            if button:
                button.update(mouse_pos)
                if event.type == pygame.MOUSEBUTTONDOWN and button.is_clicked(event):
                    # Deselect all buttons (regular and animated)
                    for b_data in buttons:
                        if b_data['button']:
                            b_data['button'].is_selected = False

                    for b_data in self.animated_tile_buttons:
                        if b_data['button']:
                            b_data['button'].is_selected = False

                    # Select this button
                    button.is_selected = True
                    return button_data

        # If we're on the last tileset, also check animated tile buttons
        if selected_tileset_index == len(self.tileset_buttons) - 1 and self.animated_tile_buttons:
            for button_data in self.animated_tile_buttons:
                button = button_data['button']
                if button:
                    button.update(mouse_pos)
                    if event.type == pygame.MOUSEBUTTONDOWN and button.is_clicked(event):
                        # Deselect all buttons (regular and animated)
                        for b_data in buttons:
                            if b_data['button']:
                                b_data['button'].is_selected = False

                        for b_data in self.animated_tile_buttons:
                            if b_data['button']:
                                b_data['button'].is_selected = False

                        # Select this button
                        button.is_selected = True
                        # Make sure the animated_tile_id is included in the returned data
                        if 'animated_tile_id' not in button_data:
                            button_data['animated_tile_id'] = button_data.get('animated_tile_id', 0)
                        return button_data

        return None