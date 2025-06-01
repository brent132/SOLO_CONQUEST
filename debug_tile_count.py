"""
Debug Tile Count - Check how many tiles are being rendered at different zoom levels
"""
import pygame
import time
import sys
import os

# Add the game_core directory to the path
sys.path.append('game_core')

from gameplay.play_screen import PlayScreen

def debug_tile_count():
    """Debug how many tiles are being rendered at different zoom levels"""
    pygame.init()
    
    # Create a smaller window for testing
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Debug Tile Count")
    
    # Create PlayScreen instance
    play_screen = PlayScreen(800, 600)
    
    # Load a test world
    try:
        play_screen.load_map("firstlevel")
    except Exception as e:
        print(f"Error loading map: {e}")
        return
    
    # Test zoom levels that show performance issues
    zoom_levels = [1.0, 1.5, 2.0, 3.0, 4.0]
    
    print("Debugging tile count at different zoom levels...")
    print("=" * 70)
    
    for zoom in zoom_levels:
        print(f"\n🔍 Analyzing zoom level: {zoom}x")
        
        # Set zoom level
        play_screen.zoom_factor = zoom
        play_screen.grid_cell_size = int(play_screen.base_grid_cell_size * zoom)
        play_screen.zoom_factor_inv = 1.0 / zoom
        play_screen.effective_screen_width = play_screen.width * play_screen.zoom_factor_inv
        play_screen.effective_screen_height = play_screen.height * play_screen.zoom_factor_inv
        
        # Calculate visible range for debugging
        surface = screen
        camera_x = play_screen.camera_x
        camera_y = play_screen.camera_y
        center_offset_x = play_screen.center_offset_x
        center_offset_y = play_screen.center_offset_y
        
        # Calculate visible area
        visible_left = camera_x - center_offset_x
        visible_top = camera_y - center_offset_y
        visible_right = visible_left + surface.get_width()
        visible_bottom = visible_top + surface.get_height()
        
        # Convert to grid coordinates
        padding = max(1, 3 - int(play_screen.grid_cell_size / 16))
        start_x = max(0, (visible_left // play_screen.grid_cell_size) - padding)
        end_x = (visible_right // play_screen.grid_cell_size) + padding + 1
        start_y = max(0, (visible_top // play_screen.grid_cell_size) - padding)
        end_y = (visible_bottom // play_screen.grid_cell_size) + padding + 1
        
        tiles_to_render = (end_x - start_x) * (end_y - start_y)
        
        print(f"  📊 Grid cell size: {play_screen.grid_cell_size}px")
        print(f"  📐 Screen size: {surface.get_width()}x{surface.get_height()}px")
        print(f"  🎯 Visible area: {visible_right - visible_left}x{visible_bottom - visible_top}px")
        print(f"  📏 Tile range: ({int(start_x)}, {int(start_y)}) to ({int(end_x)}, {int(end_y)})")
        print(f"  🔢 Tiles to render: {int(tiles_to_render)}")
        print(f"  📦 Padding: {padding}")
        
        # Calculate how many layers we have
        if hasattr(play_screen.map_system.processor, 'layers') and play_screen.map_system.processor.layers:
            num_layers = len(play_screen.map_system.processor.layers)
            total_tile_operations = int(tiles_to_render) * num_layers
            print(f"  🎭 Number of layers: {num_layers}")
            print(f"  ⚡ Total tile operations: {total_tile_operations}")
            
            # Performance analysis
            if total_tile_operations > 50000:
                print(f"  ❌ EXCESSIVE tile operations: {total_tile_operations}")
            elif total_tile_operations > 20000:
                print(f"  ⚠️  High tile operations: {total_tile_operations}")
            else:
                print(f"  ✅ Reasonable tile operations: {total_tile_operations}")
        
        # Check if this explains the performance drop
        if zoom > 1.0:
            zoom_1x_tiles = (800 // 16 + 6) * (600 // 16 + 6)  # Approximate for 1.0x
            current_tiles = int(tiles_to_render)
            ratio = current_tiles / zoom_1x_tiles if zoom_1x_tiles > 0 else 0
            print(f"  📈 Tile count ratio vs 1.0x: {ratio:.2f}x")
            
            if ratio > 2.0:
                print(f"  ⚠️  Rendering {ratio:.1f}x more tiles than 1.0x zoom!")
    
    print("\n" + "=" * 70)
    print("Tile count analysis completed!")
    
    pygame.quit()

if __name__ == "__main__":
    debug_tile_count()
