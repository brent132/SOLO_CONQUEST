"""
Debug Zoom Performance - Investigate what's causing the frame drops
"""
import pygame
import time
import sys
import os

# Add the game_core directory to the path
sys.path.append('game_core')

from gameplay.play_screen import PlayScreen

def debug_zoom_performance():
    """Debug performance issues at different zoom levels"""
    pygame.init()
    
    # Create a smaller window for testing
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Debug Zoom Performance")
    clock = pygame.time.Clock()
    
    # Create PlayScreen instance
    play_screen = PlayScreen(800, 600)
    
    # Load a test world
    try:
        play_screen.load_map("firstlevel")
    except Exception as e:
        print(f"Error loading map: {e}")
        return
    
    # Test zoom levels that show performance issues
    zoom_levels = [1.0, 1.5, 2.0]
    
    print("Debugging zoom performance...")
    print("=" * 60)
    
    for zoom in zoom_levels:
        print(f"\n🔍 Analyzing zoom level: {zoom}x")
        
        # Set zoom level
        play_screen.zoom_factor = zoom
        play_screen.grid_cell_size = int(play_screen.base_grid_cell_size * zoom)
        
        # Calculate visible range for debugging
        surface = screen
        camera_x = play_screen.camera_x
        camera_y = play_screen.camera_y
        center_offset_x = 0
        center_offset_y = 0
        
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
        print(f"  📐 Visible area: {visible_right - visible_left}x{visible_bottom - visible_top}px")
        print(f"  🎯 Tile range: ({start_x}, {start_y}) to ({end_x}, {end_y})")
        print(f"  🔢 Tiles to render: {tiles_to_render}")
        print(f"  📏 Padding: {padding}")
        
        # Test a few frames to see performance
        frame_times = []
        for i in range(10):  # Test 10 frames
            frame_start = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
            
            # Update and render
            try:
                play_screen.update()
                play_screen.draw(screen)
                pygame.display.flip()
            except Exception as e:
                print(f"Error during update/draw: {e}")
                break
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            
            clock.tick(60)
        
        if frame_times:
            avg_frame_time = sum(frame_times) / len(frame_times)
            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            print(f"  ⚡ Average FPS: {avg_fps:.1f}")
            print(f"  ⏱️  Average frame time: {avg_frame_time*1000:.2f}ms")
            
            # Performance analysis
            if tiles_to_render > 10000:
                print(f"  ⚠️  Too many tiles to render: {tiles_to_render}")
            
            if avg_frame_time > 0.033:  # More than 33ms = less than 30 FPS
                print(f"  ❌ Performance issue detected!")
                print(f"     Frame time: {avg_frame_time*1000:.2f}ms (should be <16.67ms for 60fps)")
            else:
                print(f"  ✅ Good performance")
    
    print("\n" + "=" * 60)
    print("Debug completed!")
    
    pygame.quit()

if __name__ == "__main__":
    debug_zoom_performance()
