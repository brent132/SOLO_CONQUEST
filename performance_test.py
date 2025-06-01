"""
Performance Test - Test frame rates at different zoom levels
"""
import pygame
import time
import sys
import os

# Add the game_core directory to the path
sys.path.append('game_core')

from gameplay.play_screen import PlayScreen

def test_zoom_performance():
    """Test performance at different zoom levels"""
    pygame.init()
    
    # Create a smaller window for testing
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Performance Test")
    clock = pygame.time.Clock()
    
    # Create PlayScreen instance
    play_screen = PlayScreen(800, 600)
    
    # Load a test world
    try:
        play_screen.load_map("firstlevel")
    except Exception as e:
        print(f"Error loading map: {e}")
        return
    
    # Test different zoom levels
    zoom_levels = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]
    test_duration = 3.0  # Test each zoom level for 3 seconds
    
    print("Starting zoom performance test...")
    print("=" * 50)
    
    for zoom in zoom_levels:
        print(f"\nTesting zoom level: {zoom}x")
        
        # Set zoom level
        play_screen.zoom_factor = zoom
        play_screen.grid_cell_size = int(play_screen.base_grid_cell_size * zoom)
        
        # Update map renderer grid size
        if hasattr(play_screen, 'map_system') and play_screen.map_system:
            if hasattr(play_screen.map_system, 'map_renderer'):
                play_screen.map_system.map_renderer.set_grid_size(play_screen.grid_cell_size)
        
        # Test performance for this zoom level
        frame_times = []
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
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
            
            # Record frame time
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            
            # Limit to 60 FPS max
            clock.tick(60)
        
        # Calculate statistics
        if frame_times:
            avg_frame_time = sum(frame_times) / len(frame_times)
            avg_fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            min_frame_time = min(frame_times)
            max_frame_time = max(frame_times)
            min_fps = 1.0 / max_frame_time if max_frame_time > 0 else 0
            max_fps = 1.0 / min_frame_time if min_frame_time > 0 else 0
            
            print(f"  Average FPS: {avg_fps:.1f}")
            print(f"  Min FPS: {min_fps:.1f}")
            print(f"  Max FPS: {max_fps:.1f}")
            print(f"  Frame count: {len(frame_times)}")
            
            # Check for performance issues
            if avg_fps < 30:
                print(f"  ⚠️  LOW PERFORMANCE at {zoom}x zoom!")
            elif avg_fps < 45:
                print(f"  ⚠️  Moderate performance issues at {zoom}x zoom")
            else:
                print(f"  ✅ Good performance at {zoom}x zoom")
        else:
            print(f"  ❌ No frames rendered at {zoom}x zoom")
    
    print("\n" + "=" * 50)
    print("Performance test completed!")
    
    pygame.quit()

if __name__ == "__main__":
    test_zoom_performance()
